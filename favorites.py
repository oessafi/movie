"""Local JSON storage for favorite movies."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FAVORITES_FILE = Path("favorites.json")


def _normalize_favorites(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen_ids: set[str] = set()
    normalized: list[dict[str, Any]] = []

    for item in items:
        if not isinstance(item, dict):
            continue

        imdb_id = str(item.get("imdbID", "")).strip()
        if not imdb_id or imdb_id in seen_ids:
            continue

        seen_ids.add(imdb_id)
        normalized.append(
            {
                "Title": item.get("Title"),
                "Year": item.get("Year"),
                "Type": item.get("Type"),
                "imdbID": imdb_id,
                "Poster": item.get("Poster"),
            }
        )

    return normalized


def _load_storage() -> list[dict[str, Any]]:
    if not FAVORITES_FILE.exists():
        return []

    try:
        data = json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    if isinstance(data, list):
        return _normalize_favorites(data)

    if not isinstance(data, dict):
        return []

    merged_favorites: list[dict[str, Any]] = []
    for favorites in data.values():
        if isinstance(favorites, list):
            merged_favorites.extend(favorites)
    return _normalize_favorites(merged_favorites)


def _save_storage(storage: list[dict[str, Any]]) -> None:
    FAVORITES_FILE.write_text(
        json.dumps(_normalize_favorites(storage), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_favorites(user_id: str | None = None) -> list[dict[str, Any]]:
    return _load_storage()


def save_favorites(favorites: list[dict[str, Any]], user_id: str | None = None) -> None:
    _save_storage(favorites)


def add_favorite(movie: dict[str, Any], user_id: str | None = None) -> bool:
    favorites = load_favorites()
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
    save_favorites(favorites)
    return True


def remove_favorite(imdb_id: str, user_id: str | None = None) -> None:
    favorites = [item for item in load_favorites() if item.get("imdbID") != imdb_id]
    save_favorites(favorites)
