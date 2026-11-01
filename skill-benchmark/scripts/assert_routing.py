from __future__ import annotations
import json

EXPECTED = {
    "candidate-00": None,
    "candidate-01": "scientific-figure-design",
    "candidate-02": "scientific-visualization",
}


def get_assert(output: str, context):
    provider_text = json.dumps(context.get("provider", {}), default=str)
    label = next((x for x in EXPECTED if x in provider_text), None)
    metadata = context.get("metadata") or {}
    calls = metadata.get("skillCalls") or []
    names = {c.get("name") for c in calls if isinstance(c, dict)}
    expected = EXPECTED.get(label)
    if label is None:
        score, reason = 0.0, "provider label unavailable"
    elif expected is None:
        score = 1.0 if not names else 0.0
        reason = f"control skill calls={sorted(x for x in names if x)}"
    else:
        score = 1.0 if expected in names else 0.0
        reason = f"expected {expected}; observed={sorted(x for x in names if x)}"
    # Routing is diagnostic; never invalidate a scientifically valid artifact by itself.
    return {
        "pass": True,
        "score": score,
        "reason": reason,
        "namedScores": {"routing_accuracy": score},
    }
