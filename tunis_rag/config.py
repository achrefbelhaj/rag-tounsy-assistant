"""Configuration centrale. Chaque valeur peut être changée par variable d'environnement."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _path(name: str, default: Path) -> Path:
    return Path(os.getenv(name, str(default)))


DATA_DIR = _path("DATA_DIR", ROOT / "data" / "tunis")
CHROMA_DIR = _path("CHROMA_DIR", ROOT / "chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "tunis_docs")

# Modèle d'embeddings multilingue (comprend le français et l'arabe).
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# LLM local chargé directement avec Transformers (1.5B : tourne sur CPU, plus vite sur GPU).
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-1.5B-Instruct")


# Recherche : nombre de morceaux et score de similarité minimal (0 à 1).
# À calibrer avec `python -m scripts.evaluate` : ne pas garder la valeur par défaut les yeux fermés.
TOP_K = int(os.getenv("TOP_K", "4"))
MIN_SCORE = float(os.getenv("MIN_SCORE", "0.30"))

ALLOWED_EXTENSIONS = {".txt", ".md", ".docx", ".pdf"}
