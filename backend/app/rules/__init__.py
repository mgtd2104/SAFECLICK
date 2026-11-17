"""Detection rule data and a cached loader for the JSON rule files.

Rules live in data files rather than long if/else chains. The loader only ever
reads these read-only project files; it never reads submitted user content.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_RULES_DIR = Path(__file__).resolve().parent


@lru_cache(maxsize=None)
def load_rules(name: str) -> list | dict:
    """Load and cache a rule file, e.g. load_rules("text") -> text_rules.json."""
    return json.loads((_RULES_DIR / f"{name}_rules.json").read_text(encoding="utf-8"))
