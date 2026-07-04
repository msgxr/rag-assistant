"""
db.py  —  SQLite şema + giriş/çıkış
Embedding'ler JSON metni olarak saklanır (küçük veri için yeterli).
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "rag.db"


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            source    TEXT NOT NULL,
            content   TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
        """
    )
    conn.commit()


def clear_documents(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM documents")


def insert_chunk(conn: sqlite3.Connection, source: str, content: str,
                 embedding: list[float]) -> None:
    conn.execute(
        "INSERT INTO documents (source, content, embedding) VALUES (?, ?, ?)",
        (source, content, json.dumps(embedding)),
    )


def count_documents(conn: sqlite3.Connection) -> int:
    return conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]


def count_by_source(conn: sqlite3.Connection) -> dict[str, int]:
    """Kaynak dosya başına chunk sayısını döndürür."""
    rows = conn.execute(
        "SELECT source, COUNT(*) as cnt FROM documents GROUP BY source ORDER BY source"
    ).fetchall()
    return {r["source"]: r["cnt"] for r in rows}


def fetch_all_chunks(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT source, content, embedding FROM documents"
    ).fetchall()
    result: list[dict] = []
    for r in rows:
        try:
            emb = json.loads(r["embedding"])
        except (json.JSONDecodeError, TypeError) as exc:
            print(f"[!] Bozuk embedding verisi ({r['source']}): {exc}")
            continue
        result.append({
            "source": r["source"],
            "content": r["content"],
            "embedding": emb,
        })
    return result
