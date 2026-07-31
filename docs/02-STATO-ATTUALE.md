# Stato attuale del progetto

Ultimo aggiornamento operativo: 31 luglio 2026.

## Obiettivo principale

Costruire un gateway fisico Ubuntu nel quale:

- la Wi-Fi interna fornisce l'uscita Internet;
- una Wi-Fi USB crea l'hotspot di laboratorio;
- Ubuntu esegue routing, firewall, NAT e monitoraggio;
- Suricata e Zeek producono eventi e log;
- Python analizza e correla i log;
- Docker ospita importer, PostgreSQL e Grafana senza gestire il routing principale;
- l'host viene sottoposto a hardening verificato senza interrompere il ruolo di gateway.

## Stato sintetico

| Fase | Stato | Nota |
|---:|---|---|
| 1. Inventario hardware e rete | COMPLETATA | Hardware, driver, route e modalità AP verificati |
| 2. Topologia e indirizzamento | COMPLETATA | Subnet e percorso definiti senza conflitti |
| 3. Hotspot Realtek | COMPLETATA | Hotspot, client, gateway e rollback verificati |
| 4. DHCP, routing e NAT | COMPLETATA | DHCP, DNS, forwarding, NAT e WPA2 verificati |
| 5. Firewall nftables | COMPLETATA | INPUT, FORWARD, logging e persistenza verificati |
| 6. tcpdump | COMPLETATA | DNS, ICMP, TCP, NAT, PCAP e AppArmor verificati |
| 7. Suricata | COMPLETATA | IDS passivo, regole, alert controllato e logrotate verificati |
| 8. Zeek | COMPLETATA | Log JSON DNS/TLS/QUIC e gestione on demand verificati |
| 9. Python | COMPLETATA | Analisi, correlazione, report JSON e 23 test verificati |
| 10. Docker dashboard | COMPLETATA | PostgreSQL, importer idempotente, Grafana e isolamento verificati |
| 11. Hardening | VERIFICATO | sysctl, servizi, permessi, firewall, update policy e socket verificati |
| 11. Backup / restore | DA COLLAUDARE | `pg_dump`, restore di prova e recovery finale ancora aperti |

## Percorso verificato

```text
Client autorizzato
  -> hotspot Wi-Fi USB
  -> Ubuntu gateway
  -> nftables INPUT/FORWARD
  -> Suricata IDS + Zeek
  -> analisi/correlazione Python
  -> report aggregati
  -> importer Docker
  -> PostgreSQL
  -> Grafana locale
  -> NAT/masquerading
  -> uplink Wi-Fi interno
  -> Internet
```

## Fase 9 - risultati Python

Sessione reale sovrapposta:

```text
Connessioni Zeek:                       35
Connessioni Zeek abbinate:              33
Copertura connessioni Zeek:          94,29%
Eventi Suricata:                       318
Eventi Suricata correlati:             101
Delta temporale medio:                0,027 s
Delta temporale massimo:              0,330 s
Test automatici:                         23
```

## Fase 10 - PostgreSQL e Grafana

Stack verificato:

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
grafana_reader - read only
        |
        v
Grafana 13 - 127.0.0.1:3000
```

PostgreSQL non pubblica la porta sull'host; l'importer è non root e idempotente; Grafana usa provisioning versionato e un account database in sola lettura.

![Dashboard Grafana](images/10-grafana-dashboard.svg)

## Fase 11 - hardening verificato

Aggiunti al repository:

```text
scripts/hardening_audit.py
configs/sysctl/99-security-gateway-hardening.conf
samples/11-hardening-report.md
docs/images/11-hardening-summary.svg
```

Valori finali principali:

```text
net.ipv4.ip_forward = 1
net.ipv4.conf.all.rp_filter = 2
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.tcp_syncookies = 1
```

Verificato inoltre:

- 0 unità systemd fallite al termine;
- nessun server SSH in ascolto;
- `logrotate` riparato dopo la rimozione di una configurazione Suricata duplicata dalla directory attiva;
- VirtualBox inutilizzato disabilitato senza disattivare Secure Boot;
- Avahi/mDNS disabilitato e UDP/5353 non più in ascolto;
- Docker socket non accessibile all'utente normale;
- nessun file world-writable nelle aree sensibili controllate;
- `unattended-upgrades` abilitato;
- rete, Internet e DNS funzionanti dopo il sysctl hardening.

![Riepilogo hardening](images/11-hardening-summary.svg)

## Servizi e modalità operative

```text
security-gateway-firewall.service: enabled / active (exited)
Suricata al boot:                   disabled - avvio on demand
Zeek al boot:                       non configurato - uso on demand
hotspot:                            avvio manuale
PostgreSQL/Grafana:                 Docker Compose on demand
SSH server:                         assente
Avahi/mDNS:                         disabled
VirtualBox service:                 disabled - non usato
unattended-upgrades:                enabled
```

## Stato reale della fase 11

La parte **hardening** è completata e verificata.

Restano aperti:

1. backup PostgreSQL con `pg_dump`;
2. restore in database di prova;
3. recovery/smontaggio completo;
4. test end-to-end specifici di backup e ripristino.

Questi elementi non vengono marcati come completati finché non saranno provati.

## Materiale pubblico recente

Guide:

- [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md)
- [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md)
- [`steps/11-test-hardening-backup.md`](steps/11-test-hardening-backup.md)

Report:

- [`../samples/09-python-log-analysis-report.md`](../samples/09-python-log-analysis-report.md)
- [`../samples/10-database-dashboard-docker-report.md`](../samples/10-database-dashboard-docker-report.md)
- [`../samples/11-hardening-report.md`](../samples/11-hardening-report.md)

## Privacy

Gli output completi restano in `reports/`, esclusa da Git. Non vengono pubblicati password, token, MAC reali, hostname, percorsi personali, PCAP grezzi, log integrali, query DNS personali, SNI TLS, certificati o credenziali PostgreSQL/Grafana.
