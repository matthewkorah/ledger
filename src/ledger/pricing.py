"""Position and P&L arithmetic.

Pure functions over trades — no database, no clock, no configuration. This is
the part of the codebase that is cheapest to change and cheapest to test.
"""

from __future__ import annotations

from collections.abc import Iterable
from decimal import Decimal

from ledger.models import Position, Side, Trade

ZERO = Decimal("0")


def build_position(symbol: str, trades: Iterable[Trade]) -> Position:
    """Net position in `symbol` using the average-cost method.

    Buys move the average cost; sells reduce quantity at the running average
    and leave the average unchanged.
    """
    quantity = ZERO
    average = ZERO

    for trade in sorted(trades, key=lambda t: t.executed_at):
        if trade.symbol != symbol:
            continue
        if trade.side is Side.BUY:
            total_cost = quantity * average + trade.notional
            quantity += trade.quantity
            average = total_cost / quantity if quantity else ZERO
        else:
            quantity -= trade.quantity

    return Position(symbol=symbol, quantity=quantity, average_cost=average)


def realized_pnl(symbol: str, trades: Iterable[Trade]) -> Decimal:
    """Profit realised by sells, valued against the running average cost."""
    quantity = ZERO
    average = ZERO
    realized = ZERO

    for trade in sorted(trades, key=lambda t: t.executed_at):
        if trade.symbol != symbol:
            continue
        if trade.side is Side.BUY:
            total_cost = quantity * average + trade.notional
            quantity += trade.quantity
            average = total_cost / quantity if quantity else ZERO
        else:
            realized += (trade.price - average) * trade.quantity
            quantity -= trade.quantity

    return realized


def unrealized_pnl(position: Position, mark_price: Decimal) -> Decimal:
    """Paper profit on the open position at `mark_price`."""
    return position.market_value(mark_price) - position.cost_basis


def portfolio_value(positions: Iterable[Position], marks: dict[str, Decimal]) -> Decimal:
    """Total market value. Symbols without a mark are valued at cost.

    TODO: valuing an unmarked symbol at cost silently hides a stale price
    feed. It should probably raise, or report which symbols were unmarked.
    """
    total = ZERO
    for position in positions:
        mark = marks.get(position.symbol)
        total += position.market_value(mark) if mark is not None else position.cost_basis
    return total
