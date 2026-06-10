"""Local JSON storage for playback sources and subtitle tracks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PLAYER_SOURCES_FILE = Path("player_sources.json")


def _sanitize_source(source: dict[str, Any]) -> dict[str, str]:
    return {
        "video_url": str(source.get("video_url", "")).strip(),
        "subtitle_url": str(source.get("subtitle_url", "")).strip(),
        "subtitle_lang": str(source.get("subtitle_lang", "fr")).strip() or "fr",
        "subtitle_label": str(source.get("subtitle_label", "Français")).strip() or "Français",
    }


def _load_storage() -> dict[str, dict[str, str]]:
    if not PLAYER_SOURCES_FILE.exists():
        return {}

    try:
        data = json.loads(PLAYER_SOURCES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if not isinstance(data, dict):
        return {}

    storage: dict[str, dict[str, str]] = {}
    for raw_imdb_id, source in data.items():
        if isinstance(source, dict):
            storage[str(raw_imdb_id)] = _sanitize_source(source)
    return storage


def _save_storage(storage: dict[str, dict[str, str]]) -> None:
    PLAYER_SOURCES_FILE.write_text(
        json.dumps(storage, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_player_source(imdb_id: str) -> dict[str, str] | None:
    if not imdb_id.strip():
        return None
    return _load_storage().get(imdb_id.strip())


def save_player_source(
    imdb_id: str,
    video_url: str,
    subtitle_url: str = "",
    subtitle_lang: str = "fr",
    subtitle_label: str = "Français",
) -> None:
    normalized_imdb_id = imdb_id.strip()
    if not normalized_imdb_id:
        return

    storage = _load_storage()
    storage[normalized_imdb_id] = _sanitize_source(
        {
            "video_url": video_url,
            "subtitle_url": subtitle_url,
            "subtitle_lang": subtitle_lang,
            "subtitle_label": subtitle_label,
        }
    )
    _save_storage(storage)


def clear_player_source(imdb_id: str) -> None:
    normalized_imdb_id = imdb_id.strip()
    if not normalized_imdb_id:
        return

    storage = _load_storage()
    storage.pop(normalized_imdb_id, None)
    _save_storage(storage)
