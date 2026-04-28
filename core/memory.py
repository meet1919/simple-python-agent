import json
import hashlib
import os
from typing import Optional, Dict, Any, List

class ProceduralMemory:
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = storage_dir
        self.memory_file = os.path.join(storage_dir, "procedural_memory.json")
        self._ensure_storage()
        self.traces = self._load_traces()

    def _ensure_storage(self):
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir)
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _load_traces(self) -> Dict[str, Any]:
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_traces(self):
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.traces, f, indent=2)

    def extract_signature(self, structural_dict: Dict[str, Any]) -> str:
        """
        Creates a fixed-length fingerprint of the task structure.
        """
        if not structural_dict:
            return ""
        # sort_keys=True ensures identical dicts produce identical strings
        canonical = json.dumps(structural_dict, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()[:16]

    def store_trace(self, structural_dict: Dict[str, Any], trace: List[str]):
        """
        Stores a solution trace based on the structural signature.
        """
        sig = self.extract_signature(structural_dict)
        if not sig:
            return
            
        self.traces[sig] = {
            "signature": structural_dict,
            "trace": trace
        }
        self._save_traces()

    def recall_trace(self, structural_dict: Dict[str, Any]) -> Optional[List[str]]:
        """
        Recalls a stored solution trace if the exact structural signature matches.
        """
        sig = self.extract_signature(structural_dict)
        if not sig:
            return None
            
        record = self.traces.get(sig)
        if record:
            return record.get("trace")
        return None
