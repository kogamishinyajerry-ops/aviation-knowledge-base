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

This section defends **Pitfall 8** (citation hallucination — LLM invents page numbers) by making the LLM **structurally incapable** of authoring its own citations. The mechanism is a three-step inject → resolve → validate flow that traps any unresolved citation token before the answer reaches the user.

This is the **Core Value** defender (per `.planning/PROJECT.md`: "**每一个 AI 回答都有 citation**；如果其他都失败，这一条不能失守"). If §5 fails, the entire system fails.

### 5.1 Token format `[CITE:c_<8hex>]`

**Locked rules — verbatim, do not relax:**

```text
Token format:        [CITE:c_<8hex>]
chunk_id derivation: c_<first-8-hex-chars-of-sha256(chunk_text + "\n" + chunk_index)>
Example:             [CITE:c_a3f1e29b]   # opaque to LLM; cannot be guessed
Match regex:         \[CITE:(c_[0-9a-f]{8})\]
```

**Why 8 hex chars (not 16, not 4):**

- 4 hex (~16 bits): collision probability ~1.5% at 1000 chunks — too high.
- 16 hex (~64 bits): astronomical collision safety but tokens become eye-strain in the LLM context window and the post-validator runs slower.
- **8 hex (~32 bits): collision probability ~0.001% at 1000 chunks, ~0.1% at 10000 chunks** — safe for v1 corpus (target ≤500 documents per ROADMAP) and easy to read in answers. Phase 7 may bump to 12 hex if corpus crosses 100k chunks; ADR required.

**Why include `chunk_index` in the SHA256 input:** identical text content can appear in two different chunks (e.g., the boilerplate "Cross-references" footer of FAR clauses). Hashing `chunk_text + chunk_index` gives each occurrence a distinct `chunk_id`, so the citation resolver can return the correct (document, page, section) tuple even when content is duplicated.

**The LLM is FORBIDDEN to author its own citations.** The system prompt MUST contain (verbatim — do not paraphrase, do not add "creative" variations):

```text
You may cite ONLY the chunks provided to you in this turn. To cite, emit
the exact token [CITE:c_xxxxxxxx] where xxxxxxxx is the chunk_id of the
chunk you are referencing. NEVER invent page numbers, document names, or
chunk_ids. The system will reject any answer containing a chunk_id that
was not in your retrieved context.
```

This prompt is enforced as a **system message header** prepended by the orchestration layer (`scripts/rag/orchestrator.py`, Phase 7). It is NOT user-facing and is NOT subject to user override (no `--system-prompt` CLI flag in v1).

### 5.2 Render-layer resolution pseudocode

The render layer runs AFTER the LLM has produced its answer with `[CITE:c_*]` tokens, but BEFORE the answer is shown to the user. It replaces tokens with human-readable, clickable citation links. Unresolved tokens are flagged for the validator (§5.3) to catch.

```python
import re
from dataclasses import dataclass

CITE_RE = re.compile(r"\[CITE:(c_[0-9a-f]{8})\]")


@dataclass(frozen=True)
class Chunk:
    chunk_id: str               # e.g. "c_a3f1e29b"
    document_uri: str           # e.g. "aviationkb://document/far-25-1309@1"
    page: int                   # 1-indexed page number from OpenDataLoader output
    section_anchor: str | None  # e.g. "§25.1309(b)(1)" or None
    url: str                    # resolves to retrieval.url in canonical-example.yaml
    score: float                # post-rerank score (§4.3); used by §6 guardrail


def render_citations(answer_text: str, retrieved_chunks: list[Chunk]) -> str:
    """
    retrieved_chunks: each has .chunk_id, .document_uri, .page, .section_anchor, .url
    Returns: answer_text with [CITE:c_xxxxxxxx] replaced by markdown footnote-style links.

    Unresolved tokens are rendered as a visible warning marker so the post-validator
    in §5.3 can detect them; in normal operation §5.3 runs FIRST and rejects the answer
    before this function is called, so the warning marker is a defense-in-depth safety net.
    """
    chunk_index = {c.chunk_id: c for c in retrieved_chunks}

    def replace(match: re.Match) -> str:
        cid = match.group(1)
        c = chunk_index.get(cid)
        if c is None:
            # Defense in depth — §5.3 should have already rejected this answer.
            return f"[⚠️ unresolved:{cid}]"
        # Resolve to (document, page, section, url) tuple.
        doc_label = c.document_uri.split("/")[-1]   # e.g. "far-25-1309@1"
        anchor = c.section_anchor or f"p.{c.page}"
        return f"[{doc_label} {anchor}]({c.url})"

    return CITE_RE.sub(replace, answer_text)
```

