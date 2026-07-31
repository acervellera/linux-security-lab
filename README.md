# Ubuntu Security Gateway Lab

Laboratorio didattico e difensivo per costruire un gateway di sicurezza su Ubuntu e verificare, passo dopo passo, networking, filtering, network monitoring, log analysis, observability e hardening.

> Usare il progetto esclusivamente su reti, sistemi e dispositivi propri o esplicitamente autorizzati.

## Architettura

```text
Dispositivo autorizzato
        |
        v
Realtek USB - hotspot Wi-Fi
        |
        v
Ubuntu security gateway
  |-- DHCP / DNS locale
  |-- routing IPv4 + NAT
  |-- nftables INPUT/FORWARD
  |-- tcpdump
  |-- Suricata IDS
  |-- Zeek
  |-- Python analytics + correlation
  |-- hardening / audit
  `-- Docker observability
        |-- importer Python non root
        |-- PostgreSQL 17
        `-- Grafana 13 - 127.0.0.1:3000
        |
        v
MediaTek interna - uplink
        |
        v
Internet
```

## Stato verificato

Le fasi 1-10 sono completate. La fase 11 ha completato e verificato il blocco di **hardening**, mentre backup e ripristino PostgreSQL restano da collaudare prima di dichiarare conclusa l'intera fase originariamente pianificata.

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
| 9. Python log analysis | COMPLETATA |
| 10. PostgreSQL + Grafana Docker | COMPLETATA |
| 11. Hardening | VERIFICATO |
| 11. Backup / restore | DA COLLAUDARE |

## Risultati tecnici principali

### Network gateway e firewall

Sono stati verificati:

- hotspot Wi-Fi reale;
- DHCP e DNS locale;
- IPv4 forwarding e NAT;
- firewall `nftables` stateful;
- logging rate-limited;
- servizio systemd dedicato e persistenza dopo reboot;
- coesistenza con NetworkManager, Docker e libvirt.

### tcpdump, Suricata e Zeek

Il laboratorio produce osservabilità a più livelli:

```text
pacchetti -> tcpdump
          -> Suricata IDS
          -> Zeek structured logs
          -> Python analysis/correlation
```

Suricata è stato verificato con AF_PACKET, oltre 52.000 regole, eventi applicativi e un alert controllato.

Zeek 8.0.9 è stato configurato come sensore standalone con log JSON per connessioni, DNS, TLS e QUIC.

### Python - analisi e correlazione

Componenti principali:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/analyze-lab
python/tests/test_phase9.py
```

Risultati della sessione reale sovrapposta:

```text
Connessioni Zeek:                       35
Connessioni Zeek abbinate:              33
Copertura connessioni Zeek:          94,29%
Eventi Suricata:                       318
Eventi Suricata correlati:             101
Delta temporale medio:                0,027 s
Delta temporale massimo:              0,330 s
Test automatici Python:                  23
```

### PostgreSQL e Grafana

La fase 10 aggiunge uno stack applicativo separato dal routing:

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
grafana_reader - SELECT only
        |
        v
Grafana 13 - localhost only
```

Verifiche principali:

- PostgreSQL senza porta pubblicata sull'host;
- volume persistente;
- importazione idempotente tramite SHA-256;
- importer non root, read-only, `cap_drop: ALL`, `no-new-privileges`;
- account `grafana_reader` in sola lettura;
- provisioning automatico del datasource e della dashboard;
- backend Docker interno e frontend separato;
- Grafana pubblicato soltanto su `127.0.0.1:3000`.

![Dashboard Grafana fase 10](docs/images/10-grafana-dashboard.svg)

### Hardening verificato

Il blocco di hardening ha introdotto un audit read-only e un profilo sysctl versionato:

```text
scripts/hardening_audit.py
configs/sysctl/99-security-gateway-hardening.conf
```

Risultati finali principali:

```text
failed systemd units:        0
IPv4 forwarding:             enabled - richiesto dal gateway
rp_filter:                   loose mode
accept ICMP redirects:       disabled
send ICMP redirects:         disabled
source routing:              disabled
martian logging:             enabled
SYN cookies:                 enabled
SSH listener:                absent
Avahi / UDP 5353:            disabled
Docker socket:               restricted
world-writable sensitive:    none found
automatic security updates:  enabled
```

![Riepilogo hardening fase 11](docs/images/11-hardening-summary.svg)

Durante il collaudo sono stati anche risolti due problemi reali:

1. `logrotate.service` falliva per una configurazione Suricata duplicata lasciata nella directory attiva;
2. `virtualbox.service` falliva perché Secure Boot rifiutava `vboxdrv`; VirtualBox, non necessario al lab, è stato disabilitato senza indebolire Secure Boot.

## Metodo di lavoro

Ogni fase viene trattata come un piccolo ciclo di engineering:

1. obiettivo;
2. teoria minima necessaria;
3. inventario;
4. modifica controllata;
5. verifica positiva;
6. verifica negativa quando utile;
7. rollback;
8. privacy review;
9. report pubblico anonimizzato;
10. aggiornamento dello stato del repository.

Una funzione viene dichiarata completata soltanto quando è stata verificata realmente.

## Da dove iniziare

1. [Obiettivi e architettura](docs/OBIETTIVI_E_PROGETTO.md)
2. [Stato attuale](docs/02-STATO-ATTUALE.md)
3. [Roadmap](docs/00-ROADMAP.md)
4. [Indice documentazione](docs/README.md)
5. [Guide operative](docs/steps)

Guide recenti:

- [`docs/steps/08-zeek.md`](docs/steps/08-zeek.md)
- [`docs/steps/09-python-log-analysis.md`](docs/steps/09-python-log-analysis.md)
- [`docs/steps/10-database-dashboard-docker.md`](docs/steps/10-database-dashboard-docker.md)
- [`docs/steps/11-test-hardening-backup.md`](docs/steps/11-test-hardening-backup.md)

## Report pubblici

I report principali anonimizzati sono in [`samples/`](samples/).

Report recenti:

```text
samples/07-suricata-report.md
samples/08-zeek-report.md
samples/09-python-log-analysis-report.md
samples/10-database-dashboard-docker-report.md
samples/11-hardening-report.md
```

## Report privati

`reports/` contiene output locali e sensibili ed è esclusa tramite `.gitignore`.

PCAP, log integrali, file `.env`, dati PostgreSQL locali e altre evidenze non necessarie alla documentazione pubblica non vengono pubblicati.

## Componenti verificati

```text
configs/nftables/security-gateway-input-filter.nft
configs/nftables/security-gateway-filter.nft
configs/sysctl/99-security-gateway-hardening.conf
configs/systemd/security-gateway-firewall.service
scripts/security-gateway-firewall
scripts/hardening_audit.py
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

## Privacy

Non pubblicare password Wi-Fi, SSID domestici, token, chiavi, MAC reali, nomi completi di interfacce che incorporano MAC, hostname, percorsi personali, PCAP grezzi, log integrali, query DNS personali, SNI TLS, certificati, credenziali PostgreSQL/Grafana o traffico appartenente a terzi.

## Cosa resta da fare

Per completare l'intera fase 11 originariamente prevista restano da verificare:

- backup PostgreSQL con `pg_dump`;
- ripristino in un database di prova;
- procedura completa di recovery/smontaggio;
- test end-to-end dedicati al backup/restore.

Questi punti restano esplicitamente aperti invece di essere dichiarati completati senza prova.

## Licenza

MIT.
