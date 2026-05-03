"""Relations validator — cross-record subject/object resolution + supersession integrity.

This validator NEEDS the corpus-level index (``ctx['by_id']``) built by
``scripts/validate.py`` so it can answer "does this URI exist as the id of any
record in the corpus?". JSON Schema can validate URI shape (per record); only
this layer can validate URI *resolution* (across records).

Rules emitted (REQ VAL-01):
  * ``relations.subject-not-found`` (alias: ``relations.broken-subject``) —
      relation's ``subject`` URI does not appear as the ``id`` of any loaded
      record. ERROR.
  * ``relations.object-not-found`` (alias: ``relations.broken-object``) —
      relation's ``object`` URI does not appear as the ``id`` of any loaded
      record. ERROR.
  * ``relations.supersession-incomplete`` —
      record has ``status == "superseded"`` but no ``superseded_by`` URI.
      ERROR. (Pitfall #6 supersession-chain integrity.)
  * ``relations.supersession-target-not-found`` —
      record has ``status == "superseded"`` and a ``superseded_by`` URI that
      does not resolve to any record. ERROR.

Both rules can fire on the same relation record (broken subject AND broken
object) — they do NOT short-circuit. Supersession integrity is checked
*independently* of the relation rules: an entity record (e.g. a
``RegulationClause`` with ``status == "superseded"``) trips the supersession
rules even though it is not a relation; a relation record never has
``status``, so it never trips the supersession rules.

Public API contract (kept stable from Wave-1 stub):

    def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]: ...

``ctx['by_id']`` is the corpus index built by ``scripts/validate.py`` /
``tests/conftest.py``. Keys are entity/relation ``id`` URIs, values are
``(path, record)`` tuples (the master CLI builds it that way; tests may pass
``(path, record)`` or just ``record`` — we only ever check membership, never
unpack, so both shapes are tolerated).
"""
from pathlib import Path
from typing import Any

from .errors import ValidationError


# Snake_case relation discriminators expected in v0.1.0 ontology. Mirrors the
# set in loader.py (kept in sync manually — see plan 03-04 frontmatter).
_RELATION_TYPES = {
    "part_of", "applicable_to", "constrained_by", "verified_by", "derived_from",
    "supersedes", "cites", "causes", "mitigated_by", "requires", "equivalent_to",
    "conflicts_with", "used_in", "interfaces_with", "complies_with",
    "applicable_during_phase",
}


def _is_relation_shape(record: dict) -> bool:
    """A record is "relation-shaped" if it declares one of the known relation
    discriminator types OR if it has both ``subject`` and ``object`` string
    fields.

    The discriminator check covers normal ontology records (``type`` is one of
    the known relation types). The structural fallback covers test fixtures
    that pass a bare ``{'subject': ..., 'object': ...}`` without a ``type``
    key — they exercise the rule but skip the schema layer. Both must work
    so the inline acceptance tests in the plan are satisfied.
    """
    rtype = record.get("type")
    if isinstance(rtype, str) and rtype in _RELATION_TYPES:
        return True
    return isinstance(record.get("subject"), str) and isinstance(record.get("object"), str)


def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]:
    """Validate one record's cross-record relation + supersession integrity.

    Returns ``[]`` on success. Returns one or more ``ValidationError`` entries
    when subject/object URIs do not resolve in ``ctx['by_id']`` or when a
    superseded record's ``superseded_by`` is missing or dangling.
    """
    errors: list[ValidationError] = []
    if not isinstance(record, dict):
        return errors

    by_id: dict = ctx.get("by_id") or {}
    file = str(path)

    # ---- A. relation subject/object resolution --------------------------- #
    if _is_relation_shape(record):
        subj = record.get("subject")
        obj = record.get("object")
        if isinstance(subj, str) and subj not in by_id:
            errors.append(ValidationError(
                rule="relations.subject-not-found",
                severity="error",
                file=file,
                message=(
                    f"relation subject URI '{subj}' does not resolve to any "
                    "record in the corpus. Either add the missing entity or "
                    "correct the URI."
                ),
                pointer="/subject",
            ))
            # Alias rule emitted alongside so VALIDATION.md's
            # `relations.broken-subject` greppable contract is also satisfied.
            errors.append(ValidationError(
                rule="relations.broken-subject",
                severity="error",
                file=file,
                message=(
                    f"relation subject URI '{subj}' is broken (alias of "
                    "relations.subject-not-found)."
                ),
                pointer="/subject",
            ))
        if isinstance(obj, str) and obj not in by_id:
            errors.append(ValidationError(
                rule="relations.object-not-found",
                severity="error",
                file=file,
                message=(
                    f"relation object URI '{obj}' does not resolve to any "
                    "record in the corpus. Either add the missing entity or "
                    "correct the URI."
                ),
                pointer="/object",
            ))
            errors.append(ValidationError(
                rule="relations.broken-object",
                severity="error",
                file=file,
                message=(
                    f"relation object URI '{obj}' is broken (alias of "
                    "relations.object-not-found)."
                ),
                pointer="/object",
            ))

    # ---- B. supersession integrity (entity-level) ------------------------ #
    # Pitfall #6: a RegulationClause (or any entity carrying the lifecycle
    # status enum) with status=='superseded' must point at a real active
    # replacement via superseded_by. The schema layer does not enforce this
    # conditional — only this validator does.
    status = record.get("status")
    if status == "superseded":
        sb = record.get("superseded_by")
        if not isinstance(sb, str) or sb.strip() == "":
            errors.append(ValidationError(
                rule="relations.supersession-incomplete",
                severity="error",
                file=file,
                message=(
                    "record has status='superseded' but no superseded_by URI; "
                    "Pitfall #6 supersession-chain integrity requires every "
                    "superseded record to point at its active replacement."
                ),
                pointer="/superseded_by",
            ))
        elif sb not in by_id:
            errors.append(ValidationError(
                rule="relations.supersession-target-not-found",
                severity="error",
                file=file,
                message=(
                    f"superseded_by='{sb}' does not resolve to any record in "
                    "the corpus. The supersession chain is broken — either "
                    "add the active replacement record or correct the URI."
                ),
                pointer="/superseded_by",
            ))

    return errors
