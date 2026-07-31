# Fase 10 — Database e dashboard con Docker

## Stato

```text
COMPLETATA E VERIFICATA — 30 luglio 2026
```

Backup, ripristino e collaudo finale di riavvio vengono completati nella fase 11.

## Obiettivo raggiunto

Containerizzare i servizi applicativi che archiviano e mostrano le statistiche prodotte da Python, senza affidare a Docker il routing principale del gateway.

## Separazione delle responsabilità

```text
Ubuntu host
    hotspot, DHCP, routing, firewall, Suricata e Zeek

Docker
    importazione dati, PostgreSQL e Grafana
```

Docker non controlla il firewall host e non usa `network_mode: host`.

## Architettura verificata

```text
reports/*-latest.json
        |
        v
Importer Python non root
        |
        v
PostgreSQL 17
        |
        v
grafana_reader (SELECT only)
        |
        v
Grafana 13
        |
        v
127.0.0.1:3000
```

## Componenti realizzati

```text
docker/compose.yaml
docker/.env.example
docker/database/init/001-schema.sql
docker/database/002-grafana-reader.sql
docker/importer/Dockerfile
docker/importer/requirements.txt
docker/importer/importer.py
docker/grafana/provisioning/datasources/postgres.yaml
docker/grafana/provisioning/dashboards/security-lab.yaml
docker/grafana/dashboards/security-lab-overview.json
```

Il file `.env` reale resta escluso da Git.

## Scelta del database

È stato scelto PostgreSQL invece di SQLite perché il laboratorio deve separare chiaramente:

- processo di importazione;
- persistenza dei dati;
- utente di sola lettura della dashboard;
- backup e ripristino futuri.

I report aggregati vengono salvati in una colonna `JSONB`. In questa fase non vengono create decine di tabelle premature: le metriche realmente usate dalla dashboard possono essere estratte con query PostgreSQL sul documento JSON.

## Schema dati

La tabella principale è `report_imports` e contiene:

- `report_kind`: `zeek`, `suricata` o `correlation`;
- `source_filename`: nome del report importato;
- `content_sha256`: hash stabile del contenuto normalizzato;
- `imported_at`: timestamp dell'importazione;
- `report`: documento aggregato in formato `JSONB`.

Il vincolo univoco:

```text
(report_kind, content_sha256)
```

rende l'importazione idempotente.

La vista `latest_report_imports` restituisce l'importazione più recente per ciascun tipo di report.

## Privacy dell'importer

Prima dell'inserimento, `importer.py`:

1. verifica che il documento principale sia un oggetto JSON;
2. richiede `raw_ip_addresses_included = false`;
3. per Zeek e correlazione richiede `zeek_uids_included = false`;
4. rimuove i campi `source` e `sources`;
5. crea una serializzazione canonica;
6. calcola SHA-256;
7. inserisce il report con `ON CONFLICT DO NOTHING`.

I campi `source` e `sources` vengono rimossi per non archiviare percorsi locali temporanei e per ottenere hash stabili.

## Container importer

L'importer usa Python 3.13 e `psycopg`.

Il processo viene eseguito con UID/GID dedicati non root:

```text
10001:10001
```

Il Dockerfile imposta direttamente proprietario e modalità di `importer.py` con `COPY --chown` e `--chmod`, evitando dipendenze dall'`umask` dell'host.

Il container usa inoltre:

- filesystem `read_only`;
- `tmpfs` limitato per `/tmp`;
- `cap_drop: ALL`;
- `no-new-privileges:true`;
- report montati in sola lettura.

## PostgreSQL

PostgreSQL usa un volume Docker dedicato:

```text
postgres_data
```

La porta `5432` non viene pubblicata sull'host. Il database è raggiungibile soltanto dai container collegati alla rete `backend`.

Healthcheck:

```text
pg_isready
```

## Utente Grafana in sola lettura

Grafana non usa l'account amministrativo PostgreSQL.

È stato creato:

```text
grafana_reader
```

con:

- `LOGIN`;
- nessun privilegio superuser;
- nessun `CREATEDB`;
- nessun `CREATEROLE`;
- transazioni predefinite in sola lettura;
- `statement_timeout` di 10 secondi;
- `USAGE` sullo schema `public`;
- `SELECT` sulle sole tabelle/vista necessarie.

Un test di scrittura controllato viene rifiutato dalla modalità read-only.

## Grafana

Grafana viene configurato tramite provisioning versionato:

```text
datasource: Security Lab PostgreSQL
dashboard:  Linux Security Lab — Fase 10
```

La password del datasource arriva da variabile d'ambiente e non viene salvata nel file YAML.

Accesso locale:

```text
http://127.0.0.1:3000
```

L'accesso anonimo e la registrazione autonoma sono disabilitati.

