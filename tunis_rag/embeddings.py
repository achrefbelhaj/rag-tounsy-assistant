"""Transforme des textes en vecteurs (embeddings) avec un modèle multilingue."""


class Embedder:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._model = None

    def _encode(self, texts: list[str]) -> list[list[float]]:
        if self._model is None:  # chargement paresseux : fait au premier appel seulement
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        vectors = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return vectors.tolist()

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return self._encode(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._encode([text])[0]
