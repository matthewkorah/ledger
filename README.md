# ledger

A small trade ledger: records executions, derives positions using the
average-cost method, and computes realised and unrealised P&L over a Postgres
store.

## What this repository is for

This is the **sandbox target** for the Linear → Claude Code pipeline. It exists
so the agent has somewhere real to work that nothing depends on.

It is deliberately shaped like the production trading platform — Python,
Postgres, pytest, GitHub Actions — rather than being a toy in a different
stack. A sandbox that does not resemble the real target produces lessons that
do not transfer.

Nothing here is used by anything. It can be deleted and recreated at will.

## Layout

```
src/ledger/
  models.py      Trade and Position
  pricing.py     pure position and P&L arithmetic — no database, no clock
  db.py          connection handling and schema
  repository.py  persistence, and positions derived from stored trades
schema.sql       the trades table
tests/           pricing tests run anywhere; repository tests need Postgres
```

## Running the tests

```bash
python3.12 -m venv .venv
./.venv/bin/pip install -e ".[dev]"
./.venv/bin/pytest
```

Repository tests are skipped unless `DATABASE_URL` is set:

```bash
export DATABASE_URL=postgresql://localhost/ledger_test
./.venv/bin/pytest
```

CI always runs them against a real Postgres service.

## CI is the gate

The sandbox phases have no human review step on pull requests, so the CI
workflow is the only thing standing between a change and `main`. It runs
`ruff` and the full test suite including the Postgres-backed tests, and it
must be configured as a **required status check** on `main`.

## Known gaps

Real, deliberate, and left in place — these are the raw material for the
agent's first tickets. Each is small, locally verifiable, and has a clear
correct answer.

1. **`Trade` accepts nonsense values.** Nothing rejects a zero or negative
   quantity, or a negative price. A validation layer belongs on construction.

2. **Overselling produces a silently wrong position.** `build_position` will
   happily drive quantity negative while leaving `average_cost` at the old
   long average, which is meaningless for a short. It should either reject the
   oversell or model shorts properly.

3. **`realized_pnl` is untested for sell-then-rebuy.** Selling out entirely and
   buying back resets the average through a path no test currently covers.

4. **`portfolio_value` hides a stale price feed.** A symbol with no mark is
   valued at cost rather than reported, so a broken feed looks like a flat day.
   See the `TODO` in `pricing.py`.

5. **`TradeRepository.trades_for` ignores its `since` argument.** The parameter
   is accepted and silently dropped instead of being pushed into the query.

6. **`TradeRepository.positions` runs one query per symbol.** Fine at this
   scale, and the obvious first thing to fix if the table grows.
