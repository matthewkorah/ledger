"""Core domain types."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class Side(StrEnum):
    BUY = "buy"
    SELL = "sell"


@dataclass(frozen=True)
class Trade:
    """A single execution.

    Quantity is always positive; direction is carried by `side`.
    """

    symbol: str
    side: Side
    quantity: Decimal
    price: Decimal
    executed_at: datetime
    id: int | None = None

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"quantity must be positive, got {self.quantity}")
        if self.price <= 0:
            raise ValueError(f"price must be positive, got {self.price}")

    @property
    def notional(self) -> Decimal:
        return self.quantity * self.price

    @property
    def signed_quantity(self) -> Decimal:
        return self.quantity if self.side is Side.BUY else -self.quantity


@dataclass(frozen=True)
class Position:
    """Net holding in one symbol, with the average cost of the open lots."""

    symbol: str
    quantity: Decimal
    average_cost: Decimal

    @property
    def cost_basis(self) -> Decimal:
        return self.quantity * self.average_cost

    def market_value(self, mark_price: Decimal) -> Decimal:
        return self.quantity * mark_price
