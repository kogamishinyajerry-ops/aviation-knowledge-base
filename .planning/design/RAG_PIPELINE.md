# RAG_PIPELINE.md — Aviation Knowledge Base RAG Pipeline Design

**Phase:** 5 (RAG Pipeline Design — document only, no run)
**Status:** v0.1.0 — design contract for Phase 6 deployment + Phase 7 implementation
**Authors:** gsd-planner / gsd-executor / Phase 5 / 2026-05-03
**Source documents:** [STACK.md](../research/STACK.md), [ARCHITECTURE.md](../research/ARCHITECTURE.md), [PITFALLS.md](../research/PITFALLS.md), [REQUIREMENTS.md](../REQUIREMENTS.md) §RAG-01..08
**Replaces:** nothing
**Replaced by:** nothing (will be amended in Phase 7 with measured benchmark numbers)

***

> ## AI 接力开发指南
>
> 本节让任何接手本文档的 AI / 人在 5 分钟内理解：这是什么文档、它能说什么不能说什么、哪些字段是 locked、哪些是 directional。
>
> This section orients an AI/human picking up `RAG_PIPELINE.md`: what is this document, what it CAN and CANNOT decide, which fields are locked vs directional, and how to navigate it.
>
> ### What this document IS
>
> The single authoritative design contract for the Aviation Knowledge Base RAG pipeline. It covers six topics:
>
> 1. **Chunking strategy** (§2) — how PDF documents become retrievable chunks, with table-as-atomic and regulation-clause-aware rules.
> 2. **Embedding selection** (§3) — which embedding + reranker model is the v1 default, plus the mini-benchmark plan to revisit it.
> 3. **Hybrid retrieval** (§4) — vector + BM25 + RRF fusion configuration, with synonym expansion weight 0.3 (AeroPower-RAG-validated).
> 4. **Citation injection** (§5) — the system-side `[CITE:c_<8hex>]` token mechanism that makes Pitfall 8 (citation hallucination) structurally impossible.
> 5. **Guardrail** (§6) — hard-coded `min_chunk_score = 0.5` and `min_chunks_required = 2` thresholds with bilingual canned no-context response and proof-of-no-LLM-call.
> 6. **Cross-lingual retrieval** (§7) — BGE-M3 native multilingual + bilingual glossary + entity i18n field at index time.
>
> Phase 7 implementers (next AI session) MUST be able to read this doc + STACK.md + ARCHITECTURE.md + PITFALLS.md and write the RAGFlow ingestion pipeline + retrieval orchestration code without further research. The doc defuses Pitfalls 6 / 7 / 8 / 9 by design, not by hope.
>
> ### What this document is NOT
>
> - **Not a tutorial.** It assumes the reader has read STACK.md (RAGFlow 0.25.1, BGE-M3) and PITFALLS.md (Pitfalls 6-9).
> - **Not measured benchmark numbers.** This Phase 5 doc specifies the protocol; Phase 7 runs `evaluation/queries.yaml` (created in plan 05-02) and writes back recall@5 / MRR / cross-lingual recall numbers.
> - **Not running code.** The pseudocode here is illustrative — production code lives in `scripts/exporters/to_ragflow.py` (skeleton from plan 05-03) and `scripts/rag/*` (Phase 7).
> - **Not a deployment plan.** Docker topology, ports, volumes, auth proxy live in Phase 6 (`deploy/`). This doc only defines what RAGFlow needs to know about chunking / embedding / retrieval / guardrail.
> - **No new dependencies introduced beyond Phase 1 STACK.md. No services started. Implementation contract for Phase 7.**
>
> ### Locked vs Directional
>
> | Section | Locked? | Notes |
> |---------|---------|-------|
> | §2 Chunking — RAGFlow OpenDataLoader-PDF backend | **Locked** | STACK.md pins RAGFlow 0.25.1; OpenDataLoader is the v1 default per §2.1 of STACK.md "Document Ingestion Stack" table |
> | §2 Atomic-chunk rules (tables / equations / regulation clauses) | **Locked** | Regex `§\s*\d+\.\d+(\([a-z]\))?(\(\d+\))?` for FAR/CCAR clause boundaries; tables and `$$...$$` blocks atomic |
> | §2.3 Chunk size 512 tokens default / 1024 max / 64 overlap | **Locked** | Concrete values; Phase 7 may tune within ±25% based on eval, not redesign |
> | §3 Default embedding = BGE-M3 + bge-reranker-v2-m3 | **Locked** | STACK.md "Embedding & LLM Layer" + AeroPower-RAG validation |
> | §3.2 Mini-benchmark candidates (nomic-embed-text, multilingual-e5-large) | Directional | Phase 7 may add candidates; cannot remove BGE-M3 baseline |
> | §4 Hybrid = Vector + BM25 + RRF | **Locked** | RAGFlow 0.25.1 native; AeroPower-RAG pattern |
> | §4.2 Synonym expansion weight 0.3 | **Locked** | AeroPower-RAG-validated; do NOT raise without re-eval |
> | §5 Citation token format `[CITE:c_<8hex>]` | **Locked** | Pitfall 8 mitigation; LLM cannot self-author citations |
> | §5.3 Post-validator REJECTS unresolved citations | **Locked** | NOT a warning — Core Value enforcement |
> | §6.1 Thresholds `min_chunk_score = 0.5`, `min_chunks_required = 2` | **Locked** | Pitfall 9 mitigation; Phase 7 may surface for ops tuning but defaults stay |
> | §6.2 Bilingual canned no-context response | **Locked** | Verbatim text, ZH + EN, both required |
> | §7 BGE-M3 native multilingual + glossary expansion + entity i18n | **Locked** | Pitfall 7 mitigation; AeroPower-RAG ZH↔EN recall@3=100% precedent |
> | §7.2 Glossary seed target ≥50 bilingual terms | Directional | Target for `docs/GLOSSARY.md` (Phase 6 deliverable, AIH-04) |
> | §3.3 Decision criteria thresholds (recall@5, latency 1.2×) | Directional | Phase 7 may refine after first measured run |
>
> ### 5-minute stranger test checklist
>
> A fresh AI / human should be able to answer ALL of these in 5 minutes by reading this doc:
>
> - [ ] Q: What PDF parser does RAGFlow use in v1, and why? → §2.1 (OpenDataLoader-PDF, ~14× faster than MinerU)
> - [ ] Q: How big is a chunk by default? → §2.3 (512 tokens, 64 overlap, 1024 hard cap, atomic blocks override)
> - [ ] Q: What stops a regulation clause from being split mid-sentence? → §2.2 (regex `§\s*\d+\.\d+...` clause-aware boundary)
> - [ ] Q: Which embedding model? Why? → §3.1 (BGE-M3, 568M params, 8192 ctx, dense+sparse+colbert-in-one)
> - [ ] Q: How does the LLM cite a chunk? → §5.1 (`[CITE:c_<8hex>]` token, opaque to LLM)
> - [ ] Q: What stops the LLM from inventing a page number? → §5.2 + §5.3 (system-side resolver + post-generation validator REJECTS unresolved tokens)
> - [ ] Q: What happens if retrieval returns 0 chunks? → §6.3 (canned bilingual response, `llm_called=False`)
> - [ ] Q: How is "涡轮叶片" matched to "turbine blade"? → §7 (BGE-M3 multilingual + glossary expansion weight 0.3 + entity i18n field at index time)
>
> If any answer is "TBD" / "see Phase 7" for a Locked field, the doc has regressed and must be patched before Phase 7 starts.
>
> ### How to read this doc
>
> 1. Read §1 (Scope) first — it defines what is in/out of this design pass.
> 2. Read §8 (Pipeline Diagram) for the end-to-end flow before diving into individual sections.
> 3. §2-§7 are the six topics in pipeline order (ingestion → query); read in order if you are implementing top-down.
> 4. §5 + §6 are the **Core Value defenders** — read these even if you are only doing chunking work, because they constrain what retrieval must hand off to the LLM.
> 5. §9 (Open Questions) is the explicit list of things deferred to Phase 7+; if you find a new one, add it there.
> 6. §10 (References) holds canonical external links; do NOT cite ad-hoc sources elsewhere.
>
> ### How to update this doc
>
> v0.1.0 is FROZEN at end of Phase 5. Allowed in-flight edits:
> - Typo fixes
> - Cross-link repair if a target file moves
> - Phase 7 amendment: append measured benchmark numbers to §3.2; update §3.3 with the chosen embedding model. Bumps doc version to v0.2.0 with a CHANGELOG entry.
>
> Changing a Locked field requires an ADR in `.planning/decisions/` plus user sign-off. No Locked-field edits in this doc without that paper trail.

