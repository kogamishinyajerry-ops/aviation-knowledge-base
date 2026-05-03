# evaluation/ — Aviation KB RAG Eval Set

> ## AI 接力开发指南
>
> **读这一节，5 分钟内你应当能接手维护 `evaluation/queries.yaml`。** (AIH-01)
>
> ### What this directory IS
>
> - The **eval contract** for the Phase 7 RAG implementation.
> - A frozen YAML file (`queries.yaml`) of ≥30 bilingual aviation queries
>   with expected source-document URIs and a `type` taxonomy.
> - The single source of truth for Phase 7 acceptance gates: recall@5,
>   cross-lingual recall@5, out-of-scope short-circuit rate, and citation
>   accuracy. See `## Phase 7 Consumption Contract` below.
>
> ### What this directory IS NOT
>
> - **NOT an executable eval harness.** Phase 5 is design-only — no
>   embeddings are computed, no retrieval is run, no LLM is called from
>   anything in this directory.
> - **NOT a place to add expected answers.** We deliberately do not write
>   "ground-truth answer text" because (a) Phase 7 must measure retrieval,
>   not generation, and (b) bilingual reference answers double the
>   maintenance cost. We measure via `expected_documents` URI overlap and
>   `expected_keywords` substring presence — both cheap and stable.
> - **NOT a benchmark vs other RAG systems.** This is an internal
>   contract for our 3-doc demo corpus (FAR §25.1309 / NASA TM-2014-218175
>   / NTSB AAR-09/03). External benchmarks (BEIR, MIRACL, MTEB) live in
>   future work.
>
> ### How Phase 7 consumes this dir
>
> 1. Load `queries.yaml` via `yaml.safe_load`.
> 2. For each query, run the production RAG pipeline (chunker →
>    embedder → hybrid retriever → reranker) with `query_zh` OR `query_en`
>    as the input.
> 3. Compare retrieved document URIs against `expected_documents`.
> 4. For `type: out_of_scope`, assert the §6 guardrail short-circuited
>    (`llm_called == False` and the canned no-context response was emitted).
> 5. Aggregate per-type metrics; assert against the gates in the
>    `## Phase 7 Consumption Contract` section.
>
> ### 5-minute "stranger test" — pass criterion
>
> A new contributor with no prior context should be able to:
> 1. Pick the next free `query_id` (sequential `q-NNN`).
> 2. Author a new bilingual query targeting one of the 3 corpus
>    documents.
> 3. Pick the right `type` from the enum.
> 4. Validate via `python -c 'import yaml; yaml.safe_load(open("evaluation/queries.yaml"))'` and `yamllint evaluation/queries.yaml`.
> 5. Submit the PR. CI's `lint` job will pick up yamllint; reviewers will
>    pick up schema/coverage issues.
>
> If a stranger fails this in 5 min, the schema or this README is broken
> — fix it before re-merging.

## Schema

Each record under the top-level `queries:` list MUST conform to this shape:

```yaml
- query_id: q-001                # REQUIRED. Kebab-case, sequential 'q-NNN'.
                                 # Stable; never renumber after merge.
  query_zh: "..."                # REQUIRED. Chinese form of the query.
  query_en: "..."                # REQUIRED. English form of the query.
                                 # For type=cross_lingual this is the form
                                 # the source document is written in.
  type: factual|table|procedural|cross_lingual|out_of_scope
                                 # REQUIRED. Exactly one of these 5 values.
  expected_documents:            # REQUIRED. List of Document URIs from
    - aviationkb://document/...  # instances/entities/document/. Empty list
                                 # ([]) for type=out_of_scope; ≥1 otherwise.
  expected_section: "§..."       # OPTIONAL. Section anchor or page hint.
                                 # Helps Phase 7 chunk-localisation tests.
  expected_keywords: ["..."]     # OPTIONAL. Strings expected in the
                                 # retrieved chunk text. Bilingual OK.
  notes: "..."                   # REQUIRED. Why this query exists, what
                                 # pitfall it stresses, what gate it feeds.
```

Validity is enforced by:

1. `python -c 'import yaml; yaml.safe_load(open("evaluation/queries.yaml"))'`
   — must parse cleanly (no YAML errors, no duplicate keys).
2. `yamllint .yamllint evaluation/queries.yaml` — style gate (mostly
   formatting, see `.yamllint` for rule rationales).
3. The Phase 7 implementer's `assert` block (see `## Phase 7 Consumption
   Contract`) — semantic gate (counts, URI validity, etc.).

## Categories

| Type             | Min count | Purpose                                                                 |
| ---------------- | --------- | ----------------------------------------------------------------------- |
| `factual`        | (no min)  | Baseline single-fact lookup (one §-clause / one paragraph).             |
| `table`          | ≥6 (≥20%) | Pitfall 6 verification — chunking must keep tables atomic.              |
| `procedural`     | (no min)  | Multi-step instruction retrieval (process / procedure / methodology).   |
| `cross_lingual`  | ≥6        | Pitfall 7 verification — ZH↔EN recall ≥0.70 per RAG_PIPELINE.md §7.     |
| `out_of_scope`   | ≥3        | Pitfall 9 verification — guardrail must short-circuit (no LLM call).    |
| **Total**        | **≥30**   | RAG-07 acceptance criterion (ROADMAP Phase-5 SC-5).                     |

Counts are enforced at write time (see Phase 7 Consumption Contract block
below) and at `validate.py` time (Phase 7 work — out of scope for Phase 5).

## Phase 7 Consumption Contract

```python
# Phase 7 implementation — pseudocode for the eval harness:
import yaml
queries = yaml.safe_load(open("evaluation/queries.yaml"))["queries"]

