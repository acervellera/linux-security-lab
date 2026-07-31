# Ubuntu Security Gateway Lab

Laboratorio didattico per costruire un gateway di sicurezza su Ubuntu e imparare, passo dopo passo:

- networking Linux;
- hotspot Wi-Fi;
- DHCP, routing e NAT;
- firewall con `nftables`;
- servizi e persistenza con systemd;
- cattura del traffico con `tcpdump`;
- rilevamento con Suricata;
- analisi dei log con Zeek;
- programmazione Python applicata alla sicurezza;
- database PostgreSQL e dashboard Grafana con Docker.

> Usare il progetto esclusivamente su reti, sistemi e dispositivi propri o esplicitamente autorizzati.

## Architettura principale

```text
Telefono / dispositivo autorizzato
                    |
                    v
        Realtek USB usata come hotspot
                    |
                    v
              Ubuntu gateway
              |-- DHCP e DNS locale
              |-- routing IPv4 e NAT
              |-- nftables INPUT/FORWARD
              |-- servizio systemd dedicato
              |-- tcpdump
              |-- Suricata
              |-- Zeek
              |-- Python
              `-- Docker
                    |-- importer Python
                    |-- PostgreSQL
                    `-- Grafana
                    |
                    v
        MediaTek interna usata come uplink
                    |
                    v
                 Internet
```

## Stato verificato

Le prime dieci fasi sono completate:

1. hardware e rete inventariati;
2. piano IP definito;
3. hotspot reale verificato;
4. DHCP, routing e NAT verificati;
5. firewall `nftables` stateful reso persistente;
6. catture tcpdump con DNS, ICMP, handshake TCP, NAT e PCAP controllato verificate;
7. Suricata IDS passivo con alert controllato, avvio on demand e rotazione log verificato;
8. Zeek 8.0.9 configurato come sensore standalone con log JSON DNS, TLS e QUIC verificati;
9. analizzatori Python per Zeek e Suricata, report JSON, correlazione e test automatici verificati;
10. importazione idempotente in PostgreSQL e dashboard Grafana Docker verificate.

La fase 11, test finali, hardening, backup e ripristino, è la prossima attività.

| Fase | Stato |
|---:|---|
| 1. Inventario hardware e rete | COMPLETATA |
| 2. Topologia e indirizzamento | COMPLETATA |
| 3. Hotspot Realtek | COMPLETATA |
| 4. DHCP, routing e NAT | COMPLETATA |
| 5. Firewall nftables | COMPLETATA |
| 6. tcpdump | COMPLETATA |
| 7. Suricata | COMPLETATA |
| 8. Zeek | COMPLETATA |
| 9. Python | COMPLETATA |
| 10. Docker dashboard | COMPLETATA |
| 11. Test e hardening | PROSSIMA |

## Risultati della fase 9

Sono stati realizzati:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/analyze-lab
python/tests/test_phase9.py
```

Funzionalità verificate:

- lettura streaming di JSON Lines e gzip;
- analisi di `conn.log` Zeek;
- analisi di Suricata `eve.json`;
- report testuali e JSON;
- esclusione di IP grezzi e UID dai report;
- correlazione bidirezionale tramite 5-tupla e timestamp;
- comando unico per coordinare le analisi;
- 23 test automatici superati.

Nella sessione reale con entrambi i sensori attivi, 33 delle 35 connessioni Zeek hanno trovato almeno un evento Suricata compatibile. Il delta temporale medio era 0,027 secondi.

## Risultati della fase 10

È stato realizzato uno stack applicativo Docker separato dal routing del gateway:

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
grafana_reader (sola lettura)
        |
        v
Grafana 13 su 127.0.0.1:3000
```

Verifiche principali:

- `docker compose config --quiet` riuscito;
- importer costruito ed eseguito come utente non root;
- PostgreSQL con volume persistente e senza porta pubblicata;
- tre report importati: Zeek, Suricata e correlazione;
- hash SHA-256 e vincolo univoco per evitare duplicati;
- seconda importazione idempotente;
- account PostgreSQL `grafana_reader` in sola lettura;
- datasource Grafana provisionato automaticamente;
- dashboard `Linux Security Lab — Fase 10` caricata automaticamente;
- Grafana pubblicato soltanto su `127.0.0.1:3000`;
- backend Docker interno separato dalla rete frontend.

