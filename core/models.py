from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class PFCOutput:
    refined_intent: str
    assumptions: List[str]
    ambiguities: List[str]
    confidence: str
    thinking_path: str
    structural_signature: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Skill:
    name: str
    description: str
    instructions: str
    allowed_tools: List[str]
    requires_pfc: bool = False
    file_path: Optional[str] = None

@dataclass
class Message:
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = {"role": self.role}
        if self.content is not None:
            d["content"] = self.content
        if self.tool_calls is not None:
            d["tool_calls"] = self.tool_calls
        if self.tool_call_id is not None:
            d["tool_call_id"] = self.tool_call_id
        if self.name is not None:
            d["name"] = self.name
        return d
