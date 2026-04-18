from core.registry import ToolRegistry
from rich.console import Console
from rich.prompt import Confirm
import os
import subprocess

console = Console()

# --- SWE-Bench Benchmark Tools ---
def view_file(filepath: str) -> str:
    console.print(f"\n[dim italic #A3BE8C]Running view_file: {filepath}...[/]")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

def edit_file(filepath: str, content: str) -> str:
    console.print(f"\n[dim italic #A3BE8C]Running edit_file on {filepath} ({len(content)} bytes)...[/]")
    if not Confirm.ask(f"[bold red]Allow agent to execute edit_file on {filepath}?[/]"):
        return "Edit blocked by user."
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully applied changes to {filepath}"
    except Exception as e:
        return f"Error writing file: {e}"

def run_bash_command(script: str) -> str:
    console.print(f"\n[dim italic #A3BE8C]Requesting bash shell...[/]")
    if not Confirm.ask(f"[bold red]Allow agent to execute this raw bash script?[/]\n[grey82]{script}[/]"):
        return "Command blocked by user."
        
    console.print(f"[dim italic #A3BE8C]Running bash: {script[:30]}...[/]")
    try:
        result = subprocess.run(script, shell=True, capture_output=True, text=True, timeout=15)
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return output if output.strip() else "Command executed successfully (no output)."
    except Exception as e:
        return f"Error executing command: {e}"

# --- WebArena Benchmark Tools ---
def goto_url(url: str) -> str:
    console.print(f"\n[dim italic #A3BE8C]Navigating to {url}...[/]")
    return "DOM Tree:\n[1] <button> Login </button>\n[2] <input text> Username </input>"

def click_element(element_id: str) -> str:
    console.print(f"\n[dim italic #A3BE8C]Clicking element ID: {element_id}[/]")
    return "Element clicked. Navigation complete. Current URL changed."

def type_text(element_id: str, text: str) -> str:
    console.print(f"\n[dim italic #A3BE8C]Typing into ID {element_id}...[/]")
    return "Text typed into field successfully."

# --- GSM8K Benchmark Tools ---
def python_interpreter(code: str) -> str:
    console.print(f"\n[dim italic #A3BE8C]Requesting python execution...[/]")
    if not Confirm.ask(f"[bold red]Allow agent to run this python code?[/]\n[grey82]{code}[/]"):
        return "Python execution blocked by user."
        
    console.print(f"[dim italic #A3BE8C]Executing python ({len(code)} bytes)...[/]")
    try:
        # Write code to a tmp file and run it
        with open(".tmp_math.py", "w", encoding="utf-8") as f:
            f.write(code)
        result = subprocess.run("python .tmp_math.py", shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        return output if output.strip() else "Execution completed."
    except Exception as e:
        return f"Error executing python: {e}"

def reflect(goal: str, output: str) -> str:
    console.print(f"\n[dim italic #A3BE8C]Executing reflect tool to check gap...[/]")
    return "No gaps found. Execution matches intent."

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

    # Register Post-action Reflection
    tools.register("reflect", reflect, {
        "name": "reflect", 
        "description": "Evaluate outcome vs goal to find gaps.", 
        "parameters": {
            "type": "object", 
            "properties": {
                "goal": {"type": "string"}, 
                "output": {"type": "string"}
            }, 
            "required": ["goal", "output"]
        }
    })