## Reti Docker

Sono presenti due reti con responsabilità separate.

### `backend`

```yaml
internal: true
```

Collega PostgreSQL, importer e Grafana. PostgreSQL resta isolato dalla rete dell'host.

### `frontend`

Rete bridge usata soltanto da Grafana per il binding locale:

```text
127.0.0.1:3000 -> container:3000
```

Questa separazione è stata introdotta dopo aver verificato che Grafana, collegato soltanto alla rete `internal`, era sano dentro il container ma non raggiungibile dall'host.

## Campione importato

Per il primo collaudo sono stati usati i campioni sintetici della fase 9 perché il file Suricata corrente era vuoto.

Sono stati prodotti:

```text
reports/zeek-latest.json
reports/suricata-latest.json
reports/correlation-latest.json
```

Risultati importati:

| Tipo | Hash abbreviato |
|---|---|
| Zeek | `c099a80904a2` |
| Suricata | `124fb2b03eb6` |
| Correlazione | `0712ed6b8d67` |

PostgreSQL conteneva esattamente tre righe dopo la prima importazione.

Una seconda esecuzione dell'importer non ha creato duplicati.

## Dashboard verificata

Metriche osservate:

| Pannello | Valore |
|---|---:|
| Eventi Zeek validi | 4 |
| Eventi Suricata validi | 8 |
| Eventi correlati | 5 |
| Delta temporale medio | 0,440 s |

La tabella `Importazioni recenti` mostra i tre report e i rispettivi hash abbreviati.

![Dashboard Grafana della fase 10](../images/10-grafana-dashboard.svg)

## Comandi operativi

Il file reale delle credenziali è `docker/.env` e non deve essere pubblicato.

Validazione:

```bash
docker compose --env-file docker/.env -f docker/compose.yaml config --quiet
```

Build importer:

```bash
docker compose --env-file docker/.env -f docker/compose.yaml build importer
```

Avvio database e Grafana:

```bash
docker compose --env-file docker/.env -f docker/compose.yaml up -d database grafana
```

Importazione:

```bash
docker compose --env-file docker/.env -f docker/compose.yaml run --rm importer
```

Stato:

```bash
docker compose --env-file docker/.env -f docker/compose.yaml ps
```

Health Grafana:

```bash
curl --fail --silent --show-error http://127.0.0.1:3000/api/health
```

## Problemi incontrati

### Accesso al socket Docker

L'utente normale non aveva permesso su `/var/run/docker.sock`. Durante il laboratorio è stato usato `sudo docker compose`; non è stato applicato `chmod 666` al socket.

### Permessi di `importer.py`

Un precedente `umask 077` aveva prodotto un file non leggibile dall'utente non root del container. Il Dockerfile ora imposta i permessi durante `COPY`.

### Log Zeek protetti

`python/analyze-lab` trovava il log più recente tramite `sudo find`, ma lo verificava poi con `[[ -e ... ]]` come utente normale. Il controllo è stato corretto per usare `sudo test -e` quando il percorso non è attraversabile dall'utente.

### Rete Grafana

Il primo avvio mostrava Grafana `healthy` ma `docker compose ps` esponeva solo `3000/tcp`. L'aggiunta della rete `frontend` ha reso effettivo il binding locale senza esporre PostgreSQL.

## Verifiche completate

- [x] definire schema dati;
- [x] creare importazione idempotente;
- [x] gestire record duplicati;
- [x] creare volumi persistenti;
- [x] creare rete Docker backend separata;
- [x] configurare healthcheck;
- [x] avviare lo stack;
- [x] importare un campione;
- [x] confrontare dashboard e report Python;
- [x] verificare datasource PostgreSQL;
- [x] limitare Grafana a `127.0.0.1`;
- [x] usare un account database read-only per Grafana.

## Condizione di completamento della fase

Verificato:

- i dati Python entrano nel database;
- la dashboard mostra valori verificabili;
- i container non controllano il firewall host;
- i report sono montati in sola lettura;
- PostgreSQL non è pubblicato sull'host;
- Grafana usa un account read-only.

Il test completo di arresto/riavvio, backup e ripristino viene eseguito nella fase 11, che è ora la prossima attività.

## Rollback

Arresto non distruttivo:

```bash
docker compose --env-file docker/.env -f docker/compose.yaml down
```

La rimozione dei volumi è deliberatamente separata:

```bash
docker compose --env-file docker/.env -f docker/compose.yaml down --volumes
```

Il secondo comando elimina i dati persistenti e non deve essere usato durante il normale arresto.

## Report pubblico

[`../../samples/10-database-dashboard-docker-report.md`](../../samples/10-database-dashboard-docker-report.md)

## Prossimo passo

Passare alla fase 11: collaudo completo, hardening, backup e ripristino.
