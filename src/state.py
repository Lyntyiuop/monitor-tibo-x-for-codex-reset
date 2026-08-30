from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_state(path: str | Path) -> dict[str, Any]:
    state_path = Path(path)
    if not state_path.exists():
        return {}
    return json.loads(state_path.read_text(encoding="utf-8") or "{}")


def save_state(path: str | Path, state: dict[str, Any]) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def is_new_post(state: dict[str, Any], handle: str, post_id: str) -> bool:
    return state.get("accounts", {}).get(handle, {}).get("last_seen_post_id") != post_id


def mark_seen(state: dict[str, Any], handle: str, post_id: str) -> dict[str, Any]:
    next_state = dict(state)
    accounts = dict(next_state.get("accounts", {}))
    accounts[handle] = {"last_seen_post_id": post_id}
    next_state["accounts"] = accounts
    return next_state
