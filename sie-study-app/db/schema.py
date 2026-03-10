import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "sie_study.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS questions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_id        INTEGER NOT NULL,
                topic_name      TEXT NOT NULL,
                stem            TEXT NOT NULL,
                option_a        TEXT NOT NULL,
                option_b        TEXT NOT NULL,
                option_c        TEXT NOT NULL,
                option_d        TEXT NOT NULL,
                correct_option  TEXT NOT NULL CHECK(correct_option IN ('A','B','C','D')),
                explanation     TEXT NOT NULL,
                difficulty      TEXT NOT NULL CHECK(difficulty IN ('easy','medium','hard')),
                source          TEXT NOT NULL DEFAULT 'generated',
                created_at      TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at          TEXT NOT NULL DEFAULT (datetime('now')),
                ended_at            TEXT,
                mode                TEXT NOT NULL CHECK(mode IN ('practice','quiz','weak_areas')),
                questions_asked     INTEGER NOT NULL DEFAULT 0,
                questions_correct   INTEGER NOT NULL DEFAULT 0,
                topic_filter        INTEGER
            );

            CREATE TABLE IF NOT EXISTS answers (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id      INTEGER NOT NULL REFERENCES sessions(id),
                question_id     INTEGER NOT NULL REFERENCES questions(id),
                chosen_option   TEXT NOT NULL CHECK(chosen_option IN ('A','B','C','D')),
                is_correct      INTEGER NOT NULL CHECK(is_correct IN (0,1)),
                time_spent_secs INTEGER,
                answered_at     TEXT NOT NULL DEFAULT (datetime('now'))
            );
        """)
