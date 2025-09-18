from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import io
import json
import re
from typing import List, Optional, Tuple, Union


# ------------------------------------------------------------------
# Passive component application matrix
# ------------------------------------------------------------------
@dataclass(slots=True, frozen=True)
class RLC_Application:
    component: str  # 'Capacitor' | 'Inductor' | 'Resistor'
    application: str  # human readable
    val_lo: float  # Ω, H or F
    val_hi: float
    freq_lo: float  # Hz  (-1 = DC or not relevant)
    freq_hi: float  # Hz  (-1 = not relevant)
    package: str  # rough footprint hint 0201…1812
    probability: float


# ------------------------------------------------------------------
# Industry-wide RLC application matrix
# ------------------------------------------------------------------
RLC_KB: Tuple[RLC_Application, ...] = (
    # ----------------  C A P A C I T O R S  -----------------------
    RLC_Application("capacitor", "HF decoupling", 10e-9, 470e-9, 1e6, 5e9, "0402…0805", 0.95),
    RLC_Application("capacitor", "LF bulk", 1e-6, 1e-3, 1e3, 1e6, "1206…1210", 0.90),
    RLC_Application("capacitor", "timing / RC", 1e-9, 10e-6, 1, 1e6, "0603…1206", 0.85),
    RLC_Application("capacitor", "AC coupling", 10e-9, 10e-6, 20, 100e6, "0402…0805", 0.87),
    RLC_Application("capacitor", "RF filter", 1e-12, 1e-9, 100e6, 10e9, "0201…0603", 0.90),
    # ----------------  I N D U C T O R S  -------------------------
    RLC_Application("inductor", "power filter", 0.47e-6, 100e-6, 1e3, 10e6, "0805…1210", 0.92),
    RLC_Application("inductor", "EMI bead", 1e-9, 1e-6, 100e6, 5e9, "0402…0805", 0.90),
    RLC_Application("inductor", "RF choke", 1e-9, 100e-9, 100e6, 10e9, "0201…0603", 0.91),
    RLC_Application("inductor", "DC-DC storage", 1e-6, 100e-6, 100e3, 10e6, "1210…1812", 0.90),
    # ----------------  R E S I S T O R S  -------------------------
    RLC_Application("resistor", "termination", 100, 100e3, -1, 100e6, "0402…0805", 0.92),
    RLC_Application("resistor", "current-sense", 1e-3, 1, -1, 1e6, "0805…2512", 0.93),
    RLC_Application("resistor", "timing / RC", 1e3, 10e6, 1, 1e6, "0603…1206", 0.85),
    RLC_Application("resistor", "RF attenuation", 50, 1e3, 100e6, 20e9, "0201…0402", 0.90),
)


# ------------------------------------------------------------------
# PartClass
# ------------------------------------------------------------------
@dataclass(slots=True, frozen=True)
class PartClass:
    keyword: str
    pin_lo: int
    pin_hi: int
    signal_nets: int
    power_nets: int
    probability: float


