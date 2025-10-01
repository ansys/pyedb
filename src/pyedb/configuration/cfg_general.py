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


class CfgGeneral:
    """Manage configuration general settings."""

    def set_parameters_to_edb(self):
        if self.anti_pads_always_on is not None:
            self.pedb.design_options.anti_pads_always_on = self.anti_pads_always_on
        if self.suppress_pads is not None:
            self.pedb.design_options.suppress_pads = self.suppress_pads

    def get_parameters_from_edb(self):
        anti_pads_always_on = self.pedb.design_options.antipads_always_on
        suppress_pads = self.pedb.design_options.suppress_pads
        data = {"anti_pads_always_on": anti_pads_always_on, "suppress_pads": suppress_pads}
        return data

    def __init__(self, pedb, data):
        self.pedb = pedb
        self.spice_model_library = data.get("spice_model_library", "")
        self.s_parameter_library = data.get("s_parameter_library", "")
        self.anti_pads_always_on = data.get("anti_pads_always_on", None)
        self.suppress_pads = data.get("suppress_pads", None)

    def apply(self):
        self.set_parameters_to_edb()

    def get_data_from_db(self):
        return self.get_parameters_from_edb()
