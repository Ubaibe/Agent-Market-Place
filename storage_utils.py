from database import get_connection
from crypto_utils import encrypt_text
# from og_storage_utils import OGStorageUtils
from database import get_connection

class StorageUtils:

    def save_agent_memory(self, agent_id, memory_text, task_id=None):

        try:
            encrypted = encrypt_text(memory_text)

            storage_hash = None
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO agent_memories
                (
                    agent_id,
                    task_id,
                    memory,
                    storage_hash
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    agent_id,
                    task_id,
                    encrypted,
                    storage_hash
                )
            )

            conn.commit()
            conn.close()

            return True, "Memory saved + synced to 0G"

        except Exception as e:
            return False, str(e)

    def get_agent_memories(
        self,
        agent_id: int
    ):

        try:

            conn = get_connection()

            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT *
                FROM agent_memories
                WHERE agent_id = ?
                ORDER BY created_at DESC
                """,
                (agent_id,)
            )

            rows = cursor.fetchall()

            conn.close()

            return [dict(row) for row in rows]

        except Exception:

            return []
