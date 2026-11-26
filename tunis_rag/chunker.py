"""Découpage : un paragraphe = un morceau (chunk).

Un paragraphe porte une idée complète, donc on ne le coupe jamais.
Le titre de section (# ...) est gardé avec chaque morceau : il s'affiche dans les sources
et il est ajouté au texte vectorisé pour mieux situer le passage.
"""
import re
from dataclasses import dataclass

from .loader import Section


@dataclass
class Chunk:
    text: str
    source: str
    page: int | None
    heading: str
    index: int

    @property
    def embed_text(self) -> str:
        return f"{self.heading}\n{self.text}" if self.heading else self.text


def _blocks(text: str):
    """Produit (titre courant, paragraphe) pour chaque paragraphe non vide."""
    heading = ""
    for raw in re.split(r"\n\s*\n", text):
        lines = raw.strip().split("\n")
        while lines and lines[0].lstrip().startswith("#"):
            heading = lines.pop(0).lstrip("# ").strip()
        paragraph = "\n".join(line.strip() for line in lines if line.strip())
        if paragraph:
            yield heading, paragraph


def chunk_section(section: Section, start_index: int = 0) -> list[Chunk]:
    return [Chunk(paragraph, section.source, section.page, heading, start_index + i)
            for i, (heading, paragraph) in enumerate(_blocks(section.text))]


def chunk_sections(sections: list[Section]) -> list[Chunk]:
    """Découpe plusieurs sections (pages) en gardant une numérotation continue."""
    chunks: list[Chunk] = []
    for section in sections:
        chunks.extend(chunk_section(section, start_index=len(chunks)))
    return chunks
