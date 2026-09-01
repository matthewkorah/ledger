from __future__ import annotations

import os
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest

from ledger.models import Side, Trade

START = datetime(2026, 1, 2, 14, 30, tzinfo=UTC)


def trade(symbol: str, side: str, qty: str, price: str, minutes: int = 0) -> Trade:
    return Trade(
        symbol=symbol,
        side=Side(side),
        quantity=Decimal(qty),
        price=Decimal(price),
        executed_at=START + timedelta(minutes=minutes),
    )


@pytest.fixture
def make_trade():
    return trade


@pytest.fixture(scope="session")
def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL not set; skipping Postgres-backed tests")
    return url


@pytest.fixture
def conn(database_url):
    import psycopg

    from ledger import db

    with psycopg.connect(database_url) as connection:
        db.reset(connection)
        yield connection