KB: Tuple[PartClass, ...] = (
    # ---------- FPGA ----------
    PartClass("XLX-FPGA", 256, 484, 180, 76, 0.30),
    PartClass("XLX-FPGA", 676, 1156, 500, 156, 0.45),
    PartClass("XLX-FPGA", 1517, 2892, 1100, 317, 0.25),
    PartClass("INT-FPGA", 256, 484, 180, 76, 0.30),
    PartClass("INT-FPGA", 676, 1156, 500, 156, 0.45),
    PartClass("INT-FPGA", 1517, 2892, 1100, 317, 0.25),
    PartClass("LAT-FPGA", 256, 484, 180, 76, 0.25),
    PartClass("MCH-FPGA", 256, 484, 180, 76, 0.20),
    # ---------- CPU ----------
    PartClass("INT-CPU", 1156, 1700, 750, 206, 0.40),
    PartClass("INT-CPU", 1800, 2466, 1200, 266, 0.50),
    PartClass("AMD-CPU", 4189, 4189, 1800, 389, 0.10),
    # ---------- MCU ----------
    PartClass("MCP-MCU", 32, 64, 40, 12, 0.55),
    PartClass("MCP-MCU", 100, 144, 100, 20, 0.35),
    PartClass("MCP-MCU", 176, 216, 150, 33, 0.10),
    PartClass("NXP-MCU", 32, 64, 40, 12, 0.55),
    PartClass("NXP-MCU", 100, 144, 100, 20, 0.35),
    PartClass("STM-MCU", 32, 64, 40, 12, 0.55),
    PartClass("REN-MCU", 32, 64, 40, 12, 0.50),
    PartClass("CYP-MCU", 32, 64, 40, 12, 0.45),
    PartClass("ESP-MCU", 32, 64, 40, 12, 0.40),
    PartClass("NUV-MCU", 32, 64, 40, 12, 0.42),  # Nuvoton
    PartClass("GIG-MCU", 32, 64, 40, 12, 0.41),  # GigaDevice
    # ---------- PMIC ----------
    PartClass("TI-PMIC", 24, 48, 28, 10, 0.60),
    PartClass("TI-PMIC", 56, 100, 60, 20, 0.30),
    PartClass("TI-PMIC", 120, 144, 90, 27, 0.10),
    PartClass("ADI-PMIC", 24, 48, 28, 10, 0.60),
    PartClass("ON-PMIC", 24, 48, 28, 10, 0.55),
    PartClass("RTK-PMIC", 24, 48, 28, 10, 0.50),
    PartClass("MPS-PMIC", 24, 48, 28, 10, 0.52),
    PartClass("SII-PMIC", 24, 48, 28, 10, 0.53),  # SII
    # ---------- DSP ----------
    PartClass("TI-DSP", 144, 256, 140, 58, 0.50),
    PartClass("TI-DSP", 384, 532, 300, 116, 0.35),
    PartClass("ADI-DSP", 144, 256, 140, 58, 0.50),
    # ---------- PHY / ETH / RF ----------
    PartClass("TI-PHY", 96, 144, 80, 32, 0.70),
    PartClass("TI-PHY", 168, 220, 130, 48, 0.30),
    PartClass("ETH", 32, 64, 30, 17, 0.80),
    PartClass("ETH", 100, 128, 70, 29, 0.20),
    PartClass("RF", 32, 64, 35, 15, 0.65),
    PartClass("RF", 80, 100, 60, 20, 0.35),
    PartClass("QRV-RF", 32, 64, 35, 15, 0.60),
    PartClass("SKY-RF", 32, 64, 35, 15, 0.58),
    # ---------- VRM ----------
    PartClass("IFX-VRM", 28, 48, 20, 8, 0.45),
    PartClass("IFX-VRM", 56, 80, 40, 16, 0.35),
    PartClass("TI-VRM", 100, 144, 90, 27, 0.20),
    PartClass("MPS-VRM", 28, 48, 20, 8, 0.48),
    # ---------- DrMOS ----------
    PartClass("IFX-DRMOS", 40, 40, 8, 32, 0.55),
    PartClass("IFX-DRMOS", 56, 56, 12, 44, 0.30),
    PartClass("TI-DRMOS", 70, 70, 16, 54, 0.15),
    PartClass("AOS-DRMOS", 40, 40, 8, 32, 0.52),
    # ---------- POL ----------
    PartClass("MPS-POL", 16, 24, 10, 8, 0.60),
    PartClass("TI-POL", 32, 48, 18, 14, 0.40),
    PartClass("RTK-POL", 16, 24, 10, 8, 0.58),
    # ---------- Connectors ----------
    PartClass("USB", 24, 24, 19, 5, 0.90),
    PartClass("HDMI", 19, 19, 16, 3, 0.95),
    PartClass("RJ45", 10, 12, 9, 2, 0.85),
    PartClass("TEC-BOARD", 30, 80, 60, 20, 0.60),
    PartClass("MLX-BOARD", 100, 200, 140, 60, 0.30),
    PartClass("APH-BOARD", 300, 600, 400, 100, 0.10),
    PartClass("HRS-FPC", 10, 60, 40, 10, 0.75),
    PartClass("SATA", 7, 67, 30, 8, 0.90),
    PartClass("POWER", 2, 6, 4, 2, 0.95),
    PartClass("SAM-CONN", 120, 400, 250, 50, 0.70),
    PartClass("JST-CONN", 2, 20, 10, 4, 0.80),
    PartClass("WRH-CONN", 2, 20, 10, 4, 0.78),  # Würth
    PartClass("PUL-CONN", 2, 20, 10, 4, 0.76),  # Pulse
    # ---------- Passives ----------
    PartClass("VSH-IND", 2, 6, 0, 2, 0.95),
    PartClass("COI-IND", 2, 6, 0, 2, 0.92),
    PartClass("TDK-CAP", 2, 6, 0, 2, 0.93),
    PartClass("MUR-CAP", 2, 6, 0, 2, 0.91),
    PartClass("YAG-RES", 2, 6, 0, 2, 0.90),
    PartClass("BOU-RES", 2, 6, 0, 2, 0.88),
    PartClass("KEM-CAP", 2, 6, 0, 2, 0.89),  # Kemet
    PartClass("AVX-CAP", 2, 6, 0, 2, 0.87),  # AVX
    # ---------- Memory ----------
    PartClass("SMI-DRAM", 60, 90, 40, 20, 0.95),
    PartClass("SKH-DRAM", 60, 90, 40, 20, 0.93),
    PartClass("MIC-DRAM", 60, 90, 40, 20, 0.92),
    PartClass("MXIC-NOR", 8, 16, 6, 2, 0.94),  # MXIC
    PartClass("WINB-NOR", 8, 16, 6, 2, 0.93),  # Winbond
)


