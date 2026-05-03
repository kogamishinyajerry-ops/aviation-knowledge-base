"""ValidationError dataclass shared across all validator modules.

Every validator returns a list of `ValidationError` (possibly empty). The
master CLI (`scripts/validate.py`) aggregates them, prints via `.format()`,
and exits non-zero if any error has severity == "error".
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ValidationError:
    """Single validation finding produced by any validator module.

    Fields:
      rule:     dotted-path identifier, e.g. "schema",
                "ids.uri-format", "provenance.h-darrieus".
      severity: "error" or "warning". Only "error" causes non-zero exit.
      file:     repo-relative or absolute path of the offending YAML record.
      message:  human-readable description.
      pointer:  optional JSON Pointer into the record (e.g. "/provenance/method").
    """

    rule: str
    severity: str  # "error" | "warning"
    file: str
    message: str
    pointer: Optional[str] = None

    def format(self) -> str:
        loc = f"{self.file}{f' @ {self.pointer}' if self.pointer else ''}"
        return f"[{self.severity.upper()}][{self.rule}] {loc}: {self.message}"
