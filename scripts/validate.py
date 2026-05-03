#!/usr/bin/env python3
"""Aviation KB ontology master validator (REQ VAL-01).

Usage:
    python scripts/validate.py [PATH ...]

If no PATH given, defaults to ``instances/``. Walks every *.yaml/*.yml under
the path(s) (excluding tests/fixtures/invalid/ — see loader.iter_instance_files),
runs every registered validator on each record, prints aggregated errors,
exits 1 if any severity == 'error' was emitted.

Wave 1 ships schema.py as a real validator and ids/provenance/relations/links
as stubs returning []. Wave 2 plans (03-03 / 03-04) fill in the stubs without
touching this file — that contract is the whole point of the dispatch loop
below.
"""
import argparse
import sys
from pathlib import Path

# Allow `python scripts/validate.py` to import the sibling validators package.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.validators import schema, ids, provenance, relations, links  # noqa: E402
from scripts.validators.errors import ValidationError  # noqa: E402
from scripts.validators.loader import iter_instance_files, load_yaml  # noqa: E402


# Order matters: schema first (cheapest filter), then per-record rules,
# then cross-record rules (relations, links) which read ctx['by_id'].
VALIDATORS = [
    ("schema", schema.validate_record),
    ("ids", ids.validate_record),
    ("provenance", provenance.validate_record),
    ("relations", relations.validate_record),
    ("links", links.validate_record),
]


def collect_records(paths: list[Path]) -> list[tuple[Path, dict]]:
    """Pre-load every record so cross-record validators can index them.

    On YAML parse failure we still keep an entry — its `record` is replaced by
    a sentinel ``{"__load_error__": "<exc-msg>"}`` which `main` turns into a
    loader-rule ValidationError instead of crashing the whole run.
    """
    records: list[tuple[Path, dict]] = []
    for root in paths:
        if root.is_file():
            yield_paths: list[Path] = [root]
        elif root.is_dir():
            yield_paths = list(iter_instance_files(root))
        else:
            # Path doesn't exist — emit one synthetic error and continue.
            records.append((root, {"__load_error__": f"path does not exist: {root}"}))
            continue
        for p in yield_paths:
            try:
                rec = load_yaml(p)
            except Exception as exc:  # ruamel.yaml.YAMLError or OSError
                records.append((p, {"__load_error__": str(exc)}))
                continue
            records.append((p, rec))
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="validate.py",
        description="Aviation KB ontology validator — runs schema/ids/provenance/relations/links rules across YAML records.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to validate. Defaults to ./instances if none given.",
    )
    args = parser.parse_args(argv)

    targets = [Path(a) for a in args.paths] if args.paths else [_REPO_ROOT / "instances"]
    records = collect_records(targets)

    # Build context shared by cross-record validators (Wave 2 will use it).
    ctx = {
        "records": records,                     # list[(Path, dict)]
        "by_id": {                              # quick lookup by record id (URI)
            rec.get("id"): (p, rec)
            for p, rec in records
            if isinstance(rec, dict) and isinstance(rec.get("id"), str)
        },
        "repo_root": _REPO_ROOT,
    }

    all_errors: list[ValidationError] = []
    for path, record in records:
        if isinstance(record, dict) and "__load_error__" in record:
            all_errors.append(ValidationError(
                rule="loader",
                severity="error",
                file=str(path),
                message=f"YAML parse failed: {record['__load_error__']}",
            ))
            continue
        for name, fn in VALIDATORS:
            # schema.validate_record signature is (path, record, schemas_dir=None);
            # the four stubs accept (path, record, **ctx). Calling pattern below
            # works for both because schema ignores **ctx kwargs and stubs absorb
            # them.
            if name == "schema":
                errs = fn(path, record)
            else:
                errs = fn(path, record, **ctx)
            all_errors.extend(errs)

    errors = [e for e in all_errors if e.severity == "error"]
    warnings = [e for e in all_errors if e.severity == "warning"]
    for e in all_errors:
        print(e.format())
    print(
        f"\nValidation summary: {len(errors)} error(s), {len(warnings)} warning(s) "
        f"across {len(records)} record(s)."
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
