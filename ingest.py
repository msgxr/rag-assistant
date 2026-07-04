"""
ingest.py  —  Dökümanları parçala, embed et, SQLite'a yaz
Çalıştır:  python ingest.py
data/ içindeki .txt ve .md dosyalarını okur.
"""
from __future__ import annotations

import sys
from pathlib import Path

import db
import foundry_client as fc

DATA_DIR = Path(__file__).parent / "data"
MAX_CHARS = 800     # bir parçanın hedef üst karakter sınırı
OVERLAP   = 100     # uzun paragraf bölünürken örtüşme (bağlam kopmasın)


def load_documents(data_dir: Path = DATA_DIR) -> list[tuple[str, str]]:
    docs: list[tuple[str, str]] = []
    for path in sorted(data_dir.glob("*")):
        if path.is_file() and path.suffix.lower() in {".txt", ".md"}:
            docs.append((path.name, path.read_text(encoding="utf-8")))
    return docs


def chunk_text(text: str, max_chars: int = MAX_CHARS,
               overlap: int = OVERLAP) -> list[str]:
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
                if end >= len(para):
                    break
                start = end - overlap
    return chunks


def ingest() -> None:
    documents = load_documents()
    if not documents:
        print(f"[!] {DATA_DIR} içinde .txt/.md yok. Önce döküman ekle.")
        return

    conn = db.get_connection()
    db.init_db(conn)
    conn.execute("BEGIN")  # tek transaction — crash'te veri tutarlılığı bozulmasın
    db.clear_documents(conn)

    total_chunks = sum(len(chunk_text(text)) for _, text in documents)
    print(f"[→] {len(documents)} döküman, tahmini {total_chunks} parça")
    print("[→] Embedding modeli ilk kullanımda indirilir (birkaç dakika sürebilir)...\n")

    done = 0
    failed = 0
    for source, text in documents:
        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks, 1):
            try:
                embedding = fc.get_embedding(chunk)
            except Exception as exc:
                print(f"\n[!] Embedding hatası ({source}, chunk {i}): {exc}")
                failed += 1
                continue
            db.insert_chunk(conn, source, chunk, embedding)
            done += 1
            # Basit ilerleme çubuğu
            pct = int(done / total_chunks * 40)
            bar = "█" * pct + "░" * (40 - pct)
            sys.stdout.write(f"\r  [{bar}] {done}/{total_chunks}  {source[:30]}")
            sys.stdout.flush()
        print(f"\r  [+] {source:<40} {len(chunks)} parça")

    conn.commit()  # tüm ingestion başarılıysa bir kerede kaydet
    final_count = db.count_documents(conn)
    conn.close()

    print(f"\n[OK] Ingestion tamamlandı.")
    if failed:
        print(f"[!] {failed} parça atlandı (embedding hatası).")
    print(f"[OK] {len(documents)} döküman → {final_count} parça → rag.db")


if __name__ == "__main__":
    ingest()
