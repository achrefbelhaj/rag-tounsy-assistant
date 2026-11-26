from tunis_rag.chunker import Chunk
from tunis_rag.rag import NOT_FOUND, RagService
from tunis_rag.store import Hit
from tests.conftest import FakeLLM, FakeStore


def test_store_returns_best_match_with_source_page_and_heading(store):
    store.add_chunks([
        Chunk("les thermes d'Antonin à Carthage", "carthage.pdf", 7, "Sites", 0),
        Chunk("le couscous et le brik tunisien", "cuisine.md", None, "Plats", 0),
    ])
    best = store.search("thermes Antonin", top_k=2)[0]
    assert (best.source, best.page, best.heading) == ("carthage.pdf", 7, "Sites")


def test_rag_refuses_without_calling_llm_when_score_is_too_low():
    llm = FakeLLM()
    service = RagService(FakeStore([Hit("texte", "a.md", None, "", 0.2)]), llm, min_score=0.5)
    result = service.ask("pizza napolitaine ?")
    assert result.answer == NOT_FOUND and result.sources == []
    assert llm.calls == []                       # le LLM n'est jamais appelé


def test_rag_answers_and_sends_numbered_sources_to_llm():
    hits = [Hit("La mosquée est dans la médina.", "medina.md", None, "Médina", 0.9),
            Hit("Les thermes sont en bord de mer.", "carthage.pdf", 7, "Sites", 0.8)]
    llm = FakeLLM("C'est dans la médina [1].")
    result = RagService(FakeStore(hits), llm, min_score=0.5).ask("où est la mosquée ?")
    assert result.answer == "C'est dans la médina [1]." and len(result.sources) == 2
    prompt = llm.calls[0][1]
    assert "[1] (medina.md, section « Médina »)" in prompt
    assert "[2] (carthage.pdf, page 7, section « Sites »)" in prompt
