"""
retrieval.py  —  get_top_chunks(query, k)  (Sahip: SİNA)
Sorguyu embed eder, tüm vektörlerle cosine similarity hesaplar, en iyi k'yı döndürür.
Küçük veri için brute-force yeterli (ek bağımlılık yok).
"""
from __future__ import annotations
import math

import db
import foundry_client as fc


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


def get_top_chunks(query: str, k: int = 3) -> list[dict]:
    """En alakalı k parça. Her dict: {text, source, score}."""
    try:
        query_emb = fc.get_embedding(query)
    except Exception as exc:
        print(f"[!] Sorgu embedding hatası: {exc}")
        return []

    conn = db.get_connection()
    rows = db.fetch_all_chunks(conn)
    conn.close()

    scored = [
        {
            "text": row["content"],
            "source": row["source"],
            "score": _cosine(query_emb, row["embedding"]),
        }
        for row in rows
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "test sorusu"
    for i, c in enumerate(get_top_chunks(q), 1):
        print(f"\n#{i} [{c['source']}] score={c['score']:.3f}")
        print(c["text"][:200])
