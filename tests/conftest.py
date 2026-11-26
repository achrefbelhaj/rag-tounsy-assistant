"""Faux composants pour tester sans télécharger de modèle."""
import re
import zlib

import pytest

from tunis_rag.store import Hit


class FakeEmbedder:
    """Sac de mots haché en 512 dimensions, normalisé : suffit pour tester la mécanique."""
    DIM = 512

    def _vector(self, text):
        vector = [0.0] * self.DIM
        for word in re.findall(r"\w+", text.lower()):
            if len(word) > 2:
                vector[zlib.crc32(word.encode()) % self.DIM] += 1.0
        norm = sum(v * v for v in vector) ** 0.5 or 1.0
        return [v / norm for v in vector]

    def embed_passages(self, texts):
        return [self._vector(t) for t in texts]

    def embed_query(self, text):
        return self._vector(text)


class FakeLLM:
    """Garde les appels reçus pour vérifier ce qu'on lui envoie."""

    def __init__(self, reply="Réponse de test [1]."):
        self.reply = reply
        self.calls = []

    def generate(self, system, user):
        self.calls.append((system, user))
        return self.reply


class FakeStore:
    """Renvoie toujours les mêmes résultats, sans ChromaDB."""

    def __init__(self, hits):
        self.hits = hits

    def search(self, query, top_k):
        return self.hits


@pytest.fixture
def store(tmp_path):
    from tunis_rag.store import VectorStore
    return VectorStore(tmp_path / "chroma", "test", FakeEmbedder())