***

## 1. Scope and Non-Goals

**In scope (this document):**

- Chunking strategy for the v1 corpus types: regulations (FAR / CCAR / EASA CS clauses), CFD papers (NASA TM equation/figure layouts), accident reports (NTSB factor tables).
- Embedding model selection rationale + a reproducible mini-benchmark plan (NOT the executed benchmark — that runs in Phase 7).
- Hybrid retrieval configuration (vector + BM25 + RRF fusion + reranker) with concrete numeric values.
- Citation injection mechanics (token format, system-side resolver, post-generation validator) — the structural defense against Pitfall 8 (citation hallucination).
- No-context guardrail with hard threshold values + bilingual canned response — the structural defense against Pitfall 9 (guardrail bypass).
- Cross-lingual retrieval (ZH↔EN) via BGE-M3 native multilingual coverage + glossary expansion + entity i18n indexing.
- An ASCII pipeline diagram tying §2-§7 into a single query→answer flow.

**Explicitly out of scope (deferred):**

- **Real benchmark numbers.** This doc specifies the mini-benchmark protocol; Phase 7 executes it against `evaluation/queries.yaml` (plan 05-02) and amends §3.2/§3.3 with measured recall/MRR.
- **LLM choice.** Pluggable per STACK.md — Phase 6 deployment plan picks Ollama Qwen2.5-14B/32B vs remote Claude/GPT based on hardware reality. This doc only defines what the LLM contract MUST honor (citation token format, no self-authoring page numbers).
- **OCR / scanned PDFs.** RAGFlow DeepDoc fallback is deferred to v2 per CLAUDE.md Out-of-Scope. v1 is text-layer-PDF only.
- **YAML entity record indexing.** Per ARCHITECTURE.md Pattern 4 + Integration Boundaries: v1 only indexes `wiki/**.md` + `docs/**/processed.md`. YAML records surface via citation back-links, not vector retrieval. Phase 7+ may add structured-record indexing via a YAML→prose template.
- **Confidence-aware retrieval filtering.** Schema field `confidence.score` already exists per ARCHITECTURE.md "Provenance & Confidence Storage"; retrieval-time filter (`confidence ≥ X`) wired in Phase 7.
- **Authentication / authorization on retrieval.** v1 single-org, single-role per CLAUDE.md Constraints. Confidentiality-tier filter (`confidentiality != restricted` and `!= itar_ear`) is enforced at INGEST time (`scripts/exporters/to_ragflow.py` plan 05-03), not at retrieval time.
- **Real-time index updates.** Phase 6 deployment plan picks polling cron vs Git webhook for `to_ragflow.py` invocation.

