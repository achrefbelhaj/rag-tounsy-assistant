"""Évalue la recherche (Hit@3) et aide à choisir MIN_SCORE : python -m scripts.evaluate"""
import json

from tunis_rag import config
from tunis_rag.embeddings import Embedder
from tunis_rag.evaluation import evaluate
from tunis_rag.store import VectorStore

QUESTIONS_FILE = config.ROOT / "eval" / "questions.json"
TOP_K = 3


def main() -> None:
    questions = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    store = VectorStore(config.CHROMA_DIR, config.COLLECTION_NAME, Embedder(config.EMBEDDING_MODEL))
    report = evaluate(store, questions, TOP_K)

    for row in report["rows"]:
        if not row["expected"]:
            status = "HORS CORPUS"
        else:
            status = "ok" if row["hit"] else "RATÉ"
        print(f"[{status:11s}] score={row['top_score']:.3f}  {row['question']}")

    good = [r["top_score"] for r in report["rows"] if r["expected"]]
    bad = [r["top_score"] for r in report["rows"] if not r["expected"]]
    print(f"\nHit@{TOP_K} = {report['hit_at_k'] * 100:.0f} %")
    print(f"Plus petit score d'une bonne question : {min(good):.3f}")
    print(f"Plus grand score d'une question hors corpus : {max(bad):.3f}")
    print(f"MIN_SCORE actuel : {config.MIN_SCORE} (à placer entre les deux scores ci-dessus)")


if __name__ == "__main__":
    main()

