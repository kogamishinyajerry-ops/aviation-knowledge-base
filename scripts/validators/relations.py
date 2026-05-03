"""relations validator — Wave-1 stub.

Wave-2 plan 03-04 will fill this in: subject and object URIs must resolve in
the corpus index (``ctx['by_id']``), else emits relations.broken-subject /
relations.broken-object errors.

Returning [] is the green-path Wave-1 stub so plan 03-01 fixtures pass the
master CLI even before Wave-2 lands.
"""
from pathlib import Path
from typing import Any

from .errors import ValidationError


def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]:
    return []
