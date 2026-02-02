# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

from ansys.edb.core.utility.value import Value as CoreValue


class PortPostProcessingProp:
    """Port post-processing properties.

    This class wraps the gRPC port post-processing properties, providing access to
    deembedding length, renormalization impedance, voltage magnitude and phase,
    and flags for deembedding and renormalization.

    Parameters
    ----------
    core : GrpcPortPostProcessing
        The underlying gRPC port post-processing object.
    """

    def __init__(self, core):
        self.core = core

    @property
    def deembed_length(self):
        """Deembedding length.

        Returns
        -------
        float
            The deembedding length value.
        """
        return self.core.deembed_length.value

    @deembed_length.setter
    def deembed_length(self, value):
        self.core.deembed_length = CoreValue(value)

    @property
    def renormalization_impedance(self):
        """Renormalization impedance.

        Returns
        -------
        float
            The renormalization impedance value.
        """
        return self.core.renormalization_impedance.value

    @renormalization_impedance.setter
    def renormalization_impedance(self, value):
        self.core.renormalization_impedance = CoreValue(value)

    @property
    def voltage_magnitude(self):
        """Voltage magnitude.

        Returns
        -------
        float
            The voltage magnitude value.
        """
        return self.core.voltage_magnitude.value

    @voltage_magnitude.setter
    def voltage_magnitude(self, value):
        self.core.voltage_magnitude = CoreValue(value)

    @property
    def voltage_phase(self):
        """Voltage phase.

        Returns
        -------
        float
            The voltage phase value.
        """
        return self.core.voltage_phase.value

    @voltage_phase.setter
    def voltage_phase(self, value):
        self.core.voltage_phase = CoreValue(value)

    @property
    def do_deembed(self):
        """Whether to perform deembedding.

        Returns
        -------
        bool
            True if deembedding is enabled, False otherwise.
        """
        return self.core.do_deembed

    @do_deembed.setter
    def do_deembed(self, value: bool):
        self.core.do_deembed = value

    @property
    def do_renormalize(self):
        """Whether to perform renormalization.

        Returns
        -------
        bool
            True if renormalization is enabled, False otherwise.
        """
        return self.core.do_renormalize

    @do_renormalize.setter
    def do_renormalize(self, value: bool):
        self.core.do_renormalize = value
