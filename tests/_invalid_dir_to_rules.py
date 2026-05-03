"""Mapping of invalid-fixture directory name → expected primary rule(s).

Sourced from ``tests/fixtures/invalid/README.md``. Each entry is the set of
rules that MUST fire for any YAML record under that subdirectory. Extra rules
are tolerated (some fixtures intentionally dual-fire — see README "Notes").

Wave-3 pytest (plan 03-05) imports this map and parametrises one test case per
fixture file.

The keys here are validated against the actual filesystem at collection time
(see ``test_validators.py::_gather_invalid_fixture_params``); a missing directory
or a directory without a mapping fails LOUDLY rather than silently passing.
"""
from __future__ import annotations


# Confirmed rule names emitted by the Wave-2 validators (verified against
# scripts/validators/{schema,ids,provenance,relations,links}.py at HEAD 34bd237):
#
#   schema                                    (schema.py)
#   ids.uri-format                            (ids.py)
#   ids.type-prefix-mismatch                  (ids.py)
#   provenance.h-darrieus                     (provenance.py)
#   provenance.pending-gate                   (provenance.py)
#   provenance.schema-version-mismatch        (provenance.py — note '-mismatch' suffix)
#   relations.subject-not-found               (relations.py)
#   relations.broken-subject                  (relations.py — alias of subject-not-found)
#   relations.object-not-found                (relations.py)
#   relations.broken-object                   (relations.py — alias of object-not-found)
#   relations.supersession-incomplete         (relations.py)
#   relations.supersession-target-not-found   (relations.py)
#   links.broken-source-ref                   (links.py)
#   links.source-not-document                 (links.py)
#   links.supersession-cycle                  (links.py)
INVALID_DIR_TO_RULES: dict[str, set[str]] = {
    "missing-provenance":          {"schema"},
    "missing-schema-version":      {"schema"},
    # bad-uri-format and bad-internal-id BOTH dual-fire schema + ids.uri-format
    # per README; we only assert the ids rule because the schema rule is a
    # passive consequence of the URI pattern, while the ids rule is the rule
    # we're actually exercising.
    "bad-uri-format":              {"ids.uri-format"},
    "bad-internal-id":             {"ids.uri-format"},
    "h-darrieus-rejected":         {"provenance.h-darrieus"},
    "h-darrieus-empty-reviewer":   {"provenance.h-darrieus"},
    "pending-not-hybrid-reviewed": {"provenance.pending-gate"},
    "broken-source-ref":           {"links.broken-source-ref"},
    "broken-relation-subject":     {"relations.subject-not-found"},
    "broken-relation-object":      {"relations.object-not-found"},
    # old-schema-version fires as a WARNING (severity=warning), not an error.
    # The mapping is "rule must fire" regardless of severity — Wave-3 collects
    # both error- and warning-severity rules into the comparison set.
    "old-schema-version":          {"provenance.schema-version-mismatch"},
    "empty-rationale":             {"schema"},
}