# ------------------------------------------------------------------
# Output object
# ------------------------------------------------------------------
@dataclass(slots=True)
class Prediction:
    part_class: str
    pin_count: int
    signal_nets: int
    power_nets: int
    probability: float
    application: str = ""
    part_name: str = ""
    refdes: str = ""
    value: float = 0.0

    @property
    def total_nets(self) -> int:
        return self.signal_nets + self.power_nets

    @property
    def power_ratio(self) -> float:
        return self.power_nets / self.total_nets if self.total_nets else 0.0


# ------------------------------------------------------------------
# Vendor map
# ------------------------------------------------------------------
VENDOR_MAP = {
    # -------------  corrected / verified prefixes  -------------
    "XLX": ("XLX", "XILINX"),
    "INT": ("INT", "INTEL", "ALTERA"),
    "AMD": ("AMD",),
    "MCP": ("MCP", "MICROCHIP", "ATMEL"),
    "NXP": ("NXP", "FREESCALE"),
    "STM": ("STM", "ST-", "STMICRO"),
    "TI": ("TI", "TEXAS"),
    "ADI": ("ADI", "ANALOG"),
    "IFX": ("IFX", "INFINEON"),
    "MPS": ("MPS", "MONOLITHIC"),
    "ON": ("ON", "ONSEMI"),
    "RTK": ("RTK", "RICHTEK"),
    "AOS": ("AOS", "ALPHA"),
    "VSH": ("VSH", "VISHAY"),
    "COI": ("COI", "COILCRAFT"),
    "TDK": ("TDK", "EPCOS"),
    "MUR": ("MUR", "MURATA"),
    "YAG": ("YAG", "YAGEO"),
    "BOU": ("BOU", "BOURNS"),
    "KEM": ("KEM", "KEMET"),
    "AVX": ("AVX",),
    "SSG": ("SSG", "SAMSUNG"),
    "SKH": ("SKH", "SKHYNIX", "SK-HYNIX"),
    "MIC": ("MIC", "MICRON"),
    "MXC": ("MXC", "MACRONIX"),
    "WINB": ("WINB", "WINBOND"),
    "QRV": ("QRV", "QORVO"),
    "SKY": ("SKY", "SKYWORKS"),
    "LAT": ("LAT", "LATTICE"),
    "MCH": ("MCH", "MICROSEMI"),
    "REN": ("REN", "RENESAS"),
    "CYP": ("CYP", "CYPRESS"),
    "ESP": ("ESP", "ESPRESSIF"),
    "NUV": ("NUV", "NUVOTON"),
    "GIG": ("GIG", "GIGADEVICE"),
    "WRH": ("WRH", "WÜRTH", "WURTH"),
    "PUL": ("PUL", "PULSE"),
    "EAT": ("EAT", "EATON"),
    "LIT": ("LIT", "LITTELFUSE"),
    "HAR": ("HAR", "HARWIN"),
    "HART": ("HART", "HARTING"),
    "ERN": ("ERN", "ERNI"),
    "PHX": ("PHX", "PHOENIX"),
    "WEI": ("WEI", "WEIDMÜLLER", "WEIDMULLER"),
    "3M": ("3M",),
    "FCI": ("FCI",),
    "GLN": ("GLN", "GLENAIR"),
    "ITT": ("ITT",),
    "SOU": ("SOU", "SOURIAU"),
    "DEU": ("DEU", "DEUTSCH"),
    "CON": ("CON", "CONESYN"),
    "CIN": ("CIN", "CINCH"),
    "SMI": ("SMI", "SMITHS"),
    "RAD": ("RAD", "RADIALL"),
    "ROS": ("ROS", "ROSENBERGER"),
    "HUB": ("HUB", "HUBER-SUHNER"),
    "JST": ("JST",),
    "SAM": ("SAM", "SAMTEC"),
    "APH": ("APH", "AMPHENOL"),
    "HRS": ("HRS", "HIROSE"),
    "TEC": ("TEC", "TE-", "TYCO"),
    "MLX": ("MLX", "MOLEX"),
}