Metriche del campione sintetico visualizzate nella dashboard:

```text
Eventi Zeek validi:       4
Eventi Suricata validi:   8
Eventi correlati:         5
Delta temporale medio:    0,440 s
```

![Dashboard Grafana fase 10](docs/images/10-grafana-dashboard.svg)

## Metodo di lavoro

Ogni fase contiene:

1. obiettivo;
2. teoria necessaria;
3. prerequisiti;
4. comandi commentati;
5. spiegazione delle opzioni;
6. risultati realmente osservati;
7. test di verifica;
8. problemi incontrati;
9. rollback;
10. stato finale.

Una fase viene segnata come completata soltanto dopo una verifica reale. Gli aspetti non testati attivamente vengono dichiarati.

## Da dove iniziare

1. [Obiettivi e architettura](docs/OBIETTIVI_E_PROGETTO.md)
2. [Stato attuale](docs/02-STATO-ATTUALE.md)
3. [Roadmap completa](docs/00-ROADMAP.md)
4. [Indice della documentazione](docs/README.md)
5. [Guide operative](docs/steps)

Guide più recenti:

- [`docs/steps/08-zeek.md`](docs/steps/08-zeek.md);
- [`docs/steps/09-python-log-analysis.md`](docs/steps/09-python-log-analysis.md);
- [`docs/steps/10-database-dashboard-docker.md`](docs/steps/10-database-dashboard-docker.md);
- [`docs/steps/11-test-hardening-backup.md`](docs/steps/11-test-hardening-backup.md).

## Report pubblici

Ogni fase completata possiede un report principale nella radice di `samples/`.

Report più recenti:

```text
samples/06-cattura-tcpdump-report.md
samples/07-suricata-report.md
samples/08-zeek-report.md
samples/09-python-log-analysis-report.md
samples/10-database-dashboard-docker-report.md
```

## Report privati

`reports/` contiene materiale locale e sensibile ed è esclusa tramite `.gitignore`.

I PCAP e i log integrali non vengono pubblicati. Anche `docker/.env` e `docker/data/` restano locali e ignorati da Git.

## Componenti verificati

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/analyze-lab
docker/compose.yaml
docker/database/init/001-schema.sql
docker/database/002-grafana-reader.sql
docker/importer/importer.py
docker/grafana/provisioning/datasources/postgres.yaml
docker/grafana/provisioning/dashboards/security-lab.yaml
docker/grafana/dashboards/security-lab-overview.json
```

Suricata e Zeek restano installati sull'host e vengono usati su richiesta durante le sessioni di laboratorio. Docker gestisce soltanto i servizi applicativi della fase 10.

## Struttura del repository

```text
.
|-- README.md
|-- SECURITY.md
|-- CONTRIBUTING.md
|-- docs/
|   |-- README.md
|   |-- OBIETTIVI_E_PROGETTO.md
|   |-- LAVORO_SVOLTO_E_PROSSIMI_PASSI.md
|   |-- 00-ROADMAP.md
|   |-- 01-METODO-DI-LAVORO.md
|   |-- 02-STATO-ATTUALE.md
|   |-- images/
|   `-- steps/
|-- configs/
|-- scripts/
|-- python/
|-- docker/
|-- samples/
`-- reports/      privato e ignorato da Git
```

## Privacy

Non pubblicare password Wi-Fi, SSID domestici, token, chiavi, MAC, nomi completi `wlx...`, hostname o percorsi personali, IP e porte completi non necessari, query DNS personali, PCAP grezzi, log integrali, file `eve.json` completi, log Zeek integrali, SNI TLS, certificati, credenziali PostgreSQL/Grafana o traffico appartenente a terzi.

## Licenza

Il progetto è distribuito con licenza MIT.