**Non-goal commitments (will not be added later in v1):**

- No SaaS embedding APIs as default (OpenAI text-embedding-3-large, Voyage-3-large) — STACK.md "What NOT to Use" excludes vendor-locked SaaS for v1 baseline. Remote LLM is OK; remote *embedding* is not, because re-embedding cost on corpus growth is unbounded.
- No graph-RAG retrieval — Phase 3+ (per ROADMAP). v1 is pure vector + BM25.
- No agentic loop / tool-calling — per CLAUDE.md "Excluded Tech: 决策型 Agent".

## 2. Chunking Strategy

Defends **Pitfall 6** (chunking breaks tables/equations) by structurally enforcing atomic chunks for the four high-value block types in aviation corpora: tables, equations, regulation clauses, and figure-caption pairs.

### 2.1 RAGFlow OpenDataLoader-PDF backend

**Decision:** RAGFlow v0.25.1 (released Apr 30, 2026 per STACK.md "Recommended Stack > Core Technologies" row) ships **OpenDataLoader-PDF as the default PDF parser** for v1. Per STACK.md "Document Ingestion Stack" table:

- **OpenDataLoader-PDF: ~14× faster than MinerU on 10K-page corpora; ~72min for 10K pages; deterministic; no GPU required.**
- Best for native (text-layer) PDFs — which matches the v1 corpus (FAR/CCAR/EASA-CS in eCFR/PDF, NASA TM CFD papers, NTSB accident reports — all text-layer).
- Single-pass: extracts text + table-structure + figure-caption pairs in one pipeline run.

