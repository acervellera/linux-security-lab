\set ON_ERROR_STOP on

CREATE TABLE IF NOT EXISTS report_imports (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    report_kind text NOT NULL CHECK (report_kind IN ('zeek', 'suricata', 'correlation')),
    source_filename text NOT NULL,
    content_sha256 character(64) NOT NULL,
    imported_at timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    report jsonb NOT NULL,
    CONSTRAINT report_imports_kind_hash_unique UNIQUE (report_kind, content_sha256)
);

CREATE INDEX IF NOT EXISTS report_imports_imported_at_idx
    ON report_imports (imported_at DESC);

CREATE INDEX IF NOT EXISTS report_imports_report_gin_idx
    ON report_imports USING gin (report);

CREATE OR REPLACE VIEW latest_report_imports AS
SELECT DISTINCT ON (report_kind)
    id,
    report_kind,
    source_filename,
    content_sha256,
    imported_at,
    report
FROM report_imports
ORDER BY report_kind, imported_at DESC, id DESC;
