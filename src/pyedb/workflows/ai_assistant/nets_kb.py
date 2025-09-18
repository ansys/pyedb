# ------------------------------------------------------------------
# Net classifier – twin of the component classifier
# ------------------------------------------------------------------
from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
import io
import json
import re
from typing import List, Optional, Union


# ------------------------------------------------------------------
# 1.  One rule → one net class
# ------------------------------------------------------------------
@dataclass(slots=True, frozen=True)
class NetRule:
    net_class: str  # short tag   (PWR, USB_P, DDR_CLK …)
    description: str  # human readable
    regex: str | None = None  # re.IGNORECASE search on net name
    prefix: str | None = None  # simple prefix match (faster)
    suffix: str | None = None  # simple suffix match
    probability: float = 1.0  # confidence if rule hits


# ------------------------------------------------------------------
# 2.  Industry net-name matrix  (IPC-2140 / vendor app-notes)
# ------------------------------------------------------------------
NET_KB: tuple[NetRule, ...] = (
    # -------------- POWER ----------------------------------------------------
    NetRule("PWR", "power rail", regex=r"(?:^|_)(vcc|vdd|vdda|vref|vttr|vbus)(?:_|$)", probability=0.98),
    NetRule("GND", "ground", regex=r"(?:^|_)(gnd|agnd|dgnd|pgnd)(?:_|$)", probability=0.99),
    # ------------- value-based power rails ---------------------------------
    NetRule("PWR", "power rail (value)", regex=r"(?:^|_)\d+\.\d+v|\d+v(?=_|$|(?=\d))", probability=0.96),
    NetRule("PWR", "DDR VREF", regex=r"(?:^|_)vrefddr", probability=0.96),
    # -------------- HIGH-SPEED DIFF PAIRS ------------------------------------
    NetRule("USB_P", "USB +", regex=r"(?:^|_)usb.*[_+]p$", probability=0.97),
    NetRule("USB_N", "USB –", regex=r"(?:^|_)usb.*[_+]n$", probability=0.97),
    # -------------- ETHERNET -------------------------------------------------
    NetRule("ETH_TX_P", "Eth TX+", regex=r"(?:^|_)eth.*tx.*[_+]?p$", probability=0.96),
    NetRule("ETH_TX_N", "Eth TX-", regex=r"(?:^|_)eth.*tx.*[_+]?n$", probability=0.96),
    NetRule("ETH_RX_P", "Eth RX+", regex=r"(?:^|_)eth.*rx.*[_+]?p$", probability=0.96),
    NetRule("ETH_RX_N", "Eth RX-", regex=r"(?:^|_)eth.*rx.*[_+]?n$", probability=0.96),
    # -------------- PCIe -----------------------------------------------------
    NetRule("PCIe_TX_P", "PCIe TX+", regex=r"(?:^|_)pcie.*tx.*[_+]?p$", probability=0.97),
    NetRule("PCIe_TX_N", "PCIe TX-", regex=r"(?:^|_)pcie.*tx.*[_+]?n$", probability=0.97),
    NetRule("PCIe_RX_P", "PCIe RX+", regex=r"(?:^|_)pcie.*rx.*[_+]?p$", probability=0.97),
    NetRule("PCIe_RX_N", "PCIe RX-", regex=r"(?:^|_)pcie.*rx.*[_+]?n$", probability=0.97),
    NetRule("PCIe_CTRL", "PCIe ctl", regex=r"(?:^|_)pcie.*(?:dis|wake|reset|perst|clkreq)", probability=0.96),
    # -------------- DDR -------------------------------------------------
    NetRule("DDR_CLK_P", "DDR clk+", regex=r"(?:^|_)ddr.*clk.*[_+]?p$", probability=0.97),
    NetRule("DDR_CLK_N", "DDR clk-", regex=r"(?:^|_)ddr.*clk.*[_+]?n$", probability=0.97),
    NetRule("DDR_DQ", "DDR data", regex=r"(?:^|_)ddr.*dq", probability=0.95),
    NetRule("DDR_DM", "DDR DM", regex=r"(?:^|_)ddr.*dm", probability=0.95),  # <-- catches DM4
    NetRule("DDR_ADDR", "DDR addr", regex=r"(?:^|_)ddr.*a\d", probability=0.95),
    NetRule("DDR_CTRL", "DDR ctrl", regex=r"(?:^|_)ddr.*(?:ras|cas|we|cke|cs|ba)", probability=0.95),
    # -------------- CLOCK -------------------------------------------------
    NetRule("CLK", "clock", regex=r"(?:^|_)clk\d*$", probability=0.94),  # CLK, CLK25, CLK_50M
    NetRule("RESET", "reset", regex=r"(?:^|_)(reset|nrst)", probability=0.98),
    NetRule("JTAG_TMS", "JTAG TMS", regex=r"(?:^|_)jtag.*tms", probability=0.97),
    NetRule("JTAG_TCK", "JTAG TCK", regex=r"(?:^|_)jtag.*tck", probability=0.97),
    NetRule("JTAG_TDI", "JTAG TDI", regex=r"(?:^|_)jtag.*tdi", probability=0.97),
    NetRule("JTAG_TDO", "JTAG TDO", regex=r"(?:^|_)jtag.*tdo", probability=0.97),
    NetRule("SWDIO", "SWD data", regex=r"(?:^|_)swdio", probability=0.97),
    NetRule("SWCLK", "SWD clk", regex=r"(?:^|_)swclk", probability=0.97),
    NetRule("ADC", "ADC", regex=r"(?:^|_)adc", probability=0.95),
    NetRule("DAC", "DAC", regex=r"(?:^|_)dac", probability=0.95),
    NetRule("LVDS_P", "LVDS +", regex=r"(?:^|_)lvds.*[_+]?p$", probability=0.97),
    NetRule("LVDS_N", "LVDS –", regex=r"(?:^|_)lvds.*[_+]?n$", probability=0.97),
    # ------------- generic differential pairs (any tech) -----------------
    NetRule(
        "DIFF_P",
        "diff pair +",
        regex=r"(?:^|_)(sfp|refclk|fmc|sata|hdmi|mipi|can|rs485|trd).*[_+]?p$",
        probability=0.96,
    ),
    NetRule(
        "DIFF_N",
        "diff pair –",
        regex=r"(?:^|_)(sfp|refclk|fmc|sata|hdmi|mipi|can|rs485|trd).*[_+]?n$",
        probability=0.96,
    ),
    # ----------------------------------------------------------
    #  catch-all must stay LAST
    # ----------------------------------------------------------
    NetRule("SIG", "unspecified signal", None, probability=0.10),
)


