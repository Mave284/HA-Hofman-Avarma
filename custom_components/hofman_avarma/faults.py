"""Fault codes of the AVARMA heat pump.

Sources (and only these):
- Hofman Energy, technical data sheet HE-AI-290-00-000V-V03 (2025-11-24),
  "Communication protocol between monoblock heat pump controller and
  mainboard": registers 0x1100+38 .. 0x1100+44, code column and description
  column ("Fault Display/Historical Faults").
- Hofman / RP Handels und Service GmbH, Originalbetriebsanleitung Wärmepumpe
  AVARMA, Version V04, chapter 8.11 "Aufrufen des Fehlerspeichers" (display
  codes and German texts).
- Akkudoktor wiki "AVARMA 290 Wärmepumpe Monoblock": Fault State 0 = E01..E16
  at 4390, E15 = bit 14 = water flow (confirms the bit order).

Where the sources disagree:
- Fault State 1 bit 4 and bit 8, Fault State 3 bit 2: the code column and the
  description column of the data sheet name different codes, and the manual
  lists all candidates as reserved. Both candidates are shown ("E21/E56"),
  the description column's code first, until confirmed on a real display.
- E18 and E59 are reserved in the manual but defined in the data sheet; they
  are included with the data sheet text.
- E101..E108 only appear in the data sheet's code column, without a text.
- Driver board codes (E20-x): the data sheet's code column is wrong in several
  places; bits are matched to codes via the description texts in data sheet
  and manual, which agree.
- Driver Board Fault Codes 1 (0x112B) holds frequency reduction warnings, not
  faults, and is deliberately not decoded.

This module has no Home Assistant imports so it can be tested standalone.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Fault:
    """One fault code."""

    code: str
    key: str
    en: str | None = None
    de: str | None = None


def _e(code: str, en: str | None = None, de: str | None = None, key: str | None = None) -> Fault:
    return Fault(
        code=code,
        key=key or code.lower().replace("-", "_").replace("/", "_"),
        en=en,
        de=de,
    )


FAULT_STATE_0 = 0x1126
FAULT_STATE_1 = 0x1127
FAULT_STATE_2 = 0x1128
FAULT_STATE_3 = 0x1129
DRIVER_FAULTS_0 = 0x112A
DRIVER_FAULTS_2 = 0x112C

# Bitfield registers: address -> {bit: Fault}
BIT_FAULTS: dict[int, dict[int, Fault]] = {
    FAULT_STATE_0: {
        0: _e("E01", "Outdoor air temp sensor error", "Sensorfehler Außenlufttemperatur"),
        1: _e("E02", "Coil temp sensor error", "Sensorfehler Verdampfertemperatur"),
        2: _e("E03", "Suction temp sensor error", "Sensorfehler Ansaugtemperatur"),
        3: _e("E04", "EVI inlet temp sensor error", "Sensorfehler EVI-Einlasstemperatur"),
        4: _e("E05", "EVI outlet temp sensor error", "Sensorfehler EVI-Auslasstemperatur"),
        5: _e("E06", "Discharge temp sensor error", "Sensorfehler Verdichtungstemperatur"),
        6: _e("E07", "DHW temp sensor error", "Sensorfehler Trinkwasser-Temperatur"),
        7: _e("E08", "Outlet temp sensor error", "Sensorfehler Austrittstemperatur"),
        8: _e("E09", "Inlet temp sensor error", "Sensorfehler Eintrittstemperatur"),
        9: _e("E10", "Liquid refrigerant temp sensor error", "Sensorfehler Kältemitteltemperatur"),
        10: _e("E11", "High pressure sensor error", "Sensorfehler Hochdruck"),
        11: _e("E12", "Low pressure sensor error", "Sensorfehler Niederdruck"),
        12: _e("E13", "High pressure protection", "Hochdruckschutz"),
        13: _e("E14", "Low pressure protection", "Niederdruckschutz"),
        14: _e("E15", "Water flow error", "Störung Wasserdurchfluss"),
        15: _e("E16", "Communication error", "Kommunikationsfehler"),
    },
    FAULT_STATE_1: {
        0: _e("E17", "Discharge temp too high protection", "Schutz gegen zu hohe Verdichtungstemperatur"),
        1: _e("E18", "EEPROM parameter error", "EEPROM-Parameterfehler"),
        2: _e("E99", "Driver board communication failure", "Kommunikationsstörung Inverterplatine"),
        3: _e("E20", "IPM abnormal protection", "Schutz IPM"),
        4: _e("E21/E56", "Voltage failure", "Spannungsfehler"),
        5: _e("E22", "Water temp differential too big", "Wassertemperaturdifferenz zu hoch"),
        6: _e("E23", "DHW anti-freeze twice", "Trinkwasser-Frostschutz 2x"),
        7: _e("E24", "A/C anti-freeze twice", "A/C-Frostschutz 2x"),
        8: _e("E56/E21", "Primary side current protection", "Primärseitiger Stromschutz"),
        9: _e("E26", "T6 temp sensor error", "Temperatur-Sensorfehler T6"),
        10: _e("E27", "Ambient temperature exceeds upper limit", "Umgebungstemperatur überschreitet Obergrenze"),
        11: _e("E28", "Inlet water temp too high (cooling)", "Wassereintrittstemperatur zu hoch (Kühlen)"),
        12: _e("E29", "Room temp sensor error", "Sensorfehler Raumtemperatur"),
        13: _e("E58", "T4 low ambient temperature protection", "Umgebungstemperatur unterschreitet untere Grenze"),
        15: _e("E32", "Outlet water temp too high (heating)", "Wasseraustrittstemperatur zu hoch (Heizen)"),
    },
    FAULT_STATE_2: {
        3: _e("E36", "Fan motor driver communication failure", "Kommunikationsfehler DC-Lüfterplatine"),
        6: _e(
            "E59",
            "Inlet and outlet water temp reverse connection or abnormal four-way valve",
            "Wasserein-/-austrittsfühler vertauscht oder Vierwegeventil gestört",
        ),
        7: _e("E40", "Cooling outlet water temp low protection", "Wasseraustrittstemperatur zu niedrig (Kühlen)"),
        11: _e("E44", "1# DC motor error", "1# DC-Motor Störung"),
        12: _e("E45", "2# DC motor error", "2# DC-Motor Störung"),
    },
    FAULT_STATE_3: {
        1: _e("E50", "Condenser overheating protection", "Schutz gegen hohe Temperatur des Verdampfers"),
        2: _e("E51/E100", "High refrigerant concentration protection", "Kältemittelkonzentration zu hoch"),
        **{bit: _e(f"E{98 + bit}") for bit in range(3, 11)},  # E101..E108, no text
    },
    DRIVER_FAULTS_0: {
        0: _e("E20-1", "IPM failure", "IPM-Störung"),
        1: _e("E20-5", "Compressor drive failure (except IPM)", "Verdichterantriebsstörung (außer IPM)"),
        2: _e("E20-320", "Compressor overcurrent", "Verdichterüberstrom"),
        5: _e("E20-288", "IPM overtemperature shutdown", "IPM-Übertemperaturabschaltung"),
        6: _e("E20-384", "PFC failure", "Störung PFC (Leistungsfaktorkorrektur)"),
        7: _e("E20-32", "DC bus overvoltage", "DC-Bus-Überspannung"),
        8: _e("E20-16", "DC bus undervoltage", "DC-Bus-Unterspannung"),
        9: _e("E20-264", "AC input over- or undervoltage", "AC-Eingangsspannung Über- und Unterspannung"),
        10: _e("E20-260", "AC input overcurrent shutdown", "AC-Eingangsstrom Überstromabschaltung"),
        15: _e("E20-257", "Abnormal communication with main control board", "Ungewöhnliche Kommunikation mit der Hauptplatine"),
    },
}

# Value register (0 = no fault): value -> Fault
VALUE_FAULTS: dict[int, dict[int, Fault]] = {
    DRIVER_FAULTS_2: {
        1: _e("E20-291", "Acceleration overcurrent", "Beschleunigung durch Überstrom"),
        2: _e("E20-292", "Deceleration overcurrent", "Verlangsamung durch Überstrom"),
        3: _e("E20-293", "Constant speed overcurrent", "Überstrom bei konstanter Drehzahl"),
        4: _e("E20-294", "Acceleration overvoltage", "Beschleunigung durch Überspannung"),
        5: _e("E20-295", "Deceleration overvoltage", "Verlangsamung durch Überspannung"),
        6: _e("E20-296", "Constant speed overvoltage", "Überspannung bei konstanter Drehzahl"),
        8: _e("E20-297", "Out of sync failure", "Ungleichschrittigkeit"),
        9: _e("E20-258", "Phase loss fault", "Phasenausfallstörung"),
        10: _e("E20-298", "IPM module hardware protection failure", "IPM-Modul Ausfall des Hardware-Schutzes"),
        19: _e("E20-299", "Abnormal current detection circuit", "Abnormale Stromerfassungsschaltung"),
    },
}

FAULT_ADDRESSES: tuple[int, ...] = (*BIT_FAULTS, *VALUE_FAULTS)

UNKNOWN_KEY = "unknown"
ALL_FAULTS: tuple[Fault, ...] = (
    *(f for bits in BIT_FAULTS.values() for f in bits.values()),
    *(f for values in VALUE_FAULTS.values() for f in values.values()),
)
EVENT_TYPES: tuple[str, ...] = (*(f.key for f in ALL_FAULTS), UNKNOWN_KEY)


@dataclass(frozen=True, kw_only=True)
class ActiveFault:
    """A fault currently reported by the heat pump."""

    code: str
    key: str
    en: str | None
    de: str | None
    address: int
    bit: int | None = None
    value: int | None = None

    @property
    def ident(self) -> tuple[int, int]:
        """Stable identity for detecting newly appeared faults."""
        return (self.address, self.bit if self.bit is not None else 0x10000 + (self.value or 0))

    def description(self, language: str | None) -> str | None:
        if language and language.lower().startswith("de"):
            return self.de or self.en
        return self.en

    def as_dict(self, language: str | None) -> dict[str, object]:
        data: dict[str, object] = {
            "code": self.code,
            "description": self.description(language),
            "register": f"0x{self.address:04X}",
        }
        if self.bit is not None:
            data["bit"] = self.bit
        else:
            data["value"] = self.value
        return data


def decode_faults(data: dict[int, int] | None) -> list[ActiveFault] | None:
    """All active faults, or None if a fault register has not been read."""
    if data is None or any(data.get(a) is None for a in FAULT_ADDRESSES):
        return None
    active: list[ActiveFault] = []
    for address, bits in BIT_FAULTS.items():
        raw = data[address]
        for bit in range(16):
            if not raw & (1 << bit):
                continue
            fault = bits.get(bit)
            if fault:
                active.append(
                    ActiveFault(code=fault.code, key=fault.key, en=fault.en, de=fault.de, address=address, bit=bit)
                )
            else:
                active.append(
                    ActiveFault(code=f"0x{address:04X}.{bit}", key=UNKNOWN_KEY, en=None, de=None, address=address, bit=bit)
                )
    for address, values in VALUE_FAULTS.items():
        raw = data[address]
        if raw == 0:
            continue
        fault = values.get(raw)
        if fault:
            active.append(
                ActiveFault(code=fault.code, key=fault.key, en=fault.en, de=fault.de, address=address, value=raw)
            )
        else:
            active.append(
                ActiveFault(code=f"0x{address:04X}={raw}", key=UNKNOWN_KEY, en=None, de=None, address=address, value=raw)
            )
    return active
