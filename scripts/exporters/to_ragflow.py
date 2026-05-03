"""
to_ragflow.py — Git → RAGFlow HTTP API exporter (STUB)

Status: STUB — implementation lands in Phase 5 (RAG Pipeline Design).
Architectural role: per .planning/research/ARCHITECTURE.md Pattern 4
("Git-Bridge Sync"), this script is the ONLY path by which knowledge
flows from Git into RAGFlow's vector store. Wiki.js and RAGFlow do
not talk to each other directly — Git is the audit log of every
cross-system message.

Contract (to be implemented in Phase 5):
- Watches/polls the Git repo for changes under `wiki/**.md` and
  `docs/**/processed.md`.
- Pushes new/changed Markdown to RAGFlow via its HTTP API
  (https://ragflow.io/docs/http_api_reference).
- Idempotent: uses content hash as the RAGFlow document_id, so
  re-uploading an unchanged file is a no-op.
- Supports `--rebuild` flag: drops RAGFlow's vector store and re-indexes
  everything from current Git HEAD. RAGFlow's vector store is declared
  rebuildable from Git in ARCHITECTURE.md ("Failure Modes & Recovery").

Inputs:
- env: RAGFLOW_API_BASE, RAGFLOW_API_TOKEN
- args: --rebuild, --dry-run, --since=<git-ref>

Outputs:
- stdout: JSON-Lines log of {file, action, ragflow_doc_id, status}
- exit 0 on success, non-zero on any upload failure

AI handoff note (per R12 / AIH-01): Future implementer should consult
.planning/research/ARCHITECTURE.md "Git Repo → RAGFlow" boundary table
for property-by-property contract. Do NOT index raw YAML from
`instances/` in v1 — short structured records embed poorly; use
narrative content (`wiki/**.md`, `docs/**/processed.md`) only.
"""
from __future__ import annotations


def main() -> int:
    raise NotImplementedError(
        "to_ragflow.py is a Phase-1 stub. Implementation lands in Phase 5 "
        "(RAG Pipeline Design). See module docstring for the contract."
    )


if __name__ == "__main__":
    raise SystemExit(main())
