from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from src.classifier import classify_with_llm
from src.config import load_config
from src.emailer import build_email, send_email
from src.feed_source import fetch_latest_post
from src.filtering import keyword_filter
from src.state import is_new_post, load_state, mark_seen, save_state


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def run() -> int:
    load_dotenv()

    config = load_config(os.environ.get("CONFIG_PATH", "config.yaml"))
    state_path = Path(os.environ.get("STATE_PATH", "data/state.json"))
    state = load_state(state_path)
    dry_run = env_bool("DRY_RUN", False)
    use_llm = env_bool("USE_LLM_CLASSIFIER", config.classification.enabled)

    sent_count = 0

    for account in config.accounts:
        try:
            post = fetch_latest_post(account.name, account.handle, account.feed_url)
        except Exception as exc:
            print(f"Could not fetch @{account.handle} from {account.feed_url}: {exc}")
            continue

        if post is None:
            print(f"No entries found for @{account.handle}.")
            continue

        if not is_new_post(state, account.handle, post.id):
            print(f"No new post for @{account.handle}.")
            continue

        filter_result = keyword_filter(
            post.text,
            any_terms=config.keywords.any_terms,
            required_any=config.keywords.required_any,
        )

        if not filter_result.matched:
            print(f"New post for @{account.handle}, but not relevant: {filter_result.reason}")
            state = mark_seen(state, account.handle, post.id)
            continue

        llm_reason = None
        if use_llm:
            classification = classify_with_llm(
                post.text,
                model=os.environ.get("OPENAI_MODEL", config.classification.model),
                minimum_confidence=config.classification.minimum_confidence,
            )
            llm_reason = f"{classification.reason} Confidence: {classification.confidence:.2f}"
            if not classification.relevant:
                print(f"LLM rejected @{account.handle} post: {llm_reason}")
                state = mark_seen(state, account.handle, post.id)
                continue

        message = build_email(post, filter_result.matched_terms, filter_result.reason, llm_reason)
        if dry_run:
            print(message)
        else:
            send_email(message)
            print(f"Sent alert for @{account.handle}: {post.url}")
        sent_count += 1
        state = mark_seen(state, account.handle, post.id)

    save_state(state_path, state)
    print(f"Done. Alerts sent: {sent_count}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
