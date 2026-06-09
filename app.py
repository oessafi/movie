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
    initial_sidebar_state="collapsed",
)

def inject_app_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #0f0f1e 0%, #1a1a2e 50%, #0f0f1e 100%);
            color: #f8f8f8;
        }
        .block-container {
            padding: 2rem 3rem 3rem;
            max-width: 1400px;
        }
        .css-18e3th9 { padding-top: 0rem; }
        
        .stButton>button {
            background-color: #e50914 !important;
            color: white !important;
            border-radius: 0.65rem !important;
            padding: 0.8rem 1rem !important;
            font-weight: 700 !important;
            box-shadow: 0 12px 24px rgba(233, 9, 20, 0.3) !important;
            transition: all 0.3s ease !important;
            border: none !important;
        }
        .stButton>button:hover {
            background-color: #ff121f !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 15px 30px rgba(233, 9, 20, 0.4) !important;
        }
        
        section[data-testid="stSidebar"] {
            background: rgba(10, 12, 22, 0.98);
            border-radius: 1rem;
            padding: 1.25rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
        }
        
        .css-1d391kg, .css-16cd23f {
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(233, 9, 20, 0.3) !important;
            border-radius: 1rem !important;
            box-shadow: 0 24px 60px rgba(0, 0, 0, 0.18) !important;
        }
        
        .stMarkdown h1 {
            color: #ff6b6b;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        
        .stMarkdown h2 {
            color: #ffd93d;
            font-size: 1.8rem;
            font-weight: 700;
            margin-top: 1.5rem;
        }
        
        .stMarkdown h3 {
            color: #f8f8f8;
            font-size: 1.4rem;
        }
        
        .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
            color: #d8d8d8;
        }
        
        .stMarkdown p, .stMarkdown span, .stText {
            color: #d8d8d8;
            line-height: 1.6;
        }
        
        .stAlert {
            border-radius: 0.85rem;
            border-left: 4px solid #e50914 !important;
        }
        
        #MainMenu, header, footer, button[title="Open the menu"], button[title="Open details"] {
            visibility: hidden !important;
            display: none !important;
        }
        
        .hero-text {
            font-size: 1.2rem;
            color: #ffd93d;
            margin-top: -0.5rem;
            margin-bottom: 2rem;
            font-weight: 300;
            letter-spacing: 0.5px;
        }
        
        .stImage {
            border-radius: 1rem;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        }
        
        .stTabs [data-baseweb="tab-list"] button {
            color: #d8d8d8 !important;
            border-bottom: 2px solid transparent !important;
            font-weight: 600 !important;
        }
        
        .stTabs [aria-selected="true"] {
            color: #e50914 !important;
            border-bottom: 2px solid #e50914 !important;
        }
        
        .stSelectbox, .stRadio {
            color: #f8f8f8 !important;
        }
        
        .stSelectbox, .stTextInput, .stNumberInput {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(233, 9, 20, 0.2) !important;
            border-radius: 0.5rem !important;
        }
        
        .stDivider {
            background-color: rgba(233, 9, 20, 0.2) !important;
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
        for idx, movie in enumerate(movies):
            render_movie_card(movie, client, context=f"trending_movie_{idx}")
    with tabs[1]:
        series = fetch_trending_titles(client, trending_series, "series")
        for idx, serie in enumerate(series):
            render_movie_card(serie, client, context=f"trending_serie_{idx}")


def render_movie_card(movie: dict[str, Any], client: OmdbClient, context: str = "") -> None:
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

            # Créer des clés uniques avec le contexte
            key_suffix = f"_{context}" if context else ""
            fav_key = f"fav_{imdb_id}{key_suffix}"
            details_key = f"details_{imdb_id}{key_suffix}"
            playimdb_url = f"https://www.playimdb.com/pt/title/{imdb_id}/" if imdb_id else ""

            button_col_1, button_col_2, button_col_3 = st.columns([1, 1, 1])
            with button_col_1:
                if st.button("📋 Détails", key=details_key, use_container_width=True):
                    st.session_state["selected_imdb_id"] = imdb_id
                    st.session_state["current_page"] = "details"
                    st.rerun()
            with button_col_2:
                if imdb_id:
                    st.markdown(
                        f'<a href="{playimdb_url}" target="_blank" style="display:inline-block;width:100%;padding:0.5rem 0.5rem;background-color:#f6c744;color:#111;text-decoration:none;border-radius:0.35rem;text-align:center;">🎬 Regarder</a>',
                        unsafe_allow_html=True,
                    )
            with button_col_3:
                if st.button("⭐ Favoris", key=fav_key, use_container_width=True):
                    added = add_favorite(movie)
                    if added:
                        st.success("Ajouté aux favoris.")
                    else:
                        st.warning("Déjà dans les favoris ou données incomplètes.")


def render_details(details: dict[str, Any], client: OmdbClient) -> None:
    st.divider()
    
    col_img, col_data = st.columns([1, 2])
    with col_img:
        poster = poster_url(details)
        if poster:
            st.image(poster, use_container_width=True)

    with col_data:
        title = details.get("Title", "Titre inconnu")
        media_type = details.get("Type", "N/A")
        st.header(f"{title}")
        st.caption(f"Type: {media_type}")
        
        st.markdown(f"**Année :** {details.get('Year', 'N/A')}")
        st.markdown(f"**Genre :** {details.get('Genre', 'N/A')}")
        
        if media_type.lower() == "series":
            st.markdown(f"**Saisons :** {details.get('totalSeasons', 'N/A')}")
            st.markdown(f"**Statut :** {details.get('Status', 'N/A')}")
        else:
            st.markdown(f"**Durée :** {details.get('Runtime', 'N/A')}")
        
        st.markdown(f"**Réalisateur :** {details.get('Director', 'N/A')}")
        st.markdown(f"**Acteurs :** {details.get('Actors', 'N/A')}")
        st.markdown(f"**Langue :** {details.get('Language', 'N/A')}")
        st.markdown(f"**Pays :** {details.get('Country', 'N/A')}")
        st.markdown(f"**IMDb rating :** {details.get('imdbRating', 'N/A')}")

    st.subheader("📖 Résumé")
    st.write(details.get("Plot", "Aucun résumé disponible."))

    # Lien direct pour regarder
    imdb_id = details.get("imdbID", "")
    if imdb_id:
        playimdb_url = f"https://www.playimdb.com/pt/title/{imdb_id}/"
        st.markdown(
            f'<a href="{playimdb_url}" target="_blank" style="display:inline-block;padding:0.7rem 1.5rem;background-color:#e50914;color:#fff;text-decoration:none;border-radius:0.5rem;font-weight:bold;font-size:1rem;">🎬 Regarder maintenant</a>',
            unsafe_allow_html=True,
        )

    ratings = details.get("Ratings", [])
    if ratings:
        st.subheader("⭐ Notes")
        st.table(ratings)
    
    # Gestion des saisons/épisodes pour les séries
    media_type = details.get("Type", "N/A").lower()
    if media_type == "series":
        st.subheader("📺 Saisons et Épisodes")
        
        total_seasons = int(details.get("totalSeasons", 0))
        if total_seasons > 0:
            season_num = st.selectbox(
                "Sélectionnez une saison",
                range(1, total_seasons + 1),
                format_func=lambda x: f"Saison {x}",
                key="season_select"
            )
            
            try:
                season_data = client.get_season(imdb_id, season_num)
                episodes = season_data.get("Episodes", [])
                
                if episodes:
                    season_title = season_data.get('Title', 'Titre')
                    st.markdown(f"### {season_title} - {len(episodes)} épisodes")
                    
                    for idx, episode in enumerate(episodes):
                        ep_num = episode.get("Episode", "?")
                        ep_title = episode.get('Title', 'Sans titre')
                        ep_rating = episode.get('imdbRating', 'N/A')
                        ep_date = episode.get('Released', 'N/A')
                        ep_plot = episode.get("Plot", "Aucun résumé.")
                        
                        with st.expander(f"📺 Épisode {ep_num}: {ep_title} ⭐ {ep_rating}", expanded=(idx == 0)):
                            col_ep1, col_ep2 = st.columns([1, 3])
                            with col_ep1:
                                st.metric("Épisode", ep_num)
                                st.metric("Note IMDb", ep_rating)
                            with col_ep2:
                                st.write(f"**Date:** {ep_date}")
                                st.write(f"**Résumé:**\n{ep_plot}")
                else:
                    st.info(f"Aucun épisode trouvé pour la saison {season_num}.")
            except OmdbError as exc:
                st.warning(f"Impossible de charger la saison {season_num}: {str(exc)}")


def fetch_season_data(client: OmdbClient, imdb_id: str, season: int) -> dict[str, Any] | None:
    """Helper to fetch season data safely."""
    try:
        return client.get_season(imdb_id, season)
    except OmdbError:
        return None


def render_favorites(client: OmdbClient) -> None:
    st.header("⭐ Mes favoris")
    favorites = load_favorites()
    if not favorites:
        st.info("Aucun favori pour le moment.")
        return

    for movie in favorites:
        col_1, col_2, col_3, col_4 = st.columns([1, 3, 1, 1])
        with col_1:
            poster = poster_url(movie)
            if poster:
                st.image(poster, width=80)
        with col_2:
            title = movie.get('Title', 'Sans titre')
            imdb_id = movie.get('imdbID', '')
            st.markdown(f"**{title}**")
            st.caption(f"{movie.get('Year', 'N/A')} | {movie.get('Type', 'N/A')}")
        with col_3:
            if st.button("📋 Détails", key=f"fav_details_{imdb_id}"):
                st.session_state["selected_imdb_id"] = imdb_id
                st.session_state["current_page"] = "details"
                st.rerun()
        with col_4:
            if st.button("❌ Supprimer", key=f"remove_{imdb_id}"):
                remove_favorite(imdb_id)
                st.rerun()
        st.divider()


def main() -> None:
    inject_app_styles()
    
    # Initialize session state
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "search"
    if "selected_imdb_id" not in st.session_state:
        st.session_state["selected_imdb_id"] = None
    if "search_query" not in st.session_state:
        st.session_state["search_query"] = ""
    if "search_page" not in st.session_state:
        st.session_state["search_page"] = 1
    if "search_media_type" not in st.session_state:
        st.session_state["search_media_type"] = "all"

    api_key = get_api_key()
    if not api_key:
        st.error("Clé API manquante. Crée un fichier .env avec OMDB_API_KEY=ta_cle_api")
        st.stop()

    client = OmdbClient(api_key=api_key)

    # PAGE: DETAILS
    if st.session_state["current_page"] == "details" and st.session_state["selected_imdb_id"]:
        if st.button("← Retour à la recherche", key="btn_back_to_search"):
            st.session_state["current_page"] = "search"
            st.session_state["selected_imdb_id"] = None
            st.rerun()
        
        try:
            details = client.get_details(st.session_state["selected_imdb_id"])
            render_details(details, client)
        except OmdbError as exc:
            st.error(str(exc))
        return

    # PAGE: SEARCH & FAVORITES
    st.title("🎬 Movie Explorer")
    st.markdown('<div class="hero-text">Découvrez films, séries et animations du monde entier.</div>', unsafe_allow_html=True)

    tab_search, tab_favorites = st.tabs(["🔍 Recherche", "⭐ Favoris"])

    with tab_search:
        top_col1, top_col2 = st.columns([4, 1])
        with top_col1:
            query = st.text_input(
                "Titre à rechercher",
                value=st.session_state["search_query"],
                placeholder="Exemple : Avatar, Breaking Bad, One Piece...",
                key="search_input"
            )
        with top_col2:
            search_clicked = st.button("Rechercher", type="primary", use_container_width=True, key="search_btn")

        if search_clicked:
            st.session_state["search_query"] = query
            st.session_state["search_page"] = 1
            st.session_state["search_media_type"] = "all"

        query = st.session_state["search_query"]
        media_type = st.session_state["search_media_type"]
        page = st.session_state["search_page"]

        # Si une recherche est active, afficher les résultats
        if query.strip():
            try:
                results = client.search_movies(query, page=int(page), media_type=media_type)
                movies = results.get("Search", [])
                total_results = int(results.get("totalResults", 0))
                total_pages = max(1, math.ceil(total_results / 10))

                st.success(f"✅ {total_results} résultat(s) trouvé(s). Page {page}/{total_pages}.")
                
                if movies:
                    for idx, movie in enumerate(movies):
                        render_movie_card(movie, client, context=f"search_page{page}_{idx}")

                    if total_pages > 1:
                        st.divider()
                        page_col1, page_col2, page_col3 = st.columns([1, 1, 1])
                        with page_col1:
                            if st.button("← Page précédente", disabled=page <= 1, key="btn_prev"):
                                st.session_state["search_page"] = max(1, page - 1)
                                st.rerun()
                        with page_col2:
                            st.markdown(f"**Page {page} / {total_pages}**")
                        with page_col3:
                            if st.button("Page suivante →", disabled=page >= total_pages, key="btn_next"):
                                st.session_state["search_page"] = min(total_pages, page + 1)
                                st.rerun()
                else:
                    st.info("Aucun résultat trouvé. Essayez une autre recherche.")

            except OmdbError as exc:
                st.error(f"Erreur de recherche: {str(exc)}")
        
        # Sinon, afficher les tendances
        else:
            render_trending_section(client)

    with tab_favorites:
        render_favorites(client)


if __name__ == "__main__":
    main()
