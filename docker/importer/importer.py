#!/usr/bin/env python3

"""Importa in PostgreSQL i report aggregati prodotti dalla fase 9.

Il programma legge i tre collegamenti ``*-latest.json``, verifica le
indicazioni di privacy, rimuove i percorsi locali presenti nei campi
``source``/``sources``, calcola un hash SHA-256 stabile e inserisce ogni
report una sola volta.
"""

import hashlib
import json
import os
from pathlib import Path
import sys

import psycopg
from psycopg.types.json import Jsonb


REPORT_FILES = {
    "zeek": "zeek-latest.json",
    "suricata": "suricata-latest.json",
    "correlation": "correlation-latest.json",
}


def require_environment(name: str) -> str:
    """Restituisce una variabile d'ambiente obbligatoria."""

    value = os.environ.get(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Variabile d'ambiente obbligatoria assente: {name}")
    return value


def check_privacy(report_kind: str, report: dict[str, object]) -> None:
    """Rifiuta report che dichiarano di contenere dati grezzi."""

    privacy = report.get("privacy")
    if not isinstance(privacy, dict):
        raise ValueError(f"{report_kind}: sezione privacy assente o non valida")

    if privacy.get("raw_ip_addresses_included") is not False:
        raise ValueError(f"{report_kind}: il report potrebbe contenere IP grezzi")

    if report_kind in {"zeek", "correlation"}:
        if privacy.get("zeek_uids_included") is not False:
            raise ValueError(f"{report_kind}: il report potrebbe contenere UID Zeek")


def load_report(
    report_kind: str,
    report_path: Path,
) -> tuple[str, str, dict[str, object]]:
    """Legge, controlla e normalizza un report JSON."""

    resolved_path = report_path.resolve(strict=True)

    with resolved_path.open("r", encoding="utf-8") as report_file:
        report = json.load(report_file)

    if not isinstance(report, dict):
        raise ValueError(f"{resolved_path.name}: il JSON principale non è un oggetto")

    check_privacy(report_kind, report)

    normalized_report = dict(report)
    normalized_report.pop("source", None)
    normalized_report.pop("sources", None)

    canonical_json = json.dumps(
        normalized_report,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    content_hash = hashlib.sha256(canonical_json).hexdigest()
    return resolved_path.name, content_hash, normalized_report


def import_report(
    connection: psycopg.Connection,
    report_kind: str,
    report_path: Path,
) -> None:
    """Inserisce un report oppure segnala che era già presente."""

    source_filename, content_hash, report = load_report(report_kind, report_path)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO report_imports (
                report_kind,
                source_filename,
                content_sha256,
                report
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (report_kind, content_sha256)
            DO NOTHING
            RETURNING id
            """,
            (
                report_kind,
                source_filename,
                content_hash,
                Jsonb(report),
            ),
        )
        inserted_row = cursor.fetchone()

    if inserted_row is None:
        print(f"Già presente: {report_kind} ({content_hash[:12]}...)")
    else:
        print(
            f"Importato: {report_kind}, "
            f"id={inserted_row[0]}, "
            f"hash={content_hash[:12]}..."
        )


def main() -> int:
    """Coordina il collegamento a PostgreSQL e le tre importazioni."""

    report_directory = Path(require_environment("REPORT_DIR"))

    connection_parameters = {
        "host": require_environment("DB_HOST"),
        "port": require_environment("DB_PORT"),
        "dbname": require_environment("DB_NAME"),
        "user": require_environment("DB_USER"),
        "password": require_environment("DB_PASSWORD"),
        "connect_timeout": 5,
    }

    try:
        with psycopg.connect(**connection_parameters) as connection:
            for report_kind, filename in REPORT_FILES.items():
                report_path = report_directory / filename
                if not report_path.exists():
                    raise FileNotFoundError(f"Report non trovato: {report_path}")
                import_report(connection, report_kind, report_path)
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        OSError,
        ValueError,
        RuntimeError,
        psycopg.Error,
    ) as error:
        print(f"Errore durante l'importazione: {error}", file=sys.stderr)
        return 1

    print("Importazione completata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
