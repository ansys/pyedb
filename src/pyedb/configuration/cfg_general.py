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
"""Build the ``general`` configuration section.

The existing :class:`CfgGeneral` class is used both by the runtime
configuration loader and by the programmatic builder API.
"""


class CfgGeneral:
    """Fluent builder for the ``general`` configuration section.

    Wraps the attribute names expected by the configuration runtime.

    Attributes
    ----------
    spice_model_library : str
        Root path used to resolve relative SPICE model file paths.
    s_parameter_library : str
        Root path used to resolve relative S-parameter file paths.
    anti_pads_always_on : bool or None
        Design-level anti-pads always-on flag.
    suppress_pads : bool or None
        Design-level suppress-pads flag.
    """

    def set_parameters_to_edb(self):
        """Write general design-option settings into the open EDB design."""
        if self.pedb is None:
            return
        if self.anti_pads_always_on is not None:
            self.pedb.design_options.anti_pads_always_on = self.anti_pads_always_on
        if self.suppress_pads is not None:
            self.pedb.design_options.suppress_pads = self.suppress_pads

    def get_parameters_from_edb(self):
        """Read general design-option settings from the open EDB design.

        Returns
        -------
        dict
            Dictionary with ``anti_pads_always_on`` and ``suppress_pads`` keys.
        """
        if self.pedb is None:
            return self.to_dict()
        anti_pads_always_on = self.pedb.design_options.anti_pads_always_on
        suppress_pads = self.pedb.design_options.suppress_pads
        data = {"anti_pads_always_on": anti_pads_always_on, "suppress_pads": suppress_pads}
        return data

    def __init__(self, pedb=None, data=None):
        """Initialize the general configuration with default empty values."""
        data = data or {}
        self.pedb = pedb
        self.spice_model_library = data.get("spice_model_library", "")
        self.s_parameter_library = data.get("s_parameter_library", "")
        self.anti_pads_always_on = data.get("anti_pads_always_on", None)
        self.suppress_pads = data.get("suppress_pads", None)

    def to_dict(self) -> dict:
        """Serialize configured general settings.

        Returns
        -------
        dict
            Dictionary containing only explicitly configured values for the
            ``general`` section.
        """
        data = {}
        if self.spice_model_library:
            data["spice_model_library"] = self.spice_model_library
        if self.s_parameter_library:
            data["s_parameter_library"] = self.s_parameter_library
        if self.anti_pads_always_on is not None:
            data["anti_pads_always_on"] = self.anti_pads_always_on
        if self.suppress_pads is not None:
            data["suppress_pads"] = self.suppress_pads
        return data

    def apply(self):
        """Write general configuration into the open EDB design."""
        self.set_parameters_to_edb()

    def get_data_from_db(self):
        """Read general settings from EDB (alias for :meth:`get_parameters_from_edb`).

        Returns
        -------
        dict
        """
        return self.get_parameters_from_edb()
