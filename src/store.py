import json
import os
from threading import Lock
from typing import Dict, Optional

class Store:
    def __init__(self, snapshot_file: str = "snapshot.json"):
        self._store: Dict[str, str] = {}
        self._lock = Lock()
        self._snapshot_file = snapshot_file
        self._load_snapshot()

    def _load_snapshot(self):
        """Load data from snapshot file if it exists."""
        if os.path.exists(self._snapshot_file):
            with open(self._snapshot_file, 'r') as f:
                self._store = json.load(f)

    def _save_snapshot(self):
        """Save current store to snapshot file."""
        with self._lock:
            with open(self._snapshot_file, 'w') as f:
                json.dump(self._store, f)
    
    def set(self, key: str, value: str) -> bool:
        """Set a key-value pair and save to snapshot."""
        with self._lock:
            self._store[key] = value
            self._save_snapshot()
            return True
    
    def get(self, key: str) -> Optional[str]:
        """Get value for a key."""
        with self._lock:
            return self._store.get(key)
    
    def delete(self, key: str) -> bool:
        """Delete a key and save to snapshot."""
        with self._lock:
            if key in self._store:
                del self._store[key]
                self._save_snapshot()
                return True
            return False