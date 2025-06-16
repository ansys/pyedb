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

from ansys.edb.core.hierarchy.spice_model import SPICEModel as GrpcSpiceModel


class SpiceModel(GrpcSpiceModel):  # pragma: no cover
    """Manage :class:`SpiceModel <ansys.edb.core.hierarchy.spice_model.SpiceModel>`"""

    def __init__(self, edb_object=None, name=None, file_path=None, sub_circuit=None):
        if edb_object:
            super().__init__(edb_object.msg)
        elif name and file_path:
            if not sub_circuit:
                sub_circuit = name
            edb_object = GrpcSpiceModel.create(name=name, path=file_path, sub_circuit=sub_circuit)
            super().__init__(edb_object.msg)

    @property
    def name(self):
        """Model name.

        Returns
        -------
        str
            Model name.

        """
        return self.model_name

    @property
    def spice_file_path(self):
        return self.model_path
