from tunis_rag.chunker import chunk_section, chunk_sections
from tunis_rag.loader import Section


def test_one_chunk_per_paragraph_and_heading_is_kept():
    section = Section("# A\n\nPremier.\n\nDeuxième.\n\n# B\n\nTroisième.", "doc.md")
    chunks = chunk_section(section)
    assert [(c.heading, c.text) for c in chunks] == [
        ("A", "Premier."), ("A", "Deuxième."), ("B", "Troisième.")]
    assert chunks[0].embed_text == "A\nPremier."   # le titre aide la recherche


def test_indexes_are_continuous_and_page_is_kept():
    chunks = chunk_sections([Section("Page un.", "doc.pdf", page=1),
                             Section("Page deux.", "doc.pdf", page=2)])
    assert [(c.index, c.page) for c in chunks] == [(0, 1), (1, 2)]
