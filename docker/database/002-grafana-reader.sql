\set ON_ERROR_STOP on
\getenv grafana_password GRAFANA_DB_PASSWORD

SELECT format(
    'CREATE ROLE grafana_reader LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOREPLICATION NOBYPASSRLS PASSWORD %L',
    :'grafana_password'
)
WHERE NOT EXISTS (
    SELECT 1 FROM pg_roles WHERE rolname = 'grafana_reader'
)
\gexec

ALTER ROLE grafana_reader WITH PASSWORD :'grafana_password';
ALTER ROLE grafana_reader SET default_transaction_read_only = on;
ALTER ROLE grafana_reader SET statement_timeout = '10s';

SELECT format(
    'GRANT CONNECT ON DATABASE %I TO grafana_reader',
    current_database()
)
\gexec

GRANT USAGE ON SCHEMA public TO grafana_reader;
REVOKE CREATE ON SCHEMA public FROM grafana_reader;
GRANT SELECT ON TABLE report_imports TO grafana_reader;
GRANT SELECT ON TABLE latest_report_imports TO grafana_reader;
