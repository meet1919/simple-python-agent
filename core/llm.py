import os
import json
import uuid
from typing import List, Dict, Any, Optional, Tuple

class UnifiedFunction:
    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments

class UnifiedToolCall:
    def __init__(self, id: str, function: UnifiedFunction):
        self.id = id
        self.type = "function"
        self.function = function

class UnifiedMessage:
    def __init__(self, content: Optional[str], tool_calls: Optional[List[UnifiedToolCall]] = None):
        self.content = content
        self.tool_calls = tool_calls or []

class LLMClient:
    def __init__(self, model_name: str = "gpt-5.4-mini", fast_model: str = "gpt-5.4-nano"):
        """
        Defaults to reasoning models, but uses API Key from environment.
        Supports multiple providers: gpt, claude, gemini, kimi, llama.
        """
        self.model_name = model_name
        self.fast_model = fast_model

    async def call(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        use_fast: bool = False
    ) -> UnifiedMessage:
        model = self.fast_model if use_fast else self.model_name
        provider = self._determine_provider(model)

        from rich.console import Console
        console = Console()
        
        with console.status(f"[dim]Reasoning with {provider} ({model})...[/]", spinner="dots"):
            if provider in ["gpt", "kimi", "llama"]:
                return await self._call_openai(provider, model, system, messages, tools)
            elif provider == "claude":
                return await self._call_claude(model, system, messages, tools)
            elif provider == "gemini":
                return await self._call_gemini(model, system, messages, tools)
            else:
                raise ValueError(f"Unsupported provider for model: {model}")

    def _determine_provider(self, model: str) -> str:
        model_low = model.lower()
        if "gpt" in model_low: return "gpt"
        if "claude" in model_low: return "claude"
        if "gemini" in model_low: return "gemini"
        if "moonshot" in model_low or "kimi" in model_low: return "kimi"
        if "llama" in model_low or "meta" in model_low: return "llama"
        return "gpt"

    async def _call_openai(self, provider: str, model: str, system: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]]) -> UnifiedMessage:
        from openai import AsyncOpenAI
        
        if provider == "kimi":
            client = AsyncOpenAI(api_key=os.getenv("MOONSHOT_API_KEY"), base_url="https://api.moonshot.cn/v1")
        elif provider == "llama":
            client = AsyncOpenAI(api_key=os.getenv("DEEPINFRA_API_KEY"), base_url="https://api.deepinfra.com/v1/openai")
        else:
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        system_msg = [{"role": "system", "content": system}]
        full_messages = system_msg + messages

        kwargs = {
            "model": model,
            "messages": full_messages,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = await client.chat.completions.create(**kwargs)
        msg = response.choices[0].message
        
        tool_calls = []
        if getattr(msg, "tool_calls", None):
            for tc in msg.tool_calls:
                tool_calls.append(UnifiedToolCall(
                    id=tc.id,
                    function=UnifiedFunction(name=tc.function.name, arguments=tc.function.arguments)
                ))
        return UnifiedMessage(content=msg.content, tool_calls=tool_calls)

    async def _call_claude(self, model: str, system: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]]) -> UnifiedMessage:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        anthropic_tools = []
        if tools:
            for t in tools:
                anthropic_tools.append({
                    "name": t["function"]["name"],
                    "description": t["function"].get("description", ""),
                    "input_schema": t["function"]["parameters"]
                })

        anthropic_messages = []
        for m in messages:
            if m["role"] == "system":
                continue 
            
            if m["role"] == "user":
                anthropic_messages.append({"role": "user", "content": m.get("content") or ""})
            elif m["role"] == "assistant":
                content = []
                if m.get("content"):
                    content.append({"type": "text", "text": m["content"]})
                if m.get("tool_calls"):
                    for tc in m["tool_calls"]:
                        content.append({
                            "type": "tool_use",
                            "id": tc["id"],
                            "name": tc["function"]["name"],
                            "input": json.loads(tc["function"]["arguments"])
                        })
                if content:
                    anthropic_messages.append({"role": "assistant", "content": content})
            elif m["role"] == "tool":
                tool_result = {
                    "type": "tool_result",
                    "tool_use_id": m.get("tool_call_id", ""),
                    "content": m.get("content", "")
                }
                if anthropic_messages and anthropic_messages[-1]["role"] == "user":
                    if isinstance(anthropic_messages[-1]["content"], list):
                        anthropic_messages[-1]["content"].append(tool_result)
                    else:
                        anthropic_messages[-1]["content"] = [{"type": "text", "text": anthropic_messages[-1]["content"]}, tool_result]
                else:
                    anthropic_messages.append({
                        "role": "user",
                        "content": [tool_result]
                    })

        kwargs = {
            "model": model,
            "system": system,
            "messages": anthropic_messages,
            "max_tokens": 4096
        }
        if anthropic_tools:
            kwargs["tools"] = anthropic_tools
            
        response = await client.messages.create(**kwargs)
        
        content = ""
        tool_calls = []
        for block in response.content:
            if block.type == "text":
                content += block.text
            elif block.type == "tool_use":
                tool_calls.append(UnifiedToolCall(
                    id=block.id,
                    function=UnifiedFunction(name=block.name, arguments=json.dumps(block.input))
                ))
                
        return UnifiedMessage(content=content if content else None, tool_calls=tool_calls)

    async def _call_gemini(self, model: str, system: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]]) -> UnifiedMessage:
        import google.generativeai as genai
        from google.generativeai.types import generation_types
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        gemini_tools = []
        if tools:
            for t in tools:
                props = t["function"]["parameters"].get("properties", {})
                req = t["function"]["parameters"].get("required", [])
                
                func_decl = {
                    "name": t["function"]["name"],
                    "description": t["function"].get("description", ""),
                    "parameters": {"type": "object", "properties": props, "required": req}
                }
                gemini_tools.append(func_decl)

        gen_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system,
            tools=[{"function_declarations": gemini_tools}] if gemini_tools else None
        )

        gemini_messages = []
        for m in messages:
            if m["role"] == "system":
                continue
                
            if m["role"] == "user":
                gemini_messages.append({"role": "user", "parts": [m.get("content") or ""]})
            elif m["role"] == "assistant":
                parts = []
                if m.get("content"):
                    parts.append(m["content"])
                if m.get("tool_calls"):
                    for tc in m["tool_calls"]:
                        parts.append(genai.types.FunctionCall({
                            "name": tc["function"]["name"],
                            "args": json.loads(tc["function"]["arguments"])
                        }))
                if parts:
                    gemini_messages.append({"role": "model", "parts": parts})
            elif m["role"] == "tool":
                try:
                    result_content = json.loads(m.get("content", "{}"))
                except json.JSONDecodeError:
                    result_content = {"result": m.get("content", "")}

                resp_part = genai.types.FunctionResponse({
                    "name": m.get("name", ""),
                    "response": result_content
                })
                gemini_messages.append({"role": "user", "parts": [resp_part]})

        response = await gen_model.generate_content_async(gemini_messages)

        content = ""
        tool_calls = []
        
        if hasattr(response, "parts"):
            for part in response.parts:
                if hasattr(part, "text") and part.text:
                    content += part.text
                if hasattr(part, "function_call") and part.function_call:
                    fc = part.function_call
                    try:
                        args_dict = dict(fc.args) if fc.args else {}
                    except Exception:
                        args_dict = type(fc).to_dict(fc).get("args", {})
                        
                    tool_calls.append(UnifiedToolCall(
                        id=f"call_{uuid.uuid4().hex[:8]}",
                        function=UnifiedFunction(name=fc.name, arguments=json.dumps(args_dict))
                    ))
        elif hasattr(response, "text") and response.text:
            content += response.text
            
        return UnifiedMessage(content=content if content else None, tool_calls=tool_calls)
