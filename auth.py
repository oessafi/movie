"""Header-based authentication helpers for proxy-managed SSO setups."""
from __future__ import annotations

import os
from dataclasses import dataclass

import streamlit as st


DEFAULT_AUTH_HEADERS = (
    "x-auth-request-email",
    "x-auth-request-user",
    "x-forwarded-email",
    "x-forwarded-user",
    "x-forwarded-preferred-username",
    "remote-user",
)
TRUTHY_VALUES = {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: str
    source: str


def auth_is_required() -> bool:
    return os.getenv("AUTH_REQUIRED", "false").strip().lower() in TRUTHY_VALUES


def get_auth_mode() -> str:
    mode = os.getenv("AUTH_MODE", "none").strip().lower()
    return mode if mode in {"none", "header"} else "none"


def _configured_header_candidates() -> tuple[str, ...]:
    raw_value = os.getenv("AUTH_HEADER_CANDIDATES", "")
    if raw_value.strip():
        return tuple(part.strip().lower() for part in raw_value.split(",") if part.strip())
    return DEFAULT_AUTH_HEADERS


def _context_headers() -> dict[str, str]:
    try:
        return {str(key).lower(): str(value) for key, value in st.context.headers.items()}
    except Exception:
        return {}


def get_authenticated_user() -> AuthenticatedUser | None:
    if get_auth_mode() != "header":
        dev_user = os.getenv("AUTH_DEV_USER", "").strip()
        return AuthenticatedUser(user_id=dev_user, source="auth_dev_user") if dev_user else None

    headers = _context_headers()
    for header_name in _configured_header_candidates():
        header_value = headers.get(header_name, "").strip()
        if header_value:
            return AuthenticatedUser(user_id=header_value, source=header_name)

    dev_user = os.getenv("AUTH_DEV_USER", "").strip()
    if dev_user:
        return AuthenticatedUser(user_id=dev_user, source="auth_dev_user")

    return None
