"""Sanity mutation tests (REQ VAL-04 mutation half).

These tests pick a known-good fixture from ``tests/fixtures/valid/``, mutate
ONE field in-memory, and assert the validators fire the rule that the
mutation should trip. They prove the regression suite is observing real
behaviour: if the validator's rule body is ever silently disabled, these
mutations will start passing the validator and these tests will go red.

Each mutation test is intentionally small (one rule per test) so a regression
points at the exact validator that broke. Mutations are NEVER persisted to
disk — they live entirely in deepcopied dicts.

The 5 mutations cover all five validator modules at least once:

  schema      — strip the ``type`` discriminator
  ids         — overwrite ``id`` with a non-URI string
  provenance  — flip a record into the H-Darrieus reject shape
  relations   — overwrite ``subject`` on a relation with a dangling URI
  links       — overwrite ``source.document_id`` with a URI not in the corpus

Plus one extra mutation (provenance.pending-gate) because PROV-05 is the
single highest-stakes rule (D-17 quarantine gate) and worth a dedicated
sanity check.
"""
from __future__ import annotations

import copy
from pathlib import Path

import pytest

from scripts.validators.errors import ValidationError
from tests.test_validators import run_all_validators


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def _pick(records: list[tuple[Path, dict]], pred) -> tuple[Path, dict]:
    """Return the first (path, record) pair that satisfies ``pred``.
    Raises pytest.skip if none match — that means the valid corpus regressed
    (different bug, different test)."""
    for path, rec in records:
        if pred(rec):
            return path, rec
    pytest.skip(f"no valid fixture matched predicate {pred.__name__}")


def _rules_fired(errs: list[ValidationError]) -> set[str]:
    return {e.rule for e in errs}


# ---------------------------------------------------------------------------
# Mutation 1 — strip type discriminator (schema layer)
# ---------------------------------------------------------------------------


@pytest.mark.sanity
def test_mutation_strip_type_fires_schema(valid_records, corpus_ctx):
    """Removing ``type`` makes the record un-schema-validatable; the schema
    layer must emit ``rule == 'schema'`` because schema_path_for_record
    returns None for a missing type."""
    assert valid_records, "no valid fixtures discovered"
    path, record = valid_records[0]
    mutated = copy.deepcopy(record)
    mutated.pop("type", None)
    errs = run_all_validators(path, mutated, corpus_ctx)
    rules = _rules_fired(errs)
    assert "schema" in rules, (
        f"stripping `type` should fire rule='schema'; got {sorted(rules)}\n"
        + "\n".join(e.format() for e in errs)
    )


# ---------------------------------------------------------------------------
# Mutation 2 — break the URI shape on `id` (ids layer)
# ---------------------------------------------------------------------------


@pytest.mark.sanity
def test_mutation_bad_id_fires_ids_uri_format(valid_records, corpus_ctx):
    """Overwriting ``id`` with a non-URI string must fire
    ``ids.uri-format``. The schema layer also fires for the pattern, but
    we only assert the ids rule because that's the one we're exercising."""
    path, record = _pick(
        valid_records,
        lambda r: isinstance(r, dict) and isinstance(r.get("id"), str),
    )
    mutated = copy.deepcopy(record)
    mutated["id"] = "not-a-uri-at-all"
    errs = run_all_validators(path, mutated, corpus_ctx)
    rules = _rules_fired(errs)
    assert "ids.uri-format" in rules, (
        f"bad id should fire ids.uri-format; got {sorted(rules)}\n"
        + "\n".join(e.format() for e in errs)
    )


# ---------------------------------------------------------------------------
# Mutation 3 — H-Darrieus reject shape (provenance layer, PROV-04)
# ---------------------------------------------------------------------------


