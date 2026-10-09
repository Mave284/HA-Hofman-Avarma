"""Register map for Hofman Energy AVARMA heat pumps (heating models).

Sources:
- auenkind/esphome, component hofman_energy_avarma (AVARMA_REGISTERS.md,
  registers/avarma_registers.py)
- Akkudoktor forum thread "AVARMA WP - Monoblock R290" (registers 4611, 4612)

All registers are holding registers, read with function 0x03 and written with
function 0x06. Values are signed 16 bit unless noted otherwise.

This module has no Home Assistant imports so it can be tested standalone.
"""

from __future__ import annotations

from dataclasses import dataclass

# --------------------------------------------------------------------------
# Read blocks
# --------------------------------------------------------------------------
# (start address, register count)
BLOCK_SETPOINTS = (0x1000, 9)  # P00 .. 0x1008 (fault reset)
BLOCK_STATUS = (0x1102, 44)  # operating state .. C1 pump PWM (0x112D)
BLOCK_FORUM = (0x1203, 2)  # 4611 pump speed, 4612 operating mode (undocumented)
BLOCK_PARAMS = (0x2001, 111)  # installer parameters P01_2 .. P115

CORE_BLOCKS = (BLOCK_SETPOINTS, BLOCK_STATUS)

# Largest number of registers requested in one read. Keeps requests small for
# cheap RS485 gateways; contiguous blocks are split automatically.
MAX_REGISTERS_PER_READ = 60


# --------------------------------------------------------------------------
# Definitions
# --------------------------------------------------------------------------
@dataclass(frozen=True, kw_only=True)
class SensorReg:
    """A measured value."""

    key: str
    address: int
    name: str
    unit: str | None = None
    device_class: str | None = None
    factor: float = 1.0
    precision: int = 0
    enabled: bool = True
    diagnostic: bool = False
    signed: bool = True


@dataclass(frozen=True, kw_only=True)
class BitReg:
    """One bit of a status register."""

    key: str
    address: int
    bit: int
    name: str
    diagnostic: bool = False


@dataclass(frozen=True, kw_only=True)
class NumberReg:
    """A writable parameter.

    raw register value = displayed value * factor
    """

    key: str
    address: int
    name: str
    min: float
    max: float
    step: float = 1.0
    factor: float = 1.0
    unit: str | None = None
    everyday: bool = False


def _temp(key: str, address: int, name: str, **kw) -> SensorReg:
    return SensorReg(
        key=key,
        address=address,
        name=name,
        unit="°C",
        device_class="temperature",
        factor=0.1,
        precision=1,
        **kw,
    )


