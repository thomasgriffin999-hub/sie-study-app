import random
import sqlite3
from typing import Optional

from db.schema import get_connection


def insert_question(
    topic_id: int,
    topic_name: str,
    stem: str,
    option_a: str,
    option_b: str,
    option_c: str,
    option_d: str,
    correct_option: str,
    explanation: str,
    difficulty: str,
    source: str = "generated",
) -> int:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO questions
                (topic_id, topic_name, stem, option_a, option_b, option_c, option_d,
                 correct_option, explanation, difficulty, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (topic_id, topic_name, stem, option_a, option_b, option_c, option_d,
             correct_option, explanation, difficulty, source),
        )
        return cursor.lastrowid


def get_questions(
    n: int,
    topic_id: Optional[int] = None,
    difficulty: Optional[str] = None,
    exclude_ids: Optional[list[int]] = None,
    weak_topic_weights: Optional[dict[int, float]] = None,
) -> list[dict]:
    exclude_ids = exclude_ids or []

    with get_connection() as conn:
        placeholders = ",".join("?" * len(exclude_ids)) if exclude_ids else "0"
        params: list = []

        query = f"SELECT * FROM questions WHERE id NOT IN ({placeholders})"
        params.extend(exclude_ids)

        if topic_id is not None:
            query += " AND topic_id = ?"
            params.append(topic_id)

        if difficulty is not None:
            query += " AND difficulty = ?"
            params.append(difficulty)

        rows = conn.execute(query, params).fetchall()

    if not rows:
        return []

    rows_as_dicts = [dict(r) for r in rows]

    if weak_topic_weights and topic_id is None:
        weights = [weak_topic_weights.get(r["topic_id"], 1.0) for r in rows_as_dicts]
        selected = random.choices(rows_as_dicts, weights=weights, k=min(n, len(rows_as_dicts)))
        seen = set()
        unique = []
        for q in selected:
            if q["id"] not in seen:
                seen.add(q["id"])
                unique.append(q)
        return unique[:n]

    return random.sample(rows_as_dicts, min(n, len(rows_as_dicts)))


def get_question_count(topic_id: Optional[int] = None) -> int:
    with get_connection() as conn:
        if topic_id is not None:
            row = conn.execute(
                "SELECT COUNT(*) FROM questions WHERE topic_id = ?", (topic_id,)
            ).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) FROM questions").fetchone()
        return row[0]


def get_all_questions_summary() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, topic_id, topic_name, difficulty, stem FROM questions ORDER BY topic_id, id"
        ).fetchall()
        return [dict(r) for r in rows]
