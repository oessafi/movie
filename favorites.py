"""Local JSON storage for favorite movies."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FAVORITES_FILE = Path("favorites.json")
DEFAULT_USER_ID = "__default__"


def _normalize_user_id(user_id: str | None) -> str:
    return user_id.strip() if user_id and user_id.strip() else DEFAULT_USER_ID


def _load_storage() -> dict[str, list[dict[str, Any]]]:
    if not FAVORITES_FILE.exists():
        return {}

    try:
        data = json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

    if isinstance(data, list):
        return {DEFAULT_USER_ID: data}

    if not isinstance(data, dict):
        return {}

    storage: dict[str, list[dict[str, Any]]] = {}
    for raw_user_id, favorites in data.items():
        if isinstance(favorites, list):
            storage[str(raw_user_id)] = favorites
    return storage


def _save_storage(storage: dict[str, list[dict[str, Any]]]) -> None:
    FAVORITES_FILE.write_text(json.dumps(storage, ensure_ascii=False, indent=2), encoding="utf-8")


def load_favorites(user_id: str | None = None) -> list[dict[str, Any]]:
    storage = _load_storage()
    return storage.get(_normalize_user_id(user_id), [])


def save_favorites(favorites: list[dict[str, Any]], user_id: str | None = None) -> None:
    storage = _load_storage()
    normalized_user_id = _normalize_user_id(user_id)

    if favorites:
        storage[normalized_user_id] = favorites
    else:
        storage.pop(normalized_user_id, None)

    _save_storage(storage)


def add_favorite(movie: dict[str, Any], user_id: str | None = None) -> bool:
    favorites = load_favorites(user_id=user_id)
    imdb_id = movie.get("imdbID")
    if not imdb_id:
        return False
    if any(item.get("imdbID") == imdb_id for item in favorites):
        return False

    favorites.append(
        {
            "Title": movie.get("Title"),
            "Year": movie.get("Year"),
            "Type": movie.get("Type"),
            "imdbID": imdb_id,
            "Poster": movie.get("Poster"),
        }
    )
    save_favorites(favorites, user_id=user_id)
    return True


def remove_favorite(imdb_id: str, user_id: str | None = None) -> None:
    favorites = [item for item in load_favorites(user_id=user_id) if item.get("imdbID") != imdb_id]
    save_favorites(favorites, user_id=user_id)
