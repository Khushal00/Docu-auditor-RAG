from __future__ import annotations

from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = PACKAGE_ROOT.parent
DATA_DIR = PROJECT_ROOT / "data"
ARTIFACTS_DIR = PACKAGE_ROOT / "artifacts"
CHROMA_DIR = PACKAGE_ROOT / "storage" / "chroma"
DEFAULT_PDF_PATH = DATA_DIR / "Fuel Supply Agreement.pdf"
COLLECTION_NAME = "fuel_supply_agreement"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
EMBEDDING_DIMENSION = 256
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_OPENAI_CHAT_MODEL = "gpt-4o-mini"
