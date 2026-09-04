from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from ledger.models import Side, Trade

EXECUTED_AT = datetime(2026, 1, 2, 14, 30, tzinfo=UTC)


def build_trade(quantity: str, price: str) -> Trade:
    return Trade(
        symbol="ACME",
        side=Side.BUY,
        quantity=Decimal(quantity),
        price=Decimal(price),
        executed_at=EXECUTED_AT,
    )


def test_valid_trade_constructs_normally():
    trade = build_trade("100", "10.00")
    assert trade.symbol == "ACME"
    assert trade.side is Side.BUY
    assert trade.quantity == Decimal("100")
    assert trade.price == Decimal("10.00")
    assert trade.executed_at == EXECUTED_AT
    assert trade.id is None
    assert trade.notional == Decimal("1000.00")


@pytest.mark.parametrize("quantity", ["0", "-1", "-0.5"])
def test_non_positive_quantity_is_rejected(quantity):
    with pytest.raises(ValueError, match="quantity must be positive"):
        build_trade(quantity, "10.00")


@pytest.mark.parametrize("price", ["0", "-1", "-0.01"])
def test_non_positive_price_is_rejected(price):
    with pytest.raises(ValueError, match="price must be positive"):
        build_trade("100", price)
