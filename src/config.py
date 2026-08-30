from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Account:
    name: str
    handle: str
    url_template: str

    @property
    def feed_url(self) -> str:
        rsshub_base_url = os.environ.get("RSSHUB_BASE_URL", "https://rsshub.app").rstrip("/")
        return self.url_template.format(handle=self.handle, rsshub_base_url=rsshub_base_url)


@dataclass(frozen=True)
class KeywordConfig:
    any_terms: list[str]
    required_any: list[str]


@dataclass(frozen=True)
class ClassifierConfig:
    enabled: bool
    model: str
    minimum_confidence: float


@dataclass(frozen=True)
class MonitorConfig:
    accounts: list[Account]
    keywords: KeywordConfig
    classification: ClassifierConfig


def load_config(path: str | Path) -> MonitorConfig:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    accounts = [
        Account(
            name=item["name"],
            handle=item["handle"],
            url_template=item["url_template"],
        )
        for item in raw["accounts"]
    ]

    keyword_raw: dict[str, Any] = raw.get("keywords", {})
    classifier_raw: dict[str, Any] = raw.get("classification", {})

    return MonitorConfig(
        accounts=accounts,
        keywords=KeywordConfig(
            any_terms=keyword_raw.get("any", []),
            required_any=keyword_raw.get("required_any", []),
        ),
        classification=ClassifierConfig(
            enabled=bool(classifier_raw.get("enabled", False)),
            model=classifier_raw.get("model", "gpt-5-mini"),
            minimum_confidence=float(classifier_raw.get("minimum_confidence", 0.7)),
        ),
    )
