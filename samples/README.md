# Sample pubblici anonimizzati

La cartella `samples/` contiene report pubblici derivati da attività realmente eseguite e revisionati prima della pubblicazione.

## Report principali

```text
01-inventario-hardware-rete-report.md
02-topologia-e-indirizzamento-report.md
03-hotspot-realtek-report.md
04-dhcp-routing-nat-report.md
05-firewall-nftables-report.md
06-cattura-tcpdump-report.md
07-suricata-report.md
08-zeek-report.md
09-python-log-analysis-report.md
10-database-dashboard-docker-report.md
11-hardening-report.md
```

Ogni fase usa un solo report principale nella radice di `samples/`. Output aggiuntivi sono ammessi solo quando aggiungono valore senza duplicare il report principale.

## Fasi recenti

### Fase 7 - Suricata

[`07-suricata-report.md`](07-suricata-report.md) documenta AF_PACKET, regole, eventi applicativi, alert controllato, statistiche di cattura e rotazione di `eve.json`.

### Fase 8 - Zeek

[`08-zeek-report.md`](08-zeek-report.md) documenta Zeek 8.0.9, log JSON, configurazione standalone, cattura e gestione on demand.

### Fase 9 - Python

[`09-python-log-analysis-report.md`](09-python-log-analysis-report.md) documenta analizzatori Python, report JSON, privacy, correlazione tra sensori e 23 test automatici.

### Fase 10 - PostgreSQL e Grafana

[`10-database-dashboard-docker-report.md`](10-database-dashboard-docker-report.md) documenta PostgreSQL, importer non root, idempotenza SHA-256, account `grafana_reader`, provisioning Grafana e isolamento Docker.

Immagine pubblica:

```text
docs/images/10-grafana-dashboard.svg
```

### Fase 11 - hardening

[`11-hardening-report.md`](11-hardening-report.md) documenta il blocco di hardening realmente verificato:

- audit read-only;
- sysctl di rete;
- mantenimento del forwarding richiesto dal gateway;
- ICMP redirects disabilitati;
- source routing disabilitato;
- martian logging e SYN cookies;
- firewall verificato;
- SSH non esposto;
- logrotate riparato;
- VirtualBox inutilizzato disabilitato mantenendo Secure Boot;
- Avahi/mDNS disabilitato;
- Docker socket ristretto;
- permessi sensibili controllati;
- aggiornamenti automatici abilitati;
- 0 unità systemd fallite nella validazione finale.

Immagine pubblica:

```text
docs/images/11-hardening-summary.svg
```

Il report dichiara esplicitamente che backup PostgreSQL e restore restano da collaudare.

## Contenuti ammessi

- report anonimizzati;
- output brevi e revisionati;
- configurazioni senza segreti;
- estratti sintetici;
- dati sintetici chiaramente dichiarati;
- screenshot o infografiche revisionate.

## Contenuti non ammessi

- password o PSK Wi-Fi;
- password PostgreSQL o Grafana;
- file `.env` reali;
- SSID domestici;
- MAC reali;
- nomi completi di interfacce che incorporano MAC;
- hostname e percorsi personali;
- IP completi non necessari;
- query DNS personali;
- SNI TLS e certificati non necessari;
- log integrali;
- PCAP grezzi;
- traffico appartenente a terzi.

Questi elementi restano in `reports/`, `docker/.env`, `docker/data/` o in storage privato esterno.

## Immagini pubbliche

```text
docs/images/04-wifi-security-before.svg
docs/images/04-wifi-security-after.svg
docs/images/10-grafana-dashboard.svg
docs/images/11-hardening-summary.svg
```

## Regola per le fasi future

1. pubblicare un solo report principale per fase;
2. aggiungere output separati solo quando utili;
3. anonimizzare valori locali non necessari;
4. collegare il report dagli indici;
5. dichiarare chiaramente ciò che non è stato provato attivamente.
