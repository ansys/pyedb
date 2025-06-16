# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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

import struct

import numpy as np
import skrf as rf


class ComponentLib:
    """Handle component libraries."""

    def __init__(self):
        self.capacitors = {}
        self.inductors = {}
        self.path = ""
        self.series = {}


class Series:
    """Handle component series."""

    def __init__(self):
        self._index_file = ""
        self._sbin_file = ""


class ComponentPart:
    """Handle component part definition."""

    def __init__(self, name, index, sbin_file):
        self.name = name
        self._index = index
        self._sbin_file = sbin_file
        self.nb_ports = 2
        self.nb_freq = 0
        self.ref_impedance = 50.0
        self._s_parameters = None
        self.type = ""

    @property
    def s_parameters(self):
        """Return a skrf.network.Network object.

        See `scikit-rf documentation <https://scikit-rf.readthedocs.io/en/latest/api/network.html#network-class>`_.
        """
        if not self._s_parameters:
            self._extract_impedance()
        return self._s_parameters

    @property
    def esr(self):
        """Return the equivalent serial resistor for capacitor only."""
        if self.type == "Capacitor":
            z11 = 1 / self.s_parameters.y[:, 0, 0]
            return np.abs(abs(np.abs(np.real((z11.min()))) - 50))
        else:
            return 0.0

    @property
    def f0(self):
        """Return the capacitor self resonant frequency in Hz."""
        if self.type == "Capacitor":
            z11 = 1 / self.s_parameters.y[:, 0, 0]
            fo_index = np.where(np.abs(z11) == np.min(np.abs(z11)))[0][0]
            return self.s_parameters.f[fo_index]
        else:
            return None

    @property
    def esl(self):
        """Return the equivalent serial inductor for capacitor only."""
        if self.type == "Capacitor":
            omega_r = 2 * np.pi * self.f0
            return 1 / (np.power(omega_r, 2) * self.cap_value)
        else:
            return 0.0

    @property
    def cap_value(self):
        """Returns the capacitance value."""
        if self.type == "Capacitor":
            return round(np.imag(self.s_parameters.y[0, 0, 0]) / (2 * np.pi * self._s_parameters.f[0]), 15)
        else:
            return 0.0

    @property
    def ind_value(self):
        """Return the inductance value."""
        if self.type == "Inductor":
            return round(np.imag(1 / self.s_parameters.y[0, 0, 0]) / (2 * np.pi * self._s_parameters.f[0]), 15)
        else:
            return 0.0

    def _extract_impedance(self):
        with open(self._sbin_file, mode="rb") as file:
            file_content = file.read()
            file.seek(self._index)
            self.nb_ports = struct.unpack("i", file_content[self._index : self._index + 4])[0]
            self._index += 4
            self.nb_freq = struct.unpack("i", file_content[self._index : self._index + 4])[0]
            self._index += 4
            self.ref_impedance = struct.unpack("f", file_content[self._index : self._index + 4])[0]
            self._index += 4
            s_matrix = np.zeros((self.nb_freq, 2, 2), dtype=complex)
            frequencies = []
            for f in range(self.nb_freq):
                freq = struct.unpack("f", file_content[self._index : self._index + 4])[0]
                self._index += 4
                s11_re_imp = struct.unpack("f", file_content[self._index : self._index + 4])[0]
                self._index += 4
                s11_im_imp = struct.unpack("f", file_content[self._index : self._index + 4])[0]
                self._index += 4
                s12_re_imp = struct.unpack("f", file_content[self._index : self._index + 4])[0]
                self._index += 4
                s12_im_imp = struct.unpack("f", file_content[self._index : self._index + 4])[0]
                self._index += 4
                s21_re_imp = struct.unpack("f", file_content[self._index : self._index + 4])[0]
                self._index += 4
                s21_im_imp = struct.unpack("f", file_content[self._index : self._index + 4])[0]
                self._index += 4
                s22_re_imp = struct.unpack("f", file_content[self._index : self._index + 4])[0]
                self._index += 4
                s22_im_imp = struct.unpack("f", file_content[self._index : self._index + 4])[0]
                self._index += 4
                s_matrix[f, 0, 0] = s11_re_imp + s11_im_imp * 1j
                s_matrix[f, 0, 1] = s12_re_imp + s12_im_imp * 1j
                s_matrix[f, 1, 0] = s21_re_imp + s21_im_imp * 1j
                s_matrix[f, 1, 1] = s22_re_imp + s22_im_imp * 1j
                frequencies.append(freq)
            self._s_parameters = rf.Network()
            self._s_parameters.frequency = tuple(frequencies)
            self._s_parameters.s = s_matrix
            file.close()
