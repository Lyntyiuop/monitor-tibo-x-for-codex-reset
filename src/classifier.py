from __future__ import annotations

import json
import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class Classification:
    relevant: bool
    confidence: float
    reason: str


def classify_with_llm(text: str, model: str, minimum_confidence: float) -> Classification:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = (
        "Decide whether this public X post announces or strongly implies a Codex usage reset, "
        "Codex quota reset, usage restoration, or similar reset-related action. "
        "Return strict JSON with keys relevant_boolean, confidence_number, reason_string.\n\n"
        f"Post:\n{text}"
    )

    response = client.responses.create(
        model=model,
        input=prompt,
        text={"format": {"type": "json_object"}},
    )
    data = json.loads(response.output_text)
    confidence = float(data.get("confidence_number", 0))
    relevant = bool(data.get("relevant_boolean", False)) and confidence >= minimum_confidence
    return Classification(relevant, confidence, str(data.get("reason_string", "")))
