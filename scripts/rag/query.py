"""Query the RAG index — retrieve, validate, call LLM, inject citations.

Pipeline (per .planning/design/RAG_PIPELINE.md):
  1. Embed query (Ollama bge-m3)
  2. Retrieve top-K via cosine similarity
  3. Guardrail: retrieved=[] OR all-below-threshold → canned no-context response, NO LLM call
  4. Inject [CITE:c_<8hex>] tokens into prompt context (LLM cannot author own)
  5. Call DeepSeek LLM
  6. Validate answer citations (regex match against retrieved chunk_ids; REJECT on unresolved)
  7. Render: replace tokens with (document, section) human-readable

Usage:
  python -m scripts.rag.query "What does FAR §25.1309 require?"

Returns: AnswerResult dataclass (json-serializable).
"""
from __future__ import annotations

import json
import math
import os
import re
import sqlite3
import struct
import sys
import urllib.request
from dataclasses import dataclass, asdict
from pathlib import Path

from scripts.rag.index import (
    DB_PATH, OLLAMA_URL, EMBED_MODEL, embed,
)

# Per RAG_PIPELINE.md §6.1
MIN_CHUNK_SCORE = 0.5         # cosine floor
MIN_CHUNKS_REQUIRED = 2       # below → guardrail trips
TOP_K = 5

CITE_RE = re.compile(r"\[CITE:(c_[0-9a-f]{8})\]")

# Per RAG_PIPELINE.md §6.2 — verbatim canned response
CANNED_NO_CONTEXT = """未在知识库中找到相关内容。可能原因：
(1) 您的问题不在当前知识库覆盖范围；
(2) 关键词不匹配，请尝试换种问法。
本系统不在无来源时生成答案。

Not found in knowledge base. Possible reasons:
(1) Your question is outside the current knowledge base scope;
(2) Keywords did not match — please try rephrasing.
This system does not generate answers without source.""".strip()

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    document_uri: str
    section: str
    text: str
    score: float = 0.0


@dataclass
class AnswerResult:
    query: str
    answer: str
    citations: list[dict]      # [{chunk_id, document_id, section, text_preview}]
    retrieved: list[dict]      # all retrieved chunks (for audit)
    guardrail_tripped: bool
    rejected_reason: str | None
    llm_called: bool


def blob_to_vec(b: bytes) -> list[float]:
    n = len(b) // 4
    return list(struct.unpack(f"{n}f", b))


def cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def retrieve(query_vec: list[float], k: int = TOP_K) -> list[Chunk]:
    """Vector cosine retrieval. Returns top-k by score (no threshold yet)."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Index missing: {DB_PATH}. Run scripts.rag.index first.")
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT chunk_id, document_id, document_uri, section, text, embedding FROM chunks"
    ).fetchall()
    conn.close()
    scored = []
    for cid, did, uri, section, text, emb in rows:
        vec = blob_to_vec(emb)
        score = cosine(query_vec, vec)
        scored.append(Chunk(cid, did, uri, section or "", text, score))
    scored.sort(key=lambda c: c.score, reverse=True)
    return scored[:k]


def apply_guardrail(chunks: list[Chunk]) -> tuple[list[Chunk], bool, str | None]:
    """Per RAG_PIPELINE.md §6.1: enforce min_chunk_score AND min_chunks_required.

    Returns (filtered_chunks, tripped, reason).
    """
    above = [c for c in chunks if c.score >= MIN_CHUNK_SCORE]
    if len(above) == 0:
        return [], True, f"all chunks below min_chunk_score={MIN_CHUNK_SCORE}"
    if len(above) < MIN_CHUNKS_REQUIRED:
        return [], True, f"only {len(above)} chunks above threshold; need ≥{MIN_CHUNKS_REQUIRED}"
    return above, False, None


def build_prompt(query: str, chunks: list[Chunk]) -> str:
    """Build LLM prompt with [CITE:c_xxx] tokens injected per chunk.

    The LLM is INSTRUCTED to use these tokens; if it invents new ones, the
    post-validator rejects the answer (§5.3).
    """
    ctx_blocks = []
    for c in chunks:
        ctx_blocks.append(
            f"[CITE:{c.chunk_id}] (source: {c.document_id}, section: {c.section or '—'})\n{c.text}"
        )
    context = "\n\n---\n\n".join(ctx_blocks)
    return f"""You are an aviation knowledge assistant. Answer the question using ONLY the context below. \
