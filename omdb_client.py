"""Small OMDb API client used by the Streamlit app."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests


BASE_URL = "https://www.omdbapi.com/"


class OmdbError(Exception):
    """Raised when OMDb returns an error or the request fails."""


@dataclass(frozen=True)
class OmdbClient:
    api_key: str
    timeout: int = 15

    def _get(self, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_key:
            raise OmdbError("Clé API OMDb manquante. Ajoute OMDB_API_KEY dans .env ou dans les variables d'environnement.")

        query = {"apikey": self.api_key, **params}
        try:
            response = requests.get(BASE_URL, params=query, timeout=self.timeout)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise OmdbError(f"Impossible de contacter OMDb: {exc}") from exc

        data = response.json()
        if data.get("Response") == "False":
            raise OmdbError(data.get("Error", "Erreur OMDb inconnue."))
        return data

    def search_movies(self, title: str, page: int = 1, media_type: str = "movie") -> dict[str, Any]:
        """Search movies/series/games by title."""
        params: dict[str, Any] = {"s": title.strip(), "page": page}
        if media_type and media_type != "all":
            params["type"] = media_type
        return self._get(params)

    def get_details(self, imdb_id: str) -> dict[str, Any]:
        """Get full details by IMDb id."""
        return self._get({"i": imdb_id, "plot": "full"})

    def get_season(self, imdb_id: str, season: int) -> dict[str, Any]:
        """Get season data including episodes for a series."""
        return self._get({"i": imdb_id, "Season": season})

    def get_by_exact_title(self, title: str, year: str | None = None) -> dict[str, Any]:
        """Get one result by exact title. Useful for quick tests."""
        params: dict[str, Any] = {"t": title.strip(), "plot": "full"}
        if year:
            params["y"] = year
        return self._get(params)
