# Docker — Fase 10

Questa cartella contiene lo stack applicativo verificato della fase 10.

Docker viene usato per importazione dati, PostgreSQL e Grafana. Routing, firewall, hotspot, Suricata e Zeek restano sul sistema Ubuntu host.

## Struttura

```text
docker/
|-- compose.yaml
|-- .env.example
|-- database/
|   |-- 002-grafana-reader.sql
|   `-- init/
|       `-- 001-schema.sql
|-- importer/
|   |-- Dockerfile
|   |-- requirements.txt
|   `-- importer.py
`-- grafana/
    |-- dashboards/
    |   `-- security-lab-overview.json
    `-- provisioning/
        |-- dashboards/security-lab.yaml
        `-- datasources/postgres.yaml
```

La directory locale `docker/data/` e il file `docker/.env` sono esclusi da Git.

## Architettura

```text
reports aggregati
      |
      v
importer Python
      |
      v
PostgreSQL
      |
      v
grafana_reader
      |
      v
Grafana
      |
      v
127.0.0.1:3000
```

## Principi di sicurezza applicati

- nessun container privilegiato;
- nessun montaggio del socket Docker;
- report montati in sola lettura;
- importer eseguito come utente non root;
- filesystem importer read-only;
- capability importer rimosse;
- `no-new-privileges`;
- PostgreSQL non pubblicato sull'host;
- Grafana pubblicato soltanto su `127.0.0.1:3000`;
- datasource Grafana con account PostgreSQL dedicato in sola lettura;
- segreti nel file locale `.env` escluso da Git;
- volumi persistenti dedicati;
- healthcheck per PostgreSQL e Grafana;
- rete `backend` interna separata dalla rete `frontend`.

## Preparazione

Copia il file di esempio:

```bash
cp docker/.env.example docker/.env
chmod 600 docker/.env
```

Sostituisci tutti i valori `CHANGE_ME` con password casuali locali. Non pubblicare `docker/.env`.

I tre report da importare devono essere disponibili sotto:

```text
docker/data/reports/zeek-latest.json
docker/data/reports/suricata-latest.json
docker/data/reports/correlation-latest.json
```

Questa directory è ignorata da Git.

## Validazione

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    config --quiet
```

## Avvio database

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    up -d database
```

## Importazione

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    build importer

docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    run --rm importer
```

Una seconda esecuzione con gli stessi report non deve creare duplicati.

## Ruolo Grafana PostgreSQL

Lo script `database/002-grafana-reader.sql` crea o aggiorna il ruolo `grafana_reader` e assegna soltanto i permessi necessari alla lettura della tabella e della vista.

Lo script viene applicato con `GRAFANA_DB_PASSWORD` presente nell'ambiente della sessione `psql`; la password non è salvata nel repository.

## Avvio Grafana

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    up -d grafana
```

Accesso locale:

```text
http://127.0.0.1:3000
```

Health check dall'host:

```bash
curl --fail --silent --show-error \
    http://127.0.0.1:3000/api/health
```

## Arresto non distruttivo

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    down
```

Non aggiungere `--volumes` durante il normale arresto: quell'opzione elimina i dati persistenti.

## Documentazione

- guida: [`../docs/steps/10-database-dashboard-docker.md`](../docs/steps/10-database-dashboard-docker.md);
- report: [`../samples/10-database-dashboard-docker-report.md`](../samples/10-database-dashboard-docker-report.md).
