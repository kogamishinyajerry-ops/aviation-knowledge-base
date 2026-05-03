"""Build RAG index: chunk docs/*/processed.md, embed via Ollama, store in SQLite.

Usage: python -m scripts.rag.index
Output: scripts/rag/store.db (SQLite, one row per chunk)
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import struct
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DOCS = ROOT / "docs"
DB_PATH = Path(__file__).resolve().parent / "store.db"
OLLAMA_URL = "http://localhost:11434/api/embed"
OLLAMA_TAGS = "http://localhost:11434/api/tags"


def _detect_embed_model() -> str:
    """Per RAG_PIPELINE.md §3, bge-m3 is the spec default; fall back to nomic-embed-text
    if bge-m3 isn't pulled yet so the demo can run."""
    try:
        with urllib.request.urlopen(OLLAMA_TAGS, timeout=5) as r:
            tags = json.loads(r.read())
        names = {m["name"].split(":")[0] for m in tags.get("models", [])}
        if "bge-m3" in names:
            return "bge-m3"
        if "nomic-embed-text" in names:
            print("  ! bge-m3 not pulled — falling back to nomic-embed-text (lower-quality demo)")
            return "nomic-embed-text"
    except Exception:
        pass
    return "bge-m3"  # let HTTP error surface if neither present


EMBED_MODEL = _detect_embed_model()

# Per RAG_PIPELINE.md §2.3
CHUNK_SIZE = 512    # tokens, approximated as words for demo
CHUNK_OVERLAP = 64
ATOMIC_MAX = 2048

# Per RAG_PIPELINE.md §2.4 — regulation clause regex DRIVES boundary
CLAUSE_RE = re.compile(r"§\s*\d+\.\d+(\([a-z]\))?(\(\d+\))?")
# Atomic-table heuristic: lines starting/ending with `|`
TABLE_LINE = re.compile(r"^\s*\|.*\|\s*$")


def chunk_id(text: str, index: int) -> str:
    """Per RAG_PIPELINE.md §5.1: c_<first-8-hex-chars-of-sha256(text + '\\n' + index)>."""
    h = hashlib.sha256((text + "\n" + str(index)).encode("utf-8")).hexdigest()
    return "c_" + h[:8]


def approx_tokens(text: str) -> int:
    """Word count + 30% inflation factor — rough proxy for BGE-M3 tokens."""
    return int(len(text.split()) * 1.3) + len(re.findall(r"[一-鿿]", text))


def split_into_blocks(md: str) -> list[tuple[str, str]]:
    """Split processed.md into typed blocks: ('table'|'clause'|'prose', text).

    Atomic blocks (table, clause-anchored regulation paragraph) are kept whole.
    Prose blocks may be subsequently split by chunk_size.
    """
    lines = md.split("\n")
    blocks: list[tuple[str, str]] = []
    buf: list[str] = []
    in_table = False

    def flush(kind: str):
        nonlocal buf
        if buf:
            text = "\n".join(buf).strip()
            if text:
                blocks.append((kind, text))
            buf = []

    for line in lines:
        if TABLE_LINE.match(line):
            if not in_table:
                flush("prose")
                in_table = True
            buf.append(line)
        else:
            if in_table:
                flush("table")
                in_table = False
            buf.append(line)
    flush("table" if in_table else "prose")

    # Within prose blocks, split on regulation-clause boundaries (each clause = own chunk)
    out: list[tuple[str, str]] = []
    for kind, text in blocks:
        if kind == "table":
            out.append((kind, text))
            continue
        # Find clause anchors and split prose at those points
        anchors = [m.start() for m in CLAUSE_RE.finditer(text)]
        if len(anchors) <= 1:
            out.append((kind, text))
            continue
        prev = 0
        for i, pos in enumerate(anchors):
            if i == 0 and pos > 0:
                out.append(("prose", text[:pos].strip()))
            if i + 1 < len(anchors):
                out.append(("clause", text[pos:anchors[i + 1]].strip()))
            else:
                out.append(("clause", text[pos:].strip()))
            prev = pos
    return [(k, t) for k, t in out if t]


def split_prose_by_size(text: str) -> list[str]:
    """Sliding window split for oversize prose blocks. Tokens ~ words."""
    words = text.split()
    if approx_tokens(text) <= CHUNK_SIZE:
        return [text]
    chunks = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    i = 0
    while i < len(words):
        window = words[i : i + CHUNK_SIZE]
        chunks.append(" ".join(window))
        i += step
    return chunks


def embed(text: str) -> list[float]:
    """Call Ollama /api/embed for bge-m3."""
    payload = json.dumps({"model": EMBED_MODEL, "input": text[:8000]}).encode("utf-8")
    req = urllib.request.Request(
        OLLAMA_URL, data=payload, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read())
    # /api/embed returns {"embeddings": [[...]]} for batch; we send single input
    embs = result.get("embeddings") or [result.get("embedding")]
    return embs[0]


def vec_to_blob(v: list[float]) -> bytes:
    return struct.pack(f"{len(v)}f", *v)


def init_db(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS chunks (
        chunk_id     TEXT PRIMARY KEY,
        document_id  TEXT NOT NULL,
        document_uri TEXT NOT NULL,
        chunk_index  INTEGER NOT NULL,
        kind         TEXT NOT NULL,
        section      TEXT,
        text         TEXT NOT NULL,
        embedding    BLOB NOT NULL,
        token_count  INTEGER NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_doc ON chunks(document_id);
    """)


def extract_section(text: str) -> str:
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("##"):
            return line.lstrip("#").strip()[:80]
    m = CLAUSE_RE.search(text)
    if m:
        return m.group(0)
    return ""


def build():
    DB_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    total = 0
    for processed in sorted(DOCS.rglob("processed.md")):
        doc_id = processed.parent.name
        document_uri = f"aviationkb://document/{doc_id}@1"
        md = processed.read_text()
        blocks = split_into_blocks(md)
        # Final chunk list: split oversize prose, atomic-keep tables/clauses
        chunks: list[tuple[str, str]] = []
        for kind, text in blocks:
            if kind == "prose":
                for sub in split_prose_by_size(text):
                    chunks.append(("prose", sub))
            else:
                chunks.append((kind, text))

        print(f"  → {doc_id}: {len(chunks)} chunks")
        for idx, (kind, text) in enumerate(chunks):
            cid = chunk_id(text, idx)
            section = extract_section(text)
            tokens = approx_tokens(text)
            try:
                vec = embed(text)
            except Exception as e:
                print(f"    ! embed failed for chunk {idx}: {e}")
                continue
            conn.execute(
                "INSERT OR REPLACE INTO chunks VALUES (?,?,?,?,?,?,?,?,?)",
                (cid, doc_id, document_uri, idx, kind, section, text,
                 vec_to_blob(vec), tokens),
            )
            total += 1
        conn.commit()

    print(f"✓ Indexed {total} chunks across {len(list(DOCS.rglob('processed.md')))} documents")
    print(f"  DB: {DB_PATH}")
    conn.close()


if __name__ == "__main__":
    sys.exit(build() or 0)
