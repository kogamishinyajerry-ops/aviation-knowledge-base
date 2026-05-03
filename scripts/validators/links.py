"""Links validator — source.document_id resolution + supersession-chain
acyclicity (PROV-06 + Pitfall #6).

This validator NEEDS the corpus-level index (``ctx['by_id']``) built by
``scripts/validate.py``. JSON Schema validates the URI *shape* of
``source.document_id`` (per record); only this layer can validate that the
URI actually *resolves* to a record AND that the resolved record's
``type == "Document"``.

Rules emitted:
  * ``links.broken-source-ref`` — ``source.document_id`` is set and does NOT
      appear as the ``id`` of any loaded record. ERROR. (REQ PROV-06)
  * ``links.source-not-document`` — ``source.document_id`` resolves but the
      resolved record's ``type != "Document"``. ERROR. (REQ PROV-06)
  * ``links.supersession-cycle`` — record has a ``superseded_by`` URI and
      walking the chain via repeated ``by_id`` lookups revisits a node.
      ERROR. (Pitfall #6 supersession-chain acyclicity, per VALIDATION.md.)

The supersession integrity *existence* checks (status='superseded' must have
superseded_by, and superseded_by must resolve) live in ``relations.py``;
this module only catches the *cyclic* failure mode.

Public API contract (kept stable from Wave-1 stub):

    def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]: ...

``ctx['by_id']`` keys are entity/relation ``id`` URIs; values are
``(path, record)`` tuples in the master CLI but tests may pass either shape
— we only ever use ``in`` membership tests and ``ctx['by_id'].get(uri)``,
then unpack defensively.

REQ PROV-06: every record citing a source MUST cite a real Document. This is
the cross-record half of source-citation integrity; the schema layer only
catches missing-or-malformed source fields.
"""
from pathlib import Path
from typing import Any, Optional

from .errors import ValidationError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unwrap_record(value: Any) -> Optional[dict]:
    """``ctx['by_id']`` values are ``(path, record)`` tuples in the master CLI.
    Tests sometimes pass bare records. This helper returns the dict either
    way (or ``None`` if the value isn't a usable record)."""
    if isinstance(value, dict):
        return value
    if isinstance(value, tuple) and len(value) >= 2 and isinstance(value[1], dict):
        return value[1]
    return None


def _detect_cycle(graph: dict, start: Any) -> bool:
    """Return True iff walking the supersession chain from ``start`` revisits
    a node before exiting via a missing edge or a ``None`` value.

    ``graph`` is a flat ``{node: next_node_or_None}`` map. ``start`` is the
    starting node id. The walk:
      - terminates with False if ``current`` is None, missing from ``graph``,
        or maps to None / non-string;
      - terminates with True the first time ``current`` is already in the
        visited set (a cycle has been entered).

    Per VALIDATION.md inline test:
        _detect_cycle({'a':'b','b':'a'}, 'a') == True
        _detect_cycle({'a':'b','b':None}, 'a') == False
    """
    visited: set = set()
    current = start
    while True:
        if current is None or not isinstance(current, str):
            return False
        if current in visited:
            return True
        visited.add(current)
        if current not in graph:
            return False
        current = graph[current]


def _build_supersession_graph(by_id: dict) -> dict:
    """Build a flat ``{record_id: superseded_by_or_None}`` map from the corpus
    index. Skips records that don't carry a ``superseded_by`` field. The
    resulting graph is what ``_detect_cycle`` walks."""
    graph: dict = {}
    for rid, raw in by_id.items():
        rec = _unwrap_record(raw)
        if not isinstance(rec, dict):
            continue
        sb = rec.get("superseded_by")
        if isinstance(sb, str) and sb.strip():
            graph[rid] = sb
        elif "superseded_by" in rec:
            graph[rid] = None
    return graph


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]:
    """Validate one record's source.document_id resolution + supersession
    chain acyclicity. Returns ``[]`` on success."""
    errors: list[ValidationError] = []
    if not isinstance(record, dict):
        return errors

    by_id: dict = ctx.get("by_id") or {}
    file = str(path)

    # ---- A. source.document_id resolution (PROV-06) ---------------------- #
    src = record.get("source")
    if isinstance(src, dict):
        doc_id = src.get("document_id")
        if isinstance(doc_id, str) and doc_id.strip():
            target_value = by_id.get(doc_id)
            target_record = _unwrap_record(target_value)
            if target_record is None:
                errors.append(ValidationError(
                    rule="links.broken-source-ref",
                    severity="error",
                    file=file,
                    message=(
                        f"source.document_id='{doc_id}' does not resolve to "
                        "any record in the corpus (PROV-06). Either add the "
                        "Document entity or correct the URI."
                    ),
                    pointer="/source/document_id",
                ))
            elif target_record.get("type") != "Document":
                errors.append(ValidationError(
                    rule="links.source-not-document",
                    severity="error",
                    file=file,
                    message=(
                        f"source.document_id='{doc_id}' resolves to a record "
                        f"of type='{target_record.get('type')}', expected "
                        "'Document'. PROV-06 requires source citations to "
                        "point at Document entities only."
                    ),
                    pointer="/source/document_id",
                ))

    # ---- B. supersession-chain acyclicity (Pitfall #6) ------------------- #
    # Only fires when this record participates in a chain (has a
    # superseded_by). Existence + resolution are checked in relations.py;
    # we only check cyclicity here so the two validators stay independent
    # and each rule maps to exactly one module per VALIDATION.md.
    sb = record.get("superseded_by")
    if isinstance(sb, str) and sb.strip() and by_id:
        rid = record.get("id")
        if isinstance(rid, str) and rid.strip():
            graph = _build_supersession_graph(by_id)
            # Ensure THIS record is in the graph (it may not be if it isn't
            # in by_id yet — e.g. when validating a single record that hasn't
            # been indexed). Prepend the in-flight edge so cycles involving
            # the current record are detected.
            graph = dict(graph)
            graph[rid] = sb
            if _detect_cycle(graph, rid):
                errors.append(ValidationError(
                    rule="links.supersession-cycle",
                    severity="error",
                    file=file,
                    message=(
                        f"supersession chain starting at '{rid}' is cyclic; "
                        "Pitfall #6 requires the supersession graph to be a "
                        "DAG so a citation can always walk forward to a "
                        "terminal active record."
                    ),
                    pointer="/superseded_by",
                ))

    return errors
