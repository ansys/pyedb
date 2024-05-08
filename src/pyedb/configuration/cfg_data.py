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

from pyedb.configuration.cfg_components import CfgComponent
from pyedb.configuration.cfg_ports_sources import CfgPort, CfgSources


class CfgData(object):
    """Manages configure data."""

    def __init__(self, pedb, **kwargs):
        self.pedb = pedb
        self.edb_comps = self.pedb.components.components

        self.general = None
        self.boundaries = None
        self.nets = None
        self.components = [CfgComponent(self, **component) for component in kwargs.get("components", [])]
        self.padstacks = None
        self.pin_groups = None
        self.ports = [CfgPort(self, **port) for port in kwargs.get("ports", [])]
        self.sources = [CfgSources(self, **source) for source in kwargs.get("sources", [])]
        self.setups = None
        self.stackup = None
        self.s_parameters = None
        self.spice_models = None
        self.package_definition = None
        self.operations = None
