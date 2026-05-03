"""ID format validator (D-23 URIs, D-24/D-25 internal-id prefixes).

Rules emitted by this module:

- ``ids.uri-format`` (severity=error)
    Any field that should be a canonical URI must match
    ``^aviationkb://[a-z][a-z-]*/[a-z0-9]+(-[a-z0-9]+)*@[0-9]+$``.
    Checked fields: top-level ``id``, relation ``subject`` / ``object``,
    ``provenance.actor``, ``provenance.reviewer`` (when present and
    non-empty), and ``source.document_id``.

- ``ids.type-prefix-mismatch`` (severity=error)
    Cross-field check: for entity records (``type`` is one of the known
    PascalCase entity discriminators), the URI's ``<type>`` segment MUST be
    the kebab-case form of ``record.type``. E.g. ``type=AircraftModel`` →
    URI segment ``aircraft-model``; ``type=CFDMethod`` → ``cfd-method``
    (acronym handled manually so we get ``cfd-method``, not
    ``c-f-d-method``).

NOTE: ``schema.py`` already enforces the URI regex via JSON Schema
``pattern``. This validator runs anyway because:
  (a) it produces clearer error messages than the raw "does not match
      pattern" wording jsonschema emits, and
  (b) the type-prefix-mismatch rule is a CROSS-FIELD check that JSON Schema
      cannot express.
"""
import re
from pathlib import Path
from typing import Any

from .errors import ValidationError


# Canonical URI pattern, kept in lockstep with ontology/_meta.schema.json $defs/uri.
URI_RE = re.compile(r"^aviationkb://[a-z][a-z-]*/[a-z0-9]+(-[a-z0-9]+)*@[0-9]+$")

# PascalCase → kebab-case helper. Inserts a hyphen before each capital letter
# (except at the very start), then lowercases. CFDMethod is the only known
# acronym entity; it gets a manual mapping below to avoid "c-f-d-method".
_KEBAB_RE = re.compile(r"(?<!^)(?=[A-Z])")

# Same set as loader.py — keep in sync if new entity types are added.
_ENTITY_TYPES = {
    "AircraftModel", "AircraftSystem", "Subsystem", "Component", "Document",
    "Requirement", "RegulationClause", "Standard", "Procedure", "MaintenanceTask",
    "AccidentCase", "ExpertNote", "FailureMode", "CFDMethod", "SimulationCase",
    "MeshRequirement", "TurbulenceModel", "Material", "TestCase", "TestReport",
    "Person", "Organization",
}

# Manual override for any entity name where naive PascalCase→kebab would split
# acronyms wrong. Currently only CFDMethod.
_TYPE_TO_URI_SEGMENT = {
    "CFDMethod": "cfd-method",
}


def _expected_uri_segment(rtype: str) -> str:
    """Return the URI ``<type>`` segment expected for a record's PascalCase type."""
    if rtype in _TYPE_TO_URI_SEGMENT:
        return _TYPE_TO_URI_SEGMENT[rtype]
    return _KEBAB_RE.sub("-", rtype).lower()


def _check_uri(value: Any, pointer: str, file: str) -> list[ValidationError]:
    """Emit ids.uri-format if value is a string that does not match URI_RE.

    Non-string values are ignored — the schema layer reports those.
    """
    if not isinstance(value, str):
        return []
    if not URI_RE.match(value):
        return [ValidationError(
            rule="ids.uri-format",
            severity="error",
            file=file,
            message=f"value '{value}' does not match aviationkb://<type>/<slug>@<version>",
            pointer=pointer,
        )]
    return []


def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]:
    """Run URI-format and type-prefix-mismatch checks on a single record."""
    errors: list[ValidationError] = []
    if not isinstance(record, dict):
        return errors
    file = str(path)

    rid = record.get("id")
    errors.extend(_check_uri(rid, "/id", file))

    # Relation records carry subject + object URIs.
    for fld in ("subject", "object"):
        if fld in record:
            errors.extend(_check_uri(record[fld], f"/{fld}", file))

    # provenance.actor and provenance.reviewer are URIs when present and non-empty.
    # Empty-string reviewer is legitimately checked elsewhere (provenance.h-darrieus
    # treats "" as no reviewer); we skip the URI-format check on "" so we do not
    # double-report it here.
    prov = record.get("provenance") or {}
    if isinstance(prov, dict):
        for fld in ("actor", "reviewer"):
            v = prov.get(fld)
            if v is not None and v != "":
                errors.extend(_check_uri(v, f"/provenance/{fld}", file))

    # source.document_id is also a URI.
    src = record.get("source") or {}
    if isinstance(src, dict) and "document_id" in src:
        errors.extend(_check_uri(src["document_id"], "/source/document_id", file))

    # Type-prefix-mismatch cross-field check. Only fires when the id is itself
    # a syntactically valid URI (otherwise ids.uri-format already covers it)
    # AND the record carries a known entity type discriminator.
    rtype = record.get("type")
    if isinstance(rid, str) and URI_RE.match(rid) and rtype in _ENTITY_TYPES:
        # rid like "aviationkb://aircraft-model/boeing-737-max-8@1"
        uri_type_segment = rid.split("//", 1)[1].split("/", 1)[0]
        expected = _expected_uri_segment(rtype)
        if uri_type_segment != expected:
            errors.append(ValidationError(
                rule="ids.type-prefix-mismatch",
                severity="error",
                file=file,
                message=(
                    f"record type='{rtype}' implies URI segment '{expected}' "
                    f"but id has segment '{uri_type_segment}'"
                ),
                pointer="/id",
            ))

    return errors
