# src/memory.py
import json
import os
from typing import Any, Dict, List

MEMORY_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'memory_store.json')

class Memory:
    """
    Simple JSON-backed memory: stores per-user events and interventions.
    For Kaggle/demo usage this is lightweight and transparent.
    """
    def __init__(self, path: str = MEMORY_FILE):
        self.path = path
        # init file
        if not os.path.exists(self.path):
            with open(self.path, 'w') as f:
                json.dump({}, f)

    def _load(self) -> Dict:
        with open(self.path, 'r') as f:
            return json.load(f)

    def _save(self, obj: Dict):
        with open(self.path, 'w') as f:
            json.dump(obj, f, indent=2)

    def save_event(self, user_id: str, key: str, payload: Any):
        store = self._load()
        if user_id not in store:
            store[user_id] = {}
        if key not in store[user_id]:
            store[user_id][key] = []
        store[user_id][key].append({"payload": payload})
        self._save(store)

    def get_recent(self, user_id: str, key: str, limit: int = 10) -> List:
        store = self._load()
        return store.get(user_id, {}).get(key, [])[-limit:]

    def get_all(self, user_id: str) -> Dict:
        store = self._load()
        return store.get(user_id, {})