@pytest.mark.sanity
def test_mutation_h_darrieus_fires_provenance_rule(valid_records, corpus_ctx):
    """Set provenance.method=ai_extracted, score>0.85, drop reviewer →
    provenance.h-darrieus must fire (per ADR-005, strict ``>``)."""
    path, record = _pick(
        valid_records,
        lambda r: isinstance(r, dict)
        and isinstance(r.get("provenance"), dict)
        and isinstance(r.get("confidence"), dict),
    )
    mutated = copy.deepcopy(record)
    mutated["provenance"]["method"] = "ai_extracted"
    mutated["provenance"].pop("reviewer", None)
    mutated["confidence"]["score"] = 0.99
    # Keep rationale length the schema requires (>= 20 chars per PROV-02).
    mutated["confidence"]["rationale"] = (
        "synthetic mutation for sanity test (h-darrieus reject path)."
    )
    errs = run_all_validators(path, mutated, corpus_ctx)
    rules = _rules_fired(errs)
    assert "provenance.h-darrieus" in rules, (
        f"H-Darrieus mutation should fire provenance.h-darrieus; got "
        f"{sorted(rules)}\n" + "\n".join(e.format() for e in errs)
    )


# ---------------------------------------------------------------------------
# Mutation 4 — pending-gate (provenance layer, PROV-05)
# ---------------------------------------------------------------------------


@pytest.mark.sanity
def test_mutation_pending_path_fires_pending_gate(valid_records, corpus_ctx):
    """Flip a record's path into a synthetic ``/_pending/`` location with
    method != hybrid_reviewed → provenance.pending-gate must fire.

    Note: we mutate the *path* the validator sees, not the record body, since
    PROV-05 is path-based per D-17.
    """
    path, record = _pick(
        valid_records,
        lambda r: isinstance(r, dict)
        and isinstance(r.get("provenance"), dict)
        and r["provenance"].get("method") != "hybrid_reviewed",
    )
    fake_pending_path = Path(
        "tests/fixtures/valid/_pending/synthetic-mutation.yaml"
    )
    errs = run_all_validators(fake_pending_path, copy.deepcopy(record), corpus_ctx)
    rules = _rules_fired(errs)
    assert "provenance.pending-gate" in rules, (
        f"pending-path mutation should fire provenance.pending-gate; got "
        f"{sorted(rules)}\n" + "\n".join(e.format() for e in errs)
    )


# ---------------------------------------------------------------------------
# Mutation 5 — broken relation subject (relations layer)
# ---------------------------------------------------------------------------


@pytest.mark.sanity
def test_mutation_dangling_subject_fires_relations(valid_records, corpus_ctx):
    """On a relation record, overwrite ``subject`` with a syntactically valid
    URI that does not resolve in by_id → relations.subject-not-found must
    fire."""
    path, record = _pick(
        valid_records,
        lambda r: isinstance(r, dict)
        and isinstance(r.get("subject"), str)
        and isinstance(r.get("object"), str),
    )
    mutated = copy.deepcopy(record)
    mutated["subject"] = "aviationkb://aircraft-model/this-id-does-not-exist@9999"
    errs = run_all_validators(path, mutated, corpus_ctx)
    rules = _rules_fired(errs)
    assert "relations.subject-not-found" in rules, (
        f"dangling subject should fire relations.subject-not-found; got "
        f"{sorted(rules)}\n" + "\n".join(e.format() for e in errs)
    )


# ---------------------------------------------------------------------------
# Mutation 6 — broken source.document_id (links layer, PROV-06)
# ---------------------------------------------------------------------------


@pytest.mark.sanity
def test_mutation_dangling_source_fires_links(valid_records, corpus_ctx):
    """Overwrite source.document_id with a URI not in by_id →
    links.broken-source-ref must fire."""
    path, record = _pick(
        valid_records,
        lambda r: isinstance(r, dict)
        and isinstance(r.get("source"), dict)
        and isinstance(r["source"].get("document_id"), str),
    )
    mutated = copy.deepcopy(record)
    mutated["source"]["document_id"] = (
        "aviationkb://document/dangling-source-fixture-mutation@9999"
    )
    errs = run_all_validators(path, mutated, corpus_ctx)
    rules = _rules_fired(errs)
    assert "links.broken-source-ref" in rules, (
        f"dangling source should fire links.broken-source-ref; got "
        f"{sorted(rules)}\n" + "\n".join(e.format() for e in errs)
    )
