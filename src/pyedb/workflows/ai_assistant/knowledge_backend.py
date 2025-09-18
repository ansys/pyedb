# knowledge_backend.py
# ---------------------------------------------------------------------------
#  Copyright (C) 2023 – 2024 ANSYS, Inc. and/or its affiliates.
#  SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
from __future__ import annotations

import json
import math
import re
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from pyedb.grpc.database.components import Component

from pyedb.workflows.ai_assistant.knowledge import Capacitor, Inductor, KnowledgeBase, Resistor


def _get_digit_count(number: float) -> int:
    frac_part = str(float(abs(number))).split(".")[1]
    return len(frac_part.rstrip("0"))


def get_component_nice_value(edb_component) -> str:
    component_type = edb_component.type.lower()
    if component_type in ["capacitor", "inductor", "resistor"]:
        mapping_unit = {"capacitor": "F", "inductor": "H", "resistor": "Ohm"}
        val = edb_component.value
        if val / 1e-12 < 100:
            unit = f"p{mapping_unit[component_type]}"
            _val = round(val / 1e-12, 6)
            return f"{_val:.{_get_digit_count(_val)}f}{unit}"
        elif val / 1e-9 < 100:
            unit = f"n{mapping_unit[component_type]}"
            _val = round(val / 1e-9, 6)
            return f"{_val:.{_get_digit_count(_val)}f}{unit}"
        elif val / 1e-6 < 100:
            unit = f"u{mapping_unit[component_type]}"
            _val = round(val / 1e-6, 6)
            return f"{_val:.{_get_digit_count(_val)}f}{unit}"
        elif val / 1e-3 < 100:
            unit = f"m{mapping_unit[component_type]}"
            _val = round(val / 1e-3, 6)
            return f"{_val:.{_get_digit_count(_val)}f}{unit}"
        elif val >= 1000:
            unit = f"k{mapping_unit[component_type]}"
            _val = round(val / 1e3, 6)
            return f"{_val:.{_get_digit_count(_val)}f}{unit}"
        else:
            _val = round(val, 6)
            unit = mapping_unit[component_type]
            return f"{_val:.{_get_digit_count(_val)}f}{unit}"


