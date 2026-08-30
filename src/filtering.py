from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FilterResult:
    matched: bool
    matched_terms: list[str]
    reason: str


def normalize_text(text: str) -> str:
    return " ".join(text.lower().split())


def find_terms(text: str, terms: list[str]) -> list[str]:
    normalized = normalize_text(text)
    return [term for term in terms if normalize_text(term) in normalized]


def keyword_filter(text: str, any_terms: list[str], required_any: list[str]) -> FilterResult:
    matched_terms = find_terms(text, any_terms)
    required_matches = find_terms(text, required_any)

    if not matched_terms:
        return FilterResult(False, [], "No monitored keywords were found.")

    if required_any and not required_matches:
        return FilterResult(
            False,
            matched_terms,
            "Keywords were found, but none of the required context terms matched.",
        )

    return FilterResult(
        True,
        matched_terms,
        f"Matched monitored terms: {', '.join(matched_terms)}.",
    )
