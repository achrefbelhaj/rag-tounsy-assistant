"""Lecture + découpage + indexation d'un fichier ou d'un dossier."""
from pathlib import Path

from . import config
from .chunker import chunk_sections
from .loader import load_file


def ingest_file(path: str | Path, store) -> int:
    sections = load_file(path)
    chunks = chunk_sections(sections)
    return store.add_chunks(chunks)


def ingest_folder(folder: str | Path, store) -> dict[str, int]:
    report = {}
    for path in sorted(Path(folder).iterdir()):
        if path.suffix.lower() in config.ALLOWED_EXTENSIONS:
            report[path.name] = ingest_file(path, store)
    return report