**DeepDoc fallback** (RAGFlow built-in, visual OCR + table-structure recognition): **deferred to v2** per CLAUDE.md Out-of-Scope ("OCR / 图像理解 — 第一阶段只处理文本文档"). v1 ingestion never invokes DeepDoc; if a scanned PDF appears, the document is rejected at ingest with a `needs_ocr` flag in `metadata.yaml` and never reaches the chunker.

**MinerU** (RAGFlow built-in, alternative DL parser): not used in v1 per STACK.md alternatives matrix ("Skip in v1; available as third option if OpenDataLoader struggles on a specific corpus"). Phase 7 may invoke MinerU on a per-document basis if OpenDataLoader produces zero-content output, but the default backend stays OpenDataLoader.

**Configuration knob (RAGFlow ingestion pipeline JSON, plan 05-03 skeleton):**

```yaml
ingestion:
  parser: opendataloader-pdf      # v1 default; do not change without ADR
  fallback_parser: null           # DeepDoc deferred; explicit null
  on_parse_failure: reject        # do not silently fall through to a worse parser
  preserve_layout: true           # required for table-structure detection in §2.2
```

### 2.2 Atomic-chunk rules (tables, equations, regulation clauses, figure-captions)

The chunker MUST treat the following blocks as **atomic** — never split mid-block, even if the block exceeds the soft size cap. Hard cap is in §2.3.

```text
Tables:               markdown table block (lines starting with `|`) → atomic chunk; do NOT split mid-row
Equation blocks:      $$...$$  →  atomic chunk (single block, even if multi-line)
Code/listings:        ```fenced``` →  atomic chunk
Regulation clauses:   regex `§\s*\d+\.\d+(\([a-z]\))?(\(\d+\))?` →  start a new chunk; never split inside one
Figure-caption pair:  "Figure N: ..." line + adjacent paragraph → atomic
List items in §-clauses: keep `(1) ... (2) ... (3) ...` enumeration intact when total ≤ 1024 tokens
```

**Why each rule (corpus-grounded):**

- **Tables atomic** — `docs/accident-reports/ntsb-aar-09-03/processed.md` contains probable-cause and contributing-factor tables. Splitting "factor row" from "header row" makes retrieval return "see Table 4-2" with no data. Per **Pitfall 6** (PITFALLS.md): "RAGFlow ingestion 配置：开启表格识别（RAGFlow 文档明确支持），表格作为整体 chunk 不切割".
- **Equations atomic** — `docs/cfd-papers/nasa-tm-2014-218175/processed.md` contains `$$...$$` equation blocks (Reynolds-averaged Navier-Stokes, k-ω closure forms). Splitting an equation across chunks loses the unknowns/symbol bindings.
- **Regulation clauses atomic** — `docs/regulations/far-25-1309/processed.md` is structured by `## (a) General`, `## (b) Failure-condition-probability matrix`, `## (c) Crew alerting`. The regex `§\s*\d+\.\d+(\([a-z]\))?(\(\d+\))?` matches FAR/CCAR/EASA-CS clause anchors (e.g., `§25.1309(b)(1)`, `§25.1309(c)`); these MUST start a new chunk and stay self-contained. This prevents Pitfall 5-class supersession-confusion failures (e.g., a chunk containing half of `(b)(1)` and half of `(b)(2)`, both with different probability tiers).
- **Figure-caption pairs** — NASA TM papers reference figures inline ("see Figure 3a"); the caption + immediately-adjacent explanatory paragraph form a semantic unit.