def _extract_vendor(part_name: str) -> str | None:
    part_name = part_name.upper()
    for prefix, aliases in VENDOR_MAP.items():
        for a in aliases:
            if a in part_name:
                return prefix
    return None


# ------------------------------------------------------------------
# Specialized classifier for RLC parts
# ------------------------------------------------------------------
def classify_rlc(component: str, value: float, freq: float = 0.0, package: str = "") -> List[Prediction]:
    """
    Classify a passive component (Capacitor, Inductor, or Resistor) into its application type.

    Parameters
    ----------
    component : str
        Type of passive component. Must be one of ``"Capacitor"``, ``"Inductor"``, or ``"Resistor"``.
    value : float
        Electrical value of the component in base units: Farad (F) for capacitors, Henry (H) for
        inductors, or Ohm (Ω) for resistors.
    freq : float, optional
        Representative operating or corner frequency in Hertz (Hz). Defaults to ``0.0``,
        which disables frequency-range filtering.
    package : str, optional
        Footprint or package size hint (e.g. ``"0402"``, ``"0805"``).
        **Currently unused** – reserved for future extension and has no effect on matching.

    Returns
    -------
    List[Prediction]
        Ordered list (highest probability first) of candidate applications. Each entry
        contains:

        - ``part_class`` – mirrors *component* (Capacitor/Inductor/Resistor)
        - ``application`` – human-readable application name (e.g. ``"HF decoupling"``)
        - ``probability`` – confidence score assigned by the knowledge base
        - ``pin_count``, ``signal_nets``, ``power_nets`` – fixed to typical 2-pin passive values

    Notes
    -----
    The function queries the module-level ``RLC_KB`` table. If no rule matches,
    a single placeholder prediction with ``application="unknown passive"`` and
    ``probability=0.0`` is returned.

    Examples
    --------
    >>> preds = classify_rlc("Capacitor", 100e-9, freq=50e6)
    >>> print(preds[0].application)
    'HF decoupling'
    """
    hits: List[Prediction] = []
    for rule in RLC_KB:
        if rule.component != component:
            continue
        if not (rule.val_lo <= value <= rule.val_hi):
            continue
        if freq and rule.freq_hi != -1:
            if not (rule.freq_lo <= freq <= rule.freq_hi):
                continue
        hits.append(
            Prediction(
                part_class=component,
                pin_count=2,
                signal_nets=0,
                power_nets=2,
                probability=rule.probability,
                application=rule.application,
            )
        )
    if not hits:
        hits.append(
            Prediction(
                part_class=component,
                pin_count=2,
                signal_nets=0,
                power_nets=2,
                probability=0.0,
                application="unknown passive",
            )
        )
    else:
        hits.sort(key=lambda p: p.probability, reverse=True)
    return hits


