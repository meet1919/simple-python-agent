import json
import os
from typing import List
from core.models import PFCOutput, Message
from core.llm import LLMClient

class PFCSubAgent:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.pfc_instructions = self._load_pfc_instructions()
        
    def _load_pfc_instructions(self) -> str:
        path = os.path.join(os.path.dirname(__file__), "..", "skills", "prefrontal-cortex", "SKILL.md")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        return parts[2].strip()
                return content
        return "You are a PFC (Prefrontal Cortex) reasoning Subagent. Analyze the request, identify assumptions and ambiguities, and refine the intent."

    async def run(self, raw_input: str, skill_context: str, chat_history: List[Message]) -> PFCOutput:
        schema = {
            "name": "submit_pfc_output",
            "description": "Submit the structured cognitive evaluation of the user request.",
            "parameters": {
                "type": "object",
                "properties": {
                    "refined_intent": {"type": "string", "description": "De-chunked, precise description of the goal"},
                    "assumptions": {"type": "array", "items": {"type": "string"}},
                    "ambiguities": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                    "thinking_path": {"type": "string", "description": "Summary of reasoning through WMM, TI, IC, MC"},
                    "structural_signature": {
                        "type": "object",
                        "description": "A dictionary of 3-5 key-value pairs defining the abstract structure of the task, ignoring specific content (e.g. {'workflow_type': 'file_editing', 'requires_search': true})."
                    }
                },
                "required": ["refined_intent", "assumptions", "ambiguities", "confidence", "thinking_path", "structural_signature"]
            }
        }
        
        system = (
            f"{self.pfc_instructions}\n\n"
            f"You are acting as the cognitive preprocessing subagent for the '{skill_context}' skill. "
            f"Review the past context and the latest user prompt.\n"
            f"Use the WMM, TI, IC, MC framework to translate the vague intent into a precise spec. "
            f"Identify any risky assumptions or ambiguities. Return your analysis using the tool call."
        )
        
        messages = []
        for m in chat_history:
            if m.content and m.role in ["user", "assistant"]:
                messages.append({"role": m.role, "content": m.content})
                
        messages.append({"role": "user", "content": raw_input})
        
        response = await self.llm_client.call(
            system=system,
            messages=messages[-5:], # Keep it focused
            tools=[{"type": "function", "function": schema}],
            use_fast=True
        )
        
        if response.tool_calls:
            call = response.tool_calls[0]
            args = json.loads(call.function.arguments)
            return PFCOutput(
                refined_intent=args.get("refined_intent", raw_input),
                assumptions=args.get("assumptions", []),
                ambiguities=args.get("ambiguities", []),
                confidence=args.get("confidence", "high"),
                thinking_path=args.get("thinking_path", ""),
                structural_signature=args.get("structural_signature", {})
            )
            
        # Fallback if no tool called
        return PFCOutput(raw_input, [], [], "high", "Fallback execution.", {})
