# Hofman Energy AVARMA – Home Assistant

Home-Assistant-Integration für Hofman-Energy-**AVARMA**-Wärmepumpen (Monoblock R290, Heizungsmodelle) über Modbus. Die Wärmepumpe wird über ein RS485-Ethernet-Gateway angebunden, ganz ohne ESP oder YAML.

*English summary below.*

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

1. HACS → Integrationen → ⋮ → *Benutzerdefinierte Repositories* → `https://github.com/GITHUB_USER/REPO_NAME`, Kategorie *Integration*
2. „Hofman Energy AVARMA“ installieren, Home Assistant neu starten
3. Einstellungen → Geräte & Dienste → Integration hinzufügen → „Hofman Energy AVARMA“
4. IP des Gateways, Port (meist 502), Slave-ID (ab Werk 1) und Protokoll eintragen

## Hinweise

- Messwerte werden alle 15 s gelesen (in den Optionen einstellbar), Installateurparameter alle 10 Minuten und direkt nach einem Schreibzugriff.
- Register 4611/4612 (Pumpendrehzahl, Betriebsmodus) stammen aus dem Akkudoktor-Forum. Liefert die Wärmepumpe sie nicht, bleiben die Entitäten „nicht verfügbar“, der Rest läuft weiter.
- Der Durchflusssensor (C10) liefert bei manchen Geräten unplausible Werte.

## Quellen

- Registerliste und Faktoren: [auenkind/esphome – hofman_energy_avarma](https://github.com/auenkind/esphome/tree/dev/esphome/components/hofman_energy_avarma)
- [Akkudoktor-Forum: AVARMA WP – Monoblock R290](https://akkudoktor.net/t/avarma-wp-monoblock-r290/16194) und [Wiki: Avarma WP](https://akkudoktor.net/t/wiki-avarma-wp/34257)

## Fehler melden

Bitte ein Issue mit Modell (kW, 230 V/400 V), Gateway-Typ und dem Diagnose-Download (Gerät → ⋮ → Diagnose herunterladen) anlegen.

---

## English summary

Unofficial Home Assistant integration for Hofman Energy AVARMA heat pumps via an RS485-to-Ethernet gateway (Modbus TCP or RTU over TCP). Connect the gateway to **Comm 3** (9600 8N1, slave 1). Provides sensors, status bits, on/off, fault reset and parameters. Everyday parameters are enabled; all other installer parameters are disabled by default; factory reset (P87) and RS485 address (P108) are never exposed. Register map based on the community work linked above. Use at your own risk.
