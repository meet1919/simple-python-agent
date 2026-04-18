import os
from typing import List, Dict, Any, Optional, Tuple
from openai import AsyncOpenAI
import json

class LLMClient:
    def __init__(self, main_model: str = "gpt-4o", fast_model: str = "gpt-4o-mini"):
        """
        Defaults to reasoning models, but uses API Key from environment.
        """
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.main_model = main_model
        self.fast_model = fast_model

    async def call(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        use_fast: bool = False
    ):
        model = self.fast_model if use_fast else self.main_model
        
        system_msg = [{"role": "system", "content": system}]
        full_messages = system_msg + messages

        kwargs = {
            "model": model,
            "messages": full_messages,
        }
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
            
        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message
