from __future__ import annotations

from decimal import Decimal


def test_notional_multiplies_quantity_by_price(make_trade):
    assert make_trade("ACME", "buy", "100", "10.00").notional == Decimal("1000.00")


def test_notional_is_positive_for_sells(make_trade):
    assert make_trade("ACME", "sell", "40", "15.00").notional == Decimal("600.00")


def test_notional_returns_a_decimal(make_trade):
    assert isinstance(make_trade("ACME", "buy", "100", "10.00").notional, Decimal)


def test_notional_keeps_fractional_precision(make_trade):
    assert make_trade("ACME", "buy", "2.5", "10.25").notional == Decimal("25.625")


def test_notional_is_zero_for_a_zero_quantity_trade(make_trade):
    assert make_trade("ACME", "buy", "0", "10.00").notional == Decimal("0")
