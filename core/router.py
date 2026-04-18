from typing import Optional
from core.models import Skill
from core.registry import SkillRegistry
from core.context import ContextManager
import json

class SkillRouter:
    def __init__(self, skill_registry: SkillRegistry):
        self.registry = skill_registry

    async def route(self, user_input: str, context: ContextManager) -> Optional[Skill]:
        if not self.registry.skills:
            return None
            
        system = (
            "You are a router. Given the conversation context and the next user input, "
            "select the most appropriate skill to handle the request. "
            "Output ONLY a JSON array with one element, the name of the selected skill. "
            "Example: [\"general\"]\n\nAvailable skills:\n"
        )
        
        for name, skill in self.registry.skills.items():
            system += f"- {name}: {skill.description}\n"

        # Using fast model to route
        # Pass a minimized context (just last 2 conversational messages)
        conversational_msgs = []
        for m in context.recent_messages:
            if m.role in ["user", "assistant"] and m.content:
                conversational_msgs.append({"role": m.role, "content": m.content})
                
        messages_for_routing = conversational_msgs[-2:]
            
        messages_for_routing.append({"role": "user", "content": user_input})

        response = await context.llm_client.call(
            system=system,
            messages=messages_for_routing,
            use_fast=True
        )

        try:
            content = response.content.replace('```json', '').replace('```', '').strip()
            skill_name = json.loads(content)[0]
            return self.registry.skills.get(skill_name)
        except Exception:
            return None # Default fallback
