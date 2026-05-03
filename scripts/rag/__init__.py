"""DIY RAG implementation following .planning/design/RAG_PIPELINE.md.

Phase 7 — turns the design spec into working code:
- chunker: regulation-clause-aware + atomic-table preservation
- embedder: Ollama bge-m3 via HTTP
- retriever: vector cosine + threshold guardrail
- citation: [CITE:c_<8hex>] inject + post-generation validate
- llm: DeepSeek API (deepseek-chat)
- guardrail: hard short-circuit on retrieved=[] OR all-below-threshold

Stack: stdlib only (no numpy / requests / chromadb). For v0.1 corpus
(~50 chunks) pure-Python cosine is fast enough.
"""
