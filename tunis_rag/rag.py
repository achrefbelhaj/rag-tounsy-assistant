"""Service RAG : recherche, filtre de pertinence, prompt, génération."""
from dataclasses import dataclass, field

from .store import Hit

NOT_FOUND = "Je ne trouve pas cette information dans les documents disponibles."

SYSTEM_PROMPT = f"""Tu es un guide documentaire sur la ville de Tunis.
Tu réponds uniquement avec les extraits numérotés fournis dans le contexte.

Règles :
- N'ajoute aucune information qui ne figure pas dans les extraits.
- Ne devine ni prix, ni horaires, ni dates.
- Cite les extraits utilisés avec leur numéro, par exemple [1] ou [2].
- Si les extraits ne permettent pas de répondre, réponds exactement : {NOT_FOUND}
- Réponds dans la langue de la question, en phrases courtes."""


@dataclass
class Answer:
    answer: str
    answered: bool
    sources: list[Hit] = field(default_factory=list)


def build_context(hits: list[Hit]) -> str:
    blocks = []
    for number, hit in enumerate(hits, start=1):
        place = hit.source
        if hit.page:
            place += f", page {hit.page}"
        if hit.heading:
            place += f", section « {hit.heading} »"
        blocks.append(f"[{number}] ({place})\n{hit.text}")
    return "\n\n".join(blocks)


class RagService:
    def __init__(self, store, llm, top_k: int = 4, min_score: float = 0.78):
        self.store = store
        self.llm = llm
        self.top_k = top_k
        self.min_score = min_score

    def ask(self, question: str, top_k: int | None = None) -> Answer:
        hits = self.store.search(question, top_k or self.top_k)
        relevant = [h for h in hits if h.score >= self.min_score]
        if not relevant:  # rien d'assez proche : inutile (et risqué) d'appeler le LLM
            return Answer(answer=NOT_FOUND, answered=False)

        user_prompt = f"EXTRAITS :\n{build_context(relevant)}\n\nQUESTION : {question}"
        text = self.llm.generate(SYSTEM_PROMPT, user_prompt)
        return Answer(answer=text, answered=NOT_FOUND not in text, sources=relevant)
