# knowledge_backend.py
# ---------------------------------------------------------------------------
#  Copyright (C) 2023 – 2024 ANSYS, Inc. and/or its affiliates.
#  SPDX-License-Identifier: MIT
# ---------------------------------------------------------------------------
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from pyedb.grpc.database.components import Component
    from pyedb.workflows.ai_assistant.components_kb import Prediction
    from pyedb.workflows.ai_assistant.nets_kb import NetPrediction

from pyedb.workflows.ai_assistant.components_kb import classify as classify_comp
from pyedb.workflows.ai_assistant.nets_kb import classify as classify_net


class AIKnowledgeBase:
    """
    The brain of the AI assistant – now powered by dataclasses.

    Public API is **identical** to the original implementation so no caller
    code has to change.
    """

    # ----------  construction  ----------
    def __init__(self, edb_app, config_path: Optional[str] = None):
        self.edb_app = edb_app
        self.logger = edb_app.logger

        self.logger and self.logger.info("AI Knowledge Base initialised")

    def classify_net_by_name(self, net_name: str) -> Union[NetPrediction, str]:
        """
        Classify a net based on its name (smart regex + legacy fallback).
        """
        result = classify_net(net_name=net_name)
        if result:
            return result
        else:
            return self._legacy_classify_net(net_name=net_name)

    def get_component_function(self, comp: Component) -> Prediction:
        """
        Determine component function (fuzzy + legacy fallback).
        """
        comp_type = comp.type.lower()
        part_name = comp.component_def or ""
        signal_nets = len([net for net in comp.nets if net in self.edb_app.nets.signal])
        power_nets = len([net for net in comp.nets if net in self.edb_app.nets.power])
        result = classify_comp(
            part_name=part_name,
            pin_count=comp.numpins,
            signal_nets=signal_nets,
            power_nets=power_nets,
            component_type=comp_type,
            value=comp.value,
            refdes=comp.refdes,
        )
        if result:
            return result[0]

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
