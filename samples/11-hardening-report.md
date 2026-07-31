# Fase 11 - Hardening del gateway Ubuntu

## Stato

```text
HARDENING VERIFICATO
BACKUP / RIPRISTINO ANCORA DA COLLAUDARE
```

Questa fase documenta l'hardening realmente applicato e verificato sul gateway. I valori locali sensibili sono stati rimossi o generalizzati.

## Obiettivo

Ridurre la superficie d'attacco senza compromettere il ruolo del sistema come gateway e senza interrompere:

- routing IPv4;
- NAT e filtro `nftables`;
- Suricata e Zeek;
- analisi Python;
- Docker/PostgreSQL/Grafana;
- rete e risoluzione DNS.

## Audit iniziale

È stato aggiunto:

```text
scripts/hardening_audit.py
```

Lo script è read-only e raccoglie:

- kernel e distribuzione;
- identità e account UID 0;
- interfacce e routing;
- socket TCP/UDP in ascolto;
- unità systemd fallite;
- stato SSH;
- sysctl di rete;
- accesso a `nftables`;
- proprietà del socket Docker.

Gli output integrali vengono salvati in `reports/`, directory privata e ignorata da Git.

## Account privilegiati

È stato verificato che l'unico account con UID 0 sia:

```text
root
```

Risultato: **PASS**.

## Hardening sysctl

Il profilo pubblico versionato è:

```text
configs/sysctl/99-security-gateway-hardening.conf
```

Valori finali verificati:

```text
net.ipv4.ip_forward = 1
net.ipv4.conf.all.rp_filter = 2
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.tcp_syncookies = 1
```

### Perché `ip_forward` resta a 1

Il sistema svolge intenzionalmente funzione di gateway. Disabilitare il forwarding avrebbe interrotto il laboratorio.

### Reverse path filtering

È stato mantenuto `rp_filter=2` (loose mode) perché il sistema usa più reti e bridge, inclusi Docker e libvirt.

### ICMP Redirect

Ricezione e invio degli ICMP Redirect sono stati disabilitati. È stata verificata anche l'impostazione sulle interfacce già esistenti.

### Source routing

Il source routing IPv4 resta disabilitato.

### Martian logging e SYN cookies

Il logging dei pacchetti anomali è stato abilitato e i SYN cookies risultano attivi.

## Test di connettività dopo l'hardening

Dopo le modifiche sono stati verificati:

- route di default;
- gateway upstream;
- connettività Internet;
- risoluzione DNS.

Risultato: **PASS**.

L'hardening non ha interrotto il percorso di rete del gateway.

## Firewall nftables

È stato verificato il servizio dedicato:

```text
security-gateway-firewall.service
```

Stato osservato:

```text
enabled
active (exited)
status=0/SUCCESS
```

Le tabelle del progetto risultavano caricate e contenevano regole stateful, logging rate-limited e blocchi dedicati al traffico non autorizzato.

Risultato: **PASS**.

## SSH

Il server OpenSSH non risultava installato/attivo e nessun listener TCP/22 era presente.

Poiché l'accesso SSH remoto non è necessario al laboratorio, l'assenza del servizio riduce la superficie d'attacco.

Risultato: **PASS**.

## Logrotate / Suricata

L'audit iniziale mostrava `logrotate.service` fallito.

La causa era un file di backup di configurazione Suricata lasciato nella directory attiva di logrotate, che generava definizioni duplicate per i log Suricata.

Il backup è stato spostato fuori dalla directory delle configurazioni attive. Successivamente:

```text
logrotate.service -> status=0/SUCCESS
```

Risultato: **PASS**.

## VirtualBox

`virtualbox.service` falliva perché Secure Boot rifiutava il modulo `vboxdrv`.

VirtualBox non è necessario al laboratorio, che usa libvirt/QEMU. Non è stato disabilitato Secure Boot e non sono state aggiunte nuove chiavi soltanto per un componente inutilizzato.

Il servizio VirtualBox è stato disabilitato.

Risultato finale:

```text
systemctl --failed
0 loaded units listed.
```

Risultato: **PASS**.

## Avahi / mDNS

`avahi-daemon` ascoltava su UDP/5353 ed effettuava discovery mDNS sulle interfacce del sistema.

Non essendo necessario alle funzioni principali del gateway, servizio e socket sono stati disabilitati.

Verifica finale:

```text
avahi-daemon: inactive / disabled
UDP/5353: non in ascolto
```

Risultato: **PASS**.

## WSD / GVFS

È stato identificato `wsdd` avviato dal contesto desktop/GVFS per Windows Service Discovery su UDP/3702.

Il componente non è stato rimosso perché integrato con funzionalità desktop. Il firewall del gateway contiene già un blocco UDP/3702 sull'interfaccia hotspot.

Risultato: **ACCEPTED / DOCUMENTED**.

## Docker socket

Il socket Docker risultava di proprietà `root:docker` e non accessibile direttamente all'utente normale.

L'utente non è stato aggiunto al gruppo `docker` soltanto per comodità, evitando di ampliare i privilegi locali.

Risultato: **PASS**.

## Permessi sensibili

Le configurazioni principali del progetto risultavano possedute da `root:root` con permessi non scrivibili da utenti generici.

La ricerca di file world-writable nelle aree sensibili controllate e nel repository non ha prodotto risultati.

Risultato: **PASS**.

## Aggiornamenti

`unattended-upgrades` risultava abilitato e configurato per il controllo e l'applicazione automatica degli aggiornamenti previsti dalla policy APT.

Durante la verifica erano disponibili aggiornamenti aggiuntivi. L'upgrade completo è stato lasciato a una finestra di manutenzione separata perché coinvolgeva componenti importanti come Docker, libvirt, driver grafici e OpenSSL.

Risultato: **WARN / MAINTENANCE**.

## Validazione finale

Risultati principali:

```text
failed systemd units:        0
IPv4 forwarding:             enabled
reverse path filtering:      loose mode
accept ICMP redirects:       disabled
send ICMP redirects:         disabled
source routing:              disabled
martian logging:             enabled
SYN cookies:                 enabled
SSH listener:                absent
Avahi UDP/5353:              disabled
Docker socket:               restricted
world-writable sensitive:    none found
automatic updates:           enabled
```

![Riepilogo hardening](../docs/images/11-hardening-summary.svg)

## Stato della fase 11

La parte di **hardening** è completata e verificata.

Restano da collaudare, prima di dichiarare conclusa l'intera fase 11 originariamente pianificata:

- backup PostgreSQL con `pg_dump`;
- ripristino in database di prova;
- procedura completa di recovery/smontaggio;
- test end-to-end specifici di backup e restore.

Questi elementi non vengono dichiarati completati finché non saranno provati realmente.

## Privacy

Non sono pubblicati:

- hostname reale;
- nomi completi di interfacce contenenti MAC;
- IP client reali;
- percorsi home personali;
- log integrali;
- password o token;
- PCAP;
- output completi dei socket;
- dati DNS/TLS appartenenti a sessioni reali.