# --------------------------------------------------------------------------
# Sensors (block 0x1100 + forum block)
# --------------------------------------------------------------------------
SENSORS: tuple[SensorReg, ...] = (
    _temp("c00_coil_temp", 0x1106, "C00 Coil temperature"),
    _temp("c01_discharge_temp", 0x1107, "C01 Discharge temperature"),
    _temp("c02_ambient_temp", 0x1108, "C02 Ambient temperature"),
    _temp("c03_suction_temp", 0x1109, "C03 Suction temperature"),
    _temp("c04_evi_inlet_temp", 0x110A, "C04 EVI inlet temperature", enabled=False),
    _temp("c05_evi_outlet_temp", 0x110B, "C05 EVI outlet temperature", enabled=False),
    _temp("c06_liquid_temp", 0x110C, "C06 Refrigerant liquid temperature"),
    _temp("c07_water_inlet_temp", 0x110D, "C07 Water inlet temperature"),
    _temp("c08_water_outlet_temp", 0x110E, "C08 Water outlet temperature"),
    _temp("c09_tank_temp", 0x110F, "C09 Tank temperature"),
    SensorReg(
        key="c10_water_flow",
        address=0x1110,
        name="C10 Water flow",
        unit="L/min",
        device_class="volume_flow_rate",
        factor=0.1,
        precision=1,
    ),
    SensorReg(
        key="c11_main_delta_t",
        address=0x1111,
        name="C11 Main circuit temperature difference",
        unit="K",
        factor=0.1,
        precision=1,
    ),
    SensorReg(
        key="c12_evi_delta_t",
        address=0x1112,
        name="C12 EVI circuit temperature difference",
        unit="K",
        factor=0.1,
        precision=1,
        enabled=False,
    ),
    # raw value in 0.01 MPa = 0.1 bar
    SensorReg(
        key="c13_high_pressure",
        address=0x1113,
        name="C13 High pressure",
        unit="bar",
        device_class="pressure",
        factor=0.1,
        precision=1,
        diagnostic=True,
    ),
    SensorReg(
        key="c14_low_pressure",
        address=0x1114,
        name="C14 Low pressure",
        unit="bar",
        device_class="pressure",
        factor=0.1,
        precision=1,
        diagnostic=True,
    ),
    SensorReg(
        key="c15_compressor_freq",
        address=0x1115,
        name="C15 Compressor frequency",
        unit="Hz",
        device_class="frequency",
    ),
    SensorReg(
        key="c16_fan1_speed",
        address=0x1116,
        name="C16 Fan 1 speed",
        unit="rpm",
        diagnostic=True,
    ),
    SensorReg(
        key="c17_fan2_speed",
        address=0x1117,
        name="C17 Fan 2 speed",
        unit="rpm",
        diagnostic=True,
        enabled=False,
    ),
    SensorReg(
        key="c20_compressor_target_freq",
        address=0x111A,
        name="C20 Compressor target frequency",
        unit="Hz",
        device_class="frequency",
        diagnostic=True,
    ),
    SensorReg(
        key="c21_compressor_current",
        address=0x111B,
        name="C21 Compressor current",
        unit="A",
        device_class="current",
        factor=0.1,
        precision=1,
    ),
    _temp("c22_ipm_temp", 0x111C, "C22 IPM temperature", diagnostic=True),
    SensorReg(
        key="c23_ac_voltage",
        address=0x111D,
        name="C23 AC voltage",
        unit="V",
        device_class="voltage",
        factor=0.1,
        precision=1,
        diagnostic=True,
    ),
    SensorReg(
        key="c24_dc_voltage",
        address=0x111E,
        name="C24 DC voltage",
        unit="V",
        device_class="voltage",
        factor=0.1,
        precision=1,
        diagnostic=True,
    ),
    _temp("c25_t6", 0x111F, "C25 T6", enabled=False),
    _temp("c26_room_temp", 0x1120, "C26 Room temperature (T2)", enabled=False),
    _temp("c27_evaporator_temp", 0x1121, "C27 Evaporator temperature"),
    _temp("c28_condenser_temp", 0x1122, "C28 Condenser temperature"),
    SensorReg(
        key="c1_pump_pwm",
        address=0x112D,
        name="C1 pump PWM",
        unit="%",
        signed=False,
    ),
    # Akkudoktor forum, not in the official register list
    SensorReg(
        key="pump_speed",
        address=0x1203,
        name="Water pump speed",
        unit="%",
        signed=False,
    ),
)

# Operating mode register 4612 (forum). Value -> state key.
MODE_ADDRESS = 0x1204
MODE_STATES: dict[int, str] = {
    0: "off",
    1: "dhw",
    2: "heating",
    3: "heating_dhw",
}

# --------------------------------------------------------------------------
# Status bits
# --------------------------------------------------------------------------
_OP = 0x1102
_OUT = 0x1103
_IN = 0x1104
_LIM = 0x1123

BITS: tuple[BitReg, ...] = (
    BitReg(key="state_standby", address=_OP, bit=0, name="Standby"),
    BitReg(key="state_power_on", address=_OP, bit=1, name="Power on"),
    BitReg(key="state_downtime", address=_OP, bit=2, name="Downtime"),
    BitReg(key="state_alarm", address=_OP, bit=3, name="Alarm"),
    BitReg(key="state_defrost", address=_OP, bit=4, name="Defrosting"),
    BitReg(key="state_sterilization", address=_OP, bit=8, name="Sterilization"),
    BitReg(key="state_antifreeze", address=_OP, bit=9, name="Antifreeze"),
    BitReg(key="state_floor_drying", address=_OP, bit=10, name="Floor drying"),
    BitReg(key="state_pv_mode", address=_OP, bit=11, name="PV mode"),
    BitReg(key="out_4way_valve", address=_OUT, bit=0, name="Four-way valve"),
    BitReg(key="out_crank_heater", address=_OUT, bit=1, name="Crankcase heater"),
    BitReg(key="out_c1_pump", address=_OUT, bit=3, name="C1 pump"),
    BitReg(key="out_c2_pump", address=_OUT, bit=4, name="C2 pump"),
    BitReg(key="out_c3_pump", address=_OUT, bit=5, name="C3 pump"),
    BitReg(key="out_e1_heater", address=_OUT, bit=6, name="E1 electric heater"),
    BitReg(key="out_e2_heater", address=_OUT, bit=7, name="E2 electric heater"),
    BitReg(key="out_g1_valve", address=_OUT, bit=8, name="G1 valve"),
    BitReg(key="out_g2_valve", address=_OUT, bit=9, name="G2 valve"),
    *(
        BitReg(
            key=f"in_k{i + 1}_open",
            address=_IN,
            bit=i,
            name=f"K{i + 1} input open",
            diagnostic=True,
        )
        for i in range(8)
    ),
    BitReg(key="limit_coil", address=_LIM, bit=0, name="Frequency limit coil temperature", diagnostic=True),
    BitReg(key="limit_high_pressure", address=_LIM, bit=1, name="Frequency limit high pressure", diagnostic=True),
    BitReg(key="limit_ac_voltage", address=_LIM, bit=2, name="Frequency limit AC voltage", diagnostic=True),
    BitReg(key="limit_discharge", address=_LIM, bit=3, name="Frequency limit discharge temperature", diagnostic=True),
    BitReg(key="limit_ac_current", address=_LIM, bit=4, name="Frequency limit AC current", diagnostic=True),
)

