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


from ansys.edb.core.simulation_setup.hfss_simulation_settings import (
    HFSSAdvancedSettings as GrpcHFSSAdvancedSettings,
)
from ansys.edb.core.simulation_setup.simulation_settings import ViaStyle as GrpcViaStyle


class HFSSAdvancedSettings(GrpcHFSSAdvancedSettings):
    def __init__(self, pedb, edb_object):
        super().__init__(edb_object)
        self._pedb = pedb

    @property
    def via_model_type(self) -> str:
        """Via model.

        Returns
        -------
        str
            Model type name.

        """
        return self.via_model_type.name

    @via_model_type.setter
    def via_model_type(self, value):
        if isinstance(value, str):
            if value.upper() == "WIREBOND":
                self.via_model_type = GrpcViaStyle.WIREBOND
            elif value.lower() == "RIBBON":
                self.via_model_type = GrpcViaStyle.RIBBON
            elif value.lower() == "MESH":
                self.via_model_type = GrpcViaStyle.MESH
            elif value.lower() == "FIELD":
                self.via_model_type = GrpcViaStyle.FIELD
            elif value.lower() == "NUM_VIA_STYLE":
                self.via_model_type = GrpcViaStyle.NUM_VIA_STYLE
