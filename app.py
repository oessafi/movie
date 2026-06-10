from __future__ import annotations

from html import escape
import math
import os
from typing import Any
from urllib.parse import urlencode

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

from auth import auth_is_required, get_authenticated_user
from favorites import add_favorite, load_favorites, remove_favorite
from omdb_client import OmdbClient, OmdbError
from player_sources import clear_player_source, get_player_source, save_player_source

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
            background:
                radial-gradient(circle at top right, rgba(229, 9, 20, 0.26), transparent 26%),
                radial-gradient(circle at top left, rgba(255, 255, 255, 0.04), transparent 18%),
                linear-gradient(180deg, #140607 0%, #090909 20%, #070707 100%);
            color: #f5f5f1;
        }

        .block-container {
            width: 100%;
            max-width: 1320px !important;
            padding: 1rem 1.15rem 3rem !important;
            margin: 0 auto !important;
        }

        .netflix-nav {
            position: sticky;
            top: 0.85rem;
            z-index: 999;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1.5rem;
            padding: 1rem 1.2rem;
            border-radius: 24px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background:
                linear-gradient(90deg, rgba(12, 12, 12, 0.95) 0%, rgba(18, 18, 18, 0.88) 55%, rgba(34, 8, 11, 0.9) 100%);
            backdrop-filter: blur(18px);
            box-shadow: 0 24px 64px rgba(0, 0, 0, 0.32);
        }

        .netflix-nav-left {
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }

        .brand-wordmark {
            color: #e50914;
            font-size: clamp(1.55rem, 3vw, 2.2rem);
            font-weight: 900;
            letter-spacing: 0.18rem;
            line-height: 1;
        }

        .nav-mini {
            display: flex;
            flex-wrap: wrap;
            gap: 0.7rem;
            color: rgba(255, 255, 255, 0.72);
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.12rem;
        }

        .nav-mini span {
            padding: 0.28rem 0.6rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.06);
        }

        .auth-chip {
            min-width: 235px;
            padding: 0.8rem 1rem;
            border-radius: 18px;
            text-align: right;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .auth-chip span {
            display: block;
            color: rgba(255, 255, 255, 0.62);
            font-size: 0.74rem;
            letter-spacing: 0.12rem;
            text-transform: uppercase;
            margin-bottom: 0.25rem;
        }

        .auth-chip strong {
            color: #ffffff;
            font-size: 0.98rem;
            word-break: break-word;
        }

        .auth-chip--connected {
            border-color: rgba(76, 175, 80, 0.28);
            background: linear-gradient(135deg, rgba(17, 56, 28, 0.82), rgba(13, 24, 16, 0.92));
        }

        .auth-chip--guest {
            border-color: rgba(229, 9, 20, 0.22);
            background: linear-gradient(135deg, rgba(58, 15, 18, 0.8), rgba(19, 14, 15, 0.92));
        }

        .auth-chip--required {
            border-color: rgba(255, 193, 7, 0.26);
            background: linear-gradient(135deg, rgba(53, 39, 8, 0.82), rgba(22, 18, 10, 0.92));
        }

        .hero-banner {
            position: relative;
            overflow: hidden;
            margin: 0.5rem 0 1.8rem;
            padding: clamp(2rem, 4vw, 3rem);
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            background:
                linear-gradient(120deg, rgba(0, 0, 0, 0.92) 0%, rgba(14, 14, 14, 0.86) 44%, rgba(88, 0, 10, 0.62) 100%);
            box-shadow: 0 26px 80px rgba(0, 0, 0, 0.34);
        }

        .hero-banner::before,
        .hero-banner::after {
            content: "";
            position: absolute;
            border-radius: 999px;
            filter: blur(6px);
        }

        .hero-banner::before {
            width: 260px;
            height: 260px;
            right: -70px;
            top: -40px;
            background: radial-gradient(circle, rgba(229, 9, 20, 0.42) 0%, rgba(229, 9, 20, 0) 70%);
        }

        .hero-banner::after {
            width: 200px;
            height: 200px;
            right: 18%;
            bottom: -90px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0) 70%);
        }

        .hero-kicker {
            color: #b4b4b4;
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.2rem;
            text-transform: uppercase;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            max-width: 760px;
            color: #ffffff;
            font-size: clamp(2.45rem, 5.5vw, 4.8rem);
            line-height: 0.96;
            font-weight: 900;
            letter-spacing: -0.08rem;
            margin-bottom: 1rem;
        }

        .hero-copy {
            max-width: 690px;
            color: rgba(255, 255, 255, 0.78);
            font-size: 1.04rem;
            line-height: 1.7;
            margin-bottom: 1.25rem;
        }

        .hero-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
        }

        .hero-badges span {
            display: inline-flex;
            align-items: center;
            padding: 0.48rem 0.85rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #f8f8f8;
            font-size: 0.86rem;
            font-weight: 600;
        }

        .search-helper {
            color: rgba(255, 255, 255, 0.72);
            text-align: left;
            font-size: 1rem;
            margin: 0 0 0.9rem 0;
        }

        div[data-testid="stForm"] {
            background: linear-gradient(180deg, rgba(17, 17, 17, 0.88) 0%, rgba(12, 12, 12, 0.94) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 26px;
            padding: 1.15rem 1rem 0.4rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 18px 48px rgba(0, 0, 0, 0.24);
            margin-bottom: 2.1rem;
        }

        div[data-testid="stFormSubmitButton"] {
            max-width: 280px;
            margin: 0.35rem auto 0.2rem;
        }

        .stTabs [data-baseweb="tab-list"] {
            border: none !important;
            gap: 0.6rem !important;
            justify-content: flex-start;
            width: 100%;
            margin: 0 0 1.4rem 0;
            background: transparent;
            padding: 0 !important;
        }

        .stTabs [data-baseweb="tab-list"] button {
            min-height: 3rem;
            color: rgba(255, 255, 255, 0.72) !important;
            background: rgba(255, 255, 255, 0.04) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 999px !important;
            font-weight: 700 !important;
            font-size: 0.96rem !important;
            padding: 0.8rem 1.15rem !important;
            transition: all 0.25s ease !important;
        }

        .stTabs [data-baseweb="tab-list"] button:hover {
            color: #ffffff !important;
            border-color: rgba(229, 9, 20, 0.4) !important;
            background: rgba(229, 9, 20, 0.12) !important;
        }

        .stTabs [aria-selected="true"] {
            color: #ffffff !important;
            background: linear-gradient(135deg, rgba(229, 9, 20, 0.96), rgba(176, 6, 16, 0.98)) !important;
            box-shadow: 0 14px 28px rgba(229, 9, 20, 0.28) !important;
            border-color: transparent !important;
        }

        .stTextInput input,
        .stSelectbox [data-baseweb="select"] > div,
        .stNumberInput input {
            background-color: rgba(255, 255, 255, 0.06) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 14px !important;
            color: #f3f3f3 !important;
            font-size: 1rem !important;
            min-height: 3.25rem !important;
            padding: 0.9rem 1rem !important;
            transition: all 0.25s ease !important;
        }

        .stTextInput input:focus,
        .stSelectbox [data-baseweb="select"] > div:focus-within,
        .stNumberInput input:focus {
            border-color: rgba(229, 9, 20, 0.7) !important;
            box-shadow: 0 0 0 1px rgba(229, 9, 20, 0.16), 0 0 26px rgba(229, 9, 20, 0.18) !important;
            background-color: rgba(255, 255, 255, 0.08) !important;
        }

        .stTextInput input::placeholder {
            color: #8f8f8f !important;
        }

        .movie-card {
            background: linear-gradient(180deg, rgba(20, 20, 20, 0.95) 0%, rgba(10, 10, 10, 0.98) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            overflow: hidden;
            transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
            display: flex;
            flex-direction: column;
            height: 100%;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.22);
        }

        .movie-card:hover {
            border-color: rgba(229, 9, 20, 0.42);
            box-shadow: 0 24px 54px rgba(0, 0, 0, 0.36);
            transform: translateY(-7px) scale(1.01);
        }

        .movie-card-poster {
            position: relative;
            width: 100%;
            aspect-ratio: 2 / 3;
            overflow: hidden;
            background: #141414;
        }

        .movie-card-poster-link {
            display: block;
            width: 100%;
            height: 100%;
            color: inherit !important;
            text-decoration: none !important;
        }

        .movie-card-poster img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.3s ease;
        }

        .movie-card:hover .movie-card-poster img {
            transform: scale(1.06);
        }

        .movie-card:hover .poster-play-chip {
            transform: translateY(-2px);
            background: rgba(229, 9, 20, 0.94);
        }

        .movie-card-poster-fallback {
            position: relative;
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 1rem;
            color: #ffffff;
            overflow: hidden;
            isolation: isolate;
        }

        .movie-card-poster-fallback::before {
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, rgba(8, 8, 8, 0.04) 0%, rgba(8, 8, 8, 0.18) 28%, rgba(5, 5, 5, 0.88) 100%);
            z-index: -1;
        }

        .movie-card-poster-fallback::after {
            content: "";
            position: absolute;
            width: 210px;
            height: 210px;
            right: -48px;
            top: -58px;
            border-radius: 999px;
            background: radial-gradient(circle, rgba(255, 255, 255, 0.22) 0%, rgba(255, 255, 255, 0) 72%);
            z-index: -1;
        }

        .poster-topline {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.6rem;
        }

        .poster-kicker,
        .poster-type {
            display: inline-flex;
            align-items: center;
            min-height: 1.9rem;
            padding: 0.18rem 0.62rem;
            border-radius: 999px;
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.12rem;
            text-transform: uppercase;
            backdrop-filter: blur(10px);
        }

        .poster-kicker {
            background: rgba(0, 0, 0, 0.28);
            border: 1px solid rgba(255, 255, 255, 0.18);
        }

        .poster-type {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.12);
        }

        .poster-bottomline {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .poster-title {
            font-size: clamp(1.4rem, 2vw, 1.85rem);
            font-weight: 900;
            line-height: 0.98;
            letter-spacing: -0.04rem;
            text-wrap: balance;
        }

        .poster-meta {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            color: rgba(255, 255, 255, 0.82);
            font-size: 0.88rem;
            font-weight: 600;
        }

        .poster-watermark {
            position: absolute;
            right: 0.9rem;
            bottom: 0.55rem;
            color: rgba(255, 255, 255, 0.11);
            font-size: 3.6rem;
            font-weight: 900;
            letter-spacing: -0.12rem;
            line-height: 1;
            pointer-events: none;
            user-select: none;
        }

        .poster-play-chip {
            position: absolute;
            left: 0.9rem;
            bottom: 0.9rem;
            z-index: 3;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            padding: 0.48rem 0.78rem;
            border-radius: 999px;
            background: rgba(8, 8, 8, 0.78);
            border: 1px solid rgba(255, 255, 255, 0.14);
            color: #ffffff;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.01rem;
            backdrop-filter: blur(12px);
            transition: transform 0.22s ease, background 0.22s ease;
        }

        .movie-card-content {
            padding: 1rem;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
        }

        .movie-card-title {
            color: #f7f7f7;
            font-weight: 800;
            font-size: 1rem;
            line-height: 1.28;
            margin-bottom: 0.45rem;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }

        .movie-card-meta {
            color: rgba(255, 255, 255, 0.64);
            font-size: 0.82rem;
            margin-bottom: 0.85rem;
            line-height: 1.4;
        }

        .section-title {
            color: #ffffff;
            font-size: 1.85rem;
            font-weight: 900;
            margin: 2.4rem 0 0.45rem 0;
            letter-spacing: -0.04rem;
            text-align: left;
        }

        .section-desc {
            color: rgba(255, 255, 255, 0.66);
            font-size: 0.98rem;
            margin-bottom: 1.3rem;
            text-align: left;
        }

        .stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            background: linear-gradient(135deg, #e50914 0%, #b00610 100%) !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            padding: 0.82rem 1.12rem !important;
            font-weight: 800 !important;
            letter-spacing: 0.01rem;
            box-shadow: 0 14px 30px rgba(229, 9, 20, 0.22) !important;
            transition: transform 0.22s ease, box-shadow 0.22s ease, filter 0.22s ease !important;
            border: none !important;
            min-height: 3rem !important;
        }

        .stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 18px 34px rgba(229, 9, 20, 0.3) !important;
            filter: brightness(1.06);
        }

        .stAlert {
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            background: rgba(255, 255, 255, 0.05) !important;
            color: #f5f5f5 !important;
        }

        .stDivider {
            background-color: rgba(255, 255, 255, 0.08) !important;
        }

        .stImage img {
            border-radius: 14px;
            box-shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
        }

        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            letter-spacing: -0.03rem;
        }

        .stExpander {
            border-radius: 18px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            background: rgba(255, 255, 255, 0.03) !important;
        }

        div[data-testid="stHorizontalBlock"] {
            align-items: stretch;
        }

        @media (max-width: 900px) {
            .netflix-nav {
                flex-direction: column;
                align-items: flex-start;
            }

            .auth-chip {
                width: 100%;
                text-align: left;
            }

            .hero-banner {
                padding: 1.7rem;
            }
        }

        @media (max-width: 768px) {
            .block-container {
                padding: 0.85rem 0.8rem 2rem !important;
            }

            div[data-testid="stForm"] {
                border-radius: 22px;
                padding: 0.95rem 0.85rem 0.25rem;
            }

            div[data-testid="stFormSubmitButton"] {
                max-width: 100%;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.45rem !important;
                flex-wrap: wrap;
            }

            .stTabs [data-baseweb="tab-list"] button {
                flex: 1 1 auto;
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

        div[data-testid="stStatusWidget"],
        #MainMenu, header, footer, button[title="Open the menu"], button[title="Open details"] {
            visibility: hidden !important;
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _normalize_api_keys(raw_value: Any) -> list[str]:
    if isinstance(raw_value, str):
        return [key.strip() for key in raw_value.split(",") if key.strip()]
    if isinstance(raw_value, (list, tuple)):
        return [str(key).strip() for key in raw_value if str(key).strip()]
    return []


def get_api_keys() -> list[str]:
    """Read one or more API keys from Streamlit secrets, .env, or environment variables."""
    try:
        secret_multi = st.secrets.get("OMDB_API_KEYS", "")
        secret_single = st.secrets.get("OMDB_API_KEY", "")
    except Exception:
        secret_multi = ""
        secret_single = ""

    env_multi = os.getenv("OMDB_API_KEYS", "")
    env_single = os.getenv("OMDB_API_KEY", "")

    api_keys = [
        *_normalize_api_keys(secret_multi),
        *_normalize_api_keys(env_multi),
        *_normalize_api_keys(secret_single),
        *_normalize_api_keys(env_single),
    ]

    # Merge every configured source, then remove duplicates while keeping the original order.
    return list(dict.fromkeys(api_keys))


def _looks_like_vtt_url(url: str) -> bool:
    normalized_url = url.strip().lower().split("?", 1)[0].split("#", 1)[0]
    return normalized_url.endswith(".vtt")


def _set_navigation_query_params(page: str = "", imdb_id: str = "", autoplay: bool = False) -> None:
    params: dict[str, str] = {}
    if page and imdb_id:
        params["page"] = page
        params["imdb"] = imdb_id
        if autoplay:
            params["autoplay"] = "1"

    try:
        st.query_params.clear()
        for key, value in params.items():
            st.query_params[key] = value
    except Exception:
        st.experimental_set_query_params(**params)


def _read_navigation_query_param(name: str) -> str:
    try:
        value = st.query_params.get(name, "")
    except Exception:
        values = st.experimental_get_query_params().get(name, [])
        value = values[0] if values else ""

    if isinstance(value, list):
        value = value[0] if value else ""
    return str(value).strip()


def sync_navigation_state_from_query_params() -> None:
    page = _read_navigation_query_param("page")
    imdb_id = _read_navigation_query_param("imdb")
    autoplay = _read_navigation_query_param("autoplay")

    if page in {"details", "watch"} and imdb_id:
        st.session_state["selected_imdb_id"] = imdb_id
        st.session_state["current_page"] = page
        st.session_state["autoplay_requested"] = autoplay == "1" or page == "watch"


def build_watch_href(imdb_id: str) -> str:
    if not imdb_id:
        return "#"
    return f"?{urlencode({'page': 'watch', 'imdb': imdb_id, 'autoplay': '1'})}"


def open_movie_page(imdb_id: str, page: str, autoplay: bool | None = None) -> None:
    if not imdb_id:
        st.warning("Aucun identifiant IMDb disponible pour ce contenu.")
        return

    should_autoplay = page == "watch" if autoplay is None else autoplay
    st.session_state["selected_imdb_id"] = imdb_id
    st.session_state["current_page"] = page
    st.session_state["autoplay_requested"] = should_autoplay
    _set_navigation_query_params(page=page, imdb_id=imdb_id, autoplay=should_autoplay)
    st.rerun()


def render_navbar(authenticated_user: Any | None) -> None:
    if authenticated_user:
        chip_class = "auth-chip auth-chip--connected"
        chip_label = "Connexion"
        chip_value = escape(authenticated_user.user_id)
    elif auth_is_required():
        chip_class = "auth-chip auth-chip--required"
        chip_label = "Connexion"
        chip_value = "Se connecter via proxy"
    else:
        chip_class = "auth-chip auth-chip--guest"
        chip_label = "Connexion"
        chip_value = "Non connecte"

    st.markdown(
        f"""
        <div class="netflix-nav">
            <div class="netflix-nav-left">
                <div class="brand-wordmark">MOVIE EXPLORER</div>
                <div class="nav-mini">
                    <span>Accueil</span>
                    <span>Ma Liste</span>
                    <span>Lecture VTT</span>
                </div>
            </div>
            <div class="{chip_class}">
                <span>{chip_label}</span>
                <strong>{chip_value}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_home_hero() -> None:
    st.markdown(
        """
        <section class="hero-banner">
            <div class="hero-kicker">Streamline Your Movie Night</div>
            <h1 class="hero-title">Un look streaming, un lecteur intégré, une seule liste de favoris.</h1>
            <p class="hero-copy">
                Recherche rapide, lecture dans l'application, sous-titres WebVTT et ambiance rouge/noir
                inspirée des grandes plateformes de streaming.
            </p>
            <div class="hero-badges">
                <span>Films</span>
                <span>Séries</span>
                <span>Sous-titres .vtt</span>
                <span>Ma liste</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def poster_url(movie: dict[str, Any]) -> str | None:
    poster = movie.get("Poster")
    if poster and poster != "N/A":
        return poster
    return None


FALLBACK_TRENDING_BY_TYPE: dict[str, list[dict[str, str]]] = {
    "movie": [
        {"Title": "Avatar", "Year": "2009", "Type": "movie", "imdbID": "tt0499549", "Poster": "N/A"},
        {"Title": "Dune", "Year": "2021", "Type": "movie", "imdbID": "tt1160419", "Poster": "N/A"},
        {"Title": "Inception", "Year": "2010", "Type": "movie", "imdbID": "tt1375666", "Poster": "N/A"},
        {"Title": "The Dark Knight", "Year": "2008", "Type": "movie", "imdbID": "tt0468569", "Poster": "N/A"},
        {"Title": "Titanic", "Year": "1997", "Type": "movie", "imdbID": "tt0120338", "Poster": "N/A"},
    ],
    "series": [
        {"Title": "Stranger Things", "Year": "2016-", "Type": "series", "imdbID": "tt4574334", "Poster": "N/A"},
        {"Title": "House of the Dragon", "Year": "2022-", "Type": "series", "imdbID": "tt11198330", "Poster": "N/A"},
        {"Title": "The Witcher", "Year": "2019-", "Type": "series", "imdbID": "tt5180504", "Poster": "N/A"},
        {"Title": "One Piece", "Year": "2023-", "Type": "series", "imdbID": "tt11737520", "Poster": "N/A"},
        {"Title": "Squid Game", "Year": "2021-", "Type": "series", "imdbID": "tt10919420", "Poster": "N/A"},
    ],
}


def fetch_trending_titles(client: OmdbClient, titles: list[str], media_type: str) -> tuple[list[dict[str, Any]], str | None]:
    results: list[dict[str, Any]] = []
    first_error: str | None = None

    for title in titles:
        try:
            search_results = client.search_movies(title, page=1, media_type=media_type).get("Search", [])
            if search_results:
                results.append(search_results[0])
                continue

            # Fallback exact match: OMDb search can occasionally miss a title even when details exist.
            exact_match = client.get_by_exact_title(title)
            if exact_match:
                results.append(exact_match)
        except OmdbError as exc:
            if first_error is None:
                first_error = str(exc)

            lowered_error = str(exc).lower()
            if "cles api omdb configurees" in lowered_error or "cle api omdb manquante" in lowered_error:
                break

    return results, first_error


def fallback_trending_titles(media_type: str) -> list[dict[str, Any]]:
    return [dict(item) for item in FALLBACK_TRENDING_BY_TYPE.get(media_type, [])]


def should_use_local_search_fallback(error_message: str) -> bool:
    lowered_message = error_message.lower()
    return any(
        token in lowered_message
        for token in (
            "request limit reached",
            "invalid api key",
            "no api key provided",
            "toutes les cles api omdb configurees",
            "aucune cle api omdb valide",
            "cle api omdb manquante",
        )
    )


def fallback_search_results(query: str, media_type: str) -> list[dict[str, Any]]:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return []

    media_types = ("movie", "series") if media_type == "all" else (media_type,)
    matches: list[dict[str, Any]] = []

    for current_media_type in media_types:
        for item in FALLBACK_TRENDING_BY_TYPE.get(current_media_type, []):
            title = str(item.get("Title", "")).strip().lower()
            if normalized_query in title or title in normalized_query:
                matches.append(dict(item))

    return matches


POSTER_FALLBACK_BACKGROUNDS = (
    "linear-gradient(145deg, #28070d 0%, #a30e1e 46%, #09090c 100%)",
    "linear-gradient(145deg, #120b2d 0%, #2956c7 44%, #05070c 100%)",
    "linear-gradient(145deg, #201405 0%, #b96a09 48%, #090909 100%)",
    "linear-gradient(145deg, #06201d 0%, #0f8d76 45%, #050708 100%)",
    "linear-gradient(145deg, #2a0718 0%, #cf2c6d 42%, #0b0a0f 100%)",
)


def build_fallback_poster_markup(title: str, year: str, media_type: str, context: str = "") -> str:
    theme_index = sum(ord(char) for char in title) % len(POSTER_FALLBACK_BACKGROUNDS)
    background = POSTER_FALLBACK_BACKGROUNDS[theme_index]
    media_label = {
        "movie": "Film",
        "series": "Serie",
        "game": "Game",
    }.get(media_type.lower(), media_type.capitalize() or "Titre")
    kicker = "Tendance" if "trending" in context else "Selection"
    watermark = escape(title[:1].upper() or "M")

    return f"""
    <div class="movie-card-poster-fallback" style="background: {background};">
        <div class="poster-topline">
            <span class="poster-kicker">{escape(kicker)}</span>
            <span class="poster-type">{escape(media_label)}</span>
        </div>
        <div class="poster-bottomline">
            <div class="poster-title">{escape(title)}</div>
            <div class="poster-meta">{escape(year)}</div>
        </div>
        <div class="poster-watermark">{watermark}</div>
    </div>
    """


def render_trending_section(client: OmdbClient) -> None:
    st.markdown('<h3 class="section-title">En ce moment</h3>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Quelques titres forts pour remplir rapidement l\'écran d\'accueil.</p>', unsafe_allow_html=True)

    tabs = st.tabs(["🎬 Films tendance", "📺 Séries tendance"])
    with tabs[0]:
        render_movies_grid(fallback_trending_titles("movie"), client, context="trending_movie_fallback")
    with tabs[1]:
        render_movies_grid(fallback_trending_titles("series"), client, context="trending_serie_fallback")


def render_movie_card(
    movie: dict[str, Any],
    client: OmdbClient,
    context: str = "",
) -> None:
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
            watch_key = f"watch_{imdb_id}{key_suffix}"

            button_col_1, button_col_2, button_col_3 = st.columns([1, 1, 1])
            with button_col_1:
                if st.button("📋 Détails", key=details_key, use_container_width=True):
                    open_movie_page(imdb_id, "details")
            with button_col_2:
                if st.button("▶ Regarder", key=watch_key, use_container_width=True):
                    open_movie_page(imdb_id, "watch")
            with button_col_3:
                if st.button("⭐ Favoris", key=fav_key, use_container_width=True):
                    added = add_favorite(movie)
                    if added:
                        st.success("Ajouté aux favoris.")
                    else:
                        st.warning("Déjà dans la liste ou données incomplètes.")


def render_movies_grid(
    movies: list[dict[str, Any]],
    client: OmdbClient,
    context: str = "",
) -> None:
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


def render_movie_grid_card(
    movie: dict[str, Any],
    client: OmdbClient,
    context: str = "",
) -> None:
    """Carte film compacte pour grid."""
    title = movie.get("Title", "Titre inconnu")
    year = movie.get("Year", "N/A")
    media_type = movie.get("Type", "N/A")
    imdb_id = movie.get("imdbID", "")
    poster = poster_url(movie)
    watch_href = build_watch_href(imdb_id)
    
    key_suffix = f"_{context}" if context else ""
    fav_key = f"fav_{imdb_id}{key_suffix}"
    details_key = f"details_{imdb_id}{key_suffix}"
    
    # Conteneur de la carte
    card_html = f"""
    <div class="movie-card">
        <div class="movie-card-poster">
            <a class="movie-card-poster-link" href="{watch_href}">
                {f'<img src="{poster}" alt="{escape(title)}">' if poster else build_fallback_poster_markup(title, year, media_type, context)}
                <span class="poster-play-chip">▶ Lecture auto</span>
            </a>
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
            open_movie_page(imdb_id, "details")
    
    with action_col2:
        if st.button("▶", key=f"watch_small_{imdb_id}{key_suffix}", help="Regarder", use_container_width=True):
            open_movie_page(imdb_id, "watch")
    
    with action_col3:
        if st.button("⭐", key=f"fav_small_{fav_key}", help="Favoris", use_container_width=True):
            added = add_favorite(movie)
            if added:
                st.toast("✅ Ajouté à Ma liste")
            else:
                st.toast("⚠️ Déjà dans Ma liste.")
    
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_player_section(details: dict[str, Any], autoplay: bool = False) -> None:
    imdb_id = details.get("imdbID", "").strip()
    source = get_player_source(imdb_id) or {}
    current_video_url = source.get("video_url", "")
    current_subtitle_url = source.get("subtitle_url", "")
    current_subtitle_lang = source.get("subtitle_lang", "fr")
    current_subtitle_label = source.get("subtitle_label", "Français")

    st.subheader("▶ Lecteur vidéo")
    st.caption("Ajoute une URL vidéo directe lisible par le navigateur, puis un sous-titre WebVTT `.vtt` si nécessaire.")

    with st.expander("Configurer la vidéo et les sous-titres", expanded=not current_video_url):
        with st.form(f"player_source_form_{imdb_id}", clear_on_submit=False):
            video_url = st.text_input(
                "URL vidéo",
                value=current_video_url,
                placeholder="https://.../movie.mp4",
            )
            subtitle_url = st.text_input(
                "URL du sous-titre `.vtt`",
                value=current_subtitle_url,
                placeholder="https://.../subtitle-fr.vtt",
            )
            subtitle_col_1, subtitle_col_2 = st.columns(2)
            with subtitle_col_1:
                subtitle_lang = st.text_input("Code langue", value=current_subtitle_lang, placeholder="fr")
            with subtitle_col_2:
                subtitle_label = st.text_input("Libellé", value=current_subtitle_label, placeholder="Français")

            action_col_1, action_col_2 = st.columns(2)
            with action_col_1:
                save_clicked = st.form_submit_button(
                    "Enregistrer",
                    type="primary",
                    use_container_width=True,
                )
            with action_col_2:
                clear_clicked = st.form_submit_button(
                    "Supprimer la source",
                    use_container_width=True,
                )

        if save_clicked:
            if not video_url.strip():
                st.error("L'URL vidéo est obligatoire pour ouvrir le lecteur.")
            elif subtitle_url.strip() and not _looks_like_vtt_url(subtitle_url):
                st.error("Le sous-titre doit pointer vers un fichier `.vtt`.")
            else:
                save_player_source(
                    imdb_id=imdb_id,
                    video_url=video_url,
                    subtitle_url=subtitle_url,
                    subtitle_lang=subtitle_lang,
                    subtitle_label=subtitle_label,
                )
                st.success("Source vidéo enregistrée.")
                st.rerun()

        if clear_clicked:
            clear_player_source(imdb_id)
            st.success("Source supprimée.")
            st.rerun()

    if not current_video_url:
        st.warning("Aucune source vidéo n'est configurée pour ce titre.")
        st.info("Utilise une URL directe de type MP4/WebM accessible depuis le navigateur. Les sous-titres doivent être au format `.vtt`.")
        return

    subtitle_track = ""
    if current_subtitle_url:
        subtitle_track = (
            f'<track kind="subtitles" src="{escape(current_subtitle_url)}" '
            f'srclang="{escape(current_subtitle_lang)}" label="{escape(current_subtitle_label)}" default>'
        )

    poster = poster_url(details) or ""
    autoplay_attribute = "autoplay" if autoplay else ""
    video_markup = f"""
    <div style="background:rgba(255,255,255,0.03);padding:1rem;border-radius:18px;border:1px solid rgba(233,9,20,0.18);">
      <video id="movie-player" controls playsinline preload="metadata" crossorigin="anonymous" poster="{escape(poster)}" {autoplay_attribute}
        style="width:100%;border-radius:12px;background:#000;max-height:70vh;">
        <source src="{escape(current_video_url)}">
        {subtitle_track}
        Votre navigateur ne supporte pas la lecture vidéo HTML5.
      </video>
    </div>
    <script>
      const video = document.getElementById("movie-player");
      const enableSubtitles = () => {{
        if (!video || !video.textTracks) {{
          return;
        }}
        for (let index = 0; index < video.textTracks.length; index += 1) {{
          video.textTracks[index].mode = index === 0 ? "showing" : "disabled";
        }}
      }};

      const tryAutoplay = async () => {{
        if (!video || !{str(autoplay).lower()}) {{
          enableSubtitles();
          return;
        }}
        enableSubtitles();
        try {{
          await video.play();
        }} catch (error) {{
          video.muted = true;
          video.defaultMuted = true;
          try {{
            await video.play();
          }} catch (mutedError) {{
            console.debug("Autoplay blocked", mutedError);
          }}
        }}
      }};

      if (video) {{
        video.addEventListener("loadedmetadata", tryAutoplay, {{ once: true }});
        video.addEventListener("loadeddata", enableSubtitles, {{ once: true }});
        enableSubtitles();
        window.setTimeout(enableSubtitles, 300);
      }}
    </script>
    """
    components.html(video_markup, height=620, scrolling=False)

    if current_subtitle_url:
        st.caption("Si le sous-titre ne s'affiche pas, vérifie que le fichier `.vtt` et la vidéo autorisent le chargement cross-origin.")


def render_details(details: dict[str, Any], client: OmdbClient, show_watch_button: bool = True) -> None:
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

    imdb_id = details.get("imdbID", "")
    if show_watch_button and imdb_id:
        if st.button("▶ Ouvrir le lecteur", key=f"open_watch_{imdb_id}", use_container_width=False):
            open_movie_page(imdb_id, "watch")

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
    st.markdown('<h3 class="section-title">Ma liste</h3>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Une seule liste de favoris, affichée pareil en invité ou connecté.</p>', unsafe_allow_html=True)
    favorites = load_favorites()
    if not favorites:
        st.info("Aucun favori pour le moment.")
        return

    for movie in favorites:
        col_1, col_2, col_3, col_4, col_5 = st.columns([1, 3, 1, 1, 1])
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
                open_movie_page(imdb_id, "details")
        with col_4:
            if st.button("▶ Regarder", key=f"watch_{imdb_id}"):
                open_movie_page(imdb_id, "watch")
        with col_5:
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
    if "autoplay_requested" not in st.session_state:
        st.session_state["autoplay_requested"] = False

    sync_navigation_state_from_query_params()

    api_keys = get_api_keys()
    if not api_keys:
        st.error("Cle API manquante. Cree un fichier .env avec OMDB_API_KEYS=cle1,cle2 ou OMDB_API_KEY=ta_cle_api")
        st.stop()

    authenticated_user = get_authenticated_user()
    current_user_id = authenticated_user.user_id if authenticated_user else None

    if auth_is_required() and not current_user_id:
        st.error("Authentification requise. Aucun utilisateur de confiance n'a ete transmis a l'application.")
        st.info(
            "Place Streamlit derriere un proxy Keycloak et transmet un header utilisateur, par exemple "
            "`X-Auth-Request-Email` ou `X-Forwarded-User`."
        )
        st.stop()

    client = OmdbClient(api_keys=tuple(api_keys))
    render_navbar(authenticated_user)

    # PAGE: DETAILS
    if st.session_state["current_page"] == "details" and st.session_state["selected_imdb_id"]:
        if st.button("← Retour à la recherche", key="btn_back_to_search"):
            st.session_state["current_page"] = "search"
            st.session_state["selected_imdb_id"] = None
            st.session_state["autoplay_requested"] = False
            _set_navigation_query_params()
            st.rerun()
        
        try:
            details = client.get_details(st.session_state["selected_imdb_id"])
            render_details(details, client)
        except OmdbError as exc:
            st.error(str(exc))
        return

    # PAGE: WATCH
    if st.session_state["current_page"] == "watch" and st.session_state["selected_imdb_id"]:
        nav_col_1, nav_col_2 = st.columns(2)
        with nav_col_1:
            if st.button("← Retour aux détails", key="btn_back_to_details", use_container_width=True):
                open_movie_page(st.session_state["selected_imdb_id"], "details", autoplay=False)
        with nav_col_2:
            if st.button("⌂ Retour à la recherche", key="btn_back_to_search_from_watch", use_container_width=True):
                st.session_state["current_page"] = "search"
                st.session_state["selected_imdb_id"] = None
                st.session_state["autoplay_requested"] = False
                _set_navigation_query_params()
                st.rerun()

        try:
            details = client.get_details(st.session_state["selected_imdb_id"])
            render_player_section(details, autoplay=st.session_state.get("autoplay_requested", False))
            render_details(details, client, show_watch_button=False)
        except OmdbError as exc:
            st.error(str(exc))
        return

    # PAGE: SEARCH & FAVORITES
    render_home_hero()

    tab_search, tab_favorites = st.tabs(["Accueil", "Ma liste"])

    with tab_search:
        st.markdown(
            '<p class="search-helper">Cherche un titre, ouvre ses détails, puis lance la lecture intégrée avec sous-titres.</p>',
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
                error_message = str(exc)
                if should_use_local_search_fallback(error_message):
                    fallback_movies = fallback_search_results(query, media_type)
                    st.warning(
                        "OMDb est indisponible pour le moment. Affichage d'une recherche locale de secours."
                    )
                    st.caption(f"Détail OMDb: {error_message}")

                    if fallback_movies:
                        render_movies_grid(fallback_movies, client, context=f"local_search_{page}")
                    else:
                        st.info("Aucun titre local ne correspond à cette recherche.")
                else:
                    st.error(f"Erreur de recherche: {error_message}")
        
        # Sinon, afficher les tendances
        else:
            render_trending_section(client)

    with tab_favorites:
        render_favorites(client)


if __name__ == "__main__":
    main()
