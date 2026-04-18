import os
import yaml
from typing import Dict, Any, Callable, List, Optional
from core.models import Skill
import inspect

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._schemas: Dict[str, Dict[str, Any]] = {}

    def register(self, name: str, func: Callable, schema: Dict[str, Any]):
        self._tools[name] = func
        self._schemas[name] = schema

    def schemas_for(self, allowed_tools: List[str]) -> List[Dict[str, Any]]:
        return [
            {"type": "function", "function": self._schemas[name]}
            for name in allowed_tools if name in self._schemas
        ]

    async def dispatch(self, tool_call_id: str, name: str, arguments: str) -> str:
        import json
        if name not in self._tools:
            return f"Error: Tool {name} not found."
            
        try:
            kwargs = json.loads(arguments)
            func = self._tools[name]
            if inspect.iscoroutinefunction(func):
                result = await func(**kwargs)
            else:
                result = func(**kwargs)
            # Make sure it's returned as string
            if isinstance(result, (dict, list)):
                return json.dumps(result)
            return str(result)
        except Exception as e:
            return f"Error executing {name}: {str(e)}"

class SkillRegistry:
    def __init__(self, skills_dir: str):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Skill] = {}
        self._load_skills()

    def _load_skills(self):
        if not os.path.exists(self.skills_dir):
            return
            
        for d in os.listdir(self.skills_dir):
            folder_path = os.path.join(self.skills_dir, d)
            if os.path.isdir(folder_path):
                skill_file = os.path.join(folder_path, "SKILL.md")
                if os.path.exists(skill_file):
                    self._parse_skill_file(skill_file)

    def _parse_skill_file(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            content = f.read()

        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) == 3:
                frontmatter = yaml.safe_load(parts[1])
                instructions = parts[2].strip()
                
                name = frontmatter.get("name", "Unknown")
                desc = frontmatter.get("description", "")
                allowed = frontmatter.get("allowed-tools", [])
                requires_pfc = frontmatter.get("requires-pfc", False)
                
                self.skills[name] = Skill(
                    name=name, 
                    description=desc, 
                    instructions=instructions, 
                    allowed_tools=allowed,
                    requires_pfc=requires_pfc
                )
