-- =============================================================
-- Cash Buyers List — Supabase Table Setup
-- =============================================================
-- Run this SQL in your Supabase Dashboard → SQL Editor
-- to create the table that stores your cash buyers.
-- =============================================================

CREATE TABLE IF NOT EXISTS cash_buyers (
    id              BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT DEFAULT '',
    phone           TEXT DEFAULT '',
    location        TEXT DEFAULT '',
    buy_criteria    TEXT DEFAULT '',
    max_budget      TEXT DEFAULT '',
    preferred_property_type TEXT DEFAULT '',
    source          TEXT DEFAULT 'manual',
    notes           TEXT DEFAULT '',
    added_at        TIMESTAMPTZ DEFAULT NOW(),
    last_contacted  TIMESTAMPTZ,
    status          TEXT DEFAULT 'active'
);

-- Index for fast lookups by status and location
CREATE INDEX IF NOT EXISTS idx_cash_buyers_status ON cash_buyers (status);
CREATE INDEX IF NOT EXISTS idx_cash_buyers_location ON cash_buyers (location);

-- Enable Row Level Security (recommended by Supabase)
ALTER TABLE cash_buyers ENABLE ROW LEVEL SECURITY;

-- Allow your service key full access
CREATE POLICY "Allow all access with service key"
    ON cash_buyers
    FOR ALL
    USING (true)
    WITH CHECK (true);
