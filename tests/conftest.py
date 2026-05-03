"""Shared pytest fixtures for the validators test suite.

The ``by_id`` fixture builds a corpus index from ``tests/fixtures/valid/`` so
Wave-3 parametrised tests (plan 03-05) can exercise relations.broken-* and
links.broken-source-ref rules against a known-good index.
"""
import sys
from pathlib import Path

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
def by_id(valid_fixtures_dir: Path) -> dict:
    """Corpus index of every valid fixture, keyed by record id (URI).

    Built once per pytest session. Wave-3 plans use this fixture to assert
    that relations / links validators correctly resolve cross-references.
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