**RAGFlow configuration knob:** atomic-block detection is enabled via the parser layout flag (§2.1 `preserve_layout: true`) plus a chunker post-pass that respects the regex anchors above. Phase 7 implements the post-pass as a small Python pre-processor in `scripts/rag/chunker_postprocess.py` that runs between OpenDataLoader output and RAGFlow's index-write step.

**Failure mode if rules ignored:** a regulation Q&A like "What is the probability tier for a Catastrophic failure under FAR 25.1309?" returns a chunk that ends mid-row of the bullet list ("Catastrophic failure conditions...") without the `≤1×10⁻⁹ per flight hour` answer; the LLM then either (a) refuses (if guardrail fires) or (b) hallucinates the number. Atomic-clause rule prevents (a) and (b).

### 2.3 Chunk size and overlap

| Parameter              | Value         | Rationale                                                                                  |
|------------------------|---------------|--------------------------------------------------------------------------------------------|
| Default chunk size     | **512 tokens**  | Balances retrieval granularity vs context (per PITFALLS Pitfall 6 "建议 512–1024 token") |
| Max chunk size         | **1024 tokens** | Soft cap for non-atomic prose blocks; oversize prose blocks are split                      |
| Overlap                | **64 tokens (12%)** | Keeps cross-sentence anaphora ("This requirement applies to...") resolvable           |
| Atomic-block override  | up to **2048 tokens** | Tables/equations/clauses ignore the 1024 cap — atomic preserved up to 2048 tokens; beyond that, log a warning and accept the oversize block (do NOT split) |
| Tokenizer              | BGE-M3 native (XLM-RoBERTa-based) | Same tokenizer as embedding model; chunk-token-count == embed-input-token-count avoids drift |

**Why 512/64 specifically:** AeroPower-RAG findings (MEMORY.md) reached recall@3=100% on Chinese aviation regulations with chunks in the 400-700 token range and 50-100 token overlap. 512/64 sits in the middle of that band. BGE-M3's 8192-token context window per STACK.md "Embedding & LLM Layer" row easily accommodates 2048-token atomic blocks.

**Phase 7 may tune ±25%** (chunk size 384-640, overlap 48-80) based on `evaluation/queries.yaml` retrieval recall numbers, but cannot exceed 1024 default or drop below 256 without ADR (per "Locked vs Directional" table in AI 接力指南).

### 2.4 Per-corpus chunking config (regulations / cfd-papers / accident-reports)

Three RAGFlow datasets, one per v1 corpus type. Each dataset has its own ingestion-pipeline JSON (skeleton in plan 05-03 `scripts/exporters/to_ragflow.py`).

**Dataset A: regulations** — `docs/regulations/<doc-id>/processed.md`
```yaml
dataset: regulations
parser: opendataloader-pdf
chunk_size: 512
chunk_overlap: 64
atomic_rules:
  - tables
  - equations
  - regulation_clauses     # regex `§\s*\d+\.\d+(\([a-z]\))?(\(\d+\))?` — DRIVES the chunk boundary
special_considerations:
  - clause-aware boundary takes precedence over size cap
  - keep enumeration list `(1)...(2)...(3)...` intact when total ≤ 1024 tokens
example_corpus: docs/regulations/far-25-1309/processed.md  # FAR §25.1309 (a)/(b)/(c)
```

**Dataset B: cfd-papers** — `docs/cfd-papers/<doc-id>/processed.md`
```yaml
dataset: cfd-papers
parser: opendataloader-pdf
chunk_size: 512
chunk_overlap: 64
atomic_rules:
  - tables
  - equations              # $$...$$ blocks — k-ω, RANS, etc. atomic
  - figure_caption_pairs   # "Figure N: ..." line + adjacent paragraph
special_considerations:
  - equation atomic preserved even if oversize (up to 2048; warn beyond)
  - section headers (## Methodology / ## Results) start new chunks
example_corpus: docs/cfd-papers/nasa-tm-2014-218175/processed.md  # NASA TM 2014-218175
```

