import os
import sqlite3
from pathlib import Path
from typing import List, Dict, Literal, Optional
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv(
    "DB_PATH",
    "/mnt/external-ssd/olawale_ai/data/olawale_ai.db",
)


def get_connection():
    """
    Returns a SQLite connection.
    We set check_same_thread=False so it can be used in FastAPI.
    """
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Create tables if they don't exist.
    - conversations: one row per session_id
    - messages: each user/assistant message
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,      -- 'user' or 'assistant'
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
        """
    )

    conn.commit()
    conn.close()


def get_or_create_conversation(session_id: str) -> int:
    """
    Return the conversation's numeric ID for a given session_id.
    Create it if it doesn't exist.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT id FROM conversations WHERE session_id = ?",
        (session_id,),
    )
    row = cur.fetchone()
    if row:
        conv_id = row["id"]
    else:
        now = datetime.utcnow().isoformat()
        cur.execute(
            "INSERT INTO conversations (session_id, created_at) VALUES (?, ?)",
            (session_id, now),
        )
        conn.commit()
        conv_id = cur.lastrowid

    conn.close()
    return conv_id


def add_message(conversation_id: int, role: Literal["user", "assistant"], content: str):
    """
    Insert a single message row.
    """
    conn = get_connection()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        """
        INSERT INTO messages (conversation_id, role, content, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (conversation_id, role, content, now),
    )
    conn.commit()
    conn.close()


def get_recent_messages(
    conversation_id: int,
    limit: int = 10,
) -> List[Dict[str, str]]:
    """
    Return the last N messages for a conversation, in chronological order.
    We map them into the format expected by the OpenAI chat API.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (conversation_id, limit),
    )
    rows = cur.fetchall()
    conn.close()

    # rows are newest-first; reverse to oldest-first
    rows = list(rows)[::-1]

    history = []
    for r in rows:
        history.append(
            {
                "role": r["role"],
                "content": r["content"],
            }
        )
    return history
