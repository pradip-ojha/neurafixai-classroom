from __future__ import annotations


PROMPT_INJECTION_PATTERNS = (
    "ignore previous instructions",
    "reveal the system prompt",
    "developer message",
    "hidden prompt",
    "bypass safety",
)


def evaluate_prompt_safety(prompt: str) -> dict:
    normalized = prompt.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if pattern in normalized:
            return {
                "flagged": True,
                "category": "prompt_injection",
                "severity": "high",
                "action": "blocked",
            }
    return {"flagged": False, "action": "allowed"}