**Why `document_uri` not raw filename:** `aviationkb://document/<doc-id>@<v>` is the canonical record-style URI per `instances/entities/expert-note/canonical-example.yaml` and ARCHITECTURE.md Pattern 3 ("Stable URI-Style IDs (KG-Ready)"). It survives file moves, supports versioning (`@1`, `@2`), and maps directly to the future graph-DB node ID without rework.

### 5.3 Post-generation validator pseudocode

The validator runs IMMEDIATELY after the LLM produces an answer and BEFORE the answer is rendered or shown. **REJECT (not warn) on unresolved citations.** A rejected answer is replaced with the canned no-context response (§6.2) — the user never sees the LLM's hallucinated page numbers.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    rejected_reason: str | None


def validate_answer_citations(
    answer_text: str,
    retrieved_chunks: list[Chunk],
) -> ValidationResult:
    """
    Returns ValidationResult(ok: bool, rejected_reason: str | None).
    Called BEFORE the answer reaches the user. If ok=False, the user sees
    a fixed error message (§6.2 canned response) instead of the answer.

    This is the structural defense against Pitfall 8 (citation hallucination):
    the LLM only ever sees opaque chunk_ids and cannot guess valid ones; if it
    invents a token, this validator catches it.
    """
    chunk_ids_in_context = {c.chunk_id for c in retrieved_chunks}
    cited_ids = set(CITE_RE.findall(answer_text))

    # Rule 1: every token must resolve to a retrieved chunk.
    unresolved = cited_ids - chunk_ids_in_context
    if unresolved:
        return ValidationResult(
            ok=False,
            rejected_reason=f"Citations not in retrieved context: {sorted(unresolved)}",
        )

    # Rule 2: if context was provided, the answer must cite at least one chunk.
    # An uncited answer with retrieved context means the LLM ignored its sources
    # and is generating from parametric knowledge — a Core Value violation.
    if not cited_ids and len(retrieved_chunks) > 0:
        return ValidationResult(
            ok=False,
            rejected_reason="Answer has no citation tokens despite retrieved context",
        )

    return ValidationResult(ok=True, rejected_reason=None)
```

**Cross-reference: this defuses Pitfall 8 by design.** Per PITFALLS.md Pitfall 8 ("Citation 注入幻觉（页码捏造）"): the LLM "**编造页码**" failure is structurally impossible because (1) the LLM never sees real page numbers in the prompt — only `chunk_id` tokens — so it cannot remember and recite them; (2) any token it invents fails SHA256-based validation; (3) the rejection happens before render. This three-step (inject → resolve → validate) mechanism makes Pitfall 8 (Citation Hallucination) structurally impossible — the LLM only ever sees opaque chunk_ids and cannot invent valid ones.

**What "rejected" looks like to the user:** the canned no-context response from §6.2, not a stack trace or error code. The system logs the rejection (orchestrator log, NOT user-facing) with the rejected_reason for ops investigation.

## 6. Guardrail (No-Context Short-Circuit)

This section defends **Pitfall 9** (guardrail bypass on retrieval failure). The guardrail is a **hard pipeline branch**, NOT a prompt instruction — the LLM cannot be "jailbroken" past it because it is never called when the guardrail trips. Per PITFALLS.md Pitfall 9: "guardrail 是 hard constraint：模型不论怎么 prompt，只要 retrieved_context 为空，pipeline 直接短路返回上述文案，不调 LLM".

### 6.1 Threshold values (min_chunk_score, min_chunks_required)

| Parameter             | Value | Rationale                                                                                            |
|-----------------------|-------|------------------------------------------------------------------------------------------------------|
| `min_chunk_score`     | **0.5** | Post-rerank score floor (bge-reranker-v2-m3 calibrated 0..1). Below → treat as no context.        |
| `min_chunks_required` | **2**   | Single-hit retrieval is too brittle (one weak match can confabulate); require corroboration.       |

**Why 0.5 specifically:** bge-reranker-v2-m3 outputs are roughly calibrated such that 0.5 corresponds to "the chunk is likely on-topic but not necessarily a direct answer". Below 0.5 is "weakly related at best" — the AeroPower-RAG-style false-positive zone. Phase 7 may surface this as an ops-tunable knob, but the v1 default is 0.5.

**Why 2 chunks required:** in aviation Q&A, single-source claims are forensically fragile — one chunk that happens to mention "catastrophic" without context can mislead the LLM. Requiring two independent passing chunks makes single-point retrieval failure trip the guardrail rather than produce a one-sided answer.

**Threshold check site:** these values are checked AFTER reranking (§4.3), AGAINST the post-rerank score. Pre-rerank vector / BM25 scores are NOT compared against 0.5 — different scale.

### 6.2 Canned no-context response (ZH + EN)

When the guardrail trips, the system returns this **verbatim** text. Both ZH and EN are required (per §1 scope: bilingual users per `.planning/design/PRD_v0.md` user archetype A "航空工程师" + B "CFD/适航研究人员"):

```text
未在知识库中找到相关内容。可能原因：
(1) 您的问题不在当前知识库覆盖范围；
(2) 关键词不匹配，请尝试换种问法。
本系统不在无来源时生成答案。

