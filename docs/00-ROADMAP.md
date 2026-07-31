# Roadmap completa

## Obiettivo generale

Costruire un gateway Ubuntu attraverso cui far passare traffico di dispositivi autorizzati, osservarlo in modo difensivo, analizzare i log con Python, visualizzare statistiche aggregate tramite Docker e ridurre la superficie d'attacco dell'host con hardening verificato.

## Architettura finale

```text
Client autorizzato
      |
      v
Hotspot Wi-Fi USB
      |
      v
Ubuntu security gateway
    |-- DHCP / DNS locale
    |-- routing e NAT
    |-- nftables INPUT/FORWARD
    |-- tcpdump
    |-- Suricata
    |-- Zeek
    |-- Python analytics
    |-- hardening / audit
    `-- Docker
          |-- importer Python
          |-- PostgreSQL
          `-- Grafana
      |
      v
Uplink Wi-Fi interno
      |
      v
Internet
```

## Sequenza delle fasi

| Fase | Documento | Risultato richiesto | Stato attuale |
|---:|---|---|---|
| 1 | [`steps/01-inventario-hardware-rete.md`](steps/01-inventario-hardware-rete.md) | Identificare hardware, driver, interfacce e uplink | COMPLETATO |
| 2 | [`steps/02-topologia-e-indirizzamento.md`](steps/02-topologia-e-indirizzamento.md) | Definire subnet, gateway e percorso | COMPLETATO |
| 3 | [`steps/03-hotspot-realtek.md`](steps/03-hotspot-realtek.md) | Creare un hotspot stabile | COMPLETATO |
| 4 | [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md) | Verificare DHCP, DNS, forwarding e NAT | COMPLETATO |
| 5 | [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md) | Applicare filtro stateful, log e persistenza | COMPLETATO |
| 6 | [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md) | Verificare protocolli, NAT e PCAP | COMPLETATO |
| 7 | [`steps/07-suricata.md`](steps/07-suricata.md) | Produrre e verificare avvisi IDS | COMPLETATO |
| 8 | [`steps/08-zeek.md`](steps/08-zeek.md) | Generare log di rete strutturati | COMPLETATO |
| 9 | [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md) | Analizzare e correlare i sensori | COMPLETATO |
| 10 | [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md) | Salvare e visualizzare dati aggregati | COMPLETATO |
| 11A | [`steps/11-test-hardening-backup.md`](steps/11-test-hardening-backup.md) | Hardening finale e validazione host | VERIFICATO |
| 11B | [`steps/11-test-hardening-backup.md`](steps/11-test-hardening-backup.md) | Backup PostgreSQL, restore e recovery | DA COLLAUDARE |

## Fasi 1-5 - gateway e firewall

Verificati inventario, topologia, hotspot, DHCP/DNS, forwarding, NAT, sicurezza Wi-Fi e firewall `nftables` stateful con servizio systemd dedicato e persistenza.

## Fase 6 - tcpdump

Verificati filtri BPF, DNS, ICMP, handshake TCP, traffico cifrato, confronto prima/dopo NAT, decremento TTL, PCAP privato limitato e AppArmor.

## Fase 7 - Suricata

Verificati Suricata 8.0.3, AF_PACKET, Hyperscan, oltre 52.000 regole, eventi applicativi, alert controllato, uso on demand e rotazione log.

## Fase 8 - Zeek

Verificati Zeek 8.0.9, ZeekControl, nodo standalone, log JSON `conn`, `dns`, `ssl` e `quic`, cattura senza drop kernel e archiviazione all'arresto.

## Fase 9 - Python

Componenti:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/analyze-lab
python/tests/test_phase9.py
```

Sessione reale sovrapposta:

```text
Connessioni Zeek:                       35
Connessioni Zeek distinte abbinate:     33
Copertura connessioni Zeek:          94,29%
Eventi Suricata:                       318
Eventi Suricata correlati:             101
Delta temporale medio:                0,027 s
Delta temporale massimo:              0,330 s
Test automatici:                         23
```

## Fase 10 - Docker

Completata e verificata il 30 luglio 2026.

Realizzati e verificati:

1. PostgreSQL 17 con volume persistente;
2. schema `report_imports` e vista `latest_report_imports`;
3. importazione idempotente tramite SHA-256;
4. importer non root con filesystem read-only;
5. `cap_drop: ALL` e `no-new-privileges`;
6. account PostgreSQL read-only per Grafana;
7. provisioning automatico del datasource;
8. provisioning automatico della dashboard;
9. backend Docker interno;
10. Grafana limitato a `127.0.0.1:3000`.

## Fase 11A - hardening verificato

Completata e verificata il 31 luglio 2026.

Artefatti pubblici:

```text
scripts/hardening_audit.py
configs/sysctl/99-security-gateway-hardening.conf
samples/11-hardening-report.md
docs/images/11-hardening-summary.svg
```

Risultati principali:

```text
failed systemd units:        0
IPv4 forwarding:             enabled
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

Sono stati inoltre risolti:

- errore `logrotate` causato da una configurazione Suricata duplicata;
- servizio VirtualBox fallito e non necessario, disabilitato mantenendo Secure Boot attivo.

La connettività locale, Internet e DNS sono stati verificati dopo le modifiche.

## Fase 11B - backup, restore e recovery

Restano da verificare:

- backup PostgreSQL con `pg_dump`;
- ripristino in database di prova;
- persistenza e recovery dello stack dopo scenario controllato;
- procedura completa di smontaggio/ripristino;
- test finali specifici del percorso backup/restore.

Questa parte resta aperta e non viene marcata completata senza prova reale.

## Criterio di completamento dell'intero progetto

Il progetto può essere dichiarato completamente chiuso quando, oltre alle verifiche già completate, saranno provati anche backup e ripristino del datastore applicativo e la procedura di recovery finale.
