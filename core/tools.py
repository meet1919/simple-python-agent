from core.registry import ToolRegistry

# --- SWE-Bench Benchmark Tools ---
def view_file(filepath: str) -> str:
    print(f"\n[Tool Executing] view_file: {filepath}")
    return f"Mock content of {filepath}:\n\nif __name__ == '__main__':\n    print('Hello World')"

def edit_file(filepath: str, content: str) -> str:
    print(f"\n[Tool Executing] edit_file: {filepath} with {len(content)} bytes")
    return f"Successfully applied changes to {filepath}"

def run_bash_command(script: str) -> str:
    print(f"\n[Tool Executing] run_bash_command: {script[:50]}...")
    return f"Mock bash execution successful: {script}"

# --- WebArena Benchmark Tools ---
def goto_url(url: str) -> str:
    print(f"\n[Tool Executing] goto_url: {url}")
    return "DOM Tree:\n[1] <button> Login </button>\n[2] <input text> Username </input>"

def click_element(element_id: str) -> str:
    print(f"\n[Tool Executing] click_element: ID {element_id}")
    return "Element clicked. Navigation complete. Current URL changed."

def type_text(element_id: str, text: str) -> str:
    print(f"\n[Tool Executing] type_text: ID {element_id} -> {text}")
    return "Text typed into field successfully."

# --- GSM8K Benchmark Tools ---
def python_interpreter(code: str) -> str:
    print(f"\n[Tool Executing] python_interpreter:\n{code}")
    return "Mock execution output: 42"

def register_all_tools(tools: ToolRegistry):
    # Register SWE-Bench Tools
    tools.register("view_file", view_file, {"name": "view_file", "description": "Read file contents", "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]}})
    tools.register("edit_file", edit_file, {"name": "edit_file", "description": "Write to file", "parameters": {"type": "object", "properties": {"filepath": {"type": "string"}, "content": {"type": "string"}}, "required": ["filepath", "content"]}})
    tools.register("run_bash_command", run_bash_command, {"name": "run_bash_command", "description": "Run bash script", "parameters": {"type": "object", "properties": {"script": {"type": "string"}}, "required": ["script"]}})
    
    # Register WebArena Tools
    tools.register("goto_url", goto_url, {"name": "goto_url", "description": "Navigate to URL", "parameters": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}})
    tools.register("click_element", click_element, {"name": "click_element", "description": "Click an element by ID", "parameters": {"type": "object", "properties": {"element_id": {"type": "string"}}, "required": ["element_id"]}})
    tools.register("type_text", type_text, {"name": "type_text", "description": "Type text into element", "parameters": {"type": "object", "properties": {"element_id": {"type": "string"}, "text": {"type": "string"}}, "required": ["element_id", "text"]}})

    # Register Math Tools
    tools.register("python_interpreter", python_interpreter, {"name": "python_interpreter", "description": "Execute python code", "parameters": {"type": "object", "properties": {"code": {"type": "string"}}, "required": ["code"]}})
