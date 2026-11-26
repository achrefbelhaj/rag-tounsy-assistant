"""Base vectorielle ChromaDB : ajout, recherche, liste et suppression de documents."""
from dataclasses import dataclass

import chromadb

from .chunker import Chunk


@dataclass
class Hit:
    text: str
    source: str
    page: int | None
    heading: str
    score: float  # similarité cosinus : 1 = identique, proche de 0 = sans rapport


class VectorStore:
    def __init__(self, path, collection_name: str, embedder):
        self.embedder = embedder
        self._client = chromadb.PersistentClient(path=str(path))
        self._collection = self._client.get_or_create_collection(
            name=collection_name, metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: list[Chunk]) -> int:
        """Indexe les morceaux. Réimporter un fichier remplace son ancienne version."""
        if not chunks:
            return 0
        for source in {c.source for c in chunks}:
            self.delete_source(source)
        self._collection.add(
            ids=[f"{c.source}::{c.index}" for c in chunks],
            documents=[c.text for c in chunks],
            embeddings=self.embedder.embed_passages([c.embed_text for c in chunks]),
            metadatas=[{"source": c.source, "page": c.page or 0,
                        "heading": c.heading, "index": c.index} for c in chunks],
        )
        return len(chunks)

    def search(self, query: str, top_k: int = 4) -> list[Hit]:
        total = self._collection.count()
        if total == 0:
            return []
        result = self._collection.query(
            query_embeddings=[self.embedder.embed_query(query)],
            n_results=min(top_k, total),
        )
        hits = []
        for text, meta, distance in zip(result["documents"][0], result["metadatas"][0],
                                        result["distances"][0]):
            hits.append(Hit(text=text, source=meta["source"], page=meta["page"] or None,
                            heading=meta["heading"], score=1.0 - float(distance)))
        return hits

    def list_sources(self) -> dict[str, int]:
        """Nombre de morceaux par document."""
        counts: dict[str, int] = {}
        for meta in self._collection.get(include=["metadatas"])["metadatas"]:
            counts[meta["source"]] = counts.get(meta["source"], 0) + 1
        return dict(sorted(counts.items()))

    def delete_source(self, source: str) -> int:
        ids = self._collection.get(where={"source": source}, include=[])["ids"]
        if ids:
            self._collection.delete(ids=ids)
        return len(ids)
