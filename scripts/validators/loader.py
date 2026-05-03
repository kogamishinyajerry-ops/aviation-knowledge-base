"""YAML loading + schema discovery helpers.

ruamel.yaml is mandated by D-15 / Gap-5 (round-trip / comment preservation
when we eventually edit instances programmatically). For Wave-1 read-only
validation we use typ="safe" which is faster and safe-by-default.
"""
import re
from pathlib import Path
from typing import Any, Iterable, Optional

from ruamel.yaml import YAML


_YAML = YAML(typ="safe")


def load_yaml(path: Path) -> Any:
    """Load a single YAML file and return the parsed Python object."""
    with path.open("r", encoding="utf-8") as fh:
        return _YAML.load(fh)


def iter_instance_files(root: Path) -> Iterable[Path]:
    """Yield *.yaml/*.yml under root, sorted, excluding tests/fixtures/invalid/.

    The master CLI must not try to validate intentionally-bad fixtures, so we
    drop any path containing ``fixtures/invalid`` regardless of where root sits.
    """
    if root.is_file():
        if "fixtures/invalid" in root.as_posix():
            return
        yield root
        return
    for p in sorted(root.rglob("*.yaml")):
        if "fixtures/invalid" in p.as_posix():
            continue
        yield p
    for p in sorted(root.rglob("*.yml")):
        if "fixtures/invalid" in p.as_posix():
            continue
        yield p


# ---- Schema discovery ------------------------------------------------------

# Map a record's "type" value to the schema file under ontology/schemas/.
# Entity types are PascalCase; the schema filename is kebab-case + entity. prefix.
# Relation types are snake_case; schema filename is kebab-case + relation. prefix.

_KEBAB_RE = re.compile(r"(?<!^)(?=[A-Z])")


def _pascal_to_kebab(name: str) -> str:
    return _KEBAB_RE.sub("-", name).lower()


def _snake_to_kebab(name: str) -> str:
    return name.replace("_", "-")


# Entity type discriminators expected in v0.1.0 ontology. Drives schema lookup.
_ENTITY_TYPES = {
    "AircraftModel", "AircraftSystem", "Subsystem", "Component", "Document",
    "Requirement", "RegulationClause", "Standard", "Procedure", "MaintenanceTask",
    "AccidentCase", "ExpertNote", "FailureMode", "CFDMethod", "SimulationCase",
    "MeshRequirement", "TurbulenceModel", "Material", "TestCase", "TestReport",
    "Person", "Organization",
}

# Relation type discriminators expected in v0.1.0 ontology.
_RELATION_TYPES = {
    "part_of", "applicable_to", "constrained_by", "verified_by", "derived_from",
    "supersedes", "cites", "causes", "mitigated_by", "requires", "equivalent_to",
    "conflicts_with", "used_in", "interfaces_with", "complies_with",
    "applicable_during_phase",
}


def schema_path_for_record(record: dict, schemas_dir: Path) -> Optional[Path]:
    """Return the schema file path for a record's declared `type`.

    Returns None if the record is not a dict, has no string `type`, or `type`
    is not one of the known entity/relation discriminators. The caller treats
    None as "unknown type" and emits a schema-validator error itself.
    """
    if not isinstance(record, dict):
        return None
    rtype = record.get("type")
    if not isinstance(rtype, str):
        return None
    if rtype in _ENTITY_TYPES:
        # CFDMethod is the only acronym; map manually so we get "cfd-method" not "c-f-d-method".
        slug = "cfd-method" if rtype == "CFDMethod" else _pascal_to_kebab(rtype)
        return schemas_dir / f"entity.{slug}.schema.json"
    if rtype in _RELATION_TYPES:
        return schemas_dir / f"relation.{_snake_to_kebab(rtype)}.schema.json"
    return None
