"""
Trishul Backend — shared FastAPI API for Web UI and CLI.

Provides conversation management, message routing with PII redaction,
and task tracking. Both the Web UI and CLI connect to this same backend.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from enum import IntEnum

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ..pii_redactor import PIIRedactor, RedactionMapping
from ..cli.clients import (
    BedrockClient,
    DirectAPIClient,
    OllamaClient,
    OpenRouterClient,
)

app = FastAPI(title="Trishul API", version="0.1.0")


# ── Models ────────────────────────────────────────────────


class Tier(IntEnum):
    FULL_ISOLATION = 1
    ANONYMOUS = 2
    OPEN = 3


class ConversationCreate(BaseModel):
    title: str | None = None
    tier: int = 2


class MessageCreate(BaseModel):
    content: str
    role: str = "user"


class TaskCreate(BaseModel):
    description: str
    tier: int = 2
    project_root: str | None = None


# ── Database helper ───────────────────────────────────────


def _get_db() -> sqlite3.Connection:
    """Get a database connection. Uses plain SQLite for portability;
    swap with SQLCipher for encrypted storage in production."""
    db_path = os.environ.get("TRISHUL_DB_PATH", "trishul.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _init_db() -> None:
    conn = _get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT,
            tier INTEGER NOT NULL DEFAULT 2,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            redacted_content TEXT,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS redaction_mappings (
            conversation_id TEXT PRIMARY KEY,
            mapping_json TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            tier INTEGER NOT NULL DEFAULT 2,
            project_root TEXT,
            status TEXT NOT NULL DEFAULT 'created',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS task_steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            step_json TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    """)
    conn.commit()
    conn.close()


_init_db()


# ── Tier Router ───────────────────────────────────────────


def _get_router(tier: int):
    """Return the appropriate LLM client for the given tier."""
    config = {
        "openrouter_api_key": os.environ.get("OPENROUTER_API_KEY", ""),
        "direct_api_key": os.environ.get("DIRECT_API_KEY", ""),
        "aws_region": os.environ.get("AWS_REGION", "us-east-1"),
        "ollama_base_url": os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        "ollama_model": os.environ.get("OLLAMA_MODEL", "llama3.1:8b"),
    }
    if tier == Tier.FULL_ISOLATION:
        if os.environ.get("USE_BEDROCK"):
            return BedrockClient(config)
        return OllamaClient(config)
    elif tier == Tier.ANONYMOUS:
        return OpenRouterClient(config)
    else:
        return DirectAPIClient(config)


# ── PII Redactor singleton ────────────────────────────────

_redactor = PIIRedactor(
    custom_terms=json.loads(
        os.environ.get("TRISHUL_CUSTOM_TERMS", "{}")
    ),
    use_ner=os.environ.get("TRISHUL_USE_NER", "true").lower() == "true",
)


# ── Conversations ─────────────────────────────────────────


@app.post("/api/conversations")
async def create_conversation(data: ConversationCreate):
    """Create a new conversation. Used by both Web UI and CLI."""
    conv_id = uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc).isoformat()
    conn = _get_db()
    conn.execute(
        "INSERT INTO conversations (id, title, tier, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (conv_id, data.title, data.tier, now, now),
    )
    conn.commit()
    conn.close()
    return {"id": conv_id, "tier": data.tier}


@app.get("/api/conversations")
async def list_conversations():
    """List all conversations."""
    conn = _get_db()
    rows = conn.execute(
        "SELECT * FROM conversations ORDER BY updated_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/api/conversations/{conv_id}")
async def get_conversation(conv_id: str):
    """Get conversation with full message history."""
    conn = _get_db()
    conv = conn.execute(
        "SELECT * FROM conversations WHERE id = ?", (conv_id,)
    ).fetchone()
    if not conv:
        conn.close()
        raise HTTPException(404, "Conversation not found")

    messages = conn.execute(
        "SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp",
        (conv_id,),
    ).fetchall()
    conn.close()

    return {
        **dict(conv),
        "messages": [dict(m) for m in messages],
    }


# ── Messages ──────────────────────────────────────────────


