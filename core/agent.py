from core.models import Skill
from core.llm import LLMClient
from core.context import ContextManager
from core.registry import ToolRegistry, SkillRegistry
# Removed unused import
from core.pfc import PFCSubAgent
from rich.console import Console
from rich.panel import Panel

console = Console()

BUDGET = 4000
MAX_ITERATIONS = 10

class MasterAgent:
    def __init__(self, tools: ToolRegistry, skills_dir: str):
        self.llm = LLMClient()
        self.registry = tools
        self.skill_registry = SkillRegistry(skills_dir)
        self.pfc_tool = PFCSubAgent(self.llm)
        
        menu_xml = self.skill_registry.generate_available_skills_xml()
        base_persona = f"You are a helpful, smart AI agent. You have access to specialized skills and tools.\n\n{menu_xml}"
        self.context = ContextManager(agent_persona=base_persona, llm_client=self.llm)
        
        self.current_skill_tools = []
        self.global_tools = ["read_skill_documentation", "reflect"]
        
        # Register the dynamic JIT skill reader
        self.registry.register(
            "read_skill_documentation", 
            self._read_skill_documentation_tool, 
            {
                "name": "read_skill_documentation", 
                "description": "Read the documentation of a specific skill by its file path. ALWAYS call this tool first if a relevant skill exists in available_skills.", 
                "parameters": {
                    "type": "object", 
                    "properties": {"file_path": {"type": "string"}}, 
                    "required": ["file_path"]
                }
            }
        )

    async def _read_skill_documentation_tool(self, file_path: str) -> str:
        console.print(f"\n[dim italic #A3BE8C]Dynamically loading skill: {file_path}[/]")
        skill = None
        for s in self.skill_registry.skills.values():
            if s.file_path == file_path:
                skill = s
                break
                
        if not skill:
            return f"Error: Skill not found at {file_path}"
            
        self.current_skill_tools = skill.allowed_tools
        if self.current_skill_tools:
            console.print(f"[dim italic #81A1C1]Bound skill-specific tools: {', '.join(self.current_skill_tools)}[/]")
        else:
            console.print(f"[dim italic #81A1C1]Skill loaded, no specific tools required.[/]")
            
        content = skill.instructions
        
        if skill.requires_pfc:
            console.print(f"\n[dim italic #A3BE8C]Skill requires PFC. Running cognitive preprocessing...[/]")
            
            # Find the most recent user message
            raw_input = "Unknown user request"
            for msg in reversed(self.context.recent_messages):
                if msg.role == "user" and msg.content:
                    raw_input = msg.content
                    break
                    
            pfc_output = await self.pfc_tool.run(
                raw_input=raw_input,
                skill_context=skill.name,
                chat_history=self.context.recent_messages
            )
            
            console.print(Panel(
                f"[#A3BE8C]Refined Intent:[/] {pfc_output.refined_intent}\n"
                f"[#A3BE8C]Thinking Path:[/] {pfc_output.thinking_path}\n"
                f"[#A3BE8C]Confidence:[/] {pfc_output.confidence}",
                title="[bold #A3BE8C]PFC Output (Injected)[/]",
                border_style="#A3BE8C",
                padding=(0, 2)
            ))

            if pfc_output.confidence == "low" and pfc_output.ambiguities:
                return f"Before I proceed, I need to ask: {pfc_output.ambiguities[0]}"
                
            pfc_text = f"\n\n### AUTOMATIC PFC COGNITIVE ANALYSIS ###\n" \
                       f"Refined Intent: {pfc_output.refined_intent}\n" \
                       f"Thinking Path: \n{pfc_output.thinking_path}\n" \
                       f"Confidence: {pfc_output.confidence}\n"
            if pfc_output.ambiguities and pfc_output.confidence == "medium":
                pfc_text += f"Assumptions & Ambiguities: {pfc_output.assumptions} / {pfc_output.ambiguities}\n"
                
            content += pfc_text
            
        return content

    async def run(self, user_input: str):
        self.context.append_user(user_input)
        
        system = self.context.build_system_prompt()
        
        iteration = 0
        while iteration < MAX_ITERATIONS:
            iteration += 1
            
            allowed_tool_names = [t for t in self.global_tools if t in self.registry._schemas]
            allowed_tool_names.extend([t for t in self.current_skill_tools if t in self.registry._schemas])
            allowed_tool_names = list(set(allowed_tool_names))
            
            active_tools = self.registry.schemas_for(allowed_tool_names)
            
            # Step 1: LLM Call
            response = await self.llm.call(
                system=system,
                messages=self.context.build_messages(),
                tools=active_tools if active_tools else None
            )
            
            self.context.append_assistant(response)

            # Step 2: Tool Execution if needed
            if not getattr(response, "tool_calls", None):
                # Text response received, terminate loop
                return response.content

            for call in response.tool_calls:
                console.print(f"\n[dim italic #81A1C1]Calling tool: {call.function.name}[/]")
                result = await self.registry.dispatch(
                    tool_call_id=call.id,
                    name=call.function.name,
                    arguments=call.function.arguments
                )
                if call.function.name == "reflect":
                    console.print(f"[dim italic #81A1C1]Reflection result: {result}[/]")
                    
                self.context.append_tool_result(call.id, result, call.function.name)

            # Step 3: Guard memory size
            if self.context.token_count() > BUDGET * 0.85:
                await self.context.compact()
                
        return "Max iterations reached. Ending current execution loop."
