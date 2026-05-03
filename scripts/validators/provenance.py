"""Provenance validator — H-Darrieus REJECT (PROV-04), _pending promotion
gate (PROV-05), schema_version cross-record check (VER-03).

These rules cannot be expressed in JSON Schema alone:

- ``provenance.h-darrieus`` (severity=error) — 3-condition AND across
  ``provenance.method``, ``confidence.score``, and reviewer presence:
  ``method == "ai_extracted" AND score > 0.85 AND (no reviewer OR reviewer == "")``.
  Boundary is STRICT ``>`` per ADR-005: ``score == 0.85`` does NOT trip.
  Empty-string reviewer is treated as "no reviewer" (PROV-04 edge case).

- ``provenance.pending-gate`` (severity=error) — path-based: any record
  whose path contains ``/_pending/`` must have
  ``provenance.method == "hybrid_reviewed"`` and a non-empty reviewer URI
  and a non-empty ``reviewed_at`` timestamp. Otherwise the record is
  stuck in quarantine and the validator rejects it (PROV-05 / D-17).

- ``provenance.schema-version-mismatch`` (severity=warning) — cross-record:
  any record whose ``schema_version`` differs from the current
  ``ontology/VERSION`` value is warned. At v0.1.0 there is no N-1 to be
  "older than", so we emit warning rather than error per VER-03 partial
  hardening — the rule will tighten to error once the ontology bumps to
  0.2.0+.
"""
from pathlib import Path
from typing import Any, Optional

from .errors import ValidationError


def _read_current_version(repo_root: Path) -> Optional[str]:
    """Read ontology/VERSION and return the trimmed string (or None if absent)."""
    vfile = repo_root / "ontology" / "VERSION"
    if not vfile.exists():
        return None
    return vfile.read_text(encoding="utf-8").strip()


def _has_nonempty_reviewer(prov: dict) -> bool:
    """True iff prov.reviewer is a string with at least one non-whitespace char."""
    rv = prov.get("reviewer")
    return isinstance(rv, str) and rv.strip() != ""


def _has_reviewed_at(prov: dict) -> bool:
    """True iff prov.reviewed_at is a string with at least one non-whitespace char."""
    rt = prov.get("reviewed_at")
    return isinstance(rt, str) and rt.strip() != ""


def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]:
    """Run H-Darrieus, _pending-gate, and schema_version checks on a record."""
    errors: list[ValidationError] = []
    if not isinstance(record, dict):
        return errors
    file = str(path)
    prov = record.get("provenance")
    conf = record.get("confidence")

    # ---- Rule 1: H-Darrieus REJECT (PROV-04) -------------------------------
    # method=ai_extracted AND score > 0.85 (STRICT) AND no/empty reviewer.
    if isinstance(prov, dict) and isinstance(conf, dict):
        method = prov.get("method")
        score = conf.get("score")
        if (
            method == "ai_extracted"
            and isinstance(score, (int, float))
            and score > 0.85
            and not _has_nonempty_reviewer(prov)
        ):
            errors.append(ValidationError(
                rule="provenance.h-darrieus",
                severity="error",
                file=file,
                message=(
                    "H-Darrieus REJECT: provenance.method='ai_extracted' AND "
                    f"confidence.score={score} > 0.85 AND no reviewer set. "
                    "Either lower confidence, set a human reviewer, or move to "
                    "instances/_pending/ and flip method to hybrid_reviewed."
                ),
                pointer="/provenance",
            ))

    # ---- Rule 2: _pending promotion gate (PROV-05) -------------------------
    # Any record whose path contains /_pending/ must have
    # method == hybrid_reviewed AND non-empty reviewer AND reviewed_at.
    # Single-segment dir match via substring (not Path.parts) so nested
    # _pending subdirs are also caught.
    if "/_pending/" in path.as_posix() and isinstance(prov, dict):
        method = prov.get("method")
        if method != "hybrid_reviewed":
            errors.append(ValidationError(
                rule="provenance.pending-gate",
                severity="error",
                file=file,
                message=(
                    f"record under _pending/ has provenance.method='{method}'; "
                    "must be 'hybrid_reviewed' to be eligible for promotion."
                ),
                pointer="/provenance/method",
            ))
        else:
            # method=hybrid_reviewed: reviewer + reviewed_at required.
            if not _has_nonempty_reviewer(prov):
                errors.append(ValidationError(
                    rule="provenance.pending-gate",
                    severity="error",
                    file=file,
                    message="hybrid_reviewed records require non-empty provenance.reviewer",
                    pointer="/provenance/reviewer",
                ))
            if not _has_reviewed_at(prov):
                errors.append(ValidationError(
                    rule="provenance.pending-gate",
                    severity="error",
                    file=file,
                    message="hybrid_reviewed records require provenance.reviewed_at",
                    pointer="/provenance/reviewed_at",
                ))

    # ---- Rule 3: schema_version cross-record (VER-03 partial) --------------
    # ctx['repo_root'] is set by validate.py; fallback to the validator's own
    # parents[2] for direct-import callers (tests, REPL probes).
    repo_root = ctx.get("repo_root") or Path(__file__).resolve().parents[2]
    current = _read_current_version(repo_root)
    if current is not None:
        rec_ver = record.get("schema_version")
        if isinstance(rec_ver, str) and rec_ver != current:
            # At v0.1.0 the "older than N-1" predicate cannot fire (no N-1
            # exists). Warn only — will harden to error once ontology bumps.
            errors.append(ValidationError(
                rule="provenance.schema-version-mismatch",
                severity="warning",
                file=file,
                message=(
                    f"record schema_version='{rec_ver}' != current ontology "
                    f"VERSION='{current}'. Will harden to error once ontology "
                    "bumps to 0.2.0+ (N-1 rule)."
                ),
                pointer="/schema_version",
            ))

    return errors
