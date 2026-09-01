CREATE TABLE IF NOT EXISTS trades (
    id          BIGSERIAL PRIMARY KEY,
    symbol      TEXT           NOT NULL,
    side        TEXT           NOT NULL CHECK (side IN ('buy', 'sell')),
    quantity    NUMERIC(20, 8) NOT NULL,
    price       NUMERIC(20, 8) NOT NULL,
    executed_at TIMESTAMPTZ    NOT NULL
);

CREATE INDEX IF NOT EXISTS trades_symbol_executed_at_idx
    ON trades (symbol, executed_at);
