# Stato attuale del progetto

Ultimo aggiornamento operativo: 30 luglio 2026.

## Obiettivo principale

Costruire un gateway fisico Ubuntu nel quale:

- la scheda Wi-Fi interna MediaTek fornisce l'uscita Internet;
- la scheda Wi-Fi USB Realtek crea l'hotspot per i dispositivi di laboratorio;
- Ubuntu esegue routing, firewall, NAT e monitoraggio;
- Suricata e Zeek producono eventi e log;
- Python analizza e correla i log;
- Docker ospita importer, PostgreSQL e Grafana senza gestire il routing principale.

## Fasi completate

### Fase 1 — Inventario hardware e rete

Verificati sistema, kernel, MediaTek, Realtek, driver, supporto AP, route, rfkill e reti Docker esistenti.

### Fase 2 — Topologia e indirizzamento

```text
UPLINK_IF=wlp13s0
AP_IF=wlx<REDACTED>
LAB_SUBNET=10.42.0.0/24
GATEWAY_IP=10.42.0.1
DNS_SERVER=10.42.0.1
HOTSPOT_PROFILE=security-gateway-ap
LAB_SSID=SecurityGatewayLab
WIFI_BAND=2.4GHz
WIFI_CHANNEL=6
```

La subnet non si sovrappone alle reti osservate sul sistema.

### Fase 3 — Hotspot Realtek

Verificati modalità AP, client reali autenticati, gateway `10.42.0.1`, raggiungibilità client→gateway, uplink mantenuto sulla MediaTek e rollback del profilo.

### Fase 4 — DHCP, routing e NAT

Completata il 16 luglio 2026.

Verificati DHCP, DNS locale, `net.ipv4.ip_forward=1`, forwarding, masquerading, traffico prima e dopo il NAT, DNS classico, TCP/443, UDP/443 e WPA2-RSN/CCMP.

### Fase 5 — Firewall nftables

Completata il 17 luglio 2026.

Verificati filtro `INPUT`, filtro `FORWARD` stateful, blocchi tra reti non previste, logging con rate limit, rollback, coesistenza con NetworkManager/Docker/libvirt, servizio systemd dedicato e persistenza dopo riavvio.

### Fase 6 — Cattura tcpdump

Completata il 18 luglio 2026.

Verificati filtri BPF, DNS, ICMP, handshake TCP, traffico cifrato, confronto prima/dopo NAT, decremento TTL, PCAP privato limitato, permessi `600` e AppArmor attivo.

### Fase 7 — Suricata IDS

Completata il 20 luglio 2026.

Verificati Suricata 8.0.3, AF_PACKET, Hyperscan, `HOME_NET=10.42.0.0/24`, oltre 52.000 regole, eventi flow/DNS/TLS/QUIC/HTTP/DHCP, alert controllato, avvio on demand e rotazione reale di `eve.json`.

### Fase 8 — Zeek

Completata il 21 luglio 2026.

Verificati Zeek 8.0.9, ZeekControl, plugin AF_PACKET/Pcap, nodo standalone sull'hotspot, rete locale `10.42.0.0/24`, JSON logs, cattura senza drop kernel, log `conn`, `dns`, `ssl` e `quic`, archiviazione all'arresto e uso on demand.

### Fase 9 — Analisi Python

Completata il 21 luglio 2026.

Programmi:

```text
python/read_zeek_json.py
python/read_suricata_json.py
python/correlate_logs.py
python/analyze-lab
python/tests/test_phase9.py
```

Risultati:

- lettura streaming di JSON Lines e gzip;
- statistiche Zeek e Suricata;
- report aggregati senza IP grezzi o UID Zeek;
- correlazione bidirezionale tramite 5-tupla e timestamp;
- comando unico `analyze-lab`;
- 23 test automatici superati;
- sessione reale con 33 connessioni Zeek abbinate su 35;
- 101 eventi Suricata correlati;
- delta temporale medio di 0,027 secondi.

### Fase 10 — Database e dashboard Docker

Completata e verificata il 30 luglio 2026.

Architettura:

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
grafana_reader (SELECT only)
        |
        v
Grafana 13
        |
        v