Not found in knowledge base. Possible reasons:
(1) Your question is outside the current knowledge base scope;
(2) Keywords did not match — please try rephrasing.
This system does not generate answers without sources.
```

**Format constraints:**

- Both languages always returned together (no language detection branch — bilingual users see both, monolingual users see their language plus a polite extra).
- No personalization, no LLM-generated variant — verbatim string lookup from a constant in `scripts/rag/orchestrator.py` (Phase 7).
- **No "would you like me to try anyway?" follow-up.** Per Core Value: "本系统不在无来源时生成答案" — there is no fallback to parametric knowledge.

**i18n note:** EN translation is included in v1 because the user base per `.planning/design/PRD_v0.md` is bilingual ZH/EN; not because of jurisdictional law. Phase 7 may add `accept-language`-based ordering but neither variant is removable.

### 6.3 LLM-not-called proof (where the short-circuit lives in the pipeline)

The guardrail is implemented as a hard branch in the orchestration function. The LLM is **physically not invoked** when the guardrail trips; this is provable from the code structure (the `llm.generate(...)` call is unreachable on the no-context branch).

```python
from dataclasses import dataclass

MIN_CHUNK_SCORE = 0.5         # §6.1
MIN_CHUNKS_REQUIRED = 2       # §6.1
NO_CONTEXT_RESPONSE = (
    "未在知识库中找到相关内容。可能原因：\n"
    "(1) 您的问题不在当前知识库覆盖范围；\n"
    "(2) 关键词不匹配，请尝试换种问法。\n"
    "本系统不在无来源时生成答案。\n"
    "\n"
    "Not found in knowledge base. Possible reasons:\n"
    "(1) Your question is outside the current knowledge base scope;\n"
    "(2) Keywords did not match — please try rephrasing.\n"
    "This system does not generate answers without sources.\n"
)


@dataclass(frozen=True)
class Answer:
    text: str
    llm_called: bool         # AUDIT FIELD: provable absence of LLM call
    citations: list[Chunk]


def answer_query(query: str) -> Answer:
    chunks = hybrid_retrieve(query)              # §4.1 + §4.2 (vector + BM25 + RRF + synonym)
    chunks = rerank(chunks)                      # §4.3 (bge-reranker-v2-m3, score_threshold=0.5)

    # ── GUARDRAIL — short-circuit BEFORE any LLM call ─────────────────────────
    # Per Pitfall 9 (PITFALLS.md): the no-context path MUST NOT reach llm.generate().
    if not chunks or all(c.score < MIN_CHUNK_SCORE for c in chunks):
        return Answer(text=NO_CONTEXT_RESPONSE, llm_called=False, citations=[])

    passing_chunks = [c for c in chunks if c.score >= MIN_CHUNK_SCORE]
    if len(passing_chunks) < MIN_CHUNKS_REQUIRED:
        return Answer(text=NO_CONTEXT_RESPONSE, llm_called=False, citations=[])
    # ──────────────────────────────────────────────────────────────────────────

    # Only here do we invoke the LLM.
    answer_raw = llm.generate(prompt_with_chunks(query, passing_chunks))

    # §5.3 post-generation validator — citation integrity check.
    validation = validate_answer_citations(answer_raw, passing_chunks)
    if not validation.ok:
        # LLM was called but its answer failed citation validation. Treat like
        # guardrail trip: return canned response, do NOT show the unsafe answer.
        # llm_called=True records that LLM was consulted (cost tracking) but the
        # output was rejected.
        return Answer(text=NO_CONTEXT_RESPONSE, llm_called=True, citations=[])

    return Answer(
        text=render_citations(answer_raw, passing_chunks),
        llm_called=True,
        citations=passing_chunks,
    )