@app.post("/api/conversations/{conv_id}/messages")
async def send_message(conv_id: str, data: MessageCreate):
    """
    Send a message in a conversation.

    The backend handles:
    1. Loading conversation history
    2. PII redaction (if Tier 2)
    3. Routing to the correct LLM provider
    4. Storing both original and redacted messages
    5. Returning the (rehydrated) response
    """
    conn = _get_db()
    conv = conn.execute(
        "SELECT * FROM conversations WHERE id = ?", (conv_id,)
    ).fetchone()
    if not conv:
        conn.close()
        raise HTTPException(404, "Conversation not found")

    tier = conv["tier"]
    now = datetime.now(timezone.utc).isoformat()

    # Load history
    history_rows = conn.execute(
        "SELECT role, content FROM messages WHERE conversation_id = ? "
        "ORDER BY timestamp",
        (conv_id,),
    ).fetchall()

    messages = [{"role": r["role"], "content": r["content"]} for r in history_rows]
    messages.append({"role": "user", "content": data.content})

    # Load or create redaction mapping
    mapping = RedactionMapping()
    if tier == Tier.ANONYMOUS:
        mapping_row = conn.execute(
            "SELECT mapping_json FROM redaction_mappings "
            "WHERE conversation_id = ?",
            (conv_id,),
        ).fetchone()
        if mapping_row:
            mapping = RedactionMapping.from_dict(
                json.loads(mapping_row["mapping_json"])
            )

        redacted_messages = _redactor.redact_messages(messages, mapping)
    else:
        redacted_messages = messages

    # Route to LLM
    router = _get_router(tier)
    response_text = router.chat(redacted_messages)

    # Rehydrate if Tier 2
    if tier == Tier.ANONYMOUS:
        response_text = mapping.rehydrate(response_text)
        # Save updated mapping
        conn.execute(
            "INSERT OR REPLACE INTO redaction_mappings "
            "(conversation_id, mapping_json) VALUES (?, ?)",
            (conv_id, json.dumps(mapping.to_dict())),
        )

    # Store messages
    conn.execute(
        "INSERT INTO messages (conversation_id, role, content, timestamp) "
        "VALUES (?, ?, ?, ?)",
        (conv_id, "user", data.content, now),
    )
    conn.execute(
        "INSERT INTO messages (conversation_id, role, content, timestamp) "
        "VALUES (?, ?, ?, ?)",
        (conv_id, "assistant", response_text, now),
    )
    conn.execute(
        "UPDATE conversations SET updated_at = ? WHERE id = ?",
        (now, conv_id),
    )
    conn.commit()
    conn.close()

    return {"role": "assistant", "content": response_text}


# ── Tasks (CLI Agent) ────────────────────────────────────


@app.post("/api/tasks")
async def create_task(data: TaskCreate):
    """Create a multi-step agent task."""
    task_id = uuid.uuid4().hex[:12]
    now = datetime.now(timezone.utc).isoformat()
    conn = _get_db()
    conn.execute(
        "INSERT INTO tasks (id, description, tier, project_root, status, "
        "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (task_id, data.description, data.tier, data.project_root, "created", now, now),
    )
    conn.commit()
    conn.close()
    return {"id": task_id, "status": "created"}


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get task status and step log."""
    conn = _get_db()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()
    if not task:
        conn.close()
        raise HTTPException(404, "Task not found")

    steps = conn.execute(
        "SELECT * FROM task_steps WHERE task_id = ? ORDER BY timestamp",
        (task_id,),
    ).fetchall()
    conn.close()

    return {
        **dict(task),
        "steps": [json.loads(s["step_json"]) for s in steps],
    }


@app.post("/api/tasks/{task_id}/steps")
async def log_task_step(task_id: str, step: dict):
    """CLI agent logs each step it takes."""
    now = datetime.now(timezone.utc).isoformat()
    conn = _get_db()
    conn.execute(
        "INSERT INTO task_steps (task_id, step_json, timestamp) "
        "VALUES (?, ?, ?)",
        (task_id, json.dumps(step), now),
    )
    conn.execute(
        "UPDATE tasks SET updated_at = ? WHERE id = ?",
        (now, task_id),
    )
    conn.commit()
    conn.close()
    return {"status": "logged"}