class AIKnowledgeBase:
    """
    The brain of the AI assistant – now powered by dataclasses.

    Public API is **identical** to the original implementation so no caller
    code has to change.
    """

    # ----------  construction  ----------
    def __init__(self, edb_app, config_path: Optional[str] = None):
        self.aedb = edb_app
        self.logger = edb_app.logger

        # ----  dataclass back-end  ----
        self._kb = KnowledgeBase()  # singleton of our new knowledge world

        # ----  legacy tables for fall-back  ----
        self._build_legacy_tables()

        # ----  optional custom JSON overlay  ----
        if config_path:
            self._load_custom_knowledge(config_path)

        self.logger and self.logger.info(
            "AI Knowledge Base (dataclass edition) initialised – %s component rules",
            sum(len(rules) for rules in self.component_rules.values()),
        )

    # ----------  public API – 100 % compatible  ----------
    def classify_net_by_name(self, net_name: str) -> Optional[str]:
        """
        Classify a net based on its name (smart regex + legacy fallback).
        """
        best_cat, best_conf = None, 0.0

        # 1.  try regex rules from dataclass
        for cat, rule in self._kb.net_regexes.__dict__.items():
            if re.match(rule.pattern, net_name, flags=re.I):
                if rule.conf > best_conf:
                    best_cat, best_conf = cat, rule.conf

        if best_cat:
            self.logger and self.logger.info("SmartNet: %s → %s (%.2f)", net_name, best_cat, best_conf)
            return best_cat

        # 2.  legacy static table
        return self._legacy_classify_net(net_name)

    def get_component_function(
        self,
        comp: Component,
    ) -> Optional[str]:
        """
        Determine component function (fuzzy + legacy fallback).
        """
        comp_type = comp.type.lower()
        comp_value = get_component_nice_value(comp)

        # 1.  fuzzy match using dataclass rules
        if comp_type in {"capacitor", "resistor", "inductor"}:
            rules = getattr(self._kb.component_fuzzy, comp_type).__dict__
            for func_name, rule in rules.items():
                if self._fuzzy_match(comp_value, rule):
                    self.logger and self.logger.info(
                        "SmartComp: %s %s → %s (%s)",
                        comp_type,
                        comp_value,
                        func_name,
                        rule.reason,
                    )
                    component_class = rules[func_name]
                    component_class.part_name = comp.component_def
                    component_class.ref_des = comp.refdes
                    component_class.value = comp.value
                    component_class.confidence = 0.8
                    return component_class
                else:
                    # 2.  legacy static table
                    return self._legacy_get_comp_func(comp)
        else:
            return self._legacy_get_comp_func(comp)

    def get_design_rule(self, rule_name: str, default=None):
        """
        Return a design-rule threshold (searches all IPC sections).
        """
        for section in (
            self._kb.ipc2221c,
            self._kb.ipc2222c,
            self._kb.ipc6012f,
            self._kb.ipc2226,
            self._kb.ipc2615,
            self._kb.ipc7351c,
            self._kb.jedec_jesd22_a104d,
            self._kb.iec_61249_2_21,
        ):
            if hasattr(section, rule_name):
                return getattr(section, rule_name)
        return default

    # ------------------------------------------------------------------
    #  private – legacy compatibility
    # ------------------------------------------------------------------
    def _build_legacy_tables(self):
        """Build the exact tables the old code expected."""
        self.net_patterns = {
            "power": {"VDD", "VCC", "VBUS", "PVDD", "PVCC", "3V3", "5V", "1V2", "1V8", "VIN"},
            "gnd": {"GND", "VSS", "PGND", "AGND", "DGND"},
            "high_speed": {"DP", "DN", "TX", "RX", "USB", "HDMI", "PCIe", "SATA", "MIPI"},
            "clock": {"CLK", "SCK", "CLKIN", "XTAL", "OSC", "MCLK"},
            "analog": {"AIN", "AOUT", "ADC", "DAC", "VREF", "AGND"},
        }

        self.component_rules = {
            "capacitor": {
                100e-9: "high_freq_decoupling",
                22e-6: "bulk_decoupling",
                1e-6: "general_decoupling",
            },
            "resistor": {49.9: "termination", 50: "termination", 0: "zero_ohm", 100: "pull_up_down"},
            "ic": {"default": "digital_ic"},
        }

        self.design_rules = {
            "max_decap_distance_mm": 5.0,
            "simplification_threshold": 3,
            "min_power_plane_width_mm": 0.2,
            "max_via_count_per_net": 50,
        }

    def _legacy_classify_net(self, net_name: str) -> Optional[str]:
        net_name_upper = net_name.upper()
        for cat, patterns in self.net_patterns.items():
            if any(p in net_name_upper for p in patterns):
                return cat
        return None

    def _legacy_get_comp_func(
        self, comp: Component
    ) -> Union[
        Resistor.PrecisionTermination,
        Resistor.PullUpDown,
        Inductor.EmiChock,
        Inductor.RfChock,
        Inductor.PowerFilter,
        Inductor.VrmOutput,
        Inductor.Unknown,
        None,
    ]:
        comp_type = comp.type.lower()
        rules = self.component_rules.get(comp_type, {})
        if comp_type == "resistor":
            comp_value = comp.value
            # Source Octopart, SourcEngine, Z2Data 2023-24
            # 70 % of all 1 kΩ resistors and above in industry are used for digital I/O housekeeping (pull-up/down)
            # or visual indication (LED)
            comp_class = Resistor().PullUpDown()
            comp_class.confidence = 0.70
            if comp_value in rules:
                comp_class = Resistor().PrecisionTermination()
                comp_class.confidence = 0.8
            comp_class.part_name = comp.component_def
            comp_class.ref_des = comp.refdes
            comp_class.value = comp.value
            return comp_class
        elif comp_type == "inductor":
            #  inductance range most frequently specified in 2024 designs, the dominant application sub-circuits, and a
            #  probability estimate (based on 2024 component libraries, distributor stocking data and reference-design
            #  surveys).
            ######################################################################
            # EMI Choke 1 mH – 10 mH (mains), 100 µH – 1 mH (DC rail) SMPS mains inlet, USB-C, HDMI, CAN, PoE,
            # LED driver 2024 usage probability 30%
            # RF Choke 10 nH – 1 µH, Antenna feed, LNA bias, PA supply, GPS / Wi-Fi / 5G modules, probability 2024 25%
            # Power Filter 1 µH – 100 µH DC-DC input π-filter, POL output, LED driver, Class-D audio probability  30%
            # VRM Output 50 nH – 300 nH per phase Multiphase buck: CPU, GPU, DDR memory rails probability 15%
            ######################################################################
            if 49e-9 < comp.value < 301e-9:
                comp_class = Inductor().VrmOutput()
                comp_class.confidence = 0.15
            elif 99e-6 < comp.value < 101e-6:
                comp_class = Inductor().PowerFilter()
                comp_class.confidence = 0.3
            elif 9e-9 < comp.value < 1.1e-6:
                comp_class = Inductor().RfChock
                comp_class.confidence = 0.25
            elif 99e-6 < comp.value < 11e-3:
                comp_class = Inductor().EmiChock()
                comp_class.confidence = 0.3
            else:
                comp_class = Inductor().Unknown()
                comp_class.confidence = 0.0
            comp_class.part_name = comp.component_def
            comp_class.ref_des = comp.refdes
            comp_class.value = comp.value
            return comp_class
        elif comp_type == "capacitor":
            # Below is a value-based industry-market classification of capacitors for the six functional roles you
            # listed. Probabilities are 2024 estimates derived from distributor stocking data, reference-design surveys,
            # and TE / Murata / TDK application notes.
            # HighFreqDecoupling 100 pF – 0.1 µF C0G/NP0 or X7R 0402/0201 MLCC probability 30%
            # RfDcBlock 1 pF – 100 pF C0G/NP0 0402/0201 MLCC probability 10%
            # BulkDecoupling 1 µF – 100 µF X5R/X7R 1210/1206 MLCC or polymer Al probability 25%
            # PackageDecoupling 10 nF – 1 µF ultra-thin X7R 0201/01005 or embedded film probability 20%
            # EsdShunt 100 pF – 1 nF high-voltage C0G 0603/0402 MLCC probability 10%
            # CrystalLoad 6 pF – 30 pF C0G/NP0 0402/0603 MLCC probability 5%
            if 99e-12 < comp.value < 0.11e-6:
                comp_class = Capacitor().HighFreqDecoupling()
                comp_class.voltage_min_V = 6.3
                comp_class.confidence = 0.30
                comp_class.package_max_mm = 0.55
            elif 0.9e-12 < comp.value < 101e-12:
                comp_class = Capacitor().RfDcBlock()
                comp_class.voltage_min_V = 25
                comp_class.package_max_mm = 0.33
                comp_class.confidence = 0.1
            elif 0.9e-6 < comp.value < 101e-6:
                comp_class = Capacitor().BulkDecoupling()
                comp_class.voltage_min_V = 16
                comp_class.package_max_mm = 1.6
                comp_class.confidence = 0.25
            elif 9e-9 < comp.value < 11e-6:
                comp_class = Capacitor().PackageDecoupling()
                comp_class.voltage_min_V = 4.0
                comp_class.package_max_mm = 0.33
                comp_class.confidence = 0.2
            elif 99e-12 < comp.value < 11e-9:
                comp_class = Capacitor().EsdShunt()
                comp_class.voltage_min_V = 50
                comp_class.package_max_mm = 0.8
                comp_class.confidence = 0.1
            elif 5e-12 < comp.value < 31e-12:
                comp_class = Capacitor().CrystalLoad()
                comp_class.voltage_min_V = 25
                comp_class.package_max_mm = 0.55
                comp_class.confidence = 0.05
            else:
                comp_class = Capacitor().Unknown()
                comp_class.voltage_min_V = 5.0
                comp_class.package_max_mm = 0.55
                comp_class.confidence = 0
            comp_class.part_name = comp.component_def
            comp_class.ref_des = comp.refdes
            comp_class.value = comp.value
            return comp_class
        elif comp_type == "ic":
            pass
        else:
            return None

    # ------------------------------------------------------------------
    #  private – fuzzy matcher
    # ------------------------------------------------------------------
    @staticmethod
    def _fuzzy_match(val, rule) -> bool:
        vrx = getattr(rule, "value_regex", None)
        if vrx is not None:
            vrx = vrx.replace(r"\\", "\\")
        if vrx and not re.match(vrx, val, flags=re.I):
            return False
        return True

    # ------------------------------------------------------------------
    #  private – custom JSON overlay (kept for compatibility)
    # ------------------------------------------------------------------
    def _load_custom_knowledge(self, path: str) -> None:
        try:
            with open(path) as f:
                cfg = json.load(f)
            for cat, patterns in cfg.get("net_patterns", {}).items():
                self.net_patterns.setdefault(cat, set()).update(patterns)
            for ctype, rules in cfg.get("component_rules", {}).items():
                self.component_rules.setdefault(ctype, {}).update(rules)
            self.design_rules.update(cfg.get("design_rules", {}))
            self.logger and self.logger.info("Custom knowledge loaded from %s", path)
        except Exception as exc:
            self.logger and self.logger.warning("Failed to load custom knowledge: %s", exc)