```

**Why `llm_called` is on the return type:** ops needs to distinguish three states for cost / debugging:

1. `llm_called=False, citations=[]` → guardrail tripped before LLM (the cheap path; ~200ms; no LLM cost)
2. `llm_called=True, citations=[]` → LLM was called but its output failed §5.3 validation (cost incurred but answer rejected — this is the "LLM tried to hallucinate" signal that should be alarmed in ops dashboards)
3. `llm_called=True, citations=[…]` → normal successful answer with verified citations

**Cross-reference Pitfall 9 explicitly.** Per PITFALLS.md Pitfall 9 ("Guardrail 在检索失败时被绕过"): the failure mode is "LLM 在没有 retrieved context 时仍然生成答案（用自己的世界知识）". The guardrail is a hard pipeline branch, NOT a prompt instruction — the LLM cannot be 'jailbroken' past it because it is never called when the guardrail trips. The `llm_called=False` audit field plus the structural impossibility of reaching `llm.generate(...)` on the no-context branch make this provable in code review (Phase 7 will add a unit test that mocks `llm.generate` to raise on call and asserts no call happens for empty retrieval).

**Test coverage requirement (Phase 7):** `evaluation/queries.yaml` must contain ≥3 `out_of_scope` queries (per plan 05-02). Phase 7 acceptance includes: 100% of out_of_scope queries return `llm_called=False` and the canned response. Any pipeline change that breaks this assertion fails the eval gate.

## 7. Cross-lingual Retrieval

This section defends **Pitfall 7** (embedding model does not recognize ZH↔EN aviation terms). The defense is three-layered: (1) a multilingual embedding model that already understands ZH+EN in the same space; (2) a bilingual glossary that expands queries with synonyms in both languages; (3) entity i18n metadata indexed at write time so structured records carry their bilingual labels into search.

### 7.1 BGE-M3 native multilingual coverage

BGE-M3 is multilingual by design (100+ languages including ZH+EN — per STACK.md "Embedding & LLM Layer" row "multilingual" attribute, and the BGE-M3 model card linked in §10). Per AeroPower-RAG findings (user's prior project, MEMORY.md), recall@3 reached **100%** on Chinese aviation regulations using a closely related multilingual stack (Ollama nomic-embed-text 768d + BM25 bigram + synonym weight 0.3 + RRF fusion). BGE-M3 is the same architectural family with broader multilingual coverage and dense+sparse-in-one — same pattern applies.

**Concrete eval target for Phase 7:** `cross_lingual_recall@5 ≥ 70%` on `evaluation/queries.yaml` (≥6 of the ≥30 queries are intentionally ZH↔EN — see plan 05-02). This is the threshold gate from §3.3 Decision Criteria #2 — no embedding model ships below 70% cross-lingual recall.

**No translation layer required.** Crucially, BGE-M3 places "涡轮叶片" and "turbine blade" in the same vector neighborhood without an intermediate translation step. This means the v1 retrieval pipeline does NOT need a query translator (LLM call) before vector search — saves latency, eliminates a hallucination surface (translator could mis-translate "适航" as "airworthiness" vs "navigability").

### 7.2 Glossary expansion (≥50 seed terms target — bilingual)

Even with BGE-M3's multilingual coverage, **explicit glossary expansion** adds robustness for domain-specific terms where embedding alone might miss colloquial / acronym variants. Per Pitfall 7 (PITFALLS.md): "维护 `data/glossary/aviation_terms.yaml`... 检索前做 query expansion：term → synonyms (weight 0.3，承袭 AeroPower-RAG 配置)".

**Glossary file format** (Phase 6 deliverable per AIH-04, target ≥50 seed bilingual terms; matches PITFALLS.md Pitfall 7 example block):

```yaml
# docs/GLOSSARY.md (Phase 6 deliverable, AIH-04 — ≥50 seed bilingual terms)
# Format (matches PITFALLS.md Pitfall 7 example):
- canonical: turbine_blade
  zh: ["涡轮叶片", "涡轮工作叶片", "动叶"]
  en: ["turbine blade", "rotor blade"]
  ata_code: "72-30"
  notes: "区分 stator vane vs rotor blade"

- canonical: catastrophic_failure
  zh: ["灾难性失效", "灾难性故障"]
  en: ["catastrophic failure", "catastrophic condition"]
  far_clause: "25.1309(b)(1)"
