# Fase 11 - Test finali, hardening e backup

## Stato

```text
HARDENING: COMPLETATO E VERIFICATO
BACKUP / RIPRISTINO: DA COLLAUDARE
```

La fase 11 era stata progettata come fase conclusiva unica. Il 31 luglio 2026 è stato completato e verificato il blocco di hardening dell'host. I test di backup/restore PostgreSQL restano invece aperti e non vengono dichiarati completati senza prova reale.

## Obiettivo

Verificare che il gateway sia sicuro, osservabile e ripetibile senza perdere le funzioni necessarie al laboratorio.

## Hardening - audit iniziale

È stato creato:

```text
scripts/hardening_audit.py
```

Lo script è read-only e raccoglie:

- kernel e distribuzione;
- identità dell'utente;
- account UID 0;
- interfacce e routing;
- socket TCP/UDP;
- unità systemd fallite;
- stato OpenSSH;
- parametri sysctl di rete;
- accesso a nftables;
- proprietà del socket Docker.

Il report completo viene scritto in `reports/`, directory privata e ignorata da Git.

## Profilo sysctl

Configurazione pubblica:

```text
configs/sysctl/99-security-gateway-hardening.conf
```

Valori finali verificati:

```text
net.ipv4.ip_forward = 1
net.ipv4.conf.all.rp_filter = 2
net.ipv4.conf.default.rp_filter = 2
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0
net.ipv4.conf.*.send_redirects = 0
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1
net.ipv4.tcp_syncookies = 1
```

### Scelta progettuale: forwarding attivo

`net.ipv4.ip_forward` resta a `1` perché il sistema deve continuare a funzionare come gateway.

### Reverse path filtering

`rp_filter=2` mantiene il loose mode, più adatto alla presenza simultanea di bridge Docker, reti libvirt e interfacce di laboratorio.

### ICMP redirect

Invio e ricezione degli ICMP Redirect sono stati disabilitati. È stato verificato che `send_redirects` fosse a zero anche sulle interfacce già presenti.

### Source routing

Il source routing IPv4 resta disabilitato.

### Martian logging e SYN cookies

Il logging dei pacchetti anomali è stato abilitato e i SYN cookies risultano attivi.

## Verifica funzionale dopo hardening

Dopo l'applicazione del profilo sono stati verificati:

```bash
ip route
ping -c 3 <gateway-upstream>
ping -c 3 1.1.1.1
getent hosts example.com
```

Risultati osservati:

- routing presente;
- gateway upstream raggiungibile;
- Internet raggiungibile;
- DNS funzionante.

L'hardening non ha interrotto il ruolo di gateway.

## Firewall nftables

Verificato:

```text
security-gateway-firewall.service
```

Stato osservato:

```text
enabled
active (exited)
status=0/SUCCESS
```

Sono state lette con privilegi amministrativi le tabelle del progetto e confermate le regole stateful e i blocchi dedicati alla rete hotspot.

## SSH

Il server OpenSSH non risultava presente/attivo e non esisteva un listener TCP/22.

Poiché SSH non è necessario al laboratorio, non è stato installato soltanto per poi doverlo hardenizzare.

## Logrotate e Suricata

L'audit iniziale mostrava:

```text
logrotate.service -> failed
```

Causa reale:

- una configurazione di backup Suricata era rimasta dentro `/etc/logrotate.d/`;
- logrotate interpretava anche il backup come configurazione attiva;
- `fast.log` ed `eve.json` risultavano definiti due volte.

Il backup è stato spostato fuori dalla directory attiva. Un test in debug non ha più mostrato duplicati e il servizio è poi terminato con `status=0/SUCCESS`.

## VirtualBox e Secure Boot

`virtualbox.service` falliva durante il caricamento di `vboxdrv`:

```text
Key was rejected by service
```

DKMS aveva costruito il modulo, ma Secure Boot era attivo. VirtualBox non viene usato dal laboratorio, che utilizza libvirt/QEMU.

Decisione di hardening:

- non disabilitare Secure Boot;
- non registrare nuove chiavi soltanto per un componente inutilizzato;
- disabilitare `virtualbox.service`.

Dopo il reset dello stato fallito:

```text
systemctl --failed
0 loaded units listed.
```

## Avahi / mDNS

`avahi-daemon` ascoltava su UDP/5353 ed eseguiva discovery mDNS su più interfacce.

Non essendo necessario al gateway, servizio e socket sono stati disabilitati.

Verifica:

```text
avahi-daemon -> inactive / disabled
UDP/5353 -> non in ascolto
```

## WSD / GVFS

È stato identificato `wsdd` avviato in sessione utente da GVFS per Windows Service Discovery su UDP/3702.

Non è stato rimosso perché legato a funzionalità desktop. La policy nftables del gateway contiene già un blocco UDP/3702 sulla rete hotspot.

Stato: **accettato e documentato**.

## Docker socket

Il socket Docker risultava `root:docker`. L'utente normale non è stato aggiunto al gruppo `docker` soltanto per comodità.

Questo evita di ampliare inutilmente i privilegi locali.

## Permessi sensibili

Sono stati verificati file di configurazione del progetto posseduti da `root:root` e non scrivibili da utenti generici.

La ricerca di file world-writable nelle aree sensibili controllate e nel repository non ha restituito risultati.

## Aggiornamenti

`unattended-upgrades.service` risultava abilitato e la configurazione APT periodica era attiva.

Durante il controllo erano presenti pacchetti aggiornabili, inclusi componenti di sicurezza. L'upgrade completo è stato lasciato a una finestra di manutenzione separata perché coinvolgeva Docker, libvirt, driver grafici, OpenSSL e componenti di sistema.

## Validazione finale hardening

Risultati:

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
Avahi UDP/5353:              disabled
Docker socket:               restricted
world-writable sensitive:    none found
automatic security updates:  enabled
```

![Riepilogo fase 11](../images/11-hardening-summary.svg)

Report pubblico:

```text
samples/11-hardening-report.md
```

## Backup PostgreSQL - ancora da verificare

Percorso privato previsto:

```text
reports/backups/
```

Esempio da collaudare in una sessione dedicata:

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    exec -T database \
    sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
    > reports/backups/security-lab.dump
```

Il backup non sarà considerato valido finché non verrà provato un ripristino in un database separato.

## Ripristino - ancora da verificare

La procedura prevista dovrà ricostruire in ordine:

1. interfacce e hotspot;
2. DHCP, routing e NAT;
3. firewall;
4. Suricata;
5. Zeek;
6. Python;
7. Docker;
8. schema PostgreSQL;
9. restore del database;
10. Grafana;
11. test end-to-end.

## Condizione per chiudere l'intera fase 11

Sono ancora richiesti:

- backup PostgreSQL verificato;
- restore verificato;
- procedura di recovery/smontaggio verificata;
- documentazione finale di quei test.

La parte hardening è già completata e documentata; backup e restore restano esplicitamente aperti.
