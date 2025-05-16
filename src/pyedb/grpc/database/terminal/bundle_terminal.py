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

from ansys.edb.core.terminal.bundle_terminal import BundleTerminal as GrpcBundleTerminal
from ansys.edb.core.terminal.terminal import (
    SourceTermToGroundType as GrpcSourceTermToGroundType,
)
from ansys.edb.core.terminal.terminal import HfssPIType as GrpcHfssPIType
from ansys.edb.core.utility.value import Value as GrpcValue

from pyedb.grpc.database.hierarchy.component import Component
from pyedb.grpc.database.layers.layer import Layer
from pyedb.grpc.database.net.net import Net
from pyedb.grpc.database.terminal.terminal import Terminal
from pyedb.grpc.database.utility.rlc import Rlc


class BundleTerminal(GrpcBundleTerminal):
    """Manages bundle terminal properties.

    Parameters
    ----------
    pedb : :class:`Edb <pyedb.grpc.edb.Edb>`
        EDB object.
    edb_object : :class:`BundleTerminal <ansys.edb.core.terminal.terminals.BundleTerminal>`
        BundleTerminal instance from EDB.
    """

    def __init__(self, pedb, edb_object):
        super().__init__(edb_object.msg)
        self._pedb = pedb
        self._edb_object = edb_object

    def decouple(self):
        """Ungroup a bundle of terminals.

        Returns
        -------
        bool
        """
        return self.ungroup()

    @property
    def component(self):
        """Component.

        Returns
        -------
        :class:`Component <pyedb.grpc.database.hierarchy.component.Component`
        """
        return Component(self._pedb, self.component)

    @property
    def impedance(self):
        """Impedance value.

        Returns
        -------
        float
            Impedance value.
        """
        return self.impedance.value

    @impedance.setter
    def impedance(self, value):
        self.impedance = GrpcValue(value)

    @property
    def net(self):
        """Returns Net object.

        Returns
        -------
        :class:`Net <pyedb.grpc.database.net.net.Net>`
        """
        return Net(self._pedb, self.net)

    @property
    def hfss_pi_type(self):
        """Returns HFSS PI type.

        Returns
        -------
        str
        """
        return self.hfss_pi_type.name

    @hfss_pi_type.setter
    def hfss_pi_type(self, value):
        if value.upper() == "DEFAULT":
            self.hfss_pi_type = GrpcHfssPIType.DEFAULT
        elif value.upper() == "COAXIAL_OPEN":
            self.hfss_pi_type = GrpcHfssPIType.COAXIAL_OPEN
        elif value.upper() == "COAXIAL_SHORTENED":
            self.hfss_pi_type = GrpcHfssPIType.COAXIAL_SHORTENED
        elif value.upper() == "GAP":
            self.hfss_pi_type = GrpcHfssPIType.GAP
        elif value.upper() == "LUMPED":
            self.hfss_pi_type = GrpcHfssPIType.LUMPED

    @property
    def reference_layer(self):
        """Returns reference layer.

        Returns
        -------
        :class:`Layer <pyedb.grpc.database.layer.layer.Layer>`
        """
        return Layer(self._pedb, self.reference_layer)

    @reference_layer.setter
    def reference_layer(self, value):
        if isinstance(value, Layer):
            self.reference_layer = value._edb_object
        elif isinstance(value, str):
            self.reference_layer = self._pedb.stackup.signal_layer[value]._edb_object

    @property
    def reference_terminal(self):
        """Returns reference terminal.

        Returns
        -------
        :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`
        """
        return Terminal(self._pedb, self.reference_terminal)

    @reference_terminal.setter
    def reference_terminal(self, value):
        if isinstance(value, Terminal):
            self.reference_terminal = value._edb_object

    @property
    def rlc_boundary_parameters(self):
        """Returns Rlc parameters

        Returns
        -------
        :class:`Rlc <pyedb.grpc.database.utility.rlc.Rlc>`
        """
        return Rlc(self._pedb, self.rlc)

    @property
    def source_amplitude(self):
        """Returns source amplitude.

        Returns
        -------
        float
        """
        return self.source_amplitude.value

    @source_amplitude.setter
    def source_amplitude(self, value):
        self.source_amplitude = GrpcValue(value)

    @property
    def source_phase(self):
        """Returns source phase.

        Returns
        -------
        float
        """
        return self.source_phase.value

    @source_phase.setter
    def source_phase(self, value):
        self.source_phase = GrpcValue(value)

    @property
    def term_to_ground(self):
        """Returns terminal to ground.

        Returns
        -------
        str
            Terminal name.
        """
        return self.term_to_ground.name

    @term_to_ground.setter
    def term_to_ground(self, value):
        if value.upper() == "NO_GROUND":
            self.term_to_ground = GrpcSourceTermToGroundType.NO_GROUND
        elif value.upper() == "NEGATIVE":
            self.term_to_ground = GrpcSourceTermToGroundType.NEGATIVE
        elif value.upper() == "POSITIVE":
            self.term_to_ground = GrpcSourceTermToGroundType.POSITIVE

    @property
    def terminals(self):
        """Returns terminals list.

        Returns
        -------
        List[:class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
        """
        return [Terminal(self._pedb, terminal) for terminal in self.terminals]
