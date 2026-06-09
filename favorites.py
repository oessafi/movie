"""Local JSON storage for favorite movies."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

FAVORITES_FILE = Path("favorites.json")


def load_favorites() -> list[dict[str, Any]]:
    if not FAVORITES_FILE.exists():
        return []
    try:
        data = json.loads(FAVORITES_FILE.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def save_favorites(favorites: list[dict[str, Any]]) -> None:
    FAVORITES_FILE.write_text(json.dumps(favorites, ensure_ascii=False, indent=2), encoding="utf-8")


def add_favorite(movie: dict[str, Any]) -> bool:
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


def remove_favorite(imdb_id: str) -> None:
    favorites = [item for item in load_favorites() if item.get("imdbID") != imdb_id]
    save_favorites(favorites)
