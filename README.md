# Hofman Energy AVARMA – Home Assistant

Home-Assistant-Integration für Hofman-Energy-**AVARMA**-Wärmepumpen (Monoblock R290, Heizungsmodelle) über Modbus. Die Wärmepumpe wird über ein RS485-Ethernet-Gateway angebunden, ganz ohne ESP oder YAML.

*English summary below.*

> [!IMPORTANT]
> **Beta:** Die Integration ist bisher nur gegen einen Modbus-Simulator getestet, noch nicht an einer echten AVARMA. Rückmeldungen mit Modell (kW, 230 V/400 V) und Gateway-Typ sind ausdrücklich erwünscht, ob es funktioniert oder nicht. Meine Avarma kommt Anfang November, dann werde ich selbst ausführlich testen.

> [!WARNING]
> Inoffizielles Community-Projekt, nicht von Hofman Energy. Die Registerbelegung stammt aus Community-Quellen und ist nicht vom Hersteller bestätigt. Parameter falsch zu setzen kann die Wärmepumpe in einen Störzustand bringen oder ihre Effizienz verschlechtern. Nutzung auf eigenes Risiko. Notiere dir **vor** dem ersten Schreibzugriff alle Werkswerte.

## Funktionen

- Einrichtung über die Oberfläche (Config Flow), ein Gerät pro Wärmepumpe
- Modbus TCP und Modbus RTU over TCP
- 30 Messwerte (Temperaturen, Drücke, Verdichter, Pumpe, Spannungen), Betriebsmodus
- 31 Statusbits (Abtauen, Alarm, Pumpen, E-Heizstäbe, Eingänge K1–K8, Frequenzbegrenzungen)
- Ein/Aus (P00) und Fehler quittieren
- Parameter als Zahlen-Entitäten:
  - **aktiv:** P01 Betriebsart, P02/P08 maximale Heiztemperatur, P04 Warmwasser-Soll, P06/P07 Hysterese, P09 Heizkurven-Offset
  - **deaktiviert (bei Bedarf in HA einschalten):** alle übrigen Parameter aus Block 0x1000/0x2000
  - **bewusst nicht enthalten:** P87 (Werksreset) und P108 (RS485-Adresse)
- Diagnose-Download mit Rohwerten aller Register für Fehlermeldungen

## Hardware

- RS485-Ethernet-Gateway, z. B. Waveshare RS485 TO ETH/POE ETH, Elfin EW11, USR-TCP232
- Anschluss an **Comm 3** der Wärmepumpe (A/B). Das Display bleibt an seinem eigenen Anschluss.
- Serielle Einstellungen am Gateway: **9600 Baud, 8 Datenbits, keine Parität, 1 Stoppbit**
- Gateway-Modus:
  - *Modbus TCP Gateway* (Modbus-TCP ↔ RTU-Umsetzung) → in HA **Modbus TCP** wählen
  - *Transparent / TCP Server* → in HA **Modbus RTU over TCP** wählen
- Wenn zusätzlich evcc oder ein anderes System abfragt: Gateway auf mehrere TCP-Clients (Multi-Host) einstellen.

## Installation

Voraussetzungen: Home Assistant ab 2025.10 und [HACS](https://hacs.xyz/docs/use/).

### Über HACS (empfohlen)

[![In HACS öffnen](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Mave284&repository=HA-Hofman-Avarma&category=integration)

1. Auf den Button klicken, die eigene Home-Assistant-Instanz bestätigen und in HACS **Herunterladen** wählen.
   Ohne Button: HACS → ⋮ → *Benutzerdefinierte Repositories* → `https://github.com/Mave284/HA-Hofman-Avarma`, Typ *Integration* → hinzufügen, dann „Hofman Energy AVARMA“ suchen und herunterladen.
2. Home Assistant neu starten.

### Manuell

1. Die ZIP des [aktuellen Releases](https://github.com/Mave284/HA-Hofman-Avarma/releases/latest) herunterladen.
2. Den Ordner `custom_components/hofman_avarma` nach `<config>/custom_components/hofman_avarma` kopieren (z. B. per Samba- oder File-Editor-Add-on).
3. Home Assistant neu starten.

Updates kommen bei der manuellen Installation nicht automatisch, dafür HACS nutzen.

## Einrichtung

[![Integration hinzufügen](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=hofman_avarma)

1. Auf den Button klicken oder: Einstellungen → Geräte & Dienste → **Integration hinzufügen** → „Hofman Energy AVARMA“.
2. Eintragen:
   - **Host:** IP-Adresse des Gateways (am besten fest per DHCP-Reservierung)
   - **Port:** meist `502` (Werkseinstellung des Gateways prüfen)
   - **Slave-ID:** ab Werk `1` (Parameter P108 an der Wärmepumpe)
   - **Protokoll:** *Modbus TCP* oder *Modbus RTU over TCP*, passend zum Gateway-Modus (siehe [Hardware](#hardware))
3. Die Integration prüft die Verbindung beim Speichern. Schlägt sie fehl, zuerst Protokoll, Verkabelung A/B und die seriellen Einstellungen am Gateway kontrollieren.

Das Abfrageintervall lässt sich später unter Gerät → **Konfigurieren** ändern.

## Hinweise

- Messwerte werden alle 15 s gelesen (in den Optionen einstellbar), Installateurparameter alle 10 Minuten und direkt nach einem Schreibzugriff.
- Register 4611/4612 (Pumpendrehzahl, Betriebsmodus) stammen aus dem Akkudoktor-Forum. Liefert die Wärmepumpe sie nicht, bleiben die Entitäten „nicht verfügbar“, der Rest läuft weiter.
- Der Durchflusssensor (C10) liefert bei manchen Geräten unplausible Werte.

## Quellen

- Registerliste und Faktoren: [auenkind/esphome – hofman_energy_avarma](https://github.com/auenkind/esphome/tree/dev/esphome/components/hofman_energy_avarma)
- [Akkudoktor-Forum: AVARMA WP – Monoblock R290](https://akkudoktor.net/t/avarma-wp-monoblock-r290/16194) und [Wiki: Avarma WP](https://akkudoktor.net/t/wiki-avarma-wp/34257)

## Entstehung

Der Code wurde mit Unterstützung von Claude (Anthropic) erstellt. Getestet und gepflegt wird er von mir.

## Fehler melden

Bitte ein Issue mit Modell (kW, 230 V/400 V), Gateway-Typ und dem Diagnose-Download (Gerät → ⋮ → Diagnose herunterladen) anlegen.

---

## English summary

**Beta:** so far only tested against a Modbus simulator, not yet on a real AVARMA. Feedback (model, gateway type) is very welcome, whether it works or not.

Unofficial Home Assistant integration for Hofman Energy AVARMA heat pumps via an RS485-to-Ethernet gateway (Modbus TCP or RTU over TCP). Connect the gateway to **Comm 3** (9600 8N1, slave 1). Install via the HACS button above (or add `https://github.com/Mave284/HA-Hofman-Avarma` as a custom repository of type *Integration*), restart Home Assistant, then add the integration with the *Add integration* button. Provides sensors, status bits, on/off, fault reset and parameters. Everyday parameters are enabled; all other installer parameters are disabled by default; factory reset (P87) and RS485 address (P108) are never exposed. Register map based on the community work linked above. Code written with the help of Claude (Anthropic), tested and maintained by me. Use at your own risk.
