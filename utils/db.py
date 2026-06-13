# utils/db.py — WealthVise Database Layer
# M4 owns this file.

# Standard library
import hashlib
import json
import sqlite3
from typing import Optional

# Internal
from config import DB_PATH


# ── Helpers ──────────────────────────────────────────────────────────────────

def _hash_username(username: str) -> str:
    """SHA-256 hash the username before storing."""
    return hashlib.sha256(username.encode()).hexdigest()


def _get_connection() -> sqlite3.Connection:
    """Return a SQLite connection to the portfolio database."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ── Public API ────────────────────────────────────────────────────────────────

def init_db() -> None:
    """
    Create the portfolios table if it does not already exist.
    Called once at app startup from app.py.
    """
    conn = _get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolios (
                username_hash TEXT PRIMARY KEY,
                portfolio_json TEXT NOT NULL,
                updated_at     TEXT NOT NULL DEFAULT (datetime('now'))
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_portfolio(username: str, portfolio: dict) -> None:
    """
    Persist a user's portfolio allocation to SQLite.

    Args:
        username:  Plain-text username (will be hashed before storage).
        portfolio: Dict mapping symbol → weight, e.g. {"TSLA": 40, "AAPL": 60}.
    """
    username_hash  = _hash_username(username)
    portfolio_json = json.dumps(portfolio)

    conn = _get_connection()
    try:
        conn.execute(
            """
            INSERT INTO portfolios (username_hash, portfolio_json, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(username_hash) DO UPDATE SET
                portfolio_json = excluded.portfolio_json,
                updated_at     = excluded.updated_at
            """,
            (username_hash, portfolio_json),
        )
        conn.commit()
    except sqlite3.Error as exc:
        # Never raise raw DB errors to the UI — log and swallow
        print(f"[db] save_portfolio error: {exc}")
    finally:
        conn.close()


def load_portfolio(username: str) -> dict:
    """
    Load a user's saved portfolio from SQLite.

    Args:
        username: Plain-text username.

    Returns:
        Dict of symbol → weight, or {} if nothing is saved yet.
    """
    username_hash = _hash_username(username)

    conn = _get_connection()
    try:
        row = conn.execute(
            "SELECT portfolio_json FROM portfolios WHERE username_hash = ?",
            (username_hash,),
        ).fetchone()
        if row:
            return json.loads(row["portfolio_json"])
        return {}
    except (sqlite3.Error, json.JSONDecodeError) as exc:
        print(f"[db] load_portfolio error: {exc}")
        return {}
    finally:
        conn.close()