After every factual claim, append the matching [CITE:c_xxxxxxxx] token from the source — \
DO NOT invent citation tokens, DO NOT cite anything not in the context.
If the context does not contain the answer, reply exactly: NOT_IN_CONTEXT.
Reply in the same language as the question.

CONTEXT:
{context}

QUESTION: {query}

ANSWER (with [CITE:c_xxxxxxxx] tokens after each factual claim):"""


def call_llm(prompt: str) -> str:
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY not set")
    payload = json.dumps({
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 800,
    }).encode("utf-8")
    req = urllib.request.Request(
        DEEPSEEK_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    return result["choices"][0]["message"]["content"]


def validate_citations(answer: str, retrieved_ids: set[str]) -> tuple[bool, str | None, list[str]]:
    """Per RAG_PIPELINE.md §5.3: REJECT on unresolved citations.

    Returns (ok, reject_reason, used_chunk_ids).
    """
    matches = CITE_RE.findall(answer)
    used = set(matches)
    unresolved = used - retrieved_ids
    if unresolved:
        return False, f"unresolved citations: {sorted(unresolved)}", []
    if not matches:
        return False, "no citations in answer (LLM produced unsourced claim)", []
    return True, None, list(used)


def ask(query: str) -> AnswerResult:
    qvec = embed(query)
    candidates = retrieve(qvec, k=TOP_K)
    filtered, tripped, reason = apply_guardrail(candidates)

    retrieved_dump = [
        {"chunk_id": c.chunk_id, "document_id": c.document_id,
         "section": c.section, "score": round(c.score, 4),
         "text_preview": c.text[:140] + ("…" if len(c.text) > 140 else "")}
        for c in candidates
    ]

    if tripped:
        return AnswerResult(
            query=query, answer=CANNED_NO_CONTEXT, citations=[],
            retrieved=retrieved_dump, guardrail_tripped=True,
            rejected_reason=f"guardrail: {reason}", llm_called=False,
        )

    prompt = build_prompt(query, filtered)
    raw = call_llm(prompt)

    if raw.strip().startswith("NOT_IN_CONTEXT"):
        return AnswerResult(
            query=query, answer=CANNED_NO_CONTEXT, citations=[],
            retrieved=retrieved_dump, guardrail_tripped=True,
            rejected_reason="LLM said NOT_IN_CONTEXT (LLM-side guardrail)",
            llm_called=True,
        )

    retrieved_ids = {c.chunk_id for c in filtered}
    ok, reject, used = validate_citations(raw, retrieved_ids)
    if not ok:
        return AnswerResult(
            query=query, answer=CANNED_NO_CONTEXT, citations=[],
            retrieved=retrieved_dump, guardrail_tripped=True,
            rejected_reason=f"citation validation failed: {reject}",
            llm_called=True,
        )

    cit_map = {c.chunk_id: c for c in filtered}
    citations_out = []
    for cid in used:
        c = cit_map[cid]
        citations_out.append({
            "chunk_id": cid, "document_id": c.document_id,
            "section": c.section, "score": round(c.score, 4),
            "text_preview": c.text[:140] + ("…" if len(c.text) > 140 else ""),
        })

    return AnswerResult(
        query=query, answer=raw, citations=citations_out,
        retrieved=retrieved_dump, guardrail_tripped=False,
        rejected_reason=None, llm_called=True,
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.rag.query <question>", file=sys.stderr)
        return 2
    q = " ".join(sys.argv[1:])
    result = ask(q)
    print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
