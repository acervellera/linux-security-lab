# Lavoro svolto e prossimi passi

## Funzione del documento

Questo file riassume l'evoluzione reale del gateway fisico Ubuntu. Per lo stato più aggiornato usare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md); per comandi e rollback usare le guide in [`steps`](steps).

## Gateway fisico

```text
Telefono / dispositivo autorizzato
  -> SecurityGatewayLab
  -> Realtek USB AP
  -> Ubuntu gateway
  -> nftables INPUT e FORWARD
  -> Suricata IDS e Zeek standalone
  -> analisi Python
  -> report aggregati
  -> Docker: importer -> PostgreSQL -> Grafana
  -> NAT/masquerading
  -> MediaTek uplink
  -> router
  -> Internet
```

## Fasi 1–5 completate — Gateway e firewall

Sono stati verificati inventario hardware, topologia, hotspot, DHCP/DNS, forwarding, NAT, WPA2-RSN/CCMP, firewall `nftables` stateful, logging, rollback, servizio systemd dedicato e persistenza dopo riavvio.

## Fase 6 completata — tcpdump

Completata il 18 luglio 2026. Verificati filtri BPF, DNS, ICMP, handshake TCP, traffico cifrato, NAT sui due lati, decremento TTL, PCAP privato limitato, permessi `600` e AppArmor.

```text
Report pubblico: samples/06-cattura-tcpdump-report.md
Report privato:  reports/06-cattura-tcpdump-private.md
```

## Fase 7 completata — Suricata IDS

Completata il 20 luglio 2026. Verificati Suricata 8.0.3, AF_PACKET, Hyperscan, `HOME_NET`, oltre 52.000 regole, eventi applicativi, alert ICMP controllato, avvio on demand e rotazione reale di `eve.json`.

```text
Report pubblico: samples/07-suricata-report.md
Report privato:  reports/07-suricata-private.md
```

## Fase 8 completata — Zeek

Completata il 21 luglio 2026. Verificati Zeek 8.0.9, ZeekControl, plugin AF_PACKET/Pcap, nodo standalone, log JSON `conn`, `dns`, `ssl` e `quic`, cattura senza drop kernel e archiviazione all'arresto.

```text
Report pubblico: samples/08-zeek-report.md
Report privato:  reports/08-zeek-private.md
```

## Fase 9 completata — Analisi Python

Completata il 21 luglio 2026.

Codice:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/analyze-lab
python/tests/test_phase9.py
```

Verificati lettura streaming, gzip, statistiche Zeek/Suricata, report JSON aggregati senza IP grezzi o UID Zeek, correlazione tramite 5-tupla e timestamp e 23 test automatici.

Sessione reale sovrapposta:

```text
Connessioni Zeek:                       35
Connessioni Zeek abbinate:              33
Eventi Suricata:                       318
Eventi Suricata correlati:             101
Copertura connessioni Zeek:          94,29%
Delta temporale medio:                0,027 s
Delta temporale massimo:              0,330 s
```

Durante l'avvio della fase 10 è stato corretto un caso reale in `analyze-lab`: un log Zeek trovato con `sudo find` poteva risultare non visibile al successivo `[[ -e ... ]]` eseguito come utente normale. Il controllo usa ora `sudo test -e` quando necessario.

```text
Report pubblico: samples/09-python-log-analysis-report.md
Report privato:  reports/09-python-log-analysis-private.md
```

## Fase 10 completata — Database e dashboard Docker

Completata e verificata il 30 luglio 2026.

### Stack

```text
report JSON aggregati
        |
        v
importer Python non root
        |
        v
PostgreSQL 17
        |
        v
grafana_reader
        |
        v
Grafana 13
        |
        v
127.0.0.1:3000
```

### Importer

L'importer:

- legge `zeek-latest.json`, `suricata-latest.json` e `correlation-latest.json`;
- verifica le dichiarazioni di privacy;
- rimuove `source` e `sources`;
- calcola un hash SHA-256 stabile;
- inserisce il documento in PostgreSQL come `JSONB`;
- usa `ON CONFLICT DO NOTHING` per l'idempotenza.

Il container viene eseguito come UID/GID `10001:10001`, con filesystem read-only, `cap_drop: ALL`, `no-new-privileges` e report montati in sola lettura.

### PostgreSQL

Realizzati:

```text
docker/database/init/001-schema.sql
docker/database/002-grafana-reader.sql
```

La tabella `report_imports` usa un vincolo univoco su `(report_kind, content_sha256)`. La vista `latest_report_imports` restituisce il report più recente per tipo.

PostgreSQL usa il volume `postgres_data` e non pubblica la porta `5432` sull'host.

### Grafana

Grafana usa provisioning versionato per datasource e dashboard.

Il datasource si collega con l'account PostgreSQL dedicato `grafana_reader`, configurato in sola lettura.

La dashboard è raggiungibile soltanto tramite:

```text
http://127.0.0.1:3000
```

Il backend Docker è una rete `internal`; Grafana possiede inoltre una rete `frontend` separata per il binding locale.

### Dati verificati

Il primo collaudo ha usato campioni sintetici della fase 9.

PostgreSQL contiene tre importazioni:

```text
zeek         c099a80904a2
suricata     124fb2b03eb6
correlation  0712ed6b8d67
```

Dashboard:

```text
Eventi Zeek validi:       4
Eventi Suricata validi:   8
Eventi correlati:         5
Delta temporale medio:    0,440 s
```

Una seconda esecuzione dell'importer non ha creato duplicati.

![Dashboard Grafana](images/10-grafana-dashboard.svg)

```text
Guida:           docs/steps/10-database-dashboard-docker.md
Report pubblico: samples/10-database-dashboard-docker-report.md
```

## Stato corrente

| Fase | Stato |
|---:|---|
| 1. Inventario | COMPLETATA |
| 2. Topologia | COMPLETATA |
| 3. Hotspot | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | COMPLETATA |
| 7. Suricata | COMPLETATA |
| 8. Zeek | COMPLETATA |
| 9. Python | COMPLETATA |
| 10. Docker | COMPLETATA |
| 11. Test e hardening | PROSSIMA |

## Prossimi passi immediati

Passare alla fase 11 e verificare, nell'ordine:

1. arresto non distruttivo dello stack;
2. riavvio di PostgreSQL e Grafana;
3. persistenza delle tre importazioni;
4. nuovo report reale dopo una sessione autorizzata;
5. backup PostgreSQL con `pg_dump`;
6. ripristino in un database di prova;
7. controllo finale delle porte pubblicate;
8. controllo di reti, capability e privilegi dei container;
9. hardening e rollback finale;
10. verifica conclusiva di privacy e documentazione.

## Report pubblici e privati

Nel repository pubblico:

- guide revisionate;
- configurazioni parametrizzate;
- script commentati;
- report principali anonimizzati;
- campioni sintetici;
- screenshot revisionati.

Restano locali e ignorati da Git:

```text
reports/
docker/.env
docker/data/
```

Non pubblicare password, token, MAC, PCAP grezzi, log integrali, query DNS personali, SNI TLS, certificati, valore di `digest_salt`, password PostgreSQL/Grafana o traffico di terzi.
