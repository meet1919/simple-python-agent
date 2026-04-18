from core.models import Skill
from core.llm import LLMClient
from core.context import ContextManager
from core.registry import ToolRegistry, SkillRegistry
from core.router import SkillRouter
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
        self.skill_router = SkillRouter(self.skill_registry)
        self.pfc_tool = PFCSubAgent(self.llm)
        
        base_persona = "You are a helpful, smart AI agent. You have access to specialized skills and tools."
        self.context = ContextManager(agent_persona=base_persona, llm_client=self.llm)

    async def run(self, user_input: str):
        # 1. Router runs once (fast & cheap check)
        skill = await self.skill_router.route(user_input, self.context)
        
        if not skill and "general" in self.skill_registry.skills:
            skill = self.skill_registry.skills["general"]

        if skill:
            console.print(f"\n[dim italic #A3BE8C]Router engaged skill: {skill.name}[/]")

        planning_input = user_input
        
        if skill and getattr(skill, "requires_pfc", False):
            console.print("\n[dim italic #A3BE8C]PFC Subagent intercepting to refine prompt...[/]")
            pfc_output = await self.pfc_tool.run(
                raw_input=user_input,
                skill_context=skill.name,
                chat_history=self.context.recent_messages
            )
            
            if pfc_output.confidence == "low" and pfc_output.ambiguities:
                return f"Before I proceed, I need to ask: {pfc_output.ambiguities[0]}"
                
            # Formatting the planning input with summarized thinking as requested by the user.
            planning_input = f"Refined Intent: {pfc_output.refined_intent}\n" \
                             f"PFC Summarized Thinking:\n{pfc_output.thinking_path}\n"
                             
            if pfc_output.ambiguities and pfc_output.confidence == "medium":
                planning_input += f"\nAssumptions & Ambiguities Identified: {pfc_output.assumptions} / {pfc_output.ambiguities}"

            # Print observability panel
            console.print(Panel(
                f"[#A3BE8C]Refined Intent:[/] {pfc_output.refined_intent}\n"
                f"[#A3BE8C]Thinking Path:[/] {pfc_output.thinking_path}\n"
                f"[#A3BE8C]Confidence:[/] {pfc_output.confidence}",
                title="[bold #A3BE8C]PFC Output[/]",
                border_style="#A3BE8C",
                padding=(0, 2)
            ))

        system = self.context.build_system_prompt(skill, extra=planning_input)
        
        active_tools = []
        if skill:
            active_tools = self.registry.schemas_for(skill.allowed_tools)

        self.context.append_user(user_input)

        iteration = 0
        while iteration < MAX_ITERATIONS:
            iteration += 1
            
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
                self.context.append_tool_result(call.id, result, call.function.name)

            # Step 3: Guard memory size
            if self.context.token_count() > BUDGET * 0.85:
                await self.context.compact()
                
        return "Max iterations reached. Ending current execution loop."
