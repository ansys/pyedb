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

import warnings

from ansys.edb.core.hierarchy.spice_model import SPICEModel as CoreSpiceModel


class SpiceModel:  # pragma: no cover
    """Manage :class:`SpiceModel <ansys.edb.core.hierarchy.spice_model.SpiceModel>`"""

    def __init__(self, component, name=None, file_path=None, sub_circuit=None):
        self._component = component

        if name and file_path:
            if not sub_circuit:
                sub_circuit = name
            edb_object = CoreSpiceModel.create(name=name, path=file_path, sub_circuit=sub_circuit)
            self.core = edb_object
        else:
            self.core = component.component_property.model

    @property
    def name(self) -> str:
        """SPICE model name.

        Returns
        -------
        str
            SPICE model name.

        """
        return self.core.model_name

    @property
    def model_name(self):
        """Model name.

        .. deprecated:: 0.70.0
                Use :attr:`name` instead.

        Returns
        -------
        str
            Model name.

        """
        warnings.warn("`model_name` is deprecated. Use `name` instead.", DeprecationWarning)
        return self.core.model_name

    @property
    def spice_file_path(self):
        return self.core.model_path

    @property
    def file_path(self):
        """SPICE file path.

        Returns
        -------
        str
            SPICE file path.

        """
        return self.core.model_path

    @file_path.setter
    def file_path(self, value):
        """Set SPICE file path.

        Parameters
        ----------
        value : str
            New SPICE file path.

        """
        self.core.model_path = value
        self._component._set_model(self.core)
