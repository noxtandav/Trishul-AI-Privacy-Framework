"""
Encrypted database setup for storing conversation history.

Uses SQLCipher (encrypted SQLite) to protect your unredacted
chat history at rest.

Requirements:
    pip install sqlcipher3
"""

import sqlcipher3


def get_db_connection(db_path: str, passphrase: str):
    """Create an encrypted database connection."""
    conn = sqlcipher3.connect(db_path)
    conn.execute(f"PRAGMA key = '{passphrase}'")
    conn.execute("PRAGMA cipher_compatibility = 4")
    return conn


def initialize_db(conn):
    """Create the schema for conversation storage."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            redacted_content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            tier INTEGER DEFAULT 2,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()


# ─────────────────────────────────────────────────────────────
# Example Usage
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    conn = get_db_connection("conversations.db", "your-strong-passphrase")
    initialize_db(conn)
    print("Encrypted database initialized successfully.")
    conn.close()
