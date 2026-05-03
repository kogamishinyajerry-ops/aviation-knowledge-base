"""
to_ragflow.py — Git → RAGFlow HTTP API exporter (Phase-5 SKELETON)

Status: STUB — implementation lands in Phase 7 (RAG implementation). This file
is a Phase-5 design skeleton: argparse + signatures + contracts; ALL real-work
paths raise NotImplementedError. NO real HTTP call is made; NO RAGFlow SDK is
imported; only stdlib imports are allowed at this layer per Phase-5 boundary.

--- Architectural role (per .planning/research/ARCHITECTURE.md Pattern 4) ---

Pattern 4 ("Git-Bridge Sync") declares Git as the single source of truth (SSOT)
for all knowledge content; RAGFlow's vector store is a *rebuildable derivative*.
This script is the ONLY path by which content flows Git → RAGFlow. Wiki.js and
RAGFlow do not communicate directly — Git is the audit log of every cross-system
message, and this exporter is the bridge that materializes Git state into the
RAGFlow side. If RAGFlow's index is ever lost, corrupted, or needs migration,
`to_ragflow.py --rebuild` reconstructs it deterministically from Git HEAD.

--- Contract (verbatim from ARCHITECTURE.md "Git Repo → RAGFlow" boundary table) ---

| Property      | Value                                                                            |
|---------------|----------------------------------------------------------------------------------|
| Module        | Custom: scripts/exporters/to_ragflow.py                                          |
| Direction     | One-way (Git → RAGFlow)                                                          |
| Trigger       | Polling cron (Phase 5 recommendation) or webhook on Git push                     |
| API           | RAGFlow HTTP API; 0.24.0+ supports batch metadata                                |
| Scope         | wiki/**.md + docs/**/processed.md (NOT raw YAML in instances/ for v1)            |
| Metadata      | Pulled from metadata.yaml sidecar; uploaded as RAGFlow doc meta_fields           |
| Idempotency   | Use file path + content hash as RAGFlow document_id; re-upload only if changed   |

--- Confidentiality gate (DOC-04) ---

Per docs/README.md §3, every Document carries `metadata.yaml.confidentiality`
∈ {public, internal, restricted, itar_ear}. The first two are eligible for
RAGFlow ingestion; the latter two MUST be filtered out BEFORE any HTTP call.

> "restricted and itar_ear documents MUST NEVER leave the local filesystem.
>  The exporter is the enforcement point for that rule — by the time a request
>  reaches RAGFlow, the gate has already been applied."
> — docs/README.md §3 (paraphrased contract)

The gate is implemented by `is_ingest_eligible()`; the contract crosswalk is
DOC-04 ↔ RAG-08 (this plan's REQ).

--- Inputs ---

Environment variables (LOCKED by Phase 5 plan 05-03):
  RAGFLOW_API_BASE   e.g. http://localhost:9380   (no trailing slash)
  RAGFLOW_API_TOKEN  bearer token from RAGFlow admin UI / API key page

CLI arguments (LOCKED by Phase 5 plan 05-03):
  --rebuild         drop RAGFlow dataset and re-upload everything from Git HEAD
  --dry-run         log actions without calling RAGFlow API
  --since GIT_REF   only process files changed since this Git ref (incremental)
  --paths PATH ...  restrict to subset of INGEST_PATHS

--- Outputs ---

stdout: JSON-Lines log; one record per processed file. Schema:
    {"file": "<path>", "action": "<upload|skip|delete>",
     "ragflow_doc_id": "<akb_…>", "status": "<ok|error|gated>",
     "content_hash": "<sha256:…>"}
exit code: 0 on success, non-zero on any upload failure (Phase 7 decides
whether partial failure is fatal — current contract: any error → non-zero).

--- Idempotency rule (LOCKED) ---

    doc_id = DOC_ID_PREFIX + sha256(str(file_path).encode() + b"\\n" + content).hexdigest()[:32]

Same `(file_path, content)` always maps to the same `doc_id`; re-uploading an
unchanged file to RAGFlow is a no-op (RAGFlow returns 409/200 idempotent
based on existing-doc check). When content changes, `doc_id` changes — Phase 7
implementation MUST delete the superseded RAGFlow document on update so the
vector store does not accumulate stale chunks.

The 32-char truncation keeps doc_ids RAGFlow-friendly (some downstream UIs
truncate IDs visually); collision risk at 128 bits is negligible for this
scale (≤10K documents v1, expansion ≤100K).

--- Rebuild semantics ---

`--rebuild` is the recovery hook declared in ARCHITECTURE.md "Failure Modes &
Recovery": if the RAGFlow vector store is lost, corrupted, or needs migration
between embedding models, this command:
  (1) HTTP DELETE the RAGFlow dataset (atomic-on-RAGFlow-side),
  (2) HTTP POST a fresh dataset with the same name + meta_field schema,
  (3) Iterate INGEST_PATHS yielding all eligible files,
  (4) For each file: load_metadata + is_ingest_eligible + compute_doc_id
      + upload_document.

Because Git is SSOT, the rebuild produces a vector store byte-for-byte
equivalent to a freshly-indexed Git HEAD. There is NO state in RAGFlow that
isn't reconstructible from Git — this is the central invariant of Pattern 4.

--- AI handoff (AIH-01 — AI 接力开发指南) ---

Future Claude / Codex / DeepSeek session implementing this file in Phase 7,
read these documents IN ORDER before writing any function body:

  1. .planning/design/RAG_PIPELINE.md (Phase-5 deliverable):
     §2 chunking strategy per doc_type
     §3 embedding model + dimension contract
     §4 hybrid retrieval (dense + sparse + RRF)
     §5 reranker stage
     §6 citation-grounded answer assembly
     §7 guardrail / refusal contract
  2. .planning/research/ARCHITECTURE.md Pattern 4 (Git-Bridge Sync) +
     "Git Repo → RAGFlow" boundary table (verbatim above) +
     "Failure Modes & Recovery" subsection.
  3. docs/README.md §2 (the 11 mandatory metadata fields) + §3
     (confidentiality enum + DOC-04 gate semantics).

Only AFTER reading those three sources may a function body be filled in.
Skipping this sequence has historically produced exporters that index raw
YAML (poor embeddings), leak restricted documents, or duplicate documents on
re-upload — all three are P0 regressions of the Pattern-4 contract.

--- Phase-5 boundary (HARD CONSTRAINT) ---

This file MUST NOT make any real HTTP call. The following imports are
FORBIDDEN at this layer in Phase 5:
    import requests          # FORBIDDEN
    import httpx              # FORBIDDEN
    import urllib.request    # FORBIDDEN (real network I/O)
    import yaml / ruamel     # FORBIDDEN (no metadata loading yet)
    import git / pygit2      # FORBIDDEN (no Git operations yet)

Only stdlib `argparse`, `hashlib`, `pathlib`, `sys`, `typing` are allowed.
Phase 7 may add `httpx` (preferred) or `requests`, plus a YAML library, plus
a Git-shellout helper. The skeleton signature locks the contract; the body
is a hole.

If you find yourself wanting to add a real import here, STOP — that work
belongs to Phase 7 plan 07-XX, not Phase 5 plan 05-03.

--- See also ---

- .planning/design/RAG_PIPELINE.md           — chunking/embedding/retrieval (Phase 5 sibling)
- .planning/research/ARCHITECTURE.md         — Pattern 4 + boundary tables (Phase 0)
- docs/README.md §2 + §3                     — metadata schema + DOC-04 gate
- scripts/exporters/to_jsonl_triples.py      — sibling stub pattern (Phase 1/2)
- scripts/exporters/to_rdf.py                — sibling stub for v0.3.0+ semantic-web export
- scripts/exporters/to_neo4j.py              — sibling stub for v0.2.0+ GraphRAG loader
"""
from __future__ import annotations

