import sqlite3


def get_connection():

    conn = sqlite3.connect(
        "payguard.db",
        check_same_thread=False
    )

    conn.row_factory = sqlite3.Row

    return conn

def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_memories (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        agent_id INTEGER NOT NULL,

        task_id INTEGER,

        memory TEXT NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    conn.close()