```

**Query-time expansion mechanics** (verbatim from §4.2 — repeated here for §7 self-containment):

- query "涡轮叶片失效" → glossary lookup returns zh+en synonyms
- query becomes vector: `[original_query] + 0.3 × [synonym_terms]`
- retrieval still hybrid (vector + BM25); BM25 also benefits from term expansion (bigram-tokenized synonyms OR'd into BM25 query)

**Why weight 0.3 (not 0.5, not 1.0):** PITFALLS.md and AeroPower-RAG-validated. Higher weights overpower the original query intent; lower weights make synonyms invisible. Locked per AI 接力指南 Locked-vs-Directional table.

**Glossary maintenance:** new terms added via PR to `docs/GLOSSARY.md` (Phase 6+). CI validates schema (canonical / zh / en non-empty). No runtime modification in v1.

### 7.3 Entity i18n field at index time

Every canonical entity record carries `i18n.label.zh` and `i18n.label.en` fields per `instances/entities/expert-note/canonical-example.yaml`:

```yaml
i18n:
  label:
    zh: "FAR 25.1309 系统失效条件等级判定 — 范例笔记"
    en: "FAR 25.1309 system failure-condition severity assessment — canonical example"
```

**Indexing rule (enforced in `scripts/exporters/to_ragflow.py`, plan 05-03 skeleton):** at index time, when processing an entity record, the exporter MUST upload **BOTH** `i18n.label.zh` and `i18n.label.en` as separate searchable metadata fields per Document/Entity. This means a query for "FAR 25.1309" or "适航条款 25.1309" both hit the same entity record's metadata, and that hit can be surfaced via citation back-link even though the entity record itself is not vector-indexed (per §1 out-of-scope: "v1 only indexes wiki/**.md + docs/**/processed.md").

**Phase 7 implementation hint:** the RAGFlow document object's `meta_fields` carries:

```python
meta_fields = {
    "label_zh": entity["i18n"]["label"]["zh"],
    "label_en": entity["i18n"]["label"]["en"],
    "entity_uri": entity["id"],            # e.g. aviationkb://expert-note/canonical-example@1
    "ata_chapter": entity.get("ata_chapter"),  # if present
    # ...other ontology metadata
}
```

These fields are searchable via RAGFlow's native metadata-filter API at retrieval time and carry through to citations rendered in §5.2.

## 8. Pipeline Diagram (ASCII)

End-to-end query → answer flow tying §2 (chunking, ingest-time only — shown in dashed box) to §4 (retrieval) → §5 (citation) → §6 (guardrail) → §7 (cross-lingual). Numbered stages 1-6 are query-time.

```text
                         INGEST-TIME (out of band, §2)
                  ┌─────────────────────────────────────┐
                  │ docs/<corpus>/<doc-id>/source.pdf   │
                  │   ↓ (RAGFlow OpenDataLoader-PDF)    │
                  │ docs/<corpus>/<doc-id>/processed.md │
                  │   ↓ (chunker, atomic-rule pass)     │
                  │ chunks → BGE-M3 embed → vector idx  │
                  │ chunks → BM25 idx (with bigram, ZH) │
                  └─────────────────────────────────────┘

                              QUERY-TIME (§§4–7)

                       ┌───────────────────────┐
                       │ User query (ZH or EN) │
                       └──────────┬────────────┘
                                  ▼
                  ┌────────────────────────────────┐
                  │ 1. Query expansion (§7.2)      │
                  │    - Glossary lookup           │
                  │    - Synonym weight 0.3        │
                  │    - Bilingual ZH↔EN           │
                  └──────────┬─────────────────────┘
                             ▼
                  ┌────────────────────────────────┐
                  │ 2. Hybrid retrieval (§4)       │
                  │    ├─ Vector (BGE-M3) k=20     │
                  │    ├─ BM25 (k1=1.2, b=0.75)    │
                  │    │       k=20, bigram=true   │
                  │    └─ RRF fusion (k=60)        │
                  │    → final_top_k = 10          │
                  └──────────┬─────────────────────┘
                             ▼
                  ┌────────────────────────────────┐
                  │ 3. Rerank (§4.3)               │
                  │    bge-reranker-v2-m3          │
                  │    → top_k=5, threshold 0.5    │
                  └──────────┬─────────────────────┘
                             ▼
                       ┌─────┴──────┐
                       │ Guardrail  │ (§6.1)
                       │ score≥0.5? │
                       │ chunks≥2?  │
                       └─┬───────┬──┘
                       NO│       │YES
                         ▼       ▼
                ┌────────────┐ ┌──────────────────────────────┐
                │ Canned     │ │ 4. LLM call                  │
                │ no-ctx     │ │    prompt + chunks           │
                │ response   │ │    + system prompt forbidding│
                │ (§6.2)     │ │      self-authored citations │
                │ ZH + EN    │ │    LLM emits [CITE:c_*] toks │
                │ llm_called │ └──────────┬───────────────────┘
                │   = False  │            ▼
                │ (§6.3)     │ ┌──────────────────────────────┐
                └────┬───────┘ │ 5. Citation validate (§5.3)  │
                     │         │    validate_answer_citations │
                     │         │    unresolved → REJECT       │
                     │         │      → return canned (§6.2)  │
                     │         │      llm_called=True (audit) │
                     │         └──────────┬───────────────────┘
                     │                    ▼
                     │         ┌──────────────────────────────┐
                     │         │ 6. Render (§5.2)             │
                     │         │    render_citations()        │
                     │         │    [CITE:c_a3f1e29b]         │
                     │         │      → [far-25-1309@1        │
                     │         │         §25.1309(b)](url)    │
                     │         └──────────┬───────────────────┘
                     │                    ▼
                     │         ┌──────────────────────────────┐
                     └────────▶│ User sees:                   │
                               │  - canned response, OR       │
                               │  - LLM answer + clickable    │
                               │    citations resolving to    │
                               │    Wiki.js / docs/<doc>/     │
                               └──────────────────────────────┘