127.0.0.1:3000
```

Componenti:

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

Verifiche:

- PostgreSQL avviato con healthcheck e volume persistente;
- porta PostgreSQL non pubblicata sull'host;
- importer Python eseguito come utente non root;
- report montati in sola lettura;
- tre report sintetici importati: Zeek, Suricata e correlazione;
- hash SHA-256 e vincolo univoco per impedire duplicati;
- seconda importazione idempotente;
- account `grafana_reader` limitato alla sola lettura;
- datasource Grafana provisionato automaticamente;
- dashboard `Linux Security Lab — Fase 10` caricata automaticamente;
- Grafana pubblicato soltanto su `127.0.0.1:3000`;
- rete `backend` interna separata dalla rete `frontend`;
- dashboard verificata nel browser.

Metriche del campione visualizzate:

```text
Eventi Zeek validi:       4
Eventi Suricata validi:   8
Eventi correlati:         5
Delta temporale medio:    0,440 s
```

![Dashboard Grafana](images/10-grafana-dashboard.svg)

```text
Guida:           docs/steps/10-database-dashboard-docker.md
Report pubblico: samples/10-database-dashboard-docker-report.md
```

## Percorso verificato

```text
Client 10.42.0.x
  -> Realtek 10.42.0.1
  -> nftables INPUT/FORWARD
  -> Suricata IDS e Zeek standalone
  -> analisi Python
  -> report aggregati
  -> importer Docker
  -> PostgreSQL
  -> Grafana locale
  -> NAT/masquerading NetworkManager
  -> MediaTek 192.168.10.x
  -> router
  -> Internet
```

## Stato delle fasi

| Fase | Stato | Nota |
|---:|---|---|
| 1. Inventario hardware e rete | COMPLETATA | Hardware, driver, route, rfkill e modalità AP verificati |
| 2. Topologia e indirizzamento | COMPLETATA | Subnet e percorso definiti senza conflitti |
| 3. Hotspot Realtek | COMPLETATA | Hotspot, client, gateway e rollback verificati |
| 4. DHCP, routing e NAT | COMPLETATA | DHCP, DNS, forwarding, NAT e WPA2-RSN/CCMP verificati |
| 5. Firewall nftables | COMPLETATA | INPUT, FORWARD, log, rollback, systemd e persistenza verificati |
| 6. tcpdump | COMPLETATA | DNS, ICMP, handshake TCP, NAT, PCAP e AppArmor verificati |
| 7. Suricata | COMPLETATA | IDS passivo, regole, alert controllato e logrotate verificati |
| 8. Zeek | COMPLETATA | Log JSON DNS/TLS/QUIC, ZeekControl e archiviazione verificati |
| 9. Python | COMPLETATA | Analisi, report JSON, correlazione, comando unico e test verificati |
| 10. Docker dashboard | COMPLETATA | PostgreSQL, importer idempotente, Grafana e isolamento verificati |
| 11. Test e hardening | PROSSIMA | Riavvio completo, backup, ripristino e hardening finale |

## Servizi e modalità operative

```text
security-gateway-firewall.service: enabled / active (exited)
nftables.service standard:         disabled / inactive
Suricata al boot:                   disabled
Zeek al boot:                       non configurato
hotspot:                            avvio manuale
PostgreSQL/Grafana:                 Docker Compose on demand
```

## Materiale pubblico più recente

Guide:

- [`steps/08-zeek.md`](steps/08-zeek.md);
- [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md);
- [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md).

Report:

- [`../samples/08-zeek-report.md`](../samples/08-zeek-report.md);
- [`../samples/09-python-log-analysis-report.md`](../samples/09-python-log-analysis-report.md);
- [`../samples/10-database-dashboard-docker-report.md`](../samples/10-database-dashboard-docker-report.md).

## Vincoli di pubblicazione

Non pubblicare password Wi-Fi, SSID domestici, MAC reali, nome completo `wlx...`, hostname o percorsi personali, IP e porte complete non necessarie, PCAP grezzi, query DNS personali, log integrali, file `eve.json` completi, log Zeek integrali, SNI TLS, certificati, `digest_salt`, password PostgreSQL o password Grafana.

Gli output completi restano in `reports/`, esclusa da Git. `docker/.env` e `docker/data/` sono anch'essi esclusi dal repository.

## Prossima azione

Passare alla fase 11: arresto e riavvio completo dello stack, backup PostgreSQL, ripristino controllato, hardening finale e verifica del rollback.
