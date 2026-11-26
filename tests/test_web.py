from tunis_rag.rag import Answer
from tunis_rag.store import Hit
from app import format_reply


def test_reply_lists_sources_with_page_and_section():
    hits = [Hit("texte", "carthage.pdf", 7, "Thermes", 0.91), Hit("texte", "medina.md", None, "", 0.85)]
    text = format_reply(Answer("C'est à Carthage [1].", True, hits))
    assert "- [1] carthage.pdf, page 7 — Thermes (score 0.91)" in text
    assert "- [2] medina.md (score 0.85)" in text
