# Indice della documentazione

## Punto di ingresso

1. leggere [`OBIETTIVI_E_PROGETTO.md`](OBIETTIVI_E_PROGETTO.md);
2. controllare [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md);
3. consultare [`00-ROADMAP.md`](00-ROADMAP.md);
4. seguire le guide operative in [`steps`](steps).

## Documenti principali

- [`OBIETTIVI_E_PROGETTO.md`](OBIETTIVI_E_PROGETTO.md): obiettivi e architettura fisica;
- [`00-ROADMAP.md`](00-ROADMAP.md): fasi e criteri di completamento;
- [`01-METODO-DI-LAVORO.md`](01-METODO-DI-LAVORO.md): verifiche, privacy e rollback;
- [`02-STATO-ATTUALE.md`](02-STATO-ATTUALE.md): stato operativo verificato;
- [`LAVORO_SVOLTO_E_PROSSIMI_PASSI.md`](LAVORO_SVOLTO_E_PROSSIMI_PASSI.md): riepilogo e attività aperte.

## Stato sintetico

```text
Fase 1   inventario hardware e rete      COMPLETATA
Fase 2   topologia e indirizzamento      COMPLETATA
Fase 3   hotspot Realtek                 COMPLETATA
Fase 4   DHCP, routing e NAT             COMPLETATA
Fase 5   firewall nftables               COMPLETATA
Fase 6   cattura tcpdump                 COMPLETATA
Fase 7   Suricata IDS                    COMPLETATA
Fase 8   Zeek                            COMPLETATA
Fase 9   analisi Python                  COMPLETATA
Fase 10  database e dashboard Docker     COMPLETATA
Fase 11A hardening                       VERIFICATA
Fase 11B backup / restore                DA COLLAUDARE
```

## Architettura sintetica

```text
Client autorizzato
  -> hotspot Wi-Fi USB
  -> Ubuntu gateway
  -> nftables INPUT/FORWARD
  -> Suricata + Zeek
  -> analisi/correlazione Python
  -> report aggregati
  -> importer Docker
  -> PostgreSQL
  -> Grafana locale
  -> NAT/masquerading
  -> uplink
  -> Internet
```

## Componenti software verificati

```text
../configs/nftables/security-gateway-input-filter.nft
../configs/nftables/security-gateway-filter.nft
../configs/sysctl/99-security-gateway-hardening.conf
../configs/systemd/security-gateway-firewall.service
../scripts/security-gateway-firewall
../scripts/hardening_audit.py
../python/read_zeek_json.py
../python/read_suricata_json.py
../python/correlate_logs.py
../python/analyze-lab
../docker/compose.yaml
../docker/database/init/001-schema.sql
../docker/database/002-grafana-reader.sql
../docker/importer/importer.py
../docker/grafana/provisioning/datasources/postgres.yaml
../docker/grafana/provisioning/dashboards/security-lab.yaml
../docker/grafana/dashboards/security-lab-overview.json
```

## Guide recenti

- [`steps/08-zeek.md`](steps/08-zeek.md)
- [`steps/09-python-log-analysis.md`](steps/09-python-log-analysis.md)
- [`steps/10-database-dashboard-docker.md`](steps/10-database-dashboard-docker.md)
- [`steps/11-test-hardening-backup.md`](steps/11-test-hardening-backup.md)

## Dashboard e hardening

![Dashboard Grafana fase 10](images/10-grafana-dashboard.svg)

![Riepilogo hardening fase 11](images/11-hardening-summary.svg)

## Sample pubblici

Report recenti:

- [`../samples/08-zeek-report.md`](../samples/08-zeek-report.md)
- [`../samples/09-python-log-analysis-report.md`](../samples/09-python-log-analysis-report.md)
- [`../samples/10-database-dashboard-docker-report.md`](../samples/10-database-dashboard-docker-report.md)
- [`../samples/11-hardening-report.md`](../samples/11-hardening-report.md)

## Stato della fase 11

Hardening verificato:

- profilo sysctl applicato e testato;
- routing/DNS/Internet preservati;
- firewall verificato;
- SSH non esposto;
- logrotate riparato;
- VirtualBox inutilizzato disabilitato senza disattivare Secure Boot;
- Avahi/mDNS disabilitato;
- Docker socket mantenuto ristretto;
- permessi sensibili verificati;
- 0 unità systemd fallite;
- aggiornamenti automatici abilitati.

Restano da collaudare backup PostgreSQL, restore di prova e recovery finale.

## Report e dati privati

La cartella locale `reports/` è ignorata da Git e può contenere output integrali, nomi reali delle interfacce, percorsi locali e report personali.

Anche `docker/.env` e `docker/data/` restano locali.

## Regola di aggiornamento

Dopo ogni sessione aggiornare:

1. il documento della fase corrente;
2. `02-STATO-ATTUALE.md`;
3. configurazioni o script realmente verificati;
4. la roadmap quando cambia lo stato;
5. il report pubblico principale;
6. gli indici del repository;
7. il report privato locale, senza aggiungerlo a Git.