# --------------------------------------------------------------------------
# Switch / button
# --------------------------------------------------------------------------
POWER_ADDRESS = 0x1000  # P00 on/off
FAULT_RESET_ADDRESS = 0x1008  # write 1 to clear faults

# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------
# P87 (factory reset, 0x2055) and P108 (RS485 address, 0x2068) are deliberately
# not exposed: one wrong click would reset the unit or cut this connection.
_B = 0x2000


def _n(key, address, name, mn, mx, step=1.0, factor=1.0, unit="°C", everyday=False):
    return NumberReg(
        key=key,
        address=address,
        name=name,
        min=mn,
        max=mx,
        step=step,
        factor=factor,
        unit=unit,
        everyday=everyday,
    )


NUMBERS: tuple[NumberReg, ...] = (
    # ---- block 0x1000: setpoints ----
    _n("p01_mode", 0x1001, "P01 Mode setting", 0, 5, unit=None, everyday=True),
    _n("p02_heating_max", 0x1002, "P02 Heating maximum temperature", 35, 75, everyday=True),
    _n("p03_cooling_setpoint", 0x1003, "P03 Cooling setpoint", 7, 25),
    _n("p04_dhw_setpoint", 0x1004, "P04 DHW setpoint", 10, 70, everyday=True),
    _n("p05_indoor_setpoint", 0x1005, "P05 Indoor setpoint", 18, 35),
    # ---- block 0x2000: installer parameters ----
    _n("p01_2_function_selection_2", _B + 1, "P01-2 Function selection 2", 0, 5, unit=None),
    _n("p105_a_platform_freq", _B + 2, "P105 Compressor A platform frequency", 20, 60, unit="Hz"),
    _n("p106_a_platform_delay", _B + 3, "P106 Compressor A platform delay", 20, 60, unit=None),
    _n("p06_heating_hysteresis", _B + 4, "P06 Heating hysteresis", 1, 15, 0.1, 10, unit="K", everyday=True),
    _n("p07_dhw_hysteresis", _B + 5, "P07 DHW hysteresis", 1, 15, 0.1, 10, unit="K", everyday=True),
    _n("p08_heating_curve_max", _B + 6, "P08 Heating curve maximum temperature", 35, 75, 0.1, 10, everyday=True),
    _n("p09_heating_curve_offset", _B + 7, "P09 Heating curve offset", -10, 10, 0.1, 10, unit="K", everyday=True),
    _n("p10_sterilization_interval", _B + 8, "P10 Sterilization interval", 1, 99, unit="d"),
    _n("p11_sterilization_start", _B + 9, "P11 Sterilization start hour", 0, 23, unit="h"),
    _n("p12_sterilization_runtime", _B + 10, "P12 Sterilization run time", 5, 99, unit="min"),
    _n("p13_sterilization_temp", _B + 11, "P13 Sterilization temperature", 50, 70, 0.1, 10),
    _n("p14_sterilization_mode", _B + 12, "P14 Sterilization mode", 0, 2, unit=None),
    _n("p15_night_start", _B + 13, "P15 Night mode start hour", 0, 23, unit="h"),
    _n("p16_night_end", _B + 14, "P16 Night mode end hour", 0, 23, unit="h"),
    _n("p17_night_enable", _B + 15, "P17 Night mode enable", 0, 1, unit=None),
    _n("p18_dhw_au", _B + 16, "P18 DHW AU function", 0, 1, unit=None),
    _n("p19_heating_au", _B + 17, "P19 Heating AU enable", 0, 1, unit=None),
    _n("p20_pump_mode", _B + 18, "P20 Water pump working mode", 0, 2, unit=None),
    _n("p21_pump_antifreeze_time", _B + 19, "P21 Water pump antifreeze time", 5, 50, unit="min"),
    _n("p22_heating_aux_start", _B + 20, "P22 Heating electric aux start ambient", -30, 20, 0.1, 10),
    _n("p23_dhw_aux_start", _B + 21, "P23 DHW electric aux start ambient", -30, 20, 0.1, 10),
    _n("p24_aux_stop_hysteresis", _B + 22, "P24 Electric aux stop hysteresis", 1, 15, 0.1, 10, unit="K"),
    _n("p25_antifreeze_temp", _B + 23, "P25 Antifreeze temperature", -15, 5, 0.1, 10),
    _n("p26_defrost_interval_mult", _B + 24, "P26 Defrost interval multiplier", 0, 4, unit=None),
    _n("p27_defrost_cycle", _B + 25, "P27 Defrost cycle", 15, 99, unit="min"),
    _n("p28_defrost_mode", _B + 26, "P28 Defrost mode", 0, 1, unit=None),
    _n("p29_defrost_start_coil", _B + 27, "P29 Defrost start coil temperature", -8, 5, 0.1, 10),
    _n("p30_defrost_end_coil", _B + 28, "P30 Defrost end coil temperature", 5, 30, 0.1, 10),
    _n("p31_defrost_max_time", _B + 29, "P31 Defrost maximum time", 2, 20, unit="min"),
    _n("p32_main_valve_mode", _B + 30, "P32 Main valve control mode", 0, 4, unit=None),
    _n("p33_main_valve_heating", _B + 31, "P33 Main valve manual opening heating", 50, 480, unit="P"),
    _n("p34_main_valve_cooling", _B + 32, "P34 Main valve manual opening cooling", 50, 480, unit="P"),
    _n("p35_dhw_compressor_limit", _B + 33, "P35 DHW compressor water temperature limit", 0, 70, 0.1, 10),
    _n("p36_compressor_e1_delay", _B + 34, "P36 Compressor to E1 start delay", 0, 999, unit="min"),
    _n("p37_heating_fan_var", _B + 35, "P37 Heating DC fan speed variable", 2, 15, 0.1, 10, unit=None),
    _n("p38_cooling_fan_var", _B + 36, "P38 Cooling DC fan speed variable", 3, 18, 0.1, 10, unit=None),
    _n("p39_compressor_model", _B + 37, "P39 Inverter compressor model", 0, 999, unit=None),
    _n("p40_set_freq_function", _B + 38, "P40 Running set frequency function", 0, 1, unit=None),
    _n("p41_oil_return_freq", _B + 39, "P41 Compressor oil return frequency", 10, 100, unit="Hz"),
    _n("p42_up_freq_current", _B + 40, "P42 Compressor up-frequency current limit", 1, 50, 0.1, 10, unit="A"),
    _n("p43_down_freq_current", _B + 41, "P43 Compressor down-frequency current", 1, 50, 0.1, 10, unit="A"),
    _n("p44_shutdown_current", _B + 42, "P44 Compressor shutdown current", 1, 50, 0.1, 10, unit="A"),
    _n("p45_compressor_max_freq", _B + 43, "P45 Compressor maximum frequency", 50, 120, unit="Hz"),
    _n("p46_compressor_min_freq", _B + 44, "P46 Compressor minimum frequency", 0, 90, unit="Hz"),
    _n("p47_defrost_freq", _B + 45, "P47 Compressor defrost frequency", 30, 90, unit="Hz"),
    _n("p48_dhw_max_freq", _B + 46, "P48 DHW maximum frequency", 2, 10, unit=None),
    _n("p49_exhaust_p", _B + 47, "P49 Exhaust overheat proportional coefficient", 0, 99, 0.1, 10, unit=None),
    _n("p50_exhaust_d", _B + 48, "P50 Exhaust overheat differential coefficient", 0, 99, unit=None),
    _n("p51_hp_prohibit_boost", _B + 49, "P51 High pressure prohibit boost", 20, 45, 0.1, 10, unit="bar"),
    _n("p52_hp_cancel_prohibit", _B + 50, "P52 High pressure cancel prohibit boost", 20, 45, 0.1, 10, unit="bar"),
    _n("p53_hp_protection", _B + 51, "P53 High pressure protection set point", 20, 45, 0.1, 10, unit="bar"),
    _n("p54_lp_protection", _B + 52, "P54 Low pressure protection set point", 0.1, 1.0, 0.1, 10, unit="bar"),
    _n("p55_hp_release_hyst", _B + 53, "P55 High pressure release hysteresis", 1.0, 10.0, 0.1, 10, unit="bar"),
    _n("p56_lp_release_hyst", _B + 54, "P56 Low pressure release hysteresis", 0.1, 5.0, 0.01, 100, unit="bar"),
    _n("p57_exhaust_protection", _B + 55, "P57 Exhaust temperature protection", 100, 125),
    _n("p58_pump_regulation_dt", _B + 56, "P58 C1 pump speed regulation temperature difference", 3, 8, 0.1, 10, unit="K"),
    _n("p59_pump_min_speed", _B + 57, "P59 PWM water pump minimum speed", 0, 100, unit="%"),
    _n("p60_fan_max_speed", _B + 58, "P60 DC fan maximum speed", 500, 1500, 10, 0.1, unit="rpm"),
    _n("p61_min_water_flow", _B + 59, "P61 Minimum water flow", 3, 80, unit="L/min"),
    _n("p62_ac_function", _B + 60, "P62 Heating/cooling function selection", 0, 2, unit=None),
    _n("p63_dhw_function", _B + 61, "P63 DHW function selection", 0, 1, unit=None),
    _n("p64_eev_min_opening", _B + 62, "P64 Expansion valve minimum opening", 0, 480, unit="P"),
    _n("p65_c2_pump_function", _B + 63, "P65 C2 pump function", 0, 1, unit=None),
    _n("p66_water_source_cooling", _B + 64, "P66 Water source air cooling option", 0, 1, unit=None),
    _n("p67_indoor_controller", _B + 65, "P67 Indoor temperature controller", 0, 1, unit=None),
    _n("p68_flow_switch_type", _B + 66, "P68 Water flow switch type", 0, 1, unit=None),
    _n("p69_fan_type", _B + 67, "P69 Fan type", 0, 3, unit=None),
    _n("p70_power_memory", _B + 68, "P70 Power-down memory", 0, 1, unit=None),
    _n("p71_fan_speed_control", _B + 69, "P71 DC fan speed control", 0, 1, unit=None),
    _n("p72_fan_manual_speed", _B + 70, "P72 DC fan manual speed", 0, 1500, 10, 10, unit="rpm"),
    _n("p73_pressure_sensor", _B + 71, "P73 Pressure sensor enable", 0, 1, unit=None),
    _n("p74_evi_valve_mode", _B + 72, "P74 Enthalpy injection valve mode", 0, 3, unit=None),
    _n("p75_evi_opening_heating", _B + 73, "P75 EVI valve initial opening heating", 40, 480, unit="P"),
    _n("p76_evi_opening_cooling", _B + 74, "P76 EVI valve initial opening cooling", 40, 480, unit="P"),
    _n("p77_evi_superheat_heating", _B + 75, "P77 EVI superheat heating", -5, 10, 0.1, 10, unit="K"),
    _n("p78_evi_superheat_cooling", _B + 76, "P78 EVI superheat cooling", -5, 10, 0.1, 10, unit="K"),
    _n("p79_wifi_upload_cycle", _B + 77, "P79 WiFi data upload cycle", 0, 5000, unit=None),
    _n("p80_min_freq_coefficient", _B + 78, "P80 Compressor minimum frequency coefficient", 0, 3276, 0.1, 10, unit=None),
    _n("p81_e1_e2_mode", _B + 79, "P81 E1/E2 function mode", 0, 3, unit=None),
    _n("p82_second_source_start", _B + 80, "P82 Second heat source start temperature", -30, 20, 0.1, 10),
    _n("p83_dhw_circ_pump_mode", _B + 81, "P83 DHW circulation pump mode", 0, 3, unit=None),
    _n("p84_dhw_circ_pump_dt", _B + 82, "P84 DHW circulation pump temperature difference", 4, 20, 0.1, 10, unit="K"),
    _n("p85_defrost_ambient", _B + 83, "P85 Defrost ambient temperature", 0, 20, 0.1, 10),
    _n("p86_defrost_ambient_coil_dt", _B + 84, "P86 Defrost ambient/coil difference", 0, 20, 0.1, 10, unit="K"),
    # P87 factory reset (_B + 85): intentionally omitted
    _n("p88_c3_pump_function", _B + 86, "P88 C3 pump function", 0, 1, unit=None),
    _n("p89_superheat_p", _B + 87, "P89 Return superheat proportional coefficient", 0, 20, 0.1, 10, unit=None),
    _n("p90_superheat_d", _B + 88, "P90 Return superheat differential coefficient", 0, 20, unit=None),
    _n("p91_defrost_ambient_coil_dt2", _B + 89, "P91 Defrost ambient/coil difference 2", 0, 20, 0.1, 10, unit="K"),
    _n("p92_heating_superheat", _B + 90, "P92 Heating return target superheat", -5, 10, 0.1, 10, unit="K"),
    _n("p93_heating_superheat_2", _B + 91, "P93 Heating return target superheat 2", -5, 10, 0.1, 10, unit="K"),
    _n("p94_heating_superheat_3", _B + 92, "P94 Heating return target superheat 3", -5, 10, 0.1, 10, unit="K"),
    _n("p95_cooling_superheat", _B + 93, "P95 Cooling return target superheat", -5, 10, 0.1, 10, unit="K"),
    _n("p96_heating_superheat_4", _B + 94, "P96 Heating return target superheat 4", -5, 10, 0.1, 10, unit="K"),
    _n("p97_parameter_96", _B + 95, "P97 Parameter 96", 10, 100, unit=None),
    _n("p98_g1_inversion", _B + 96, "P98 G1 valve signal inversion", 0, 1, unit=None),
    _n("p99_g2_inversion", _B + 97, "P99 G2 valve signal inversion", 0, 1, unit=None),
    _n("p100_g3_inversion", _B + 98, "P100 G3 valve signal inversion", 0, 1, unit=None),
    _n("p101_eev_defrost_steps", _B + 99, "P101 EEV steps for defrosting", 0, 480, unit="P"),
    _n("p102_water_dt_protection", _B + 100, "P102 Inlet/outlet difference protection", 8, 20, 0.1, 10, unit="K"),
    _n("p103_eev_hold_time", _B + 101, "P103 EEV initial opening hold time", 0, 300, unit="s"),
    _n("p104_capacity_calc_freq", _B + 102, "P104 Initial frequency for capacity calculation", 20, 60, unit="Hz"),
    _n("p107_prt_volume", _B + 103, "P107 PRt calculation volume", 1, 100, unit=None),
    # P108 RS485 address (_B + 104): intentionally omitted
    _n("p109_discharge_limit_1", _B + 105, "P109 Discharge temperature frequency limit 1", 80, 125),
    _n("p110_discharge_limit_2", _B + 106, "P110 Discharge temperature frequency limit 2", 80, 125),
    _n("p111_discharge_limit_3", _B + 107, "P111 Discharge temperature frequency limit 3", 80, 125),
    _n("p112_eev_adjust_temp", _B + 108, "P112 EEV adjustment discharge temperature", 80, 125),
    _n("p113_eev_adjust_time", _B + 109, "P113 EEV adjustment time", 1, 120, unit="s"),
    _n("p114_freq_reduction", _B + 110, "P114 Frequency reduction after setpoint reached", 0, 60, unit="%"),
    _n("p115_outlet_protection", _B + 111, "P115 Outlet temperature protection", 70, 90),
)

FORBIDDEN_WRITE_ADDRESSES = frozenset({_B + 85, _B + 104})


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------
def to_signed(raw: int) -> int:
    """Interpret a 16 bit register as signed."""
    return raw - 0x10000 if raw & 0x8000 else raw


def to_register(value: int) -> int:
    """Encode a signed integer as a 16 bit register value."""
    if not -0x8000 <= value <= 0xFFFF:
        raise ValueError(f"value {value} does not fit into 16 bit")
    return value & 0xFFFF


def split_block(start: int, count: int, max_len: int = MAX_REGISTERS_PER_READ):
    """Yield (address, count) chunks of at most max_len registers."""
    end = start + count
    while start < end:
        n = min(max_len, end - start)
        yield start, n
        start += n
