import asyncio
import os
from dotenv import load_dotenv
from core.agent import MasterAgent
from core.registry import ToolRegistry
from core.tools import register_all_tools
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

# Load env variables
load_dotenv()
console = Console()

def print_welcome_banner():
    logo = """
   ▄▄▄▄▄▄   
 ▄████████▄ 
 ███▄██▄███ 
 ▀▀██████▀▀ 
 ▄▀      ▀▄ 
"""
    left_content = Text()
    left_content.append("Welcome back!\n\n", style="bold white")
    left_content.append(logo, style="#A3BE8C")
    left_content.append("\ngpt-5.4-mini · Agent Pro · CLI\n", style="grey62")

    right_content = Text()
    right_content.append("Tips for getting started\n", style="#A3BE8C")
    right_content.append("Try running a SWE-bench task or Web navigation\n\n", style="grey62")
    right_content.append("Recent activity\n", style="#A3BE8C")
    right_content.append("No recent activity", style="grey62")

    table = Table(show_header=False, show_edge=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Left", justify="center", width=40)
    table.add_column("Right", width=40)
    table.add_row(left_content, right_content)

    panel = Panel(
        table,
        title="[bold #A3BE8C] Simple Python Agent v0.1.0 [/]",
        title_align="left",
        border_style="#A3BE8C",
        padding=(1, 2)
    )
    console.print(panel)

async def main():
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[bold red]Missing OPENAI_API_KEY in environment.[/]")
    
    tools = ToolRegistry()
    register_all_tools(tools)

    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    agent = MasterAgent(tools=tools, skills_dir=skills_dir)
    
    console.clear()
    print_welcome_banner()
    
    while True:
        try:
            user_input = console.input("\n[bold]> [/]")
            if not user_input.strip():
                continue
            if user_input.lower() in ['exit', 'quit']:
                break
                
            with console.status("[dim italic #A3BE8C]Reasoning...[/]", spinner="dots"):
                response = await agent.run(user_input)
                
            console.print(f"\n[grey82]{response}[/]", highlight=False)
            console.print("\n" + "[dim]─[/]" * console.width)
            
        except KeyboardInterrupt:
            console.print("\n[dim]Goodbye![/]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/] {e}")

if __name__ == "__main__":
    asyncio.run(main())