# ------------------------------------------------------------------
# 3.  Prediction object (same spirit as the component one)
# ------------------------------------------------------------------
@dataclass(slots=True)
class NetPrediction:
    net_name: str
    net_class: str
    description: str
    probability: float

    @property
    def is_power(self) -> bool:
        return self.net_class in {"PWR", "GND"}

    @property
    def is_diff_pair(self) -> bool:
        return "_P" in self.net_class or "_N" in self.net_class


# ------------------------------------------------------------------
# 4.  Core classifier
# ------------------------------------------------------------------
def classify(net_name: str) -> NetPrediction:
    """
    Return the best matching NetPrediction for the supplied net name.
    If nothing matches, we fall back to NetRule('SIG','unspecified signal',…).
    """
    if not net_name:
        net_name = ""
    name_u = net_name.strip().upper()

    best: Optional[NetPrediction] = None
    for rule in NET_KB:
        hit = False
        if rule.prefix and name_u.startswith(rule.prefix.upper()):
            hit = True
        elif rule.suffix and name_u.endswith(rule.suffix.upper()):
            hit = True
        elif rule.regex and re.search(rule.regex, name_u, re.IGNORECASE):
            hit = True

        if hit:
            cand = NetPrediction(
                net_name=net_name,
                net_class=rule.net_class,
                description=rule.description,
                probability=rule.probability,
            )
            if best is None or cand.probability > best.probability:
                best = cand

    if best is None:  # fallback
        best = NetPrediction(
            net_name=net_name,
            net_class="SIG",
            description="unspecified signal",
            probability=0.10,
        )
    return best


def net_predictions_to_json(
    preds: List[NetPrediction], *, file: Optional[str] = None, indent: Union[None, int, str] = 2
) -> str:
    data = [asdict(p) for p in preds]
    txt = json.dumps(data, indent=indent, ensure_ascii=False)
    if file:
        with open(file, "w", encoding="utf-8") as fp:
            fp.write(txt)
    return txt


def net_predictions_to_csv(preds: List[NetPrediction], *, file: Optional[str] = None) -> str:
    if not preds:
        return ""
    out = io.StringIO()
    fieldnames = list(asdict(preds[0]).keys())
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for p in preds:
        writer.writerow(asdict(p))
    txt = out.getvalue()
    if file:
        with open(file, "w", newline="", encoding="utf-8") as fp:
            fp.write(txt)
    return txt


# ------------------------------------------------------------------
# 6.  Quick demo
# ------------------------------------------------------------------
if __name__ == "__main__":
    demo_nets = [
        "VDD_1V8",
        "GND",
        "USB1_DP",
        "USB1_DM",
        "DDR4_A0",
        "DDR4_CLK_P",
        "ETH_TX+",
        "CLK_25M",
        "ADC_VBAT",
        "nRST",
        "JTAG_TMS",
        "GPIO_07",
    ]
    predictions = [classify(n) for n in demo_nets]
    print(net_predictions_to_csv(predictions))
