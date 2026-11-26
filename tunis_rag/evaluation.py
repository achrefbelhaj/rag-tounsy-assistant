"""Évaluation de la recherche (sans LLM) avec la métrique Hit@k."""


def evaluate(store, questions: list[dict], top_k: int = 3) -> dict:
    """Hit@k = part des questions dont le document attendu est dans les top_k résultats.

    Une question sans "expected_source" est hors corpus : on garde seulement son meilleur
    score, pour choisir MIN_SCORE (il doit être au-dessus de ces scores).
    """
    rows = []
    for item in questions:
        results = store.search(item["question"], top_k)
        sources = [r.source for r in results]
        expected = item.get("expected_source")
        rows.append({
            "question": item["question"],
            "expected": expected,
            "hit": expected in sources if expected else None,
            "top_score": results[0].score if results else 0.0,
        })
    with_answer = [r for r in rows if r["expected"]]
    hit_at_k = sum(r["hit"] for r in with_answer) / len(with_answer) if with_answer else 0.0
    return {"hit_at_k": hit_at_k, "rows": rows}
