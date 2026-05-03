"""JSON Schema (Draft 2020-12) validator.

This is the only Wave-1 validator that does real work. It:
  1. Looks up the JSON Schema file matching ``record["type"]``.
  2. Loads it with `referencing` so that ``$ref: "../_meta.schema.json#/..."``
     and ``$ref: "entity.base.schema.json"`` resolve correctly.
  3. Runs ``jsonschema.Draft202012Validator`` and converts each error to a
     ``ValidationError`` with rule == "schema".

Pitfall #9 lock: Draft 2020-12 (NOT Draft-07) — required by every leaf
schema's ``$schema`` declaration in ontology/schemas/.
"""
import json
from pathlib import Path
from typing import Any, Optional

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

from .errors import ValidationError
from .loader import schema_path_for_record


_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMAS_DIR = _REPO_ROOT / "ontology" / "schemas"
_META_PATH = _REPO_ROOT / "ontology" / "_meta.schema.json"


def _build_registry() -> Registry:
    """Build a Registry that resolves leaf-schema cross-refs.

    Leaf schemas use two reference forms:
      - ``$ref: "entity.base.schema.json"`` — sibling schema by filename
      - ``$ref: "../_meta.schema.json#/$defs/baseFields"`` — parent-relative

    We register every schema under THREE keys so jsonschema's resolver can find
    them no matter which form the caller's $ref used:
      1. The schema's canonical ``$id``
      2. The bare filename (for sibling refs from leaf schemas)
      3. ``../_meta.schema.json`` for the meta schema (parent-relative form
         used by every leaf via ``allOf: [{$ref: "../_meta.schema.json#/..."}]``)
    """
    resources: dict[str, Resource] = {}

    if not _META_PATH.exists():
        # Defensive: missing meta schema means Phase 2 was incomplete.
        return Registry()

    with _META_PATH.open("r", encoding="utf-8") as fh:
        meta_data = json.load(fh)
    meta_resource = Resource(contents=meta_data, specification=DRAFT202012)
    resources[meta_data["$id"]] = meta_resource
    resources["../_meta.schema.json"] = meta_resource
    resources["_meta.schema.json"] = meta_resource

    if _SCHEMAS_DIR.exists():
        for sf in sorted(_SCHEMAS_DIR.glob("*.schema.json")):
            with sf.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            resource = Resource(contents=data, specification=DRAFT202012)
            if "$id" in data:
                resources[data["$id"]] = resource
            # Bare filename — matches sibling refs like "entity.base.schema.json".
            resources[sf.name] = resource
            # Also "./<name>" form used by some schemas (e.g. entity.person uses
            # ``$ref: "./entity.base.schema.json"``).
            resources[f"./{sf.name}"] = resource

    return Registry().with_resources(resources.items())


_REGISTRY = _build_registry()


def validate_record(
    path: Path,
    record: Any,
    schemas_dir: Optional[Path] = None,
) -> list[ValidationError]:
    """Validate one record against its declared type's JSON Schema.

    Returns [] on success. Returns one or more ValidationError(severity="error")
    on schema violation, unknown/missing type, or non-mapping root.
    """
    schemas_dir = schemas_dir or _SCHEMAS_DIR

    if not isinstance(record, dict):
        return [ValidationError(
            rule="schema",
            severity="error",
            file=str(path),
            message="record root must be a YAML mapping/object",
        )]

    rtype = record.get("type")
    if not isinstance(rtype, str):
        return [ValidationError(
            rule="schema",
            severity="error",
            file=str(path),
            message="record missing required field `type` (string)",
            pointer="/type",
        )]

    schema_file = schema_path_for_record(record, schemas_dir)
    if schema_file is None or not schema_file.exists():
        return [ValidationError(
            rule="schema",
            severity="error",
            file=str(path),
            message=f"no schema found for type='{rtype}' (looked in {schemas_dir})",
            pointer="/type",
        )]

    with schema_file.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)

    validator = Draft202012Validator(schema, registry=_REGISTRY)

    errors: list[ValidationError] = []
    for err in validator.iter_errors(record):
        # Build a JSON Pointer from the error's absolute_path; root-level
        # errors get pointer="/" so the formatter still prints something.
        ptr = "/" + "/".join(str(p) for p in err.absolute_path) if err.absolute_path else "/"
        errors.append(ValidationError(
            rule="schema",
            severity="error",
            file=str(path),
            message=err.message,
            pointer=ptr,
        ))
    return errors
