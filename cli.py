import asyncio
import os
from dotenv import load_dotenv
from core.agent import MasterAgent
from core.registry import ToolRegistry
from core.tools import register_all_tools

# Load env variables
load_dotenv()

async def main():
    if not os.getenv("OPENAI_API_KEY"):
        print("Missing OPENAI_API_KEY in environment. Agent cannot route effectively.")
        # Proceed anyway to allow local tool checking
    
    tools = ToolRegistry()
    register_all_tools(tools)

    skills_dir = os.path.join(os.path.dirname(__file__), "skills")
    agent = MasterAgent(tools=tools, skills_dir=skills_dir)
    
    print("Welcome to Simple Python Agent (Research Benchmarks Edition)")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ")
            if not user_input.strip():
                continue
            if user_input.lower() in ['exit', 'quit']:
                break
                
            response = await agent.run(user_input)
            print(f"\nAgent: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n[Error]: {e}")

if __name__ == "__main__":
    asyncio.run(main())
