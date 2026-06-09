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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        .stApp {
            background: linear-gradient(135deg, #0f0f1e 0%, #15162b 50%, #0f0f1e 100%);
            color: #e0e0e0;
        }
        
        .block-container {
            width: 100%;
            max-width: 1120px !important;
            padding: 2rem 1rem 3rem !important;
            margin: 0 auto !important;
        }
        
        .main-wrapper {
            width: 100%;
            display: flex;
            justify-content: center;
            padding: 2.5rem 1rem;
        }
        
        .main-content {
            width: 100%;
            max-width: 1200px;
            padding: 0;
        }
        
        .css-18e3th9 { padding-top: 0 !important; }
        
        /* Header modern */
        .header-container {
            margin-bottom: 2.25rem;
            border-bottom: 1px solid rgba(233, 9, 20, 0.15);
            padding-bottom: 1.5rem;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.75rem;
        }
        
        .header-container h1 {
            color: #ff1e2d !important;
            font-size: clamp(2.35rem, 6vw, 4.4rem) !important;
            font-weight: 900 !important;
            letter-spacing: -1.5px;
            line-height: 1;
            margin-bottom: 0 !important;
        }
        
        .hero-text {
            color: #a8a8b8;
            font-size: clamp(1rem, 1.6vw, 1.1rem);
            font-weight: 300;
            letter-spacing: 0.3px;
            text-align: center;
            line-height: 1.7;
            margin: 0 auto !important;
            max-width: 680px;
        }

        .search-helper {
            color: #a8a8b8;
            text-align: center;
            font-size: 0.98rem;
            margin: 0 0 1rem 0;
        }

        div[data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.035);
            border: 1px solid rgba(233, 9, 20, 0.18);
            border-radius: 24px;
            padding: 1.15rem 1rem 0.35rem;
            backdrop-filter: blur(16px);
            margin-bottom: 2.5rem;
        }

        div[data-testid="stFormSubmitButton"] {
            max-width: 240px;
            margin: 0.35rem auto 0.2rem;
        }
        
        /* Tabs modern */
        .stTabs [data-baseweb="tab-list"] {
            border: 1px solid rgba(233, 9, 20, 0.12) !important;
            gap: 0.5rem !important;
            justify-content: center;
            width: fit-content;
            margin: 0 auto 2rem auto;
            background: rgba(255, 255, 255, 0.03);
            padding: 0.35rem !important;
            border-radius: 999px;
        }
        
        .stTabs [data-baseweb="tab-list"] button {
            color: #a0a0b0 !important;
            border-bottom: 3px solid transparent !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            padding: 0.8rem 1.25rem !important;
            transition: all 0.3s ease !important;
            border-radius: 999px !important;
        }
        
        .stTabs [data-baseweb="tab-list"] button:hover {
            color: #ff1e2d !important;
        }
        
        .stTabs [aria-selected="true"] {
            color: #ff1e2d !important;
            border-bottom: 3px solid transparent !important;
            background: rgba(255, 30, 45, 0.12) !important;
            box-shadow: 0 10px 26px rgba(255, 30, 45, 0.14) !important;
        }
        
        /* Search bar enhanced */
        .search-container {
            display: flex;
            gap: 1rem;
            margin-bottom: 2.5rem;
            align-items: flex-end;
            justify-content: center;
        }
        
        .stTextInput input {
            background-color: rgba(255, 255, 255, 0.08) !important;
            border: 1.5px solid rgba(233, 9, 20, 0.25) !important;
            border-radius: 12px !important;
            color: #e0e0e0 !important;
            font-size: 1rem !important;
            min-height: 3.35rem !important;
            padding: 0.95rem 1.2rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput input:focus {
            background-color: rgba(255, 255, 255, 0.12) !important;
            border-color: #ff1e2d !important;
            box-shadow: 0 0 20px rgba(255, 30, 45, 0.2) !important;
        }
        
        .stTextInput input::placeholder {
            color: #808090 !important;
        }
        
        /* Button primary (search) */
        .btn-search {
            background: linear-gradient(135deg, #ff1e2d 0%, #e50914 100%) !important;
            color: white !important;
            border-radius: 12px !important;
            padding: 0.95rem 2rem !important;
            font-weight: 700 !important;
            border: none !important;
            box-shadow: 0 8px 24px rgba(255, 30, 45, 0.3) !important;
            transition: all 0.3s ease !important;
            cursor: pointer !important;
        }
        
        .btn-search:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 32px rgba(255, 30, 45, 0.4) !important;
        }
        
        /* Card grid */
        .movies-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
            justify-content: center;
        }
        
        @media (max-width: 1024px) {
            .movies-grid { grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); }
        }
        
        @media (max-width: 768px) {
            .movies-grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem; }
        }
        
        @media (max-width: 480px) {
            .movies-grid { grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
        }
        
        /* Movie card */
        .movie-card {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(233, 9, 20, 0.15);
            border-radius: 14px;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            cursor: pointer;
            display: flex;
            flex-direction: column;
            height: 100%;
        }
        
        .movie-card:hover {
            border-color: rgba(255, 30, 45, 0.4);
            box-shadow: 0 12px 48px rgba(255, 30, 45, 0.15);
            transform: translateY(-6px);
            background: rgba(255, 255, 255, 0.06);
        }
        
        .movie-card-poster {
            width: 100%;
            aspect-ratio: 2/3;
            overflow: hidden;
            background: rgba(0, 0, 0, 0.4);
        }
        
        .movie-card-poster img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.4s ease;
        }
        
        .movie-card:hover .movie-card-poster img {
            transform: scale(1.05);
        }
        
        .movie-card-content {
            padding: 1rem;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }
        
        .movie-card-title {
            color: #f0f0f0;
            font-weight: 700;
            font-size: 0.95rem;
            line-height: 1.3;
            margin-bottom: 0.5rem;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
        
        .movie-card-meta {
            color: #909098;
            font-size: 0.8rem;
            margin-bottom: 0.75rem;
            line-height: 1.4;
        }
        
        .movie-card-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: auto;
        }
        
        .movie-card-actions button {
            flex: 1;
            padding: 0.6rem !important;
            font-size: 0.8rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            border: none !important;
        }
        
        .btn-details {
            background-color: #ff1e2d !important;
            color: white !important;
        }
        
        .btn-details:hover {
            background-color: #ff5559 !important;
            transform: translateY(-2px) !important;
        }
        
        .btn-fav {
            background-color: rgba(233, 9, 20, 0.3) !important;
            color: #ff1e2d !important;
            border: 1px solid rgba(255, 30, 45, 0.3) !important;
        }
        
        .btn-fav:hover {
            background-color: rgba(233, 9, 20, 0.5) !important;
            border-color: #ff1e2d !important;
        }
        
        .btn-watch {
            background-color: #f6c744 !important;
            color: #111 !important;
            font-weight: 700 !important;
            flex: 1.2;
            border: none !important;
        }
        
        .btn-watch:hover {
            background-color: #ffd93d !important;
        }
        
        /* Sections */
        .section-title {
            color: #ff1e2d;
            font-size: 1.6rem;
            font-weight: 800;
            margin: 2.5rem 0 0.5rem 0;
            letter-spacing: -0.5px;
            text-align: center;
        }
        
        .section-desc {
            color: #a0a0b0;
            font-size: 0.95rem;
            margin-bottom: 1.5rem;
            text-align: center;
        }
        
        /* Standard buttons */
        .stButton>button, div[data-testid="stFormSubmitButton"] > button {
            background-color: #ff1e2d !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0.8rem 1.2rem !important;
            font-weight: 700 !important;
            box-shadow: 0 8px 20px rgba(255, 30, 45, 0.3) !important;
            transition: all 0.3s ease !important;
            border: none !important;
            min-height: 3.1rem !important;
        }
        
        .stButton>button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #ff5559 !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 12px 28px rgba(255, 30, 45, 0.4) !important;
        }
        
        /* Selects */
        .stSelectbox, .stRadio {
            color: #e0e0e0 !important;
        }
        
        .stSelectbox, .stNumberInput {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(233, 9, 20, 0.2) !important;
            border-radius: 10px !important;
        }
        
        /* Other elements */
        .stAlert {
            border-radius: 12px !important;
            border-left: 4px solid #ff1e2d !important;
            background: rgba(255, 30, 45, 0.1) !important;
        }
        
        .stDivider {
            background-color: rgba(233, 9, 20, 0.15) !important;
        }
        
        .stImage {
            border-radius: 12px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        }
        
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            letter-spacing: -0.5px;
        }

        div[data-testid="stHorizontalBlock"] {
            align-items: stretch;
        }

        @media (max-width: 768px) {
            .block-container {
                padding: 1rem 0.85rem 2rem !important;
            }

            .header-container {
                margin-bottom: 1.75rem;
                padding-bottom: 1.15rem;
            }

            .hero-text {
                max-width: 100%;
                line-height: 1.55;
            }

            .search-helper {
                font-size: 0.92rem;
            }

            div[data-testid="stForm"] {
                border-radius: 20px;
                padding: 0.9rem 0.85rem 0.2rem;
            }

            div[data-testid="stFormSubmitButton"] {
                max-width: 100%;
            }

            .stTabs [data-baseweb="tab-list"] {
                width: 100%;
                gap: 0.35rem !important;
                padding: 0.35rem !important;
                border-radius: 20px;
            }

            .stTabs [data-baseweb="tab-list"] button {
                flex: 1 1 0;
                justify-content: center;
                padding: 0.8rem 0.75rem !important;
                font-size: 0.95rem !important;
            }

            .section-title {
                font-size: 1.4rem;
                margin-top: 2rem;
            }

            div[data-testid="stHorizontalBlock"] {
                flex-wrap: wrap;
                gap: 0.75rem;
            }

            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                min-width: 100% !important;
                flex: 1 1 100% !important;
            }
        }

        @media (max-width: 480px) {
            .header-container h1 {
                font-size: 2rem !important;
            }

            .stTextInput input {
                font-size: 0.96rem !important;
            }

            .stTabs [data-baseweb="tab-list"] button {
                font-size: 0.9rem !important;
            }
        }
        
        #MainMenu, header, footer, button[title="Open the menu"], button[title="Open details"] {
            visibility: hidden !important;
            display: none !important;
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
    st.markdown('<h3 class="section-title">🔥 Tendances</h3>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Découvrez les films et séries les plus populaires du moment.</p>', unsafe_allow_html=True)

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

    tabs = st.tabs(["🎬 Films tendance", "📺 Séries tendance"])
    with tabs[0]:
        movies = fetch_trending_titles(client, trending_movies, "movie")
        render_movies_grid(movies, client, context="trending_movie")
    with tabs[1]:
        series = fetch_trending_titles(client, trending_series, "series")
        render_movies_grid(series, client, context="trending_serie")


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


