"""Small OMDb API client used by the Streamlit app."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import requests


BASE_URL = "https://www.omdbapi.com/"
RETRYABLE_API_ERRORS = (
    "request limit reached",
    "invalid api key",
    "no api key provided",
)


class OmdbError(Exception):
    """Raised when OMDb returns an error or the request fails."""


@dataclass
class OmdbClient:
    api_keys: tuple[str, ...]
    timeout: int = 15
    _active_key_index: int = field(default=0, init=False, repr=False)

    def __post_init__(self) -> None:
        self.api_keys = tuple(key.strip() for key in self.api_keys if key and key.strip())

    def _should_try_next_key(self, error_message: str) -> bool:
        lowered_message = error_message.lower()
        return any(token in lowered_message for token in RETRYABLE_API_ERRORS)

    def _request_with_key(self, api_key: str, params: dict[str, Any]) -> dict[str, Any]:
        query = {"apikey": api_key, **params}
        try:
            response = requests.get(BASE_URL, params=query, timeout=self.timeout)
        except requests.RequestException as exc:
            raise OmdbError(f"Impossible de contacter OMDb: {exc}") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise OmdbError(f"Reponse OMDb invalide ({response.status_code}).") from exc

        if response.status_code >= 400:
            raise OmdbError(data.get("Error", f"Erreur HTTP OMDb {response.status_code}."))

        if data.get("Response") == "False":
            raise OmdbError(data.get("Error", "Erreur OMDb inconnue."))
        return data

    def _get(self, params: dict[str, Any]) -> dict[str, Any]:
        if not self.api_keys:
            raise OmdbError(
                "Cle API OMDb manquante. Ajoute OMDB_API_KEYS ou OMDB_API_KEY dans .env ou dans les variables d'environnement."
            )

        last_error: OmdbError | None = None
        total_keys = len(self.api_keys)

        for offset in range(total_keys):
            key_index = (self._active_key_index + offset) % total_keys
            api_key = self.api_keys[key_index]

            try:
                data = self._request_with_key(api_key, params)
            except OmdbError as exc:
                last_error = exc
                if self._should_try_next_key(str(exc)) and offset < total_keys - 1:
                    continue
                if self._should_try_next_key(str(exc)) and total_keys > 1:
                    raise OmdbError("Toutes les cles API OMDb configurees sont epuisees ou invalides.") from exc
                raise

            self._active_key_index = key_index
            return data

        if last_error is not None:
            raise last_error
        raise OmdbError("Aucune cle API OMDb valide n'est configuree.")

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
