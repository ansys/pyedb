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

    @property
    def s_parameters(self):
        """Return skrf.network.Network object
        See `scikit-rf documentation <https://scikit-rf.readthedocs.io/en/latest/api/network.html#network-class>`
        """
        if not self._s_parameters:
            self._extract_impedance()
        return self._s_parameters

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
