"""
run_eval.py  —  Soru setini koştur, sonuçları raporla  (Sahip: Ortak)
Çalıştır (proje kökünden):  python eval/run_eval.py
"""
from __future__ import annotations
import sys
from pathlib import Path

import yaml

# eval/ alt klasöründeyiz; proje kökünü import yoluna ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generation import answer_query  # noqa: E402

QUESTIONS = Path(__file__).parent / "questions.yaml"
# Sistem "bilmiyorum" dediğinde cevapta geçmesi muhtemel ifadeler
FALLBACK_MARKERS = ["bilgi yok", "bilmiyorum", "elimdeki dökümanlarda", "bulunmamaktadır"]


def is_fallback(answer: str) -> bool:
    low = answer.lower()
    return any(m in low for m in FALLBACK_MARKERS)


def main() -> None:
    cases = yaml.safe_load(QUESTIONS.read_text(encoding="utf-8"))
    passed = 0
    for i, case in enumerate(cases, 1):
        q = case["question"]
        qtype = case.get("type", "answerable")
        r = answer_query(q)
        ans = r["answer"]

        if qtype == "unanswerable":
            ok = is_fallback(ans)
        else:
            expect = case.get("expect_contains")
            ok = (not is_fallback(ans)) and (
                expect.lower() in ans.lower() if expect else True
            )

        passed += int(ok)
        print(f"\n[{i}] ({qtype}) {q}")
        print(f"    -> {ans[:160]}")
        print(f"    {'PASS' if ok else 'FAIL'}   kaynaklar={r['sources']}")

    print(f"\n=== {passed}/{len(cases)} geçti ===")


if __name__ == "__main__":
    main()
