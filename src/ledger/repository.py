"""Persistence for trades, and positions derived from them."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import psycopg

from ledger.models import Position, Side, Trade
from ledger.pricing import build_position

INSERT = """
INSERT INTO trades (symbol, side, quantity, price, executed_at)
VALUES (%s, %s, %s, %s, %s)
RETURNING id
"""

SELECT_BY_SYMBOL = """
SELECT id, symbol, side, quantity, price, executed_at
FROM trades
WHERE symbol = %s
ORDER BY executed_at, id
"""

SELECT_SYMBOLS = "SELECT DISTINCT symbol FROM trades ORDER BY symbol"


def _row_to_trade(row: tuple) -> Trade:
    trade_id, symbol, side, quantity, price, executed_at = row
    return Trade(
        id=trade_id,
        symbol=symbol,
        side=Side(side),
        quantity=Decimal(quantity),
        price=Decimal(price),
        executed_at=executed_at,
    )


class TradeRepository:
    def __init__(self, conn: psycopg.Connection) -> None:
        self.conn = conn

    def add(self, trade: Trade) -> int:
        row = self.conn.execute(
            INSERT,
            (trade.symbol, str(trade.side), trade.quantity, trade.price, trade.executed_at),
        ).fetchone()
        self.conn.commit()
        return row[0]

    def add_many(self, trades: list[Trade]) -> list[int]:
        return [self.add(trade) for trade in trades]

    def trades_for(self, symbol: str, since: datetime | None = None) -> list[Trade]:
        """All trades in a symbol, oldest first.

        TODO: `since` is accepted but ignored — the filter is applied in
        Python by the caller, if at all. It should be pushed into the query.
        """
        rows = self.conn.execute(SELECT_BY_SYMBOL, (symbol,)).fetchall()
        return [_row_to_trade(row) for row in rows]

    def symbols(self) -> list[str]:
        return [row[0] for row in self.conn.execute(SELECT_SYMBOLS).fetchall()]

    def position(self, symbol: str) -> Position:
        return build_position(symbol, self.trades_for(symbol))

    def positions(self) -> list[Position]:
        """Every position held.

        One query per symbol. Fine at sandbox scale, and the obvious thing to
        fix first if the trade table grows.
        """
        return [self.position(symbol) for symbol in self.symbols()]
