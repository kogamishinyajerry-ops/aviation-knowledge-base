"""Run sample queries from evaluation/queries.yaml against the RAG index.

Picks 5 queries spanning factual / table / cross_lingual / out_of_scope
to demonstrate every code path including the guardrail.

Usage: python -m scripts.rag.eval_run
Output: scripts/rag/eval_results.json + demo/ask.html (regenerated)
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parent.parent.parent
QUERIES = ROOT / "evaluation" / "queries.yaml"
RESULTS = Path(__file__).resolve().parent / "eval_results.json"

# Sample query selection — one per type, picked to exercise full pipeline
SAMPLE_QUERY_IDS = [
    "q-001",   # factual — should retrieve & cite
    "q-010",   # table — atomic-table chunk
    "q-019",   # procedural / cross
    "q-025",   # cross_lingual — bilingual entity
    "q-028",   # out_of_scope — must trip guardrail
]


def load_queries():
    yaml = YAML(typ="safe")
    data = yaml.load(QUERIES.read_text())
    by_id = {q["query_id"]: q for q in data["queries"]}
    return by_id


def main():
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("ERROR: DEEPSEEK_API_KEY not set; cannot run end-to-end queries.", file=sys.stderr)
        return 2

    from scripts.rag.query import ask

    queries = load_queries()
    selected = []
    for qid in SAMPLE_QUERY_IDS:
        if qid not in queries:
            # fallback: pick first of right type
            for q in queries.values():
                if qid == q["query_id"]:
                    selected.append(q)
                    break
            else:
                print(f"  ! query {qid} not found, skipping")
                continue
        else:
            selected.append(queries[qid])

    if len(selected) < 5:
        # Pad with first few queries of various types
        seen = {q["query_id"] for q in selected}
        for q in queries.values():
            if q["query_id"] not in seen and len(selected) < 5:
                selected.append(q)

    results = []
    for q in selected:
        print(f"\n→ [{q['query_id']}] type={q['type']} : {q.get('query_en') or q.get('query_zh')}")
        question = q.get("query_en") or q.get("query_zh")
        try:
            r = ask(question)
            d = asdict(r)
            d["query_meta"] = {
                "query_id": q["query_id"],
                "type": q["type"],
                "query_zh": q.get("query_zh"),
                "query_en": q.get("query_en"),
                "expected_documents": q.get("expected_documents", []),
            }
            results.append(d)
            if r.guardrail_tripped:
                print(f"  ⚠️  GUARDRAIL: {r.rejected_reason}")
            else:
                print(f"  ✓  answer ({len(r.citations)} citations)")
                print(f"     {r.answer[:200]}…" if len(r.answer) > 200 else f"     {r.answer}")
        except Exception as e:
            print(f"  ! exception: {e}")
            results.append({
                "query_meta": {"query_id": q["query_id"], "type": q["type"]},
                "error": str(e),
            })

    RESULTS.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\n✓ Saved {len(results)} results to {RESULTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
