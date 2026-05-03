"""ids validator — Wave-1 stub.

Wave-2 plan 03-03 will fill this in: enforces URI form
``aviationkb://<type>/<slug>@<version>`` per D-23 and internal-id form
``<type-prefix>:<kebab-slug>`` per D-24/D-25.

Returning [] is the green-path Wave-1 stub so plan 03-01 fixtures pass the
master CLI even before Wave-2 lands.
"""
from pathlib import Path
from typing import Any

from .errors import ValidationError


def validate_record(path: Path, record: Any, **ctx) -> list[ValidationError]:
    return []