import argparse
import hashlib  # noqa: F401  — used by Phase 7 in compute_doc_id
import sys  # noqa: F401  — used by Phase 7 for non-zero exit on partial failure
from pathlib import Path
from typing import Iterator


# ----------------------------------------------------------------------------
# Module-level constants (LOCKED — Phase 7 reads, does not mutate)
# ----------------------------------------------------------------------------

INGEST_PATHS = ("wiki", "docs")
"""Paths under repo root that get indexed.

NOT instances/ — per v1 design, structured YAML records embed poorly
(short fields, repetitive keys, no narrative context). YAML records are
exposed to RAG indirectly: the wiki/ pages and docs/<doc>/processed.md
files reference them by URI, and Phase 7 retrieval rerankers can dereference
those URIs against instances/ when needed.
"""

INELIGIBLE_CONFIDENTIALITY = ("restricted", "itar_ear")
"""DOC-04: documents with this confidentiality MUST be filtered before upload.

The exporter is the SOLE enforcement point for the DOC-04 gate. Any future
service that bypasses this exporter and writes to RAGFlow directly (e.g. a
hypothetical Wiki.js → RAGFlow webhook) MUST re-implement the same gate.
"""

DOC_ID_PREFIX = "akb_"
"""SHA-256-derived doc_id prefix; full format: akb_<32 hex chars>.

`akb_` = "aviation knowledge base" — distinguishes our IDs from RAGFlow's
auto-assigned UUIDs in mixed datasets. The 32-char truncation is documented
in module docstring "Idempotency rule".
"""


