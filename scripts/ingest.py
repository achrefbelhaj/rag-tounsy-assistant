"""Indexe un dossier ou un fichier.

    python -m scripts.ingest                       # tout le dossier data/tunis
    python -m scripts.ingest mon_fichier.pdf       # un seul fichier
    python -m scripts.ingest un_autre_dossier
"""
import sys
from pathlib import Path

from tunis_rag import config
from tunis_rag.embeddings import Embedder
from tunis_rag.ingestion import ingest_file, ingest_folder
from tunis_rag.store import VectorStore


def main() -> None:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else config.DATA_DIR
    store = VectorStore(config.CHROMA_DIR, config.COLLECTION_NAME, Embedder(config.EMBEDDING_MODEL))

    if target.is_file():
        if target.suffix.lower() not in config.ALLOWED_EXTENSIONS:
            sys.exit(f"Formats acceptés : {', '.join(sorted(config.ALLOWED_EXTENSIONS))}")
        report = {target.name: ingest_file(target, store)}
    else:
        report = ingest_folder(target, store)

    for name, count in report.items():
        print(f"{name:35s} {count:3d} morceaux" + ("   (aucun texte : PDF scanné ?)" if count == 0 else ""))
    print("Total en base :", sum(store.list_sources().values()), "morceaux")


if __name__ == "__main__":
    main()
