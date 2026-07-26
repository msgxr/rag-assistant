"""
hello_model.py  —  "Hello Model" testi (Hafta 1)

Foundry Local kurulumunun gerçekten çalıştığını doğrular: chat modelini
yükler, tek bir basit completion üretir ve modeli bellekten boşaltır.

Çalıştır (proje kökünden):
    python examples/hello_model.py
    python examples/hello_model.py "Kendi promptun"

Not: fc.chat() ilk çağrıda embedding modelini de yükler; böylece bu test
tüm runtime'ın uçtan uca çalıştığını da doğrulamış olur.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Windows terminali bazen CP1254 kullanır; Türkçe karakterler için UTF-8'e geç
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# examples/ içinden çalıştırılınca proje kökünü import yoluna ekle
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import foundry_client as fc  # noqa: E402


def main() -> None:
    prompt = " ".join(sys.argv[1:]) or "Say hello in one sentence."
    print(f"[->] Chat modeli: {fc.CHAT_MODEL_ALIAS}")
    print("[->] Model yükleniyor (ilk çalıştırmada indirme birkaç dakika sürebilir)...")

    answer = fc.chat([{"role": "user", "content": prompt}])

    print(f"\nPROMPT : {prompt}")
    print(f"CEVAP  : {answer.strip()}")
    fc.shutdown()


if __name__ == "__main__":
    main()