**Dataset C: accident-reports** — `docs/accident-reports/<doc-id>/processed.md`
```yaml
dataset: accident-reports
parser: opendataloader-pdf
chunk_size: 512
chunk_overlap: 64
atomic_rules:
  - tables                 # probable-cause + contributing-factor tables — STRONGLY atomic
  - factor_enumerations    # bulleted factor lists treated like tables
special_considerations:
  - "Probable Cause" section is its own chunk regardless of size (legal-grade exact text)
  - factor numbering preserved (do not renumber across chunk boundary)
example_corpus: docs/accident-reports/ntsb-aar-09-03/processed.md  # NTSB AAR-09-03
```

**Indexing isolation:** each dataset is a separate RAGFlow knowledge base ID per ARCHITECTURE.md Integration Boundaries "Git Repo → RAGFlow" row. Cross-dataset retrieval at query time is RAGFlow's built-in capability; per-dataset isolation at ingest time keeps chunking config decoupled.

## 3. Embedding Selection

Defends against the "默认 embedding 不够" failure mode in **Pitfall 7** (cross-lingual recall) by pinning a multilingual default and committing to a benchmark protocol.

### 3.1 Default: BGE-M3 + bge-reranker-v2-m3

**Decision:** v1 default embedding is **BGE-M3** (BAAI), reranker is **bge-reranker-v2-m3**. Both per STACK.md "Embedding & LLM Layer" table:

- **BGE-M3:** 568M params, 8192-token context window, multilingual (100+ languages including ZH+EN), dense + sparse + ColBERT multi-vector in one model. Available via Ollama (`ollama pull bge-m3`, ~2GB on disk) or RAGFlow's built-in Xinference.
- **bge-reranker-v2-m3:** pairs natively with BGE-M3, supports ZH/EN, RAGFlow has built-in `--reranker bge-reranker-v2-m3` config.

**Rationale (concrete, not "industry standard"):**