# ------------------------------------------------------------------
# Generic classifier – extended to call classify_rlc automatically
# ------------------------------------------------------------------
def classify(
    part_name: str,
    pin_count: int,
    signal_nets: Optional[int] = None,
    power_nets: Optional[int] = None,
    *,
    component_type: Optional[str] = None,  # <-- renamed
    value: Optional[float] = None,
    freq: float = 0.0,
    package: str = "",
    refdes: str = "",  # <-- NEW
    tol: int = 0,
    power_tol: int = 0,
) -> List[Prediction]:
    """
    Unified part classifier.

    Automatically choose between **digital/connector** and **passive-RLC**
    classification paths:

    *   If *component* is supplied and is one of ``"Capacitor"``, ``"Inductor"``,
        or ``"Resistor"``, the function calls: func:`classify_rlc` and returns
        immediately.
    *   Otherwise, the legacy digital knowledge base (FPGA, CPU, PMIC, connectors,
        etc.) is queried.

    Parameters
    ----------
    part_name : str
        Manufacturer part number or free-form description.
    pin_count : int
        Total number of physical pins.
    signal_nets : int, optional
        Number of signal nets connected to the part.
    power_nets : int, optional
        Number of power/ground nets connected to the part.
    component : str, optional
        **RLC mode switch** – supply ``"Capacitor"``, ``"Inductor"``, or
        ``"Resistor"`` to force passive-only classification.
    value : float, optional
        **RLC mode** – electrical value in base units (Farad, Henry, Ohm).
        *Required* when *component* is given.
    freq : float, optional
        **RLC mode** – typical operating or corner frequency (Hz). Defaults to
        ``0.0`` (no frequency filtering).
    package : str, optional
        **RLC mode** – footprint hint (e.g. ``"0402"``). Currently unused,
        reserved for future extensions.
    tol : int, optional
        Tolerance for *signal_nets* matching in digital mode (default ``0``).
    power_tol : int, optional
        Tolerance for *power_nets* matching in digital mode (default ``0``).

    Returns
    -------
    List[Prediction]
        an Ordered list (the highest probability first) of candidate classes. Each
        prediction contains at least:

        * ``part_class`` – either the digital keyword (``"XLX-FPGA"``, ``"USB"``,
          …) or the literal *component* string (``"Capacitor"`` …)
        * ``application`` – human-readable application name for RLC parts,
          empty string for digital parts
        * ``probability`` – confidence score
        * ``pin_count``, ``signal_nets``, ``power_nets`` – supplied or inferred
          counts

    Raises
    ------
    ValueError
        When *component* is supplied, but *value* is missing.

    Examples
    --------
    Digital part::

        >>> preds = classify("STM32F407", 100, 100)
        >>> preds[0].part_class
        'STM-MCU'

    Passive part::

        >>> preds = classify("GRM188R71C", 2,
        ...                  component="Capacitor", value=100e-9, freq=50e6)
        >>> preds[0].application
        'HF decoupling'
    """
    if component_type and component_type.lower() in {"capacitor", "inductor", "resistor"}:
        if value is None:
            raise ValueError("RLC classification requires *value* (Ohm, H or F)")
        preds = classify_rlc(component_type, value, freq, package)
        for p in preds:
            p.part_name = part_name
            p.refdes = refdes
            p.value = round(value, 13) if value is not None else 0.0
        return preds

        # ---------- digital branch ----------
    vendor = _extract_vendor(part_name)
    part_name_u = part_name.upper()
    hits: List[Prediction] = []

    for rule in KB:
        if not (rule.pin_lo <= pin_count <= rule.pin_hi):
            continue
        kw_vendor, _, kw_class = rule.keyword.partition("-")
        if vendor:
            if kw_vendor and kw_vendor != vendor:
                continue
        else:
            if kw_vendor:
                continue
        if not re.search(kw_class or rule.keyword, part_name_u):
            continue
        if signal_nets is not None and abs(rule.signal_nets - signal_nets) > tol:
            continue
        if power_nets is not None and abs(rule.power_nets - power_nets) > power_tol:
            continue
        hits.append(
            Prediction(
                part_class=rule.keyword,
                pin_count=pin_count,
                signal_nets=rule.signal_nets,
                power_nets=rule.power_nets,
                probability=rule.probability,
                application="",
                part_name=part_name,
                refdes=refdes,
                value=round(value, 13) if value is not None else 0.0,
            )
        )

    if not hits:  # Unknown – keep everything
        hits.append(
            Prediction(
                part_class="Unknown",
                pin_count=pin_count,
                signal_nets=signal_nets or 0,
                power_nets=power_nets or 0,
                probability=0.0,
                application="",
                part_name=part_name,
                refdes=refdes,
                value=round(value, 13) if value is not None else 0.0,
            )
        )
    else:
        hits.sort(key=lambda p: p.probability, reverse=True)
    return hits


