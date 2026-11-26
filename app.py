"""Interface chat dans le navigateur (Gradio) : python app.py

Ouvre ensuite http://127.0.0.1:7860. Si la base est vide, les documents de
data/tunis sont indexés automatiquement au démarrage.
"""
from tunis_rag import config
from tunis_rag.embeddings import Embedder
from tunis_rag.ingestion import ingest_folder
from tunis_rag.llm import LLMUnavailable, QwenClient
from tunis_rag.rag import RagService
from tunis_rag.store import VectorStore

EXAMPLES = [
    "Comment aller à Sidi Bou Saïd depuis Tunis ?",
    "Depuis quand la médina de Tunis est-elle inscrite à l'UNESCO ?",
    "Que contient un brik ?",
    "Quelle est la meilleure saison pour visiter Tunis ?",
]


def build_service() -> RagService:
    store = VectorStore(config.CHROMA_DIR, config.COLLECTION_NAME, Embedder(config.EMBEDDING_MODEL))
    return RagService(store, QwenClient(config.LLM_MODEL), config.TOP_K, config.MIN_SCORE)


def format_reply(result) -> str:
    """Réponse du LLM suivie de la liste des sources (fichier, page, section, score)."""
    text = result.answer
    if result.sources:
        text += "\n\n**Sources :**"
        for number, hit in enumerate(result.sources, start=1):
            place = hit.source + (f", page {hit.page}" if hit.page else "")
            if hit.heading:
                place += f" — {hit.heading}"
            text += f"\n- [{number}] {place} (score {hit.score:.2f})"
    return text


def build_demo(service):
    import gradio as gr

    def respond(message, history):
        try:
            return format_reply(service.ask(message))
        except LLMUnavailable as exc:
            return f"Erreur : {exc}"

    return gr.ChatInterface(
        fn=respond,
        title="Assistant Tounsy",
        description="Marhba ! Posez votre question, je réponds avec mes documents et je cite mes sources.",
        examples=EXAMPLES,
    )


def main() -> None:
    service = build_service()
    if not service.store.list_sources():
        print("Base vide : indexation de", config.DATA_DIR)
        ingest_folder(config.DATA_DIR, service.store)
    build_demo(service).launch()


if __name__ == "__main__":
    main()