1. **AeroPower-RAG validation (user's prior project, MEMORY.md):** recall@3=100% on Chinese aviation regulations using a closely related multilingual stack (Ollama nomic-embed-text 768d + BM25 bigram + synonym weight 0.3 + RRF fusion). BGE-M3 is the same architectural family with broader multilingual coverage and dense+sparse-in-one (no need for a second sparse pipeline).
2. **One model, three retrieval signals:** BGE-M3's dense + sparse + ColBERT outputs let RAGFlow's hybrid retrieval (§4) draw from a single embedding pass — fewer moving parts, lower memory, simpler ops.
3. **Hardware-friendly on v1 target:** macOS Apple Silicon dev box per CLAUDE.md MEMORY.md. 568M params fits in ~2GB RAM; CPU-friendly per STACK.md "Stack Patterns by Variant" (Apple Silicon row).
4. **Native ZH+EN cross-lingual:** the entire point of §7 — covered without a translation hop.

### 3.2 Mini-benchmark plan (candidates, metrics, baseline eval set)

**Phase 7 MUST execute this benchmark before flipping the default**, even if Phase 7 ends up keeping BGE-M3. The protocol is:

| Candidate                  | Source                  | Why considered                                                                  |
|----------------------------|-------------------------|----------------------------------------------------------------------------------|
| **BGE-M3** (default)       | BAAI / Ollama           | Multilingual, validated above, dense+sparse+colbert-in-one                       |
| **nomic-embed-text v1.5**  | Nomic / Ollama          | AeroPower-RAG actually used the 768d variant; smaller (~280MB), faster, monolingual-leaning |
| **multilingual-e5-large**  | intfloat / Hugging Face | Strong cross-lingual baseline in 2026 leaderboards; ~560M params, 512 ctx       |

**Metrics (locked):**

- `recall@5` — % of golden queries where ≥1 expected chunk_id appears in top-5 retrieved.
- `cross_lingual_recall@5` — recall@5 restricted to queries with `type: cross_lingual` (ZH→EN and EN→ZH).
- `MRR@10` — mean reciprocal rank of the first relevant chunk in top-10.
- `p50_query_latency_ms` — wall-clock from query submission to top-k returned (no LLM call).

**Baseline eval set:** `evaluation/queries.yaml` (Phase 5 plan 05-02 deliverable, ≥30 queries, ≥6 table-type, ≥6 cross-lingual, ≥3 out-of-scope).

**Run protocol (Phase 7):**

1. Index v1 corpus into three parallel RAGFlow knowledge bases, one per candidate embedding model. Use identical chunking config (§2.4) so embedding is the only variable.
2. For each candidate × each query in `evaluation/queries.yaml`: run hybrid retrieval (§4 config), record top-10 chunk_ids + scores + latency.
3. Compute the 4 metrics. Write per-candidate row into `evaluation/results/<run-id>.yaml`.
4. Append the table to §3.2 of THIS doc as "Phase 7 measured results (run-id YYYY-MM-DD)" and bump RAG_PIPELINE.md to v0.2.0.

### 3.3 Decision criteria

**Adopt a non-default candidate** (i.e., switch from BGE-M3) **if and only if** ALL of the following are true:

1. `recall@5` ≥ baseline's 95% (i.e., new candidate gives up at most 5 percentage points of baseline recall — translation: do not regress on the dominant query class).
2. `cross_lingual_recall@5` ≥ **70%** (per Pitfall 7 acceptance threshold; this is the hard floor — no candidate ships below 70%).
3. `p50_query_latency_ms` ≤ baseline's 1.2× (latency budget — embedding model swap should not blow up p50 by more than 20%).
4. Materially better on at least one metric (e.g., +5pp on `recall@5` or +10pp on `cross_lingual_recall@5`); a candidate that merely matches baseline does NOT win — staying on BGE-M3 has zero migration cost.

**Default outcome:** If no candidate satisfies all four criteria, **stay on BGE-M3**. The mini-benchmark is a guardrail, not a requirement to switch. Phase 7 amends §3.3 with the actual decision + measured numbers.

## 4. Hybrid Retrieval

Implements RAGFlow 0.25.1's native hybrid retrieval per STACK.md row "RAGFlow v0.25.1 — native citation grounding, hybrid retrieval, ZH localization". Mirrors AeroPower-RAG's validated pattern (BM25 + vector + RRF + synonym expansion weight 0.3, MEMORY.md).

### 4.1 Vector + BM25 + RRF fusion

**Configuration (locked for v1):**

```yaml
retrieval:
  strategy: hybrid
  vector:
    model: bge-m3           # §3.1 default; switchable per §3.3 decision
    top_k: 20               # cast wide; reranker narrows to final_top_k
    similarity: cosine      # BGE-M3 is L2-normalized; cosine == dot product
  bm25:
    k1: 1.2                 # standard Okapi default; tested on aviation ZH/EN per AeroPower-RAG
    b: 0.75                 # standard Okapi default
    top_k: 20               # parallel with vector top_k for symmetric fusion
    bigram: true            # ZH bigram-index per AeroPower-RAG MEMORY.md (recall@3=100% precedent)
  fusion:
    algorithm: rrf          # Reciprocal Rank Fusion
    k: 60                   # RRF rank constant; AeroPower-RAG-validated default
                            # (per RRF paper: k=60 dampens low-rank noise; do NOT tune below 40)
  final_top_k: 10           # passed downstream to reranker (§4.3)
```

**Why RRF (not weighted score blend):** RRF (Cormack 2009) is rank-based, so it does not require calibrating vector cosine scores against BM25 BM25 scores (different scales, different distributions). Weighted-score blends were tried in AeroPower-RAG and underperformed RRF on ZH↔EN queries. Per **Pitfall 7** (PITFALLS.md): "引入 BM25 + 向量 + RRF（用户已有经验，直接复用）".

**Why top_k=20 for each pre-fusion lane:** RAGFlow internal benchmark + AeroPower-RAG observation that for hybrid fusion to add value over single-lane retrieval, each lane needs to surface enough candidates that fusion has rank-disagreement signal to exploit. Top-5 from each lane is too narrow; top-50 wastes reranker budget. 20 is the sweet spot.

### 4.2 Query expansion (synonym dict, weight 0.3)

**Configuration (locked):**

```yaml
query_expansion:
  source: docs/GLOSSARY.md (Phase 6 deliverable, AIH-04) + ontology/vocabularies/
  weight: 0.3              # AeroPower-RAG-validated; do NOT raise without re-eval
  bilingual: true          # ZH↔EN expansion enabled by default
  apply_to:
    - vector_query         # synonym terms appended to query embedding input
    - bm25_query           # synonym terms OR'd into BM25 query
```

**Mechanism (Phase 7 implementation hint):**

```text
original_query = "涡轮叶片失效"
glossary_lookup → {
  zh: ["涡轮叶片", "涡轮工作叶片", "动叶"],
  en: ["turbine blade", "rotor blade"]
}
expanded_vector_input  = original_query + " " + 0.3 * "涡轮叶片 涡轮工作叶片 动叶 turbine blade rotor blade"
expanded_bm25_query    = original_query OR ("涡轮叶片" OR "涡轮工作叶片" OR "动叶" OR "turbine blade" OR "rotor blade")
```

The 0.3 weight is verbatim from PITFALLS.md Pitfall 7 example block ("term → synonyms (weight 0.3，承袭 AeroPower-RAG 配置)"). It expresses "synonyms are useful but not authoritative" — raising past 0.5 starts overpowering the original query intent.

**Glossary file (`docs/GLOSSARY.md`, Phase 6, AIH-04):** seed target ≥50 bilingual terms. Format documented in §7.2.

### 4.3 Reranking

**Configuration (locked):**

```yaml
rerank:
  model: bge-reranker-v2-m3   # §3.1 default; pairs with BGE-M3
  input_top_k: 10             # from §4.1 final_top_k
  output_top_k: 5             # passed to LLM context (§5/§6)
  score_threshold: 0.5        # below this → drop chunk; feeds §6 Guardrail
  return_scores: true         # required by §6.1 min_chunk_score check
```

The reranker is the **scoring authority** for the guardrail (§6.1). Vector cosine and BM25 scores are NOT directly comparable to the 0.5 threshold; the reranker normalizes both into a single 0..1 calibrated score. The post-rerank score is what `min_chunk_score = 0.5` checks against.

**Chunks below threshold:** dropped before LLM call. If `len(chunks_above_threshold) < 2`, guardrail fires (§6).

## 5. Citation Injection

TBD in Task 2/3/4

### 5.1 Token format `[CITE:c_<8hex>]`

TBD in Task 2/3/4

### 5.2 Render-layer resolution pseudocode

TBD in Task 2/3/4

### 5.3 Post-generation validator pseudocode

TBD in Task 2/3/4

## 6. Guardrail (No-Context Short-Circuit)

TBD in Task 2/3/4

### 6.1 Threshold values (min_chunk_score, min_chunks_required)

TBD in Task 2/3/4

### 6.2 Canned no-context response (ZH + EN)

TBD in Task 2/3/4

### 6.3 LLM-not-called proof (where the short-circuit lives in the pipeline)

TBD in Task 2/3/4

## 7. Cross-lingual Retrieval

TBD in Task 2/3/4

### 7.1 BGE-M3 native multilingual coverage

TBD in Task 2/3/4

### 7.2 Glossary expansion (≥50 seed terms target — bilingual)

TBD in Task 2/3/4

### 7.3 Entity i18n field at index time

TBD in Task 2/3/4

## 8. Pipeline Diagram (ASCII)

TBD in Task 2/3/4

## 9. Open Questions / Phase 7+ Follow-ups

TBD in Task 2/3/4

## 10. References

TBD in Task 2/3/4