# Per-type metrics
metrics = {
    "recall@5":                   measure_recall_at_k(queries, k=5),
    "cross_lingual_recall@5":     measure_recall_at_k(
        [q for q in queries if q["type"] == "cross_lingual"], k=5),
    "out_of_scope_short_circuit_rate": measure_short_circuit(
        [q for q in queries if q["type"] == "out_of_scope"]),
    "citation_accuracy":          measure_citation_accuracy(queries, sample_n=20),
    "table_recall@5":             measure_recall_at_k(
        [q for q in queries if q["type"] == "table"], k=5),
}

# Acceptance gates (per RAG_PIPELINE.md §3.3 + §7 + §6):
assert metrics["recall@5"]                        >= 0.80   # overall
assert metrics["cross_lingual_recall@5"]          >= 0.70   # §7 — Pitfall 7
assert metrics["out_of_scope_short_circuit_rate"] == 1.00   # §6 — Pitfall 9 (HARD)
assert metrics["citation_accuracy"]               >= 0.95   # §5 — RAG-04 gate
assert metrics["table_recall@5"]                  >= 0.80   # §2 — Pitfall 6
```

Notes:

- `measure_recall_at_k` = `len(retrieved_top_k ∩ expected_documents) /
  len(expected_documents)`, averaged over the relevant query subset.
- `measure_short_circuit` = fraction of `out_of_scope` queries that the
  guardrail rejected with `llm_called == False`. **Must be 1.00.**
- `measure_citation_accuracy` = on a sample of in-scope queries, fraction
  of `[CITE:c_*]` tokens in the LLM answer that resolve to a real chunk
  in the retrieved set (Pitfall 8 — citation hallucination).

## File Layout

```
evaluation/
├── README.md      ← this file (AI 接力 + schema + Phase-7 contract)
└── queries.yaml   ← ≥30 query records (RAG-07 deliverable)
```

Phase 7 will additionally create:

```
evaluation/
├── results/                ← per-run metric JSON (gitignored)
│   └── 2026-MM-DD-bge-m3.json
└── harness/                ← Python eval runner (Phase 7)
    └── run_eval.py
```

— but those are out of scope for Phase 5.

## Adding a New Query (Phase 7+)

1. Pick the next free `query_id`: `grep -c '^  - query_id:' evaluation/queries.yaml`
   — your new ID is `q-{N+1:03d}`.
2. Confirm every URI in `expected_documents` exists in
   `instances/entities/document/`:
   `ls instances/entities/document/ | sed 's/.yaml//'` — every URI must
   match `aviationkb://document/<basename>@1`.
3. Pick `type` from the 5-value enum. If unsure, default to `factual`
   and let the reviewer reclassify.
4. For `type: out_of_scope`, set `expected_documents: []` (empty list)
   and reference Pitfall 9 in `notes`.
5. For `type: table`, reference "Pitfall 6" or "table chunking" in
   `notes` to make grep verification trivial.
6. For `type: cross_lingual`, reference "Pitfall 7" or "cross-lingual"
   in `notes`. Author the `query_zh` in domain Chinese and the `query_en`
   in the form the source document uses.
7. Run the gates locally:
   ```bash
   python -c 'import yaml; yaml.safe_load(open("evaluation/queries.yaml"))'
   yamllint .yamllint evaluation/queries.yaml
   ```
8. Open the PR. CI catches the rest.

## Cross-References

- **Schema source**: this file's `## Schema` section (mirrored from
  `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-02-PLAN.md`
  `<interfaces>` block).
- **Pipeline design**: `.planning/design/RAG_PIPELINE.md` §3.2 names
  `evaluation/queries.yaml` as the baseline eval set.
- **Pitfalls referenced** (from `.planning/research/PITFALLS.md`):
  - Pitfall 6 — table chunking (drives `type: table` ≥6).
  - Pitfall 7 — cross-lingual recall (drives `type: cross_lingual` ≥6).
  - Pitfall 9 — guardrail bypass (drives `type: out_of_scope` ≥3).
  - Pitfall 12 — eval set missing (this file IS the fix).
- **REQ-coverage**: RAG-07 (Phase 5 plan 05-02) is fully delivered by
  `queries.yaml` + this README. Verifier command lives in
  `.planning/phases/05-rag-pipeline-design-document-only-no-run/05-VALIDATION.md`.
- **Document URIs**: enumerated in `instances/entities/document/`. The
  3 documents that back this eval set are:
  - `aviationkb://document/far-25-1309@1`
  - `aviationkb://document/nasa-tm-2014-218175@1`
  - `aviationkb://document/ntsb-aar-09-03@1`

## Last Touched By

Phase 5 plan 05-02 (RAG eval set), 2026-05-03. See
`.planning/phases/05-rag-pipeline-design-document-only-no-run/05-02-SUMMARY.md`
for the delivery summary.
