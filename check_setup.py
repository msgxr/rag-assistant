"""
Check the local RAG project setup without loading the chat or embedding models.

This script is meant for students before they run ingestion:

    python check_setup.py
    python check_setup.py --models
"""
from __future__ import annotations

import argparse
import importlib.metadata as metadata
import platform
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "rag.db"


def package_version(*names: str) -> str | None:
    for name in names:
        try:
            return f"{name} {metadata.version(name)}"
        except metadata.PackageNotFoundError:
            continue
    return None


def print_section(title: str) -> None:
    print(f"\n== {title} ==")


def load_project_config():
    try:
        import foundry_client as fc
    except Exception as exc:
        print(f"[FAIL] Could not import foundry_client.py: {exc}")
        print("       Run: pip install -r requirements.txt")
        return None
    return fc


def get_catalog():
    try:
        from foundry_local_sdk import Configuration, FoundryLocalManager
    except Exception as exc:
        print(f"[FAIL] Could not import Foundry Local SDK: {exc}")
        print("       Run: pip install -r requirements.txt")
        return None

    try:
        FoundryLocalManager.initialize(Configuration(app_name="rag-assistant-check"))
    except Exception as exc:
        if FoundryLocalManager.instance is None:
            print(f"[FAIL] Foundry Local could not initialize: {exc}")
            return None

    return FoundryLocalManager.instance.catalog


def describe_model(model) -> str:
    caps = model.capabilities or "general"
    cached = "cached" if model.is_cached else "not cached"
    loaded = "loaded" if model.is_loaded else "not loaded"
    return f"{model.alias} ({caps}, {cached}, {loaded})"


def check_alias(catalog, role: str, alias: str) -> bool:
    model = catalog.get_model(alias)
    if model is None:
        print(f"[FAIL] {role} alias not found in catalog: {alias}")
        return False

    print(f"[OK]   {role}: {describe_model(model)}")
    return True


def print_model_list(models: list) -> None:
    for model in models:
        caps = model.capabilities or "general"
        context = model.context_length or "unknown"
        print(f"{model.alias:28} {caps:24} context={context}")


def check_data_and_db() -> None:
    docs = sorted(
        p for p in DATA_DIR.glob("*")
        if p.is_file() and p.suffix.lower() in {".md", ".txt"}
    )
    print(f"[OK]   data documents: {len(docs)}")
    for path in docs[:5]:
        print(f"       - {path.relative_to(ROOT)}")
    if len(docs) > 5:
        print(f"       ... {len(docs) - 5} more")

    if not DB_PATH.exists():
        print("[INFO] rag.db does not exist yet. Run: python ingest.py")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        conn.close()
    except sqlite3.Error as exc:
        print(f"[WARN] rag.db exists but could not be read: {exc}")
        return

    print(f"[OK]   database chunks: {count}")
    if count == 0:
        print("       Run: python ingest.py")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the local RAG assistant setup.")
    parser.add_argument(
        "--models",
        action="store_true",
        help="Print all model aliases from the Foundry Local catalog.",
    )
    args = parser.parse_args()

    print_section("Python")
    print(f"[OK]   {sys.version.split()[0]} on {platform.system()} {platform.release()}")

    print_section("Packages")
    sdk = package_version("foundry-local-sdk-winml", "foundry-local-sdk")
    if sdk is None:
        print("[FAIL] Foundry Local SDK is not installed.")
        print("       Run: pip install -r requirements.txt")
        return 1
    print(f"[OK]   {sdk}")

    print_section("Project config")
    fc = load_project_config()
    if fc is None:
        return 1
    print(f"[OK]   chat model alias: {fc.CHAT_MODEL_ALIAS}")
    print(f"[OK]   embedding model alias: {fc.EMBEDDING_MODEL_ALIAS}")

    print_section("Foundry Local catalog")
    catalog = get_catalog()
    if catalog is None:
        return 1

    try:
        models = catalog.list_models()
    except Exception as exc:
        print(f"[FAIL] Could not read model catalog: {exc}")
        return 1

    print(f"[OK]   catalog models: {len(models)}")
    aliases_ok = True
    aliases_ok &= check_alias(catalog, "chat", fc.CHAT_MODEL_ALIAS)
    aliases_ok &= check_alias(catalog, "embedding", fc.EMBEDDING_MODEL_ALIAS)

    if args.models:
        print_section("Available model aliases")
        print_model_list(models)

    print_section("Local data")
    check_data_and_db()

    if not aliases_ok:
        print("\nUpdate CHAT_MODEL_ALIAS or EMBEDDING_MODEL_ALIAS in foundry_client.py.")
        return 1

    print("\nSetup check complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
