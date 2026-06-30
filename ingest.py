"""
ingest.py  —  Dökümanları parçala, embed et, SQLite'a yaz  (Sahip: SİNA)
Çalıştır:  python ingest.py
data/ içindeki .txt ve .md dosyalarını okur.
"""
from __future__ import annotations
from pathlib import Path

import db
import foundry_client as fc

DATA_DIR = Path(__file__).parent / "data"
MAX_CHARS = 800     # bir parçanın hedef üst karakter sınırı
OVERLAP = 100       # uzun paragraf bölünürken örtüşme (bağlam kopmasın)


def load_documents(data_dir: Path = DATA_DIR) -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []
    for path in sorted(data_dir.glob("*")):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            docs.append((path.name, path.read_text(encoding="utf-8")))
    return docs


def chunk_text(text: str, max_chars: int = MAX_CHARS, overlap: int = OVERLAP) -> list[str]:
    """Önce paragraflara böl; çok uzun paragrafları örtüşmeli pencerelerle parçala."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    for para in paragraphs:
        if len(para) <= max_chars:
            chunks.append(para)
        else:
            start = 0
            while start < len(para):
                end = start + max_chars
                piece = para[start:end].strip()
                if piece:
                    chunks.append(piece)
                start = end - overlap
    return chunks


def ingest() -> None:
    conn = db.get_connection()
    db.init_db(conn)
    db.clear_documents(conn)   # her çalıştırmada temiz kurulum

    documents = load_documents()
    if not documents:
        print(f"[!] {DATA_DIR} içinde .txt/.md yok. Önce döküman ekle.")
        conn.close()
        return

    total = 0
    for source, text in documents:
        chunks = chunk_text(text)
        for chunk in chunks:
            embedding = fc.get_embedding(chunk)
            db.insert_chunk(conn, source, chunk, embedding)
            total += 1
        print(f"  [+] {source}: {len(chunks)} parça")
    conn.commit()

    print(f"\n[OK] Ingestion bitti — {len(documents)} döküman, {total} parça.")
    print(f"[OK] DB kayıt sayısı: {db.count_documents(conn)}")
    conn.close()


if __name__ == "__main__":
    ingest()
