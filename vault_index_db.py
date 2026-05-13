import sqlite3


DB_NAME = "vault_index.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_vault_index():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault_sync_index (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER UNIQUE,
            root_hash TEXT,
            last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_root_hash(agent_id: int, root_hash: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO vault_sync_index (agent_id, root_hash)
        VALUES (?, ?)
        ON CONFLICT(agent_id)
        DO UPDATE SET
            root_hash = excluded.root_hash,
            last_synced_at = CURRENT_TIMESTAMP
    """, (agent_id, root_hash))

    conn.commit()
    conn.close()


def get_root_hash(agent_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT root_hash
        FROM vault_sync_index
        WHERE agent_id = ?
    """, (agent_id,))

    row = cursor.fetchone()
    conn.close()

    return row["root_hash"] if row else None

def get_all_sync_records():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT agent_id, root_hash, last_synced_at
        FROM vault_sync_index
        ORDER BY last_synced_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
