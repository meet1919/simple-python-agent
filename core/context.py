from typing import List, Dict, Any
from core.models import Skill, Message
from core.llm import LLMClient
import tiktoken

class ContextManager:
    def __init__(self, agent_persona: str, llm_client: LLMClient):
        self.agent_persona = agent_persona
        self.llm_client = llm_client
        self.recent_messages: List[Message] = []
        self.compacted_summary: str = ""
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def build_system_prompt(self, skill: Skill = None, extra: str = None) -> str:
        parts = [self.agent_persona]
        if skill:
            parts.append(skill.instructions)
        if extra:
            parts.append(f"### PFC Planning Input / Refined Context ###\n{extra}")
        return "\n\n---\n\n".join(parts)

    def build_messages(self) -> List[Dict[str, Any]]:
        messages = []
        if self.compacted_summary:
            messages.append({
                "role": "user",
                "content": f"[Earlier in this session: {self.compacted_summary}]"
            })
            messages.append({"role": "assistant", "content": "Understood."})
            
        messages.extend([m.to_dict() for m in self.recent_messages])
        return messages

    def append_user(self, content: str):
        self.recent_messages.append(Message(role="user", content=content))

    def append_assistant(self, message_obj):
        # Handle the LLM message object which might have tool calls
        tool_calls = None
        if hasattr(message_obj, "tool_calls") and message_obj.tool_calls:
            tool_calls = []
            for tc in message_obj.tool_calls:
                tool_calls.append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })
        self.recent_messages.append(Message(
            role="assistant",
            content=getattr(message_obj, "content", None),
            tool_calls=tool_calls
        ))

    def append_tool_result(self, tool_call_id: str, content: str, name: str):
        self.recent_messages.append(Message(
            role="tool",
            tool_call_id=tool_call_id,
            content=content,
            name=name
        ))

    def token_count(self) -> int:
        # Rough estimation
        text = ""
        if self.compacted_summary:
            text += self.compacted_summary
        for m in self.recent_messages:
            if m.content:
                text += m.content
        return len(self.encoding.encode(text))

    async def compact(self):
        # Keep recent messages, compress the rest. Find a safe split point around -6.
        if len(self.recent_messages) <= 6:
            return
            
        target_split = len(self.recent_messages) - 6
        
        # Move backwards to ensure we don't sever a tool call from its assistant generator
        while target_split > 0 and self.recent_messages[target_split].role == "tool":
            target_split -= 1
            
        if target_split <= 0:
            return # Cannot reliably compact without breaking context
            
        to_compact = self.recent_messages[:target_split]
        self.recent_messages = self.recent_messages[target_split:]
        
        text_to_summarize = ""
        for m in to_compact:
            text_to_summarize += f"{m.role.upper()}: {m.content or '[Tool Calls]'}\n"
            
        summary_prompt = "You are an assistant memory module. Summarize the following past conversation succinctly, keeping all critical facts, URLs, IDs, and tool execution outcomes. Retain the previous summary context."
        if self.compacted_summary:
            text_to_summarize = f"PREVIOUS SUMMARY: {self.compacted_summary}\n\nNEW CONVERSATION:\n{text_to_summarize}"
            
        # We call the fast LLM to summarize
        response = await self.llm_client.call(
            system=summary_prompt,
            messages=[{"role": "user", "content": text_to_summarize}],
            use_fast=True
        )
        self.compacted_summary = response.content
