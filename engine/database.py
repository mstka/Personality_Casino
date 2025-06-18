"""Database utilities using SQLite."""
import sqlite3
from pathlib import Path
from typing import List, Tuple, Any

_DB_PATH = Path("casino_logs.db")


def init_db() -> sqlite3.Connection:
    """Initialize database and return connection."""
    conn = sqlite3.connect(_DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            game TEXT,
            bet INTEGER,
            choice TEXT,
            result TEXT,
            duration REAL
        )"""
    )
    conn.commit()
    return conn


def log_play(conn: sqlite3.Connection, game: str, bet: int, choice: str, result: str, duration: float) -> None:
    """Insert a game play log into the database."""
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (game, bet, choice, result, duration) VALUES (?, ?, ?, ?, ?)",
        (game, bet, choice, result, duration),
    )
    conn.commit()


def fetch_logs(conn: sqlite3.Connection) -> List[Tuple[Any, ...]]:
    """Fetch all game logs."""
    cur = conn.cursor()
    cur.execute("SELECT game, bet, choice, result, duration FROM logs")
    return cur.fetchall()
