# Roadmap completa

## Obiettivo generale

Costruire un gateway Ubuntu attraverso cui far passare il traffico di dispositivi autorizzati, osservarlo in modo difensivo, analizzarne i log con Python e visualizzare statistiche aggregate tramite servizi Docker separati dal routing.

## Architettura finale

```text
Client autorizzato
      |
      v
Hotspot Realtek USB
      |
      v
Ubuntu gateway
    |-- DHCP / DNS locale
    |-- routing e NAT
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
MediaTek interna
      |
      v
Internet
```

## Sequenza delle fasi

| Fase | Documento | Risultato richiesto | Stato attuale |
|---:|---|---|---|
| 1 | [`steps/01-inventario-hardware-rete.md`](steps/01-inventario-hardware-rete.md) | Identificare hardware, driver, interfacce e uplink | COMPLETATO |
| 2 | [`steps/02-topologia-e-indirizzamento.md`](steps/02-topologia-e-indirizzamento.md) | Definire nomi, subnet, gateway e percorso | COMPLETATO |
| 3 | [`steps/03-hotspot-realtek.md`](steps/03-hotspot-realtek.md) | Creare un hotspot stabile | COMPLETATO |
| 4 | [`steps/04-dhcp-routing-nat.md`](steps/04-dhcp-routing-nat.md) | Verificare DHCP, DNS, forwarding, NAT e Wi-Fi | COMPLETATO |
| 5 | [`steps/05-firewall-nftables.md`](steps/05-firewall-nftables.md) | Applicare filtro stateful, log e persistenza | COMPLETATO |
| 6 | [`steps/06-cattura-tcpdump.md`](steps/06-cattura-tcpdump.md) | Verificare filtri, protocolli, NAT e PCAP | COMPLETATO |
| 7 | [`steps/07-suricata.md`](steps/07-suricata.md) | Produrre e verificare avvisi IDS | COMPLETATO |
| 8 | [`steps/08-zeek.md`](steps/08-zeek.md) | Generare log di rete strutturati | COMPLETATO |
| 9 | [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md) | Leggere log, produrre statistiche e correlare sensori | COMPLETATO |
| 10 | [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md) | Salvare e visualizzare dati aggregati | COMPLETATO |
| 11 | [`steps/11-test-hardening-backup.md`](steps/11-test-hardening-backup.md) | Test finali, hardening, backup e ripristino | PROSSIMO |

## Fasi 1–5 — Gateway e firewall

Sono stati verificati inventario hardware, topologia, hotspot, DHCP/DNS, forwarding, NAT, WPA2-RSN/CCMP e firewall `nftables` stateful con servizio systemd dedicato e persistenza dopo riavvio.

## Fase 6 — tcpdump

Completata il 18 luglio 2026. Verificati filtri BPF, DNS, ICMP, handshake TCP, traffico cifrato, confronto prima/dopo NAT, decremento TTL, PCAP privato limitato e AppArmor attivo.

## Fase 7 — Suricata

Completata il 20 luglio 2026. Verificati Suricata 8.0.3, AF_PACKET, Hyperscan, oltre 52.000 regole, eventi applicativi, alert controllato, avvio su richiesta e rotazione reale dei log.

## Fase 8 — Zeek

Completata il 21 luglio 2026. Verificati Zeek 8.0.9, ZeekControl, nodo standalone, log JSON `conn`, `dns`, `ssl` e `quic`, cattura senza drop kernel e archiviazione all'arresto.

## Fase 9 — Python

Completata il 21 luglio 2026.

Componenti:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/analyze-lab
python/tests/test_phase9.py
```

Verificati analisi streaming, gzip, esportazione JSON, privacy, correlazione tramite 5-tupla/timestamp e 23 test automatici.

Sessione reale sovrapposta:

```text
Connessioni Zeek:                       35
Eventi Suricata:                       318
Eventi Suricata correlati:             101
Connessioni Zeek distinte abbinate:     33
Copertura connessioni Zeek:          94,29%
Delta temporale medio:                0,027 s
Delta temporale massimo:              0,330 s
```

## Fase 10 — Docker

Completata e verificata il 30 luglio 2026.

Architettura applicativa:

```text
report aggregati fase 9
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
```

Realizzato:

1. schema PostgreSQL `report_imports` con campo `JSONB`;
2. vista `latest_report_imports`;
3. importazione idempotente tramite hash SHA-256;
4. controllo delle dichiarazioni di privacy prima dell'importazione;
5. volume persistente PostgreSQL;
6. rete `backend` interna;
7. account PostgreSQL read-only per Grafana;
8. provisioning automatico del datasource;
9. provisioning automatico della dashboard;
10. rete `frontend` separata;
11. Grafana pubblicato soltanto su `127.0.0.1:3000`;
12. healthcheck per database e dashboard;
13. container importer non root, read-only e senza capability.

Campione verificato:

```text
Eventi Zeek validi:       4
Eventi Suricata validi:   8
Eventi correlati:         5
Delta temporale medio:    0,440 s
Importazioni PostgreSQL:  3
```

Una seconda importazione dello stesso contenuto non crea duplicati.

```text
Guida:           docs/steps/10-database-dashboard-docker.md
Report pubblico: samples/10-database-dashboard-docker-report.md
```

## Fase 11 — Test, hardening, backup e ripristino

Prossime verifiche:

- arresto e riavvio completo dello stack Docker;
- persistenza dei dati dopo riavvio;
- backup PostgreSQL con `pg_dump`;
- ripristino in database di prova;
- verifica dei volumi Grafana/PostgreSQL;
- test con un nuovo report reale;
- controllo finale delle porte pubblicate;
- controllo delle capability e dei privilegi dei container;
- verifica delle reti Docker e dell'isolamento;
- prova di uplink assente;
- isolamento tra client;
- casi `ct state invalid` controllati;
- spazio disco e rotazione log;
- procedura di rollback completa;
- verifica finale di privacy prima della pubblicazione.

## Criterio di completamento del progetto

Il progetto è completato quando un dispositivo autorizzato:

1. si collega all'hotspot;
2. riceve configurazione IP corretta;
3. usa Ubuntu come unico gateway;
4. raggiunge Internet tramite MediaTek;
5. è filtrato da nftables;
6. genera log Suricata e Zeek;
7. compare nei report Python;
8. produce dati importabili in PostgreSQL;
9. compare nella dashboard Grafana;
10. continua a funzionare dopo i test finali;
11. può essere fermato, ripristinato e sottoposto a backup con procedure documentate.
