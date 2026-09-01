"""Postgres connection handling and schema management."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import psycopg

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schema.sql"


class NotConfigured(RuntimeError):
    """DATABASE_URL is not set."""


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise NotConfigured(
            "DATABASE_URL is not set. Example:\n"
            "  export DATABASE_URL=postgresql://localhost/ledger"
        )
    return url


@contextmanager
def connect(url: str | None = None) -> Iterator[psycopg.Connection]:
    """A connection that commits on success and rolls back on error."""
    with psycopg.connect(url or database_url()) as conn:
        yield conn


def apply_schema(conn: psycopg.Connection) -> None:
    conn.execute(SCHEMA_PATH.read_text())
    conn.commit()


def reset(conn: psycopg.Connection) -> None:
    """Drop and recreate. Test helper — never call this against real data."""
    conn.execute("DROP TABLE IF EXISTS trades CASCADE")
    conn.commit()
    apply_schema(conn)
