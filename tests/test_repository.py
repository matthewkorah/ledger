"""Postgres-backed tests. Skipped locally unless DATABASE_URL is set; CI
always runs them against a real Postgres service."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ledger.repository import TradeRepository

pytestmark = pytest.mark.postgres


def test_round_trips_a_trade(conn, make_trade):
    repo = TradeRepository(conn)
    trade_id = repo.add(make_trade("ACME", "buy", "100", "10.00"))
    assert trade_id > 0

    stored = repo.trades_for("ACME")
    assert len(stored) == 1
    assert stored[0].symbol == "ACME"
    assert stored[0].quantity == Decimal("100")
    assert stored[0].price == Decimal("10.00")


def test_trades_come_back_in_execution_order(conn, make_trade):
    repo = TradeRepository(conn)
    repo.add(make_trade("ACME", "buy", "10", "12.00", 5))
    repo.add(make_trade("ACME", "buy", "10", "10.00", 0))
    prices = [t.price for t in repo.trades_for("ACME")]
    assert prices == [Decimal("10.00"), Decimal("12.00")]


def test_position_is_derived_from_stored_trades(conn, make_trade):
    repo = TradeRepository(conn)
    repo.add_many(
        [
            make_trade("ACME", "buy", "100", "10.00", 0),
            make_trade("ACME", "buy", "100", "12.00", 1),
            make_trade("ACME", "sell", "50", "15.00", 2),
        ]
    )
    position = repo.position("ACME")
    assert position.quantity == Decimal("150")
    assert position.average_cost == Decimal("11.00")


def test_symbols_and_positions_cover_every_symbol(conn, make_trade):
    repo = TradeRepository(conn)
    repo.add(make_trade("ACME", "buy", "10", "10.00"))
    repo.add(make_trade("BETA", "buy", "5", "20.00"))
    assert repo.symbols() == ["ACME", "BETA"]
    assert {p.symbol for p in repo.positions()} == {"ACME", "BETA"}
