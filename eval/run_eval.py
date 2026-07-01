"""
run_eval.py  —  Soru setini koştur, sonuçları raporla
Çalıştır (proje kökünden):  python eval/run_eval.py
Seçenekler:
  --verbose   Her sorudan sonra tam cevabı göster
  --fail-only Yalnızca başarısız soruları göster
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Windows terminali bazen CP1252/CP1254 kullanır; UTF-8'e geç
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import yaml

# eval/ alt klasöründeyiz; proje kökünü import yoluna ekle
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generation import answer_query  # noqa: E402

QUESTIONS = Path(__file__).parent / "questions.yaml"

# Sistem "bilmiyorum" dediğinde cevapta geçmesi muhtemel ifadeler
FALLBACK_MARKERS = [
    "bilgi yok",
    "bilmiyorum",
    "elimdeki dökümanlarda",
    "bulunmamaktadır",
    "bulamadım",
    "yeterli bilgi",
]


def is_fallback(answer: str) -> bool:
    low = answer.lower()
    return any(m in low for m in FALLBACK_MARKERS)


def evaluate_case(case: dict) -> tuple[bool, str, dict]:
    """Tek bir test case'i değerlendir. (ok, reason, result) döndürür."""
    q = case["question"]
    qtype = case.get("type", "answerable")
    t0 = time.perf_counter()
    result = answer_query(q)
    elapsed = time.perf_counter() - t0
    ans = result["answer"]

    if qtype == "unanswerable":
        ok = is_fallback(ans)
        reason = "correct fallback" if ok else "should have said it doesn't know"
    else:
        expect = case.get("expect_contains")
        if is_fallback(ans):
            ok = False
            reason = "gave fallback when answer exists in docs"
        elif expect and expect.lower() not in ans.lower():
            ok = False
            reason = f"expected '{expect}' not found in answer"
        else:
            ok = True
            reason = "correct"

    result["_elapsed"] = elapsed
    result["_reason"] = reason
    return ok, reason, result


def print_result(i: int, case: dict, ok: bool, reason: str, result: dict,
                 verbose: bool, fail_only: bool) -> None:
    q = case["question"]
    qtype = case.get("type", "answerable")
    status = "[PASS]" if ok else "[FAIL]"
    elapsed = result.get("_elapsed", 0.0)

    if fail_only and ok:
        return

    print(f"\n[{i:02d}] [{qtype:>12}] {q}")
    print(f"      {status}  ({elapsed:.2f}s)  - {reason}")
    print(f"      kaynaklar: {result['sources'] or '-'}")

    if verbose or not ok:
        preview = result["answer"][:300].replace("\n", " ")
        print(f"      cevap: {preview}")


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG evaluation runner")
    parser.add_argument("--verbose", action="store_true",
                        help="Her sorudan sonra tam cevabı göster")
    parser.add_argument("--fail-only", action="store_true",
                        help="Yalnızca başarısız soruları göster")
    args = parser.parse_args()

    cases = yaml.safe_load(QUESTIONS.read_text(encoding="utf-8"))
    answerable = [c for c in cases if c.get("type", "answerable") == "answerable"]
    unanswerable = [c for c in cases if c.get("type") == "unanswerable"]

    print(f"=== RAG Evaluation - {len(cases)} sorular "
          f"({len(answerable)} answerable, {len(unanswerable)} unanswerable) ===")

    passed = 0
    total_time = 0.0

    for i, case in enumerate(cases, 1):
        ok, reason, result = evaluate_case(case)
        passed += int(ok)
        total_time += result.get("_elapsed", 0.0)
        print_result(i, case, ok, reason, result, args.verbose, args.fail_only)

    failed = len(cases) - passed
    avg_time = total_time / len(cases) if cases else 0.0

    print("\n" + "-" * 60)
    print(f"  Gecti : {passed}/{len(cases)}")
    print(f"  Kaldi : {failed}/{len(cases)}")
    print(f"  Ort.  : {avg_time:.2f}s / soru")
    print("-" * 60)

    if failed > 0:
        print("\nİpucu: data/ belgelerini genişlet, chunk boyutunu veya top-k'yı ayarla.")
    else:
        print("\nTüm testler geçti. Proje hazır!")


if __name__ == "__main__":
    main()
