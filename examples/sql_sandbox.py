"""
sql_sandbox.py  —  SQLite alıştırması (Hafta 2)

Python'un yerleşik sqlite3 modülüyle bellekte (in-memory) küçük bir
documents tablosu kurar, örnek satırlar ekler ve iki temel sorgu gösterir:
id ile kayıt çekme ve LIKE ile anahtar kelime filtreleme.

Foundry Local gerekmez; embedding'ler sahte JSON vektörlerdir.

Çalıştır:  python examples/sql_sandbox.py
"""
from __future__ import annotations

import json
import sqlite3
import sys

# Windows terminali bazen CP1254 kullanır; Türkçe karakterler için UTF-8'e geç
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SAMPLE_ROWS = [
    ("rag_nedir.md", "RAG üç adımdan oluşur: getir, zenginleştir, üret.", [0.1, 0.2, 0.3]),
    ("sqlite.md", "SQLite veriyi tek bir dosyada saklar, sunucu gerektirmez.", [0.4, 0.5, 0.6]),
    ("embeddings.md", "Embedding vektörleri anlam benzerliğini ölçmeyi sağlar.", [0.7, 0.8, 0.9]),
]


def main() -> None:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row

    # db.py'deki gerçek şemanın birebir aynısı
    conn.execute(
        """
        CREATE TABLE documents (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            source    TEXT NOT NULL,
            content   TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
        """
    )

    for source, content, vector in SAMPLE_ROWS:
        conn.execute(
            "INSERT INTO documents (source, content, embedding) VALUES (?, ?, ?)",
            (source, content, json.dumps(vector)),
        )
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
    print(f"[OK] {count} örnek satır eklendi.\n")

    # 1) id ile tek kayıt çekme
    row = conn.execute(
        "SELECT id, source, content FROM documents WHERE id = ?", (2,)
    ).fetchone()
    print("id = 2 olan kayıt:")
    print(f"  [{row['id']}] {row['source']}: {row['content']}\n")

    # 2) Anahtar kelimeyle filtreleme (parametreli LIKE — SQL injection'a kapalı)
    keyword = "vektör"
    rows = conn.execute(
        "SELECT id, source, content FROM documents WHERE content LIKE ?",
        (f"%{keyword}%",),
    ).fetchall()
    print(f"İçinde '{keyword}' geçen kayıtlar:")
    for r in rows:
        print(f"  [{r['id']}] {r['source']}: {r['content']}")

    conn.close()


if __name__ == "__main__":
    main()
