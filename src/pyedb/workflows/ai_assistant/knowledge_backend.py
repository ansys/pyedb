# knowledge_backend.py
# ---------------------------------------------------------------------------
#  Copyright (C) 2023 – 2024 ANSYS, Inc. and/or its affiliates.
#  SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
from __future__ import annotations

import json
import math
import re
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from knowledge import KnowledgeBase


# ---------------------------------------------------------------------------
# 2.  Drop-in replacement class
# ---------------------------------------------------------------------------
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
        comp_type: str,
        comp_value: str,
        package: str = "",
        voltage: str = "",
        tolerance: str = "",
        dielectric: str = "",
    ) -> Optional[str]:
        """
        Determine component function (fuzzy + legacy fallback).
        """
        comp_type = comp_type.lower()
        comp_value = (comp_value or "").strip()

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
                    return func_name

        # 2.  legacy static table
        return self._legacy_get_comp_func(comp_type, comp_value)

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
                "0.1uF": "high_freq_decoupling",
                "100nF": "high_freq_decoupling",
                "10uF": "bulk_decoupling",
                "22uF": "bulk_decoupling",
                "1uF": "general_decoupling",
            },
            "resistor": {"49.9": "termination", "50": "termination", "0": "zero_ohm", "100": "pull_up_down"},
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

    def _legacy_get_comp_func(self, comp_type: str, comp_value: str) -> Optional[str]:
        comp_type = comp_type.lower()
        rules = self.component_rules.get(comp_type, {})
        return rules.get(comp_value, rules.get("default"))

    # ------------------------------------------------------------------
    #  private – fuzzy matcher
    # ------------------------------------------------------------------
    @staticmethod
    def _fuzzy_match(val, pkg, v, tol, dielec, rule) -> bool:
        if (vrx := getattr(rule, "value_regex", None)) and not re.match(vrx, val, flags=re.I):
            return False

        def _float_safe(text, default=0.0):
            try:
                return float(re.search(r"(\d+\.?\d*)", text or "").group(1))
            except Exception:
                return default

        if (pmax := getattr(rule, "package_max_mm", math.inf)) < math.inf:
            if _float_safe(pkg, 999) > pmax:
                return False
        if (vmin := getattr(rule, "voltage_min_V", 0)) > 0:
            if _float_safe(v, 999) < vmin:
                return False
        if (tmax := getattr(rule, "tolerance_max_pct", math.inf)) < math.inf:
            if _float_safe(tol, 999) > tmax:
                return False
        if dlist := getattr(rule, "dielectric", []):
            if dielec.upper() not in (d.upper() for d in dlist):
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
