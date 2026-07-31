# Fase 11 — Test finali, hardening e backup

## Stato

```text
PROSSIMA
```

La fase 10 è completata e verificata. Questa fase deve ora collaudare il sistema completo, compreso lo stack Docker PostgreSQL/Grafana.

## Obiettivo

Verificare che il gateway sia ripetibile, sicuro, osservabile e ripristinabile anche dopo errori o riavvii.

## Test end-to-end

Il dispositivo di laboratorio deve:

1. collegarsi all'hotspot;
2. ricevere indirizzo, gateway e DNS corretti;
3. raggiungere Ubuntu;
4. raggiungere Internet attraverso la MediaTek;
5. essere filtrato da `nftables`;
6. comparire nelle catture `tcpdump`;
7. generare log Suricata;
8. generare log Zeek;
9. comparire nei report Python;
10. produrre report `*-latest.json` importabili;
11. entrare in PostgreSQL senza duplicati inattesi;
12. comparire nella dashboard Grafana.

## Primo collaudo da eseguire

### Arresto non distruttivo

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    down
```

Il comando non deve rimuovere i volumi.

### Riavvio

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    up -d database grafana
```

Verificare:

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    ps

curl --fail --silent --show-error \
    http://127.0.0.1:3000/api/health
```

Dopo il riavvio le tre importazioni della fase 10 devono essere ancora presenti.

## Test negativi

- uplink disconnesso;
- hotspot fermato;
- forwarding disabilitato;
- regola firewall volutamente restrittiva;
- Suricata fermata;
- Zeek fermato;
- importer Python non eseguito;
- database non disponibile;
- Grafana non disponibile;
- report `*-latest.json` mancante;
- report con dichiarazione privacy non valida;
- tentativo di scrittura tramite `grafana_reader`;
- disco quasi pieno simulato in modo sicuro;
- file di log malformato;
- riavvio del gateway.

Ogni test deve indicare il comportamento atteso e quello osservato.

## Hardening

Valutare:

- servizi in ascolto;
- accesso amministrativo;
- aggiornamenti di sicurezza;
- permessi su configurazioni e log;
- utenti dei servizi;
- porte pubblicate da Docker;
- reti Docker `backend` e `frontend`;
- capability dei container;
- `no-new-privileges`;
- filesystem read-only dell'importer;
- account PostgreSQL `grafana_reader`;
- policy firewall;
- protezione da log eccessivi;
- rotazione;
- spazio disco;
- sincronizzazione oraria;
- disattivazione dei componenti non usati.

## Comandi di inventario finale

```bash
ss -lntup
systemctl --failed
sudo nft list ruleset
ip -4 address
ip -4 route
nmcli connection show --active
docker compose --env-file docker/.env -f docker/compose.yaml ps
docker network ls
docker volume ls
```

Controllare in particolare che:

- PostgreSQL non sia pubblicato sull'host;
- Grafana sia pubblicato soltanto su `127.0.0.1:3000`;
- nessun container monti `/var/run/docker.sock`;
- nessun container sia `privileged`.

## Backup PostgreSQL

Creare un backup logico con `pg_dump` senza pubblicare password o dati privati.

Percorso previsto:

```text
reports/backups/
```

La directory `reports/` è ignorata da Git.

Esempio operativo, da adattare e verificare durante la fase:

```bash
docker compose \
    --env-file docker/.env \
    -f docker/compose.yaml \
    exec -T database \
    sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
    > reports/backups/security-lab.dump
```

Il backup deve essere verificato con un ripristino in un database di prova, non soltanto creato.

## Backup generale

Dovranno essere salvati almeno:

- profili NetworkManager esportabili o ricostruibili;
- configurazione `nftables`;
- configurazione Suricata;
- configurazione Zeek;
- codice Python;
- `docker/compose.yaml`;
- schema PostgreSQL;
- provisioning Grafana;
- backup database;
- elenco dei pacchetti;
- documentazione dei valori usati.

I backup non devono includere password in chiaro o log personali non necessari.

## Ripristino

La procedura deve poter ricostruire il laboratorio in ordine:

1. interfacce;
2. hotspot;
3. DHCP e indirizzamento;
4. forwarding;
5. firewall e NAT;
6. Suricata;
7. Zeek;
8. Python;
9. Docker;
10. schema PostgreSQL;
11. ripristino database;
12. Grafana;
13. test end-to-end.

## Smontaggio del laboratorio

Documentare anche come:

- fermare i servizi;
- disattivare l'hotspot;
- rimuovere le sole regole del progetto;
- disabilitare forwarding se non serve ad altro;
- arrestare i container senza cancellare i volumi;
- conservare o cancellare deliberatamente i dati;
- ripristinare la configurazione iniziale.

## Condizione di completamento

Il progetto è completo quando:

- tutti i test positivi passano;
- i test negativi falliscono nel modo previsto;
- il gateway riparte correttamente;
- PostgreSQL conserva i dati dopo riavvio;
- Grafana torna operativo dopo riavvio;
- esiste un backup verificato;
- esiste un ripristino verificato;
- esiste una procedura di smontaggio;
- la documentazione descrive soltanto risultati reali.
