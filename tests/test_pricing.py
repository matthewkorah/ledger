from __future__ import annotations

from decimal import Decimal

from ledger.models import Position
from ledger.pricing import build_position, realized_pnl, unrealized_pnl


def test_single_buy_sets_average_to_the_fill_price(make_trade):
    trades = [make_trade("ACME", "buy", "100", "10.00")]
    position = build_position("ACME", trades)
    assert position.quantity == Decimal("100")
    assert position.average_cost == Decimal("10.00")


def test_second_buy_blends_the_average(make_trade):
    trades = [
        make_trade("ACME", "buy", "100", "10.00", 0),
        make_trade("ACME", "buy", "100", "12.00", 1),
    ]
    position = build_position("ACME", trades)
    assert position.quantity == Decimal("200")
    assert position.average_cost == Decimal("11.00")


def test_sell_reduces_quantity_and_leaves_the_average(make_trade):
    trades = [
        make_trade("ACME", "buy", "100", "10.00", 0),
        make_trade("ACME", "sell", "40", "15.00", 1),
    ]
    position = build_position("ACME", trades)
    assert position.quantity == Decimal("60")
    assert position.average_cost == Decimal("10.00")


def test_other_symbols_are_ignored(make_trade):
    trades = [
        make_trade("ACME", "buy", "100", "10.00", 0),
        make_trade("OTHER", "buy", "999", "1.00", 1),
    ]
    assert build_position("ACME", trades).quantity == Decimal("100")


def test_trades_are_ordered_by_execution_time_not_input_order(make_trade):
    trades = [
        make_trade("ACME", "buy", "100", "12.00", 1),
        make_trade("ACME", "buy", "100", "10.00", 0),
    ]
    assert build_position("ACME", trades).average_cost == Decimal("11.00")


def test_empty_history_is_a_flat_position():
    position = build_position("ACME", [])
    assert position.quantity == Decimal("0")
    assert position.average_cost == Decimal("0")


def test_realized_pnl_values_sells_against_average_cost(make_trade):
    trades = [
        make_trade("ACME", "buy", "100", "10.00", 0),
        make_trade("ACME", "sell", "40", "15.00", 1),
    ]
    assert realized_pnl("ACME", trades) == Decimal("200.00")


def test_realized_pnl_is_zero_with_no_sells(make_trade):
    trades = [make_trade("ACME", "buy", "100", "10.00")]
    assert realized_pnl("ACME", trades) == Decimal("0")


def test_unrealized_pnl_marks_the_open_position():
    position = Position("ACME", Decimal("60"), Decimal("10.00"))
    assert unrealized_pnl(position, Decimal("12.00")) == Decimal("120.00")
    assert unrealized_pnl(position, Decimal("8.00")) == Decimal("-120.00")
