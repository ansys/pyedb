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

from pyedb.workflows.ai_assistant.knowledge import KnowledgeBase, Resistor


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
        package: str = "",
        voltage: str = "",
        tolerance: str = "",
        dielectric: str = "",
    ) -> Optional[str]:
        """
        Determine component function (fuzzy + legacy fallback).
        """
        comp_type = comp.type.lower()
        comp_value = get_component_nice_value(comp)

        # 1.  fuzzy match using dataclass rules
        if comp_type in {"capacitor", "resistor", "inductor", "ferrite_bead"}:
            rules = getattr(self._kb.component_fuzzy, comp_type).__dict__
            for func_name, rule in rules.items():
                if self._fuzzy_match(comp_value, package, voltage, tolerance, dielectric, rule):
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

    def _legacy_get_comp_func(self, comp: Component) -> Union[Resistor.PrecisionTermination, Resistor.PullUpDown, None]:
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
            pass
        elif comp_type == "capacitor":
            pass
        elif comp_type == "ic":
            pass
        else:
            return None

    # ------------------------------------------------------------------
    #  private – fuzzy matcher
    # ------------------------------------------------------------------
    @staticmethod
    def _fuzzy_match(val, pkg, v, tol, dielec, rule) -> bool:
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
