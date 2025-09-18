# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
from pathlib import Path

import pytest

from pyedb.workflows.ai_assistant.knowledge_backend import AIKnowledgeBase
from tests.system.base_test_class import BaseTestClass

pytestmark = [pytest.mark.system]


class TestClass(BaseTestClass):
    @pytest.fixture(autouse=True)
    def init(self, local_scratch):
        working_dir = Path(local_scratch.path)
        self.working_dir = working_dir

    def test_ai_component_knowledge(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        ai = AIKnowledgeBase(edbapp)
        component_functions = []
        for refdes, comp in edbapp.components.instances.items():
            component_functions.append(ai.get_component_function(comp=comp))
        assert len(component_functions) == 380
        assert len([cap for cap in component_functions if cap.application == "HF decoupling"]) == 296
        edbapp.close()

    def test_ai_nets_knowledge(self, edb_examples):
        edbapp = edb_examples.get_si_verse()
        ai = AIKnowledgeBase(edbapp)
        nets_functions = []
        for net_name, net in edbapp.nets.nets.items():
            nets_functions.append(ai.classify_net_by_name(net_name))
        assert len(nets_functions) == 348
        assert len([net for net in nets_functions if net.net_class == "PCIe_RX_N"]) == 4
        assert len([net for net in nets_functions if net.net_class == "DDR_DQ"]) == 80
        assert len([net for net in nets_functions if net.net_class == "DDR_ADDR"]) == 16
        assert len([net for net in nets_functions if net.net_class == "PWR"]) == 13
        assert len([net for net in nets_functions if net.net_class == "GND"]) == 2
        edbapp.close()
