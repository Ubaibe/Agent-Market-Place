import os
import json
from datetime import datetime


class StorageUtils:
    def __init__(self):
        self.data_dir = "data"
        os.makedirs(self.data_dir, exist_ok=True)

    def save_agent_memory(self, agent_id: int, memory_text: str, task_id: int = None):
        """Save persistent memory for an agent"""
        try:
            filename = f"{self.data_dir}/agent_{agent_id}_memory.json"

            # Load existing memories or create new
            try:
                with open(filename, "r") as f:
                    memories = json.load(f)
            except:
                memories = []

            memory_entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "memory": memory_text,
                "task_id": task_id
            }

            memories.append(memory_entry)

            with open(filename, "w") as f:
                json.dump(memories, f, indent=2)

            return True, "Memory saved successfully"
        except Exception as e:
            return False, str(e)

    def get_agent_memories(self, agent_id: int):
        """Get all memories for an agent"""
        try:
            filename = f"{self.data_dir}/agent_{agent_id}_memory.json"
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return []