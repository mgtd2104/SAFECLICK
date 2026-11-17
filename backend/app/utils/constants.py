"""Shared constants for the SafeClick API."""

# Per-field character limits. Kept in sync with ui/api_client.MAX_INPUT_CHARS.
MAX_TEXT_CHARS = 10_000
MAX_URL_CHARS = 10_000

# Raw request-body limit, enforced before the body is parsed. Generous enough to
# hold both max-length fields even when JSON escaping expands non-ASCII input.
MAX_REQUEST_BYTES = 262_144  # 256 KiB

# Reported in the response metadata; bump when the rule set changes.
DETECTOR_VERSION = "stage4-rules-v1"

# Category boundaries (inclusive lower bound). Boundary ties go to the higher category.
CATEGORY_BOUNDARIES = ((75, "critical"), (50, "high"), (25, "medium"), (0, "low"))

# Optional AI assistance: the most a single AI signal may add to the rule-based
# score. AI can only raise the score, never lower it.
AI_MAX_ADDITION = 20
AI_TIMEOUT_SECONDS = 20
