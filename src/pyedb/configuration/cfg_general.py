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


class CfgGeneral:
    """Manage configuration general settings."""

    def __init__(self, pedb, data):
        self._pedb = pedb
        self.spice_model_library = data.get("spice_model_library", "")
        self.s_parameter_library = data.get("s_parameter_library", "")
        self.anti_pads_always_on = data.get("anti_pads_always_on", False)
        self.suppress_pads = data.get("suppress_pads", True)

    def apply(self):
        self._pedb.design_options.antipads_always_on = self.anti_pads_always_on
        self._pedb.design_options.suppress_pads = self.suppress_pads

    def get_data_from_db(self):
        self.anti_pads_always_on = self._pedb.design_options.antipads_always_on
        self.suppress_pads = self._pedb.design_options.suppress_pads

        data = {}
        data["anti_pads_always_on"] = self.anti_pads_always_on
        data["suppress_pads"] = self.suppress_pads
        return data