def predictions_to_json(
    predictions: List[Prediction], file: Optional[str] = None, indent: Union[None, int, str] = 2
) -> str:
    """
    Serialize a list of `Prediction` objects to a JSON string.

    Parameters
    ----------
    predictions : List[Prediction]
        Predictions obtained from: func:`classify` or: func:`classify_rlc`.
    file : str, optional
        When provided the JSON string is **also** written to this path
        (UTF-8 encoded). If the file exists, it will be overwritten.
    indent : int | str | None, default ``2``
        Passed directly to :py:func:`json.dumps` to control pretty-printing.
        Use None for the most compact representation.

    Returns
    -------
    str
        JSON-encoded string of the prediction list. Each element is the
        dictionary representation of a: class:`Prediction` instance
        (keys: ``part_class``, ``pin_count``, ``signal_nets``, ``power_nets``,
        ``probability``, ``application``).

    Examples
    --------
    >>> preds = classify("GRM188R71C", 2, component="Capacitor", value=100e-9)
    >>> json_str = predictions_to_json(preds)
    >>> print(json_str)
    [
      {
        "part_class": "Capacitor",
        "pin_count": 2,
        "signal_nets": 0,
        "power_nets": 2,
        "probability": 0.95,
        "application": "HF decoupling"
      }
    ]
    """
    if not predictions:  # handle an empty list
        return "[]"

    data = [asdict(p) for p in predictions]
    json_str = json.dumps(data, indent=indent, ensure_ascii=False)

    if file:
        with open(file, "w", encoding="utf-8") as fp:
            fp.write(json_str)
    return json_str


def predictions_to_csv(predictions: List[Prediction], *, file: Optional[str] = None) -> str:
    """
    Serialize a list of `Prediction` objects to a CSV string.

    Parameters
    ----------
    predictions : List[Prediction]
        Predictions obtained from: func:`classify` or: func:`classify_rlc`.
    file : str, optional
        When provided the CSV string is **also** written to this path
        (UTF-8 encoded, POSIX line endings). If the file exists, it will be
        overwritten.

    Returns
    -------
    str
        CSV-encoded string with a **header row**. Columns are ordered as:
        ``part_class, pin_count, signal_nets, power_nets, probability, application``.

    Examples
    --------
    >>> preds = classify("STM32F407", 100, 100)
    >>> csv_str = predictions_to_csv(preds)
    >>> print(csv_str)
    part_class, pin_count, signal_nets, power_nets, probability, application
    STM-MCU,100,100,20,0.55,
    """
    if not predictions:  # handle an empty list
        return ""

    output = io.StringIO()
    fieldnames = list(asdict(predictions[0]).keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for p in predictions:
        writer.writerow(asdict(p))

    csv_str = output.getvalue()
    if file:
        with open(file, "w", newline="", encoding="utf-8") as fp:
            fp.write(csv_str)
    return csv_str


# ------------------------------------------------------------------
# Quick demo
# ------------------------------------------------------------------
if __name__ == "__main__":
    # 1. Digital part – legacy path
    print("Digital part:")
    print(predictions_to_csv(classify("STM32F407", 100, 100)))

    # 2. RLC parts – new path
    print("\nCapacitor 100 nF @ 50 MHz:")
    print(predictions_to_csv(classify("GRM188R71C", 2, component="Capacitor", value=100e-9, freq=50e6)))

    print("\nInductor 10 µH:")
    print(predictions_to_csv(classify("744777910", 2, component="Inductor", value=10e-6)))

    print("\nResistor 10 mΩ current-sense:")
    print(predictions_to_csv(classify("LR1206-R010", 2, component="Resistor", value=10e-3)))
