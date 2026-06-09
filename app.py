from __future__ import annotations

import math
import os
from typing import Any

import streamlit as st
from dotenv import load_dotenv
import requests

from favorites import add_favorite, load_favorites, remove_favorite
from omdb_client import OmdbClient, OmdbError

load_dotenv()

st.set_page_config(
    page_title="Movie Explorer",
    layout="wide",
)

def inject_app_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: radial-gradient(circle at top, #11141d 0%, #07090f 50%, #030405 100%);
            color: #f8f8f8;
        }
        .block-container {
            padding: 2rem 3rem 3rem;
            max-width: 1280px;
        }
        .css-18e3th9 { padding-top: 0rem; }
        .stButton>button {
            background-color: #e50914 !important;
            color: white !important;
            border-radius: 0.65rem !important;
            padding: 0.8rem 1rem !important;
            font-weight: 700 !important;
            box-shadow: 0 12px 24px rgba(233, 9, 20, 0.3) !important;
        }
        .stButton>button:hover {
            background-color: #ff121f !important;
        }
        section[data-testid="stSidebar"] {
            background: rgba(10, 12, 22, 0.98);
            border-radius: 1rem;
            padding: 1.25rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
        }
        .css-1d391kg, .css-16cd23f {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 1rem !important;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18) !important;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #f8f8f8;
        }
        .stMarkdown p, .stMarkdown span, .stText {
            color: #d8d8d8;
        }
        .stAlert {
            border-radius: 0.85rem;
        }
        #MainMenu, header, footer, button[title="Open the menu"], button[title="Open details"] {
            visibility: hidden !important;
            display: none !important;
        }
        .hero-text {
            font-size: 1.15rem;
            color: #c4c8d4;
            margin-top: -1rem;
            margin-bottom: 1.8rem;
        }
        .movie-card {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 1.1rem;
            padding: 1.2rem;
            margin-bottom: 1rem;
        }
        .stImage {
            border-radius: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_api_key() -> str:
    """Read API key from Streamlit secrets, .env, or environment variables."""
    try:
        return st.secrets.get("OMDB_API_KEY", "") or os.getenv("OMDB_API_KEY", "")
    except Exception:
        return os.getenv("OMDB_API_KEY", "")


def poster_url(movie: dict[str, Any]) -> str | None:
    poster = movie.get("Poster")
    if poster and poster != "N/A":
        return poster
    return None


def fetch_trending_titles(client: OmdbClient, titles: list[str], media_type: str) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for title in titles:
        try:
            search_results = client.search_movies(title, page=1, media_type=media_type).get("Search", [])
            if search_results:
                results.append(search_results[0])
        except OmdbError:
            continue
    return results


def render_trending_section(client: OmdbClient) -> None:
    st.subheader("Tendances")
    st.write("Découvrez les films et séries les plus populaires du moment.")

    trending_movies = [
        "Avatar",
        "Dune",
        "Inception",
        "The Dark Knight",
        "Titanic",
    ]
    trending_series = [
        "Stranger Things",
        "House of the Dragon",
        "The Witcher",
        "One Piece",
        "Squid Game",
    ]

    tabs = st.tabs(["Films tendance", "Séries tendance"])
    with tabs[0]:
        movies = fetch_trending_titles(client, trending_movies, "movie")
        for movie in movies:
            render_movie_card(movie, client)
    with tabs[1]:
        series = fetch_trending_titles(client, trending_series, "series")
        for serie in series:
            render_movie_card(serie, client)


def render_movie_card(movie: dict[str, Any], client: OmdbClient) -> None:
    with st.container(border=True):
        col_img, col_info = st.columns([1, 3])

        with col_img:
            poster = poster_url(movie)
            if poster:
                st.image(poster, use_container_width=True)
            else:
                st.info("Aucune affiche")

        with col_info:
            title = movie.get("Title", "Titre inconnu")
            year = movie.get("Year", "N/A")
            media_type = movie.get("Type", "N/A")
            imdb_id = movie.get("imdbID", "")

            st.subheader(f"{title} ({year})")
            st.caption(f"Type: {media_type} | IMDb ID: {imdb_id}")

            fav_key = f"fav_{imdb_id}"
            playimdb_url = f"https://www.playimdb.com/pt/title/{imdb_id}/" if imdb_id else ""

            button_col_1, button_col_2 = st.columns([1, 1])
            with button_col_1:
                if imdb_id:
                    st.markdown(
                        f'<a href="{playimdb_url}" target="_blank" style="display:inline-block;padding:0.5rem 1rem;background-color:#f6c744;color:#111;text-decoration:none;border-radius:0.35rem;">Voir le film</a>',
                        unsafe_allow_html=True,
                    )
            with button_col_2:
                if st.button("Ajouter aux favoris", key=fav_key, use_container_width=True):
                    added = add_favorite(movie)
                    if added:
                        st.success("Ajouté aux favoris.")
                    else:
                        st.warning("Déjà dans les favoris ou données incomplètes.")


def render_details(details: dict[str, Any]) -> None:
    st.divider()
    st.header(details.get("Title", "Détails"))

    col_img, col_data = st.columns([1, 2])
    with col_img:
        poster = poster_url(details)
        if poster:
            st.image(poster, use_container_width=True)

    with col_data:
        st.markdown(f"**Année :** {details.get('Year', 'N/A')}")
        st.markdown(f"**Genre :** {details.get('Genre', 'N/A')}")
        st.markdown(f"**Durée :** {details.get('Runtime', 'N/A')}")
        st.markdown(f"**Réalisateur :** {details.get('Director', 'N/A')}")
        st.markdown(f"**Acteurs :** {details.get('Actors', 'N/A')}")
        st.markdown(f"**Langue :** {details.get('Language', 'N/A')}")
        st.markdown(f"**Pays :** {details.get('Country', 'N/A')}")
        st.markdown(f"**IMDb rating :** {details.get('imdbRating', 'N/A')}")

    st.subheader("Résumé")
    st.write(details.get("Plot", "Aucun résumé disponible."))

    # Lien direct pour regarder le film
    imdb_id = details.get("imdbID", "")
    if imdb_id:
        playimdb_url = f"https://www.playimdb.com/pt/title/{imdb_id}/"
        st.markdown(
            f'<a href="{playimdb_url}" target="_blank" style="display:inline-block;padding:0.5rem 1rem;background-color:#f6c744;color:#111;text-decoration:none;border-radius:0.35rem;">Voir le film</a>',
            unsafe_allow_html=True,
        )

    ratings = details.get("Ratings", [])
    if ratings:
        st.subheader("Notes")
        st.table(ratings)


def render_favorites() -> None:
    st.header("⭐ Mes favoris")
    favorites = load_favorites()
    if not favorites:
        st.info("Aucun favori pour le moment.")
        return

    for movie in favorites:
        col_1, col_2, col_3 = st.columns([1, 4, 1])
        with col_1:
            poster = poster_url(movie)
            if poster:
                st.image(poster, width=80)
        with col_2:
            st.markdown(f"**{movie.get('Title', 'Sans titre')}**")
            st.caption(f"{movie.get('Year', 'N/A')} | {movie.get('Type', 'N/A')} | {movie.get('imdbID', '')}")
        with col_3:
            if st.button("Supprimer", key=f"remove_{movie.get('imdbID')}"):
                remove_favorite(movie.get("imdbID", ""))
                st.rerun()
        st.divider()


def main() -> None:
    inject_app_styles()
    st.title("Movie Explorer")
    st.markdown('<div class="hero-text">Toutes les origines cinéma, séries et animation réunies en un seul endroit.</div>', unsafe_allow_html=True)

    api_key = get_api_key()
    if not api_key:
        st.error("Clé API manquante. Crée un fichier .env avec OMDB_API_KEY=ta_cle_api")
        st.stop()

    client = OmdbClient(api_key=api_key)

    tab_search, tab_favorites = st.tabs(["Recherche", "Favoris"])

    with tab_search:
        if "search_query" not in st.session_state:
            st.session_state["search_query"] = ""
        if "search_page" not in st.session_state:
            st.session_state["search_page"] = 1
        if "search_media_type" not in st.session_state:
            st.session_state["search_media_type"] = "movie"

        top_col1, top_col2, top_col3 = st.columns([4, 3, 1])
        with top_col1:
            query = st.text_input(
                "Titre à rechercher",
                value=st.session_state["search_query"],
                placeholder="Exemple : Avatar, Batman, Inception...",
            )
        with top_col2:
            media_type = st.radio(
                "Type",
                options=["movie", "series", "game", "all"],
                index=["movie", "series", "game", "all"].index(st.session_state["search_media_type"]),
                horizontal=True,
            )
        with top_col3:
            search_clicked = st.button("Rechercher", type="primary", use_container_width=True)

        if search_clicked:
            st.session_state["search_query"] = query
            st.session_state["search_page"] = 1
            st.session_state["search_media_type"] = media_type

        render_trending_section(client)

        query = st.session_state["search_query"]
        media_type = st.session_state["search_media_type"]
        page = st.session_state["search_page"]

        if query.strip():
            try:
                results = client.search_movies(query, page=int(page), media_type=media_type)
                movies = results.get("Search", [])
                total_results = int(results.get("totalResults", 0))
                total_pages = max(1, math.ceil(total_results / 10))

                st.success(f"{total_results} résultat(s) trouvé(s). Page {page}/{total_pages}.")
                for movie in movies:
                    render_movie_card(movie, client)

                if total_pages > 1:
                    page_col1, page_col2, page_col3 = st.columns([1, 1, 1])
                    with page_col1:
                        if st.button("← Page précédente", disabled=page <= 1):
                            st.session_state["search_page"] = max(1, page - 1)
                            st.experimental_rerun()
                    with page_col2:
                        st.markdown(f"**Page {page} / {total_pages}**")
                    with page_col3:
                        if st.button("Page suivante →", disabled=page >= total_pages):
                            st.session_state["search_page"] = min(total_pages, page + 1)
                            st.experimental_rerun()

            except OmdbError as exc:
                st.error(str(exc))

        selected_imdb_id = st.session_state.get("selected_imdb_id")
        if selected_imdb_id:
            try:
                details = client.get_details(selected_imdb_id)
                render_details(details)
            except OmdbError as exc:
                st.error(str(exc))

    with tab_favorites:
        render_favorites()


if __name__ == "__main__":
    main()
