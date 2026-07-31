# Fase 10 — Database e dashboard con Docker

## Stato

```text
IMPLEMENTAZIONE PRINCIPALE COMPLETATA E VERIFICATA — 30 luglio 2026
Backup, ripristino e collaudo finale di riavvio restano nella fase 11.
```

## Obiettivo raggiunto

I report aggregati prodotti dagli analizzatori Python della fase 9 vengono importati in PostgreSQL e visualizzati in Grafana, mantenendo routing, firewall, hotspot, Suricata e Zeek sull'host Ubuntu.

## Architettura verificata

```text
Report JSON aggregati
        |
        v
Importer Python non root
        |
        v
PostgreSQL
        |
        v
Utente grafana_reader in sola lettura
        |
        v
Grafana su 127.0.0.1:3000
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

Il file `docker/.env` contiene le credenziali reali ed è escluso da Git.

## Importazione verificata

Sono stati importati tre report aggregati del campione sintetico della fase 9:

| Tipo | File | Hash abbreviato |
|---|---|---|
| Zeek | `zeek-latest.json` | `c099a80904a2` |
| Suricata | `suricata-latest.json` | `124fb2b03eb6` |
| Correlazione | `correlation-latest.json` | `0712ed6b8d67` |

L'importazione è idempotente: il vincolo univoco su tipo di report e SHA-256 impedisce di inserire due volte lo stesso contenuto.

## Dashboard verificata

La dashboard Grafana mostra correttamente i dati del campione:

| Metrica | Valore |
|---|---:|
| Eventi Zeek validi | 4 |
| Eventi Suricata validi | 8 |
| Eventi correlati | 5 |
| Delta temporale medio | 0,440 secondi |

![Dashboard Grafana della fase 10](../docs/images/10-grafana-dashboard.svg)

La tabella delle importazioni mostra i tre documenti presenti in PostgreSQL.

## Sicurezza applicata

- PostgreSQL non pubblica porte sull'host;
- Grafana è pubblicato soltanto su `127.0.0.1:3000`;
- il datasource usa un account PostgreSQL dedicato in sola lettura;
- l'importer viene eseguito come utente non root;
- i report sono montati nel container in sola lettura;
- i container non usano `privileged: true`;
- non viene montato `/var/run/docker.sock`;
- le credenziali reali restano in `docker/.env`;
- PostgreSQL e Grafana usano volumi persistenti;
- PostgreSQL e Grafana possiedono healthcheck;
- la rete `backend` è interna e separata dalla rete `frontend` usata da Grafana per il solo binding locale.

## Verifiche eseguite

```bash
docker compose config --quiet
docker compose build importer
docker compose up -d database
docker compose run --rm importer
docker compose up -d grafana
docker compose ps
curl http://127.0.0.1:3000/api/health
```

Sono stati verificati:

- build dell'immagine importer;
- avvio e healthcheck di PostgreSQL;
- creazione dello schema;
- importazione dei tre report;
- presenza di tre righe nel database;
- datasource PostgreSQL caricato da Grafana;
- dashboard caricata tramite provisioning;
- accesso locale alla dashboard;
- visualizzazione corretta delle metriche;
- account PostgreSQL Grafana configurato per sola lettura.

## Problemi incontrati

### Permessi Docker

L'utente normale non aveva accesso a `/var/run/docker.sock`. Durante il laboratorio è stato usato `sudo docker compose` invece di rendere il socket scrivibile globalmente.

### Permessi dell'importer

Un `umask 077` aveva reso `importer.py` non leggibile dall'utente non root del container. Il Dockerfile imposta ora proprietario e modalità direttamente con `COPY --chown` e `--chmod`.

### Log Zeek protetti

`analyze-lab` trovava un log tramite `sudo find` ma lo ricontrollava come utente normale. Il controllo è stato corretto per verificare l'esistenza tramite `sudo test -e` quando necessario.

### Grafana raggiungibile solo nel container

Grafana era inizialmente collegato soltanto alla rete Docker `internal`. È stata aggiunta una rete `frontend` separata e la porta è pubblicata esclusivamente su `127.0.0.1:3000`.

## Privacy

I report importati sono aggregati e dichiarano esplicitamente l'assenza di IP grezzi. I report Zeek e correlazione dichiarano inoltre l'assenza degli UID Zeek. L'importer rimuove i campi `source` e `sources` prima del salvataggio, evitando di archiviare percorsi locali temporanei.

La schermata pubblicata non contiene password, token, indirizzi IP privati del laboratorio o contenuti di traffico.

## Rollback non distruttivo

```bash
docker compose down
```

Il comando arresta e rimuove container e reti mantenendo i volumi persistenti.

La rimozione dei volumi è deliberatamente separata:

```bash
docker compose down --volumes
```

Quest'ultimo comando elimina i dati persistenti e non deve essere usato durante il normale arresto del laboratorio.

## Attività successive

Backup, ripristino, collaudo completo di riavvio, hardening finale e prove con nuovi report reali vengono demandati alla fase 11.
