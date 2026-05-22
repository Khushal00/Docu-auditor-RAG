from __future__ import annotations

import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
SRC_DIR = PROJECT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from audit_extraction_engine.query import ask_question


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python scripts/ask_contract.py "Your question here"')

    question = sys.argv[1]
    result = ask_question(question)
    print(json.dumps(result, indent=2))
