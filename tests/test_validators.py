"""Validator regression tests (REQ VAL-04).

Two test groups:

1. ``test_valid_corpus_zero_errors`` — every record under
   ``tests/fixtures/valid/`` MUST produce zero ERROR-severity ValidationError
   entries when run through all five validators against the full corpus_ctx
   index. Warning-severity entries (e.g. provenance.schema-version-mismatch
   at v0.1.0) are tolerated.

2. ``test_invalid_fixture_triggers_expected_rule`` — parametrised over every
   YAML file under ``tests/fixtures/invalid/<dir>/``. For each fixture, asserts
   the rule name(s) registered in ``_INVALID_DIR_TO_RULES[<dir>]`` are present
   in the set of rules emitted across all five validators. Extra rules are
   tolerated (some fixtures dual-fire by design — see README).

Sanity mutation tests live in ``test_mutations.py`` so the parametrised file
stays focused.

Public-API contract: every validator exposes ``validate_record(path, record,
**ctx) -> list[ValidationError]``. ``ctx`` carries ``records``, ``by_id``, and
``repo_root``. ``schema.validate_record`` does NOT accept ``**ctx`` — it is
called separately with the sole ``schemas_dir`` kwarg defaulted, mirroring
``scripts/validate.py``'s dispatch loop.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.validators import schema as v_schema
from scripts.validators import ids as v_ids
from scripts.validators import provenance as v_prov
from scripts.validators import relations as v_rel
from scripts.validators import links as v_links
from scripts.validators.errors import ValidationError
from scripts.validators.loader import load_yaml

from tests._invalid_dir_to_rules import INVALID_DIR_TO_RULES


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def run_all_validators(
    path: Path,
    record: dict,
    ctx: dict,
) -> list[ValidationError]:
    """Run every validator on the record and aggregate ValidationError entries.

    Mirrors ``scripts/validate.py``'s dispatch loop: schema first (no ctx),
    then the four cross-aware validators with ``**ctx``. Returns warnings AND
    errors — callers filter by severity if they care.
    """
    errors: list[ValidationError] = []
    errors.extend(v_schema.validate_record(path, record))
    errors.extend(v_ids.validate_record(path, record, **ctx))
    errors.extend(v_prov.validate_record(path, record, **ctx))
    errors.extend(v_rel.validate_record(path, record, **ctx))
    errors.extend(v_links.validate_record(path, record, **ctx))
    return errors


# ---------------------------------------------------------------------------
# Group 1: valid corpus must pass cleanly
# ---------------------------------------------------------------------------


@pytest.mark.valid_corpus
def test_valid_corpus_zero_errors(valid_records, corpus_ctx):
    """Every record under ``tests/fixtures/valid/`` must produce zero
    ERROR-severity ValidationErrors when run through all five validators.

    Warning-severity entries (e.g. schema-version-mismatch when a record's
    declared version differs from ontology/VERSION) are tolerated; valid
    fixtures should not trip warnings either, but the contract is on errors.
    """
    assert valid_records, (
        "no valid fixtures discovered under tests/fixtures/valid/ — "
        "Wave 1 must have failed to populate the corpus."
    )

    failures: list[str] = []
    for path, record in valid_records:
        errs = run_all_validators(path, record, corpus_ctx)
        error_severity = [e for e in errs if e.severity == "error"]
        if error_severity:
            failures.append(
                f"{path.relative_to(corpus_ctx['repo_root'])}:\n  "
                + "\n  ".join(e.format() for e in error_severity)
            )

    assert not failures, (
        f"{len(failures)} valid fixture(s) produced ERROR-severity "
        "validation errors:\n\n" + "\n\n".join(failures)
    )


# ---------------------------------------------------------------------------
# Group 2: each invalid fixture triggers its expected rule
# ---------------------------------------------------------------------------


def _gather_invalid_fixture_params() -> list:
    """Walk ``tests/fixtures/invalid/`` and yield (path, expected_rules) per
    YAML file.

    Collection-time guards:
      * a directory listed in INVALID_DIR_TO_RULES but missing on disk →
        synthetic xfail param flagged at collection (rather than silent skip).
      * a directory present on disk but missing from INVALID_DIR_TO_RULES →
        synthetic xfail param so reviewers see exactly which dir is unmapped.
    """
    invalid_dir = (
        Path(__file__).resolve().parent / "fixtures" / "invalid"
    )
    if not invalid_dir.exists():
        return []

    params: list = []
    on_disk: set[str] = set()

    for sub in sorted(invalid_dir.iterdir()):
        if not sub.is_dir():
            continue
        on_disk.add(sub.name)
        expected = INVALID_DIR_TO_RULES.get(sub.name)
        if expected is None:
            params.append(pytest.param(
                sub, set(), id=f"{sub.name}/<unmapped>",
                marks=pytest.mark.xfail(
                    reason=f"directory '{sub.name}' has no mapping in "
                           "tests/_invalid_dir_to_rules.py",
                    strict=False,
                ),
            ))
            continue
        yaml_files = sorted(sub.rglob("*.yaml")) + sorted(sub.rglob("*.yml"))
        # de-duplicate while preserving order
        seen: set[Path] = set()
        for yaml_file in yaml_files:
            if yaml_file in seen:
                continue
            seen.add(yaml_file)
            params.append(pytest.param(
                yaml_file, expected,
                id=f"{sub.name}/{yaml_file.name}",
            ))

    # Mappings that exist in the dict but no directory on disk: surface them
    # as a final synthetic xfail so the contract stays bidirectional.
    for missing in sorted(set(INVALID_DIR_TO_RULES) - on_disk):
        params.append(pytest.param(
            None, INVALID_DIR_TO_RULES[missing], id=f"{missing}/<missing-on-disk>",
            marks=pytest.mark.xfail(
                reason=f"directory '{missing}' is in the rule map but not "
                       "present on disk",
                strict=False,
            ),
        ))

    return params


@pytest.mark.invalid_corpus
@pytest.mark.parametrize(
    "fixture_path, expected_rules",
    _gather_invalid_fixture_params(),
)
def test_invalid_fixture_triggers_expected_rule(
    fixture_path,
    expected_rules: set,
    corpus_ctx,
):
    """For each invalid fixture, assert the rule(s) named by its parent
    directory appear in the set of rules emitted by the validators.

    The assertion is on rule NAMES, not severity — ``old-schema-version``
    fires as a warning, ``h-darrieus-rejected`` fires as an error; both are
    "fired" for the purpose of this test.
    """
    record = load_yaml(fixture_path)
    errs = run_all_validators(fixture_path, record, corpus_ctx)
    fired_rules = {e.rule for e in errs}
    missing = expected_rules - fired_rules
    assert not missing, (
        f"Fixture {fixture_path.name} expected rules {sorted(expected_rules)} "
        f"but only fired {sorted(fired_rules)} (missing: {sorted(missing)}).\n"
        "Full validator output:\n  "
        + "\n  ".join(e.format() for e in errs)
    )
