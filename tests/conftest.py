"""Shared pytest fixtures for the validators test suite.

The original Wave-1 ``by_id`` fixture (built from ``tests/fixtures/valid/``) is
preserved verbatim — Wave-2 plans 03-03 and 03-04 already consume it. Wave 3
(plan 03-05) adds session-scoped corpus loaders + a ``corpus_ctx`` dict that
mirrors the shape of the ``ctx`` dict ``scripts/validate.py`` builds at runtime,
so cross-record validators (relations, links) see the same lookup surface in
tests that they see in CI.
"""
import sys
from pathlib import Path
from typing import Iterator

import pytest

# Allow ``from scripts.validators import ...`` from inside tests.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.validators.loader import iter_instance_files, load_yaml  # noqa: E402


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return _REPO_ROOT


@pytest.fixture(scope="session")
def valid_fixtures_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures" / "valid"


@pytest.fixture(scope="session")
def invalid_fixtures_dir(repo_root: Path) -> Path:
    return repo_root / "tests" / "fixtures" / "invalid"


@pytest.fixture(scope="session")
def by_id(valid_fixtures_dir: Path) -> dict:
    """Corpus index of every valid fixture, keyed by record id (URI).

    Built once per pytest session. Wave-2 plans 03-03/03-04 use this fixture
    to assert that relations/links validators correctly resolve cross-references
    across the valid corpus.
    """
    index: dict[str, tuple[Path, dict]] = {}
    if not valid_fixtures_dir.exists():
        return index
    for path in iter_instance_files(valid_fixtures_dir):
        try:
            rec = load_yaml(path)
        except Exception:
            continue
        if isinstance(rec, dict) and isinstance(rec.get("id"), str):
            index[rec["id"]] = (path, rec)
    return index


# ---------------------------------------------------------------------------
# Wave 3 additions (plan 03-05): session-scoped corpus + ctx loaders.
# ---------------------------------------------------------------------------


def _walk_yaml(root: Path) -> Iterator[Path]:
    """Yield every *.yaml/*.yml under root (sorted, recursive).

    Unlike ``iter_instance_files`` this DOES include ``fixtures/invalid/``
    paths — the invalid corpus is exactly what Wave 3 parametrises over.
    """
    seen: set[Path] = set()
    for ext in ("*.yaml", "*.yml"):
        for p in sorted(root.rglob(ext)):
            if p not in seen:
                seen.add(p)
                yield p


@pytest.fixture(scope="session")
def valid_records(valid_fixtures_dir: Path) -> list[tuple[Path, dict]]:
    """Every record under ``tests/fixtures/valid/`` (sorted, recursive)."""
    out: list[tuple[Path, dict]] = []
    if not valid_fixtures_dir.exists():
        return out
    for p in _walk_yaml(valid_fixtures_dir):
        try:
            rec = load_yaml(p)
        except Exception:
            continue
        out.append((p, rec))
    return out


@pytest.fixture(scope="session")
def invalid_records(invalid_fixtures_dir: Path) -> list[tuple[Path, dict]]:
    """Every record under ``tests/fixtures/invalid/`` (sorted, recursive).

    README.md is filtered out by the *.yaml/*.yml glob. Records that fail to
    parse are skipped silently — they would otherwise be a separate kind of
    test failure (parse-vs-validate) which Wave 1 fixtures already exercise.
    """
    out: list[tuple[Path, dict]] = []
    if not invalid_fixtures_dir.exists():
        return out
    for p in _walk_yaml(invalid_fixtures_dir):
        try:
            rec = load_yaml(p)
        except Exception:
            continue
        out.append((p, rec))
    return out


@pytest.fixture(scope="session")
def corpus_ctx(
    valid_records: list[tuple[Path, dict]],
    invalid_records: list[tuple[Path, dict]],
    repo_root: Path,
) -> dict:
    """Mirror the ctx dict that ``scripts/validate.py`` builds at runtime.

    Includes BOTH valid and invalid records in ``by_id`` so that cross-record
    validators (relations.subject-not-found, links.broken-source-ref) can see
    the same lookup surface they see when ``validate.py`` walks a real corpus.
    Without this, an invalid fixture whose subject URI happens to point at
    *another invalid* fixture (e.g. ``broken-relation-subject/`` referencing
    a deliberately-bad URI) would falsely "resolve" because we'd only have
    indexed the valid set.
    """
    all_records = list(valid_records) + list(invalid_records)
    by_id: dict[str, tuple[Path, dict]] = {
        rec.get("id"): (p, rec)
        for p, rec in all_records
        if isinstance(rec, dict) and isinstance(rec.get("id"), str)
    }
    return {
        "records": all_records,
        "by_id": by_id,
        "repo_root": repo_root,
    }
