"""Lecture des fichiers TXT, Markdown, Word et PDF.

Un PDF donne une section par page (pour pouvoir citer le numéro de page).
Les autres formats donnent une seule section.
"""
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Section:
    text: str
    source: str
    page: int | None = None


def load_file(path: str | Path) -> list[Section]:
    path = Path(path)
    ext = path.suffix.lower()

    if ext in (".txt", ".md"):
        return [Section(path.read_text(encoding="utf-8-sig"), path.name)]

    if ext == ".docx":
        from docx import Document

        lines = []
        for paragraph in Document(path).paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue
            # Les titres Word deviennent des titres Markdown : le chunker les reconnaît.
            if paragraph.style is not None and paragraph.style.name.startswith("Heading"):
                text = f"# {text}"
            lines.append(text)
        return [Section("\n\n".join(lines), path.name)]

    if ext == ".pdf":
        from pypdf import PdfReader

        sections = []
        for number, page in enumerate(PdfReader(path).pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                sections.append(Section(text, path.name, page=number))
        return sections

    raise ValueError(f"Format non supporté : {ext}")
