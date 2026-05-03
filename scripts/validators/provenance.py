"""provenance validator — Wave-1 stub.

Wave-2 plan 03-03 will fill this in: enforces the H-Darrieus REJECT rule
(method == ai_extracted AND confidence.score > 0.85 AND no reviewer),
the _pending promotion gate (any path under /_pending/ requires
method == hybrid_reviewed), and the schema_version warning per VER-03.

Returning [] is the green-path Wave-1 stub so plan 03-01 fixtures pass the
master CLI even before Wave-2 lands.
"""
from pathlib import Path
from typing import Any

from .errors import ValidationError


def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]:
    return []
