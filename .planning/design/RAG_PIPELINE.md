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

TBD in Task 2/3/4

## 2. Chunking Strategy

TBD in Task 2/3/4

### 2.1 RAGFlow OpenDataLoader-PDF backend

TBD in Task 2/3/4

### 2.2 Atomic-chunk rules (tables, equations, regulation clauses, figure-captions)

TBD in Task 2/3/4

### 2.3 Chunk size and overlap

TBD in Task 2/3/4

### 2.4 Per-corpus chunking config (regulations / cfd-papers / accident-reports)

TBD in Task 2/3/4

## 3. Embedding Selection

TBD in Task 2/3/4

### 3.1 Default: BGE-M3 + bge-reranker-v2-m3

TBD in Task 2/3/4

### 3.2 Mini-benchmark plan (candidates, metrics, baseline eval set)

TBD in Task 2/3/4

### 3.3 Decision criteria

TBD in Task 2/3/4

## 4. Hybrid Retrieval

TBD in Task 2/3/4

### 4.1 Vector + BM25 + RRF fusion

TBD in Task 2/3/4

### 4.2 Query expansion (synonym dict, weight 0.3)

TBD in Task 2/3/4

### 4.3 Reranking

TBD in Task 2/3/4

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
