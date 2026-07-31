# Sample pubblici anonimizzati

La cartella `samples/` contiene esempi pubblici derivati da attività realmente eseguite e verificati prima della pubblicazione.

## Organizzazione

Ogni fase completata possiede un solo report pubblico principale nella radice di `samples/`:

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
```

Non viene usata una sottocartella `samples/reports/`. Gli output supplementari sono ammessi soltanto quando aggiungono materiale utile senza duplicare il report principale.

## Fase 4

[`04-dhcp-routing-nat-report.md`](04-dhcp-routing-nat-report.md) documenta DHCP, DNS locale, forwarding IPv4, NAT, traffico prima e dopo la traduzione e sicurezza WPA2-RSN/CCMP.

[`04-dhcp-routing-nat-output.md`](04-dhcp-routing-nat-output.md) contiene output brevi e revisionati collegati alla fase.

## Fase 5

[`05-firewall-nftables-report.md`](05-firewall-nftables-report.md) documenta filtri `INPUT` e `FORWARD`, test attivi dei blocchi, logging con rate limit, rollback, coesistenza con NetworkManager/Docker/libvirt, script amministrativo, servizio systemd e persistenza dopo riavvio.

## Fase 6

[`06-cattura-tcpdump-report.md`](06-cattura-tcpdump-report.md) riunisce filtri BPF, protocolli, handshake TCP, confronto prima/dopo NAT, PCAP privato limitato, AppArmor e privacy.

Il PCAP grezzo non è pubblicato.

## Fase 7

[`07-suricata-report.md`](07-suricata-report.md) documenta installazione, AF_PACKET, regole, eventi applicativi, alert controllato, statistiche di cattura e rotazione reale di `eve.json`.

Il file completo `eve.json`, i log integrali e i valori locali sensibili non sono pubblicati.

## Fase 8

[`08-zeek-report.md`](08-zeek-report.md) documenta Zeek 8.0.9, plugin AF_PACKET/Pcap, log JSON, configurazione standalone, cattura senza drop kernel e gestione on demand.

Il nome reale dell'interfaccia, gli IP client, le query DNS, gli SNI TLS, i certificati e i log integrali non sono pubblicati.

## Fase 9

[`09-python-log-analysis-report.md`](09-python-log-analysis-report.md) documenta analizzatori Python, lettura streaming, statistiche, esportazione JSON, esclusione di indirizzi IP e UID, correlazione tra sensori e 23 test automatici.

I campioni tecnici usati dai test sono sotto `python/samples/`, sono sintetici e usano indirizzi riservati alla documentazione.

## Fase 10

[`10-database-dashboard-docker-report.md`](10-database-dashboard-docker-report.md) documenta:

- PostgreSQL 17 con volume persistente;
- schema `report_imports` e vista `latest_report_imports`;
- importer Python non root;
- importazione idempotente tramite SHA-256;
- verifica delle dichiarazioni di privacy prima dell'inserimento;
- tre report sintetici importati senza duplicati;
- account PostgreSQL `grafana_reader` in sola lettura;
- provisioning automatico del datasource Grafana;
- provisioning automatico della dashboard;
- rete Docker backend interna e frontend separata;
- Grafana limitato a `127.0.0.1:3000`;
- schermata revisionata della dashboard.

Immagine pubblica:

```text
docs/images/10-grafana-dashboard.svg
```

La schermata mostra soltanto metriche aggregate del campione sintetico e non contiene password, token o traffico grezzo.

## Contenuti ammessi

- report pubblici anonimizzati;
- output brevi e revisionati;
- configurazioni prive di segreti;
- estratti di log anonimizzati;
- dati sintetici chiaramente dichiarati;
- screenshot ricostruiti o revisionati.

## Contenuti non ammessi

- password o PSK Wi-Fi;
- password PostgreSQL o Grafana;
- file `.env` reali;
- SSID domestici;
- MAC reali;
- nome completo di interfacce `wlx...` che incorpora un MAC;
- hostname e percorsi personali;
- IP completi non necessari;
- porte temporanee associate a sessioni reali;
- query DNS personali;
- SNI TLS e certificati non necessari;
- valore di `digest_salt`;
- log integrali;
- PCAP grezzi;
- traffico appartenente a terzi.

Questi elementi devono restare nella cartella locale `reports/`, in `docker/.env`, in `docker/data/` o in una directory privata esterna al repository.

## Immagini pubbliche

```text
docs/images/04-wifi-security-before.svg
docs/images/04-wifi-security-after.svg
docs/images/10-grafana-dashboard.svg
```

Le immagini vengono revisionate prima della pubblicazione.

## Regola per le fasi future

1. creare un solo report principale `NN-nome-fase-report.md`;
2. aggiungere output separati soltanto quando utili e non duplicati;
3. anonimizzare ogni valore locale o remoto non necessario;
4. collegare il report dagli indici e dallo stato attuale;
5. dichiarare chiaramente ciò che non è stato provato attivamente.