```

**Stage-to-section map:**

| Stage | Section(s)        | Component                           |
|-------|-------------------|-------------------------------------|
| 1     | §7.2              | Glossary expansion (synonym 0.3)    |
| 2     | §4.1              | Vector + BM25 + RRF                 |
| 3     | §4.3              | bge-reranker-v2-m3 + threshold 0.5  |
| Guardrail | §6.1, §6.3   | min_chunk_score / min_chunks_required + hard pipeline branch |
| 4     | §5.1              | LLM call with token-injection prompt |
| 5     | §5.3              | Post-generation citation validator  |
| 6     | §5.2              | Render layer (chunk_id → URL)       |

## 9. Open Questions / Phase 7+ Follow-ups

These are explicitly deferred to Phase 7 or later. Each item is a known gap, NOT a hidden assumption — Phase 7 readers should expect to resolve these.

- **LLM choice (Ollama Qwen2.5-14B/32B vs remote Claude/GPT)** — deferred to Phase 6 deployment plan. The decision depends on hardware reality (macOS Apple Silicon RAM headroom, network policy, cost). This doc only specifies the LLM contract (must honor citation token format §5.1, must not self-author citations).
- **Mini-benchmark numbers (recall, MRR, latency)** — not measured in Phase 5. Phase 7 runs the §3.2 protocol against `evaluation/queries.yaml` (plan 05-02) and amends §3.2 + §3.3 with measured values. THIS doc bumps to v0.2.0 at that point.
- **RAGFlow OIDC SSO** — deferred to v2 per STACK.md "Auth / Reverse Proxy" section ("RAGFlow OIDC integration is broken/incomplete in 2026-05, issue #3495 open, #12568 OIDC redirect-loop"). v1 uses local accounts on each service per CLAUDE.md Constraints "single org, admin + reader only".
- **DeepDoc OCR fallback** — deferred to v2 per CLAUDE.md Out-of-Scope ("OCR / 图像理解 — 第一阶段只处理文本文档"). v1 ingestion rejects scanned PDFs with `needs_ocr` flag (§2.1).
- **Entity-record indexing (YAML → embeddable prose)** — Phase 7+. v1 only indexes `wiki/**.md` + `docs/**/processed.md` per ARCHITECTURE.md Pattern 4. YAML records surface via citation back-links + entity-i18n metadata fields (§7.3), NOT vector retrieval.
- **Confidence-aware retrieval (filter by `confidence.score ≥ X`)** — Phase 7. Schema field exists per `instances/entities/expert-note/canonical-example.yaml`; retrieval-time filter not wired in v1.
- **Citation-token cardinality scaling (8 hex → 12 hex)** — Phase 7+ if corpus crosses ~100k chunks. Current 8-hex format is safe up to ~10k chunks (§5.1 collision analysis). ADR required for the bump.
- **Real-time index updates (polling cron vs Git webhook)** — Phase 6 deployment plan picks one. Affects how fast a Wiki.js page edit becomes searchable.
- **Reranker score calibration** — bge-reranker-v2-m3 outputs are roughly calibrated 0..1, but per-corpus calibration (does 0.5 mean the same on regulations vs CFD papers?) is a Phase 7 follow-up. May require per-corpus thresholds.

## 10. References

**Phase 5 source documents (this repo):**

- [.planning/PROJECT.md](../PROJECT.md) — Core Value (citation requirement), R8 RAG-design requirement.
- [.planning/ROADMAP.md](../ROADMAP.md) — Phase 5 success criteria.
- [.planning/REQUIREMENTS.md](../REQUIREMENTS.md) — RAG-01 through RAG-08 IDs covered by this doc.
- [.planning/research/STACK.md](../research/STACK.md) — RAGFlow v0.25.1, BGE-M3, OpenDataLoader-PDF version pins (verbatim cited throughout §2-§4).
- [.planning/research/ARCHITECTURE.md](../research/ARCHITECTURE.md) — Pattern 4 Git-Bridge Sync; Integration Boundaries Git→RAGFlow; entity URI scheme.
- [.planning/research/PITFALLS.md](../research/PITFALLS.md) — Pitfalls 6 (chunking), 7 (cross-lingual), 8 (citation hallucination), 9 (guardrail bypass).
- [.planning/design/PRD_v0.md](./PRD_v0.md) — bilingual user archetypes (drives §6.2 ZH+EN canned response).
- [docs/regulations/far-25-1309/processed.md](../../docs/regulations/far-25-1309/processed.md) — concrete §-clause structure example for §2.2 regex.
- [docs/cfd-papers/nasa-tm-2014-218175/processed.md](../../docs/cfd-papers/nasa-tm-2014-218175/processed.md) — equation block + figure-caption layout for §2.2.
- [docs/accident-reports/ntsb-aar-09-03/processed.md](../../docs/accident-reports/ntsb-aar-09-03/processed.md) — factor-table structure for §2.2.
- [instances/entities/expert-note/canonical-example.yaml](../../instances/entities/expert-note/canonical-example.yaml) — i18n field (§7.3) + URI scheme (§5.2 `aviationkb://document/...@v`).
- [scripts/validators/README.md](../../scripts/validators/README.md) — AI 接力开发指南 style precedent for the top-of-doc orientation block.

