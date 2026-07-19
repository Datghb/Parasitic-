BEGIN;

CREATE TABLE IF NOT EXISTS cases (
    id VARCHAR(128) PRIMARY KEY,
    status VARCHAR(32) NOT NULL DEFAULT 'new',
    version INTEGER NOT NULL DEFAULT 1 CHECK (version > 0),
    payload JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_cases_status ON cases (status);
CREATE INDEX IF NOT EXISTS ix_cases_updated_at ON cases (updated_at DESC);

CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(128) NOT NULL REFERENCES cases(id),
    decision VARCHAR(32) NOT NULL,
    corrected_label VARCHAR(32),
    note TEXT NOT NULL DEFAULT '',
    actor VARCHAR(128) NOT NULL,
    case_version INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_reviews_case_id ON reviews (case_id);

CREATE TABLE IF NOT EXISTS audit_events (
    id BIGSERIAL PRIMARY KEY,
    case_id VARCHAR(128) NOT NULL REFERENCES cases(id),
    action VARCHAR(64) NOT NULL,
    actor VARCHAR(128) NOT NULL,
    old_value TEXT NOT NULL DEFAULT '',
    new_value TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_audit_events_case_id ON audit_events (case_id);

REVOKE UPDATE, DELETE ON audit_events FROM PUBLIC;
COMMIT;