# ----------------------------------------------------------------------------
# Function signatures — Phase 7 fills in the bodies
# ----------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments. WORKS in skeleton (no NotImplementedError).

    This is the ONLY function with a real implementation in the Phase-5
    skeleton — `python scripts/exporters/to_ragflow.py --help` MUST print
    help text without raising, so argparse is built out completely here.

    Surface (LOCKED by Phase 5 plan 05-03):
      --rebuild         drop RAGFlow dataset and re-upload everything from Git HEAD
      --dry-run         log actions without calling RAGFlow API
      --since GIT_REF   only process files changed since this Git ref (incremental)
      --paths PATH ...  restrict to subset of INGEST_PATHS
    """
    parser = argparse.ArgumentParser(
        prog="to_ragflow",
        description=(
            "Git → RAGFlow exporter (Phase-5 skeleton; Phase-7 implementation pending). "
            "See module docstring for full contract."
        ),
    )
    parser.add_argument(
        "--rebuild",
        action="store_true",
        help="drop RAGFlow dataset and re-index from Git HEAD",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="log actions without HTTP calls",
    )
    parser.add_argument(
        "--since",
        default=None,
        help="Git ref; only process files changed since this ref",
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        default=list(INGEST_PATHS),
        help=f"path filter (default: {INGEST_PATHS})",
    )
    return parser.parse_args(argv)


def iter_changed_files(since: str | None, paths: list[str]) -> Iterator[Path]:
    """Yield file paths under `paths` that changed since the given Git ref.

    When `since` is None, yields all files matching the ingest patterns
    (wiki/**.md, docs/**/processed.md). When `since` is set, yields only
    files whose Git status indicates Add/Modify since that ref (deletes
    are handled separately — Phase 7 emits delete actions for files that
    were removed from Git and currently exist in RAGFlow).

    Phase 7 implementation hint: shell out to
        git diff --name-only --diff-filter=AM <since> HEAD -- wiki docs
    when `since` is set; otherwise walk the filesystem with Path.rglob('*.md')
    filtered by INGEST_PATHS and the docs/**/processed.md pattern.

    Raises:
        NotImplementedError: Phase 7 fills this in.
    """
    raise NotImplementedError(
        "iter_changed_files: Phase 7 task. Use git diff --name-only when since is set; "
        "use Path.rglob('*.md') filtered by INGEST_PATHS otherwise. See module docstring."
    )


def load_metadata(doc_dir: Path) -> dict:
    """Load metadata.yaml sidecar for a doc directory.

    For wiki/**.md files: derive minimal metadata from path + frontmatter
    (no sidecar metadata.yaml exists for wiki pages — they use Wiki.js's
    own page metadata, which the exporter approximates by reading any
    YAML frontmatter block at the top of the .md file).

    For docs/**/processed.md files: load the sibling metadata.yaml verbatim;
    this is the canonical case that exercises the full DOC-02 schema.

    Returns:
        dict with at least the 11 mandatory fields per docs/README.md §2:
        {title, doc_type, language, source_url, publication_date,
         effective_date, confidentiality, domain_tags, version,
         file_hash, processed_by}.

    Raises:
        NotImplementedError: Phase 7 fills this in. ruamel.yaml or PyYAML
        acceptable; PyYAML's safe_load is sufficient (no custom tags in our
        metadata schema).
    """
    raise NotImplementedError(
        "load_metadata: Phase 7 task. See docs/README.md §2 for the 11 mandatory fields. "
        "PyYAML safe_load is sufficient — no custom tags in metadata schema."
    )


def is_ingest_eligible(metadata: dict) -> bool:
    """DOC-04 confidentiality gate.

    Returns False if metadata['confidentiality'] in INELIGIBLE_CONFIDENTIALITY.
    Returns True if 'public' or 'internal'.
    Raises ValueError if confidentiality is missing or unknown enum value
    (better to fail-closed than fail-open at the gate layer).

    This gate runs BEFORE any HTTP call to RAGFlow — restricted and itar_ear
    documents NEVER leave the local filesystem. The gate is the SOLE
    enforcement point for DOC-04; any code path that uploads to RAGFlow
    without going through this gate is a P0 regression.

    Raises:
        NotImplementedError: Phase 7 fills this in. Logic is straightforward;
        skeleton signature locks the contract:
            return metadata['confidentiality'] not in INELIGIBLE_CONFIDENTIALITY
        plus the explicit ValueError for missing/unknown values.
    """
    raise NotImplementedError(
        "is_ingest_eligible: Phase 7 task. "
        "Returns metadata['confidentiality'] not in INELIGIBLE_CONFIDENTIALITY. "
        "ValueError on missing/unknown confidentiality enum (fail-closed)."
    )


def compute_doc_id(file_path: Path, content: bytes) -> str:
    """Idempotent RAGFlow document_id derivation.

    Rule (LOCKED by Phase 5 plan 05-03):
        doc_id = DOC_ID_PREFIX + sha256(str(file_path).encode() + b"\\n" + content).hexdigest()[:32]

    Same (file_path, content) always produces the same doc_id; RAGFlow re-upload
    on identical content is a no-op (idempotent). When content changes, doc_id
    changes — the new upload supersedes the old one (Phase 7 must delete the
    superseded RAGFlow document on update so the vector store does not accumulate
    stale chunks for the same source file).

    The path is included in the hash input so that two files with identical
    content but different paths get distinct doc_ids (e.g. a regulation quoted
    verbatim in two different processed.md files).

    Raises:
        NotImplementedError: Phase 7 fills this in. Implementation is the
        one-liner in this docstring.
    """
    raise NotImplementedError(
        "compute_doc_id: Phase 7 task. Implementation is the one-liner in this docstring: "
        "DOC_ID_PREFIX + hashlib.sha256(str(file_path).encode() + b'\\n' + content).hexdigest()[:32]"
    )


def upload_document(
    file_path: Path,
    metadata: dict,
    doc_id: str,
    dry_run: bool = False,
) -> dict:
    """POST a document to RAGFlow via HTTP API.

    See https://ragflow.io/docs/http_api_reference for endpoint shape.
    Endpoint (Phase 7 verifies against RAGFlow v0.25.1):
        POST {RAGFLOW_API_BASE}/api/v1/datasets/<dataset_id>/documents
    with bearer auth: Authorization: Bearer {RAGFLOW_API_TOKEN}.

    When dry_run=True, returns a stub dict
        {action: 'would-upload', doc_id, file: str(file_path), status: 'dry-run'}
    WITHOUT making any HTTP call (Phase 5 honors this — see module docstring
    "Phase-5 boundary"; Phase 7 retains dry-run support for diagnostics).

    Returns:
        dict with at least {file, action, ragflow_doc_id, status, content_hash}
        suitable for JSON-Lines stdout logging per the "Outputs" section of
        the module docstring.

    Phase 7 must:
      - Check existing doc by doc_id BEFORE POSTing (idempotency check); if
        exists with same content_hash, return action='skip', status='ok'.
      - On content change, DELETE the previous doc with this base file_path
        before POSTing the new one.
      - Map metadata fields to RAGFlow meta_fields per the
        "Per-corpus metadata mapping reference" section below.

    Raises:
        NotImplementedError: Phase 7 fills this in. Use httpx (preferred) or
        requests; bearer auth from RAGFLOW_API_TOKEN env var; idempotency
        check before POST.
    """
    raise NotImplementedError(
        "upload_document: Phase 7 task. Honors --dry-run by returning stub dict. "
        "Real path makes HTTP POST to RAGFLOW_API_BASE + '/api/v1/datasets/<id>/documents'."
    )


def rebuild_index() -> int:
    """--rebuild path: drop RAGFlow dataset, re-upload everything from Git HEAD.

    Per ARCHITECTURE.md "Failure Modes & Recovery": RAGFlow vector store is a
    rebuildable derivative of Git. This function is the recovery hook —
    invoked when the RAGFlow index is lost, corrupted, or needs migration
    between embedding models.

    Returns:
        Exit code (0 on success, non-zero on partial failure).

    Phase 7 steps:
        (1) HTTP DELETE the dataset (or all documents within it).
        (2) HTTP POST a fresh dataset with the same name + meta_field schema.
        (3) Iterate INGEST_PATHS yielding all eligible files.
        (4) For each file: load_metadata + is_ingest_eligible + compute_doc_id
            + upload_document.
        (5) Emit a final summary record to stdout: total/uploaded/gated/errors.

    Raises:
        NotImplementedError: Phase 7 fills this in.
    """
    raise NotImplementedError(
        "rebuild_index: Phase 7 task. Steps: (1) HTTP DELETE the dataset, "
        "(2) HTTP POST a fresh dataset, (3) iterate INGEST_PATHS yielding all files, "
        "(4) for each: load_metadata + is_ingest_eligible + compute_doc_id + upload_document."
    )


def main(argv: list[str] | None = None) -> int:
    """Entry point. argparse-help path WORKS; real-work paths raise NotImplementedError.

    Phase-5 contract: `python scripts/exporters/to_ragflow.py --help` MUST exit 0
    and print the help text. ANY OTHER invocation (including --dry-run with no
    args, or --rebuild) raises NotImplementedError with a pointer to this
    module's docstring.
    """
    args = parse_args(argv)
    if args.rebuild:
        return rebuild_index()
    # Incremental sync path
    raise NotImplementedError(
        "Incremental sync (Phase 7 task). Read module docstring 'Contract' section. "
        "Pseudocode: for f in iter_changed_files(args.since, args.paths): "
        "meta = load_metadata(f.parent); "
        "if not is_ingest_eligible(meta): continue; "
        "doc_id = compute_doc_id(f, f.read_bytes()); "
        "result = upload_document(f, meta, doc_id, dry_run=args.dry_run); "
        "print(json.dumps(result))"
    )


if __name__ == "__main__":
    raise SystemExit(main())