**External references (verified in STACK.md):**

- [RAGFlow HTTP API reference](https://ragflow.io/docs/http_api_reference) — ingestion + metadata API used by `scripts/exporters/to_ragflow.py` (plan 05-03).
- [RAGFlow Select PDF parser docs](https://ragflow.io/docs/select_pdf_parser) — DeepDoc / MinerU / OpenDataLoader / Docling backend selection.
- [BGE-M3 model card](https://huggingface.co/BAAI/bge-m3) — 568M params, 8192 ctx, dense+sparse+colbert-in-one, multilingual.
- [BGE-M3 on Ollama](https://ollama.com/library/bge-m3) — `ollama pull bge-m3` for local self-hosted path (~2GB on disk).
- [bge-reranker-v2-m3 model card](https://huggingface.co/BAAI/bge-reranker-v2-m3) — companion reranker, ZH/EN, RAGFlow built-in support.
- [OpenDataLoader PDF review (Emelia 2026)](https://emelia.io/hub/opendataloader-pdf-review) — 72min vs 16.5h vs 6day comparison on 10K pages (the "~14× faster" claim source).
- [PDF parser benchmark — Procycons 2025](https://procycons.com/en/blogs/pdf-data-extraction-benchmark/) — supplementary parser-quality data.

**User's prior projects (HIGH confidence — first-hand):**

- AeroPower-RAG (per CLAUDE.md MEMORY.md) — hybrid retrieval (BM25 + vector + RRF), recall@3=100% on ZH aviation regulations, synonym weight 0.3, BM25 bigram. The validated pattern this doc inherits.
- cfd-harness-unified — Notion/Git dual-truth + audit-trail discipline. Background context for Core Value commitment.
- cfd-ai-workbench Case 3 (H-Darrieus) — "捏造图表" failure mode. Direct motivation for §5 citation injection mechanism (Pitfall 8 defense).

## 11. REQ-Coverage Matrix

This matrix is the forward-traceability index for Phase 5. For each requirement,
the table shows the section in this document (or sibling artifact) that delivers
the design AND a shell command the Phase-5 verifier can run to confirm presence.
The reverse-traceability matrix (artifact → REQ-IDs) lives in
`.planning/phases/05-rag-pipeline-design-document-only-no-run/05-COVERAGE.md`.

| REQ-ID  | Delivered by                                                          | Section / File                                  | Verifier command                                                                                                                                              |
|---------|-----------------------------------------------------------------------|-------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| RAG-01  | Chunking strategy with table-atomic + §-clause-atomic rules           | RAG_PIPELINE.md §2                              | `grep -q "OpenDataLoader-PDF" .planning/design/RAG_PIPELINE.md && grep -q "atomic" .planning/design/RAG_PIPELINE.md`                                          |
| RAG-02  | BGE-M3 default + bge-reranker-v2-m3 + mini-benchmark plan             | RAG_PIPELINE.md §3                              | `grep -q "BGE-M3" .planning/design/RAG_PIPELINE.md && grep -q "bge-reranker-v2-m3" .planning/design/RAG_PIPELINE.md && grep -qE "nomic-embed-text\|multilingual-e5-large" .planning/design/RAG_PIPELINE.md` |
| RAG-03  | Hybrid retrieval vector + BM25 + RRF + query expansion w=0.3          | RAG_PIPELINE.md §4                              | `grep -qE "RRF\|rrf" .planning/design/RAG_PIPELINE.md && grep -q "weight: 0.3" .planning/design/RAG_PIPELINE.md`                                              |
| RAG-04  | Citation injection (token + render + validator)                       | RAG_PIPELINE.md §5                              | `grep -q "\[CITE:c_" .planning/design/RAG_PIPELINE.md && grep -q "validate_answer_citations" .planning/design/RAG_PIPELINE.md`                                |
| RAG-05  | Guardrail short-circuit (no-LLM-call when below threshold)            | RAG_PIPELINE.md §6                              | `grep -q "min_chunk_score" .planning/design/RAG_PIPELINE.md && grep -q "llm_called=False" .planning/design/RAG_PIPELINE.md`                                   |
| RAG-06  | Cross-lingual: BGE-M3 multilingual + glossary expansion + i18n        | RAG_PIPELINE.md §7                              | `grep -q "i18n" .planning/design/RAG_PIPELINE.md && grep -qE "glossary\|GLOSSARY" .planning/design/RAG_PIPELINE.md`                                           |
| RAG-07  | Eval set with ≥30 queries, ≥20% table, ≥3 out-of-scope                | evaluation/queries.yaml + evaluation/README.md  | `python -c "import yaml; q=yaml.safe_load(open('evaluation/queries.yaml'))['queries']; assert len(q)>=30 and sum(1 for x in q if x['type']=='table')>=6 and sum(1 for x in q if x['type']=='out_of_scope')>=3"` |
| RAG-08  | to_ragflow.py skeleton: argparse + Git-watch + idempotency + --rebuild | scripts/exporters/to_ragflow.py                 | `python scripts/exporters/to_ragflow.py --help > /dev/null && grep -q "compute_doc_id" scripts/exporters/to_ragflow.py && grep -q "rebuild_index" scripts/exporters/to_ragflow.py` |

### ROADMAP success-criterion mapping

These are the Phase-5 success criteria copied verbatim from
`.planning/ROADMAP.md` "Phase 5: RAG Pipeline Design" → "Success Criteria" 1-6,
mapped to the REQ-IDs that deliver each one.

| ROADMAP SC# | Description (verbatim from ROADMAP.md Phase 5)                                                       | REQ-ID(s)         |
|-------------|------------------------------------------------------------------------------------------------------|-------------------|
| SC-1        | RAG_PIPELINE.md documents chunking with table preservation, citing RAGFlow 0.25.1                    | RAG-01            |
| SC-2        | Embedding rationale + mini-benchmark plan + cross-lingual                                            | RAG-02 + RAG-06   |
| SC-3        | Citation injection: system-side token, render layer resolves, post-validator rejects unresolved      | RAG-04            |
| SC-4        | Guardrail hard-codes empty/below-threshold → "not found" without LLM                                 | RAG-05            |
| SC-5        | evaluation/queries.yaml ≥30, ≥20% table, out-of-scope                                                | RAG-07            |
| SC-6        | to_ragflow.py skeleton: Git-watch, content-hash idempotency, --rebuild                              | RAG-08            |

The Phase-5 verifier (`/gsd-execute-phase` next step) executes each Verifier
command above and asserts exit code 0; any failing row blocks Phase 5 closure.

