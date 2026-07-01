"""
main.py  —  CLI giriş noktası

Kullanım:
    python ingest.py          # önce bir kez: veritabanını kur
    python main.py            # soru-cevap döngüsü (CLI)
    python main.py "sorum"    # tek soru, çıkış

    streamlit run ui_streamlit.py   # web arayüzü
"""
from __future__ import annotations

import sys

import db
import foundry_client as fc
from generation import answer_query


def _banner(chunk_count: int) -> None:
    print("=" * 58)
    print("  Local RAG Assistant  ·  Foundry Local  ·  Offline")
    print(f"  {chunk_count} chunk yüklü  ·  çıkmak için: exit")
    print("=" * 58)
    print()


def _print_answer(result: dict) -> None:
    print()
    print(result["answer"])
    if result["sources"]:
        print(f"\n  [kaynak] {', '.join(result['sources'])}")
    print()


def main() -> None:
    # DB kontrolü
    conn = db.get_connection()
    db.init_db(conn)
    chunk_count = db.count_documents(conn)
    conn.close()

    if chunk_count == 0:
        print("[!] Veritabanı boş. Önce çalıştır:  python ingest.py")
        sys.exit(1)

    # Tek soru modası: python main.py "sorum nedir"
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        result = answer_query(question)
        _print_answer(result)
        fc.shutdown()
        return

    # İnteraktif döngü
    _banner(chunk_count)
    print("  (İlk soruda modeller yükleniyor olabilir, lütfen bekleyin.)\n")

    try:
        while True:
            try:
                q = input("Soru> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nÇıkılıyor...")
                break

            if q.lower() in {"exit", "quit", "q", "çık", "cik", ""}:
                if q == "":
                    continue
                break

            result = answer_query(q)
            _print_answer(result)

    finally:
        fc.shutdown()


if __name__ == "__main__":
    main()
