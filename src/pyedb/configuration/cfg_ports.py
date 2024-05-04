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

from enum import Enum

from pyedb.configuration.cfg_terminal import (CfgPosTerm, CfgNegTerm)


class CfgPort:
    """Manage port."""

    class CfgPortType(Enum):
        """Port type."""

        circuit = [str]
        coax = [str]

    @property
    def pedb(self):
        """Edb."""
        return self.pdata.pedb

    def __init__(self, pdata, **kwargs):
        self.pdata = pdata
        self.name = kwargs.get("name", None)
        self.type = kwargs.get("type", None)
        self.reference_designator = kwargs.get("reference_designator", None)
        pos_term = kwargs.get("positive_terminal", None)
        neg_term = kwargs.get("negative_terminal", None)
        if pos_term:
            self.positive_terminal = CfgPosTerm(
                pport=self, type=list(pos_term.keys())[0], value=list(pos_term.values())[0]
            )
        if neg_term:
            self.negative_terminal = CfgNegTerm(
                pport=self, type=list(neg_term.keys())[0], value=list(neg_term.values())[0]
            )
        self.distributed = kwargs.get("distributed", False)

        self._port_name = None

    def create(self):
        """Create port."""
        if self.type == "circuit":
            candidates = [i for i in self.negative_terminal.get_candidates().values()][0]
            neg_term = candidates.get_terminal(create_new_terminal=True)
        else:
            neg_term = None
        ports = []
        for name, p in self.positive_terminal.get_candidates().items():
            if self.distributed:
                port_name = f"{self.name}_{name}" if self.name else name
            else:
                port_name = self.name if self.name else name
            pos_term = p.get_terminal(port_name, create_new_terminal=True)
            is_circuit_port = True if self.type == "circuit" else False
            port = self.pedb.create_port(pos_term, neg_term, is_circuit_port)
            ports.append(port)
        return ports