def render_movies_grid(movies: list[dict[str, Any]], client: OmdbClient, context: str = "") -> None:
    """Affiche les films en grid responsive."""
    if not movies:
        st.info("Aucun film à afficher.")
        return
    
    cols_per_row = 4
    for i in range(0, len(movies), cols_per_row):
        cols = st.columns(cols_per_row)
        for col_idx, col in enumerate(cols):
            movie_idx = i + col_idx
            if movie_idx < len(movies):
                movie = movies[movie_idx]
                with col:
                    render_movie_grid_card(movie, client, context=f"{context}_{movie_idx}")


def render_movie_grid_card(movie: dict[str, Any], client: OmdbClient, context: str = "") -> None:
    """Carte film compacte pour grid."""
    title = movie.get("Title", "Titre inconnu")
    year = movie.get("Year", "N/A")
    media_type = movie.get("Type", "N/A")
    imdb_id = movie.get("imdbID", "")
    poster = poster_url(movie)
    
    key_suffix = f"_{context}" if context else ""
    fav_key = f"fav_{imdb_id}{key_suffix}"
    details_key = f"details_{imdb_id}{key_suffix}"
    playimdb_url = f"https://www.playimdb.com/pt/title/{imdb_id}/" if imdb_id else ""
    
    # Conteneur de la carte
    card_html = f"""
    <div class="movie-card">
        <div class="movie-card-poster">
            {f'<img src="{poster}" alt="{title}">' if poster else '<div style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;background:#222;color:#888;">Pas d\'affiche</div>'}
        </div>
        <div class="movie-card-content">
            <div class="movie-card-title">{title}</div>
            <div class="movie-card-meta">
                {year} • {media_type}
            </div>
            <div class="movie-card-actions">
    """
    
    st.markdown(card_html, unsafe_allow_html=True)
    
    # Boutons
    action_col1, action_col2, action_col3 = st.columns([1, 1.2, 1])
    
    with action_col1:
        if st.button("📋", key=f"details_small_{details_key}", help="Détails", use_container_width=True):
            st.session_state["selected_imdb_id"] = imdb_id
            st.session_state["current_page"] = "details"
            st.rerun()
    
    with action_col2:
        if imdb_id:
            st.markdown(
                f'<a href="{playimdb_url}" target="_blank" style="display:block;padding:0.55rem;background-color:#f6c744;color:#111;text-decoration:none;border-radius:8px;text-align:center;font-weight:600;font-size:0.8rem;">🎬 Regarder</a>',
                unsafe_allow_html=True,
            )
    
    with action_col3:
        if st.button("⭐", key=f"fav_small_{fav_key}", help="Favoris", use_container_width=True):
            added = add_favorite(movie)
            if added:
                st.toast("✅ Ajouté aux favoris!")
            else:
                st.toast("⚠️ Déjà dans les favoris.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)


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
            # Sélecteur de saison
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
                    
                    # Sélecteur d'épisode
                    episode_options = [f"E{ep.get('Episode', '?').zfill(2)}: {ep.get('Title', 'Sans titre')}" for ep in episodes]
                    selected_ep_idx = st.selectbox(
                        "Choisir un épisode",
                        range(len(episodes)),
                        format_func=lambda x: episode_options[x],
                        key=f"episode_select_s{season_num}"
                    )
                    
                    # Afficher les détails de l'épisode sélectionné
                    episode = episodes[selected_ep_idx]
                    ep_num = episode.get("Episode", "?")
                    ep_title = episode.get('Title', 'Sans titre')
                    ep_rating = episode.get('imdbRating', 'N/A')
                    ep_date = episode.get('Released', 'N/A')
                    ep_plot = episode.get("Plot", "Aucun résumé.")
                    
                    st.divider()
                    
                    # Header de l'épisode
                    ep_col1, ep_col2, ep_col3 = st.columns([2, 1, 1])
                    with ep_col1:
                        st.markdown(f"#### 📺 Épisode {ep_num}: {ep_title}")
                    with ep_col2:
                        st.metric("Note IMDb", ep_rating)
                    with ep_col3:
                        st.metric("Date", ep_date)
                    
                    # Résumé
                    st.markdown("**Résumé :**")
                    st.write(ep_plot)
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
    st.markdown('<h3 class="section-title">⭐ Mes favoris</h3>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Retrouvez ici votre sélection enregistrée.</p>', unsafe_allow_html=True)
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
    st.markdown(
        """
        <div class="header-container">
            <h1>🎬 Movie Explorer</h1>
            <p class="hero-text">Découvrez films, séries et animations du monde entier.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_search, tab_favorites = st.tabs(["🔍 Recherche", "⭐ Favoris"])

    with tab_search:
        st.markdown(
            '<p class="search-helper">Recherchez un titre et retrouvez rapidement où le consulter.</p>',
            unsafe_allow_html=True,
        )

        with st.form("search_form", clear_on_submit=False):
            query = st.text_input(
                "Recherche",
                value=st.session_state["search_query"],
                placeholder="Exemple : Avatar, Breaking Bad, One Piece...",
                key="search_input",
                label_visibility="collapsed",
            )
            search_clicked = st.form_submit_button(
                "Rechercher",
                type="primary",
                use_container_width=True,
            )

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
                    render_movies_grid(movies, client, context=f"search_page{page}")

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
