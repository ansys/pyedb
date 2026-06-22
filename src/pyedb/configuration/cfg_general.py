# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
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

"""Build the ``general`` configuration section."""

from typing import Any, Optional

from pydantic import BaseModel, PrivateAttr, field_validator


class CfgGeneral(BaseModel):
    """Fluent builder for the ``general`` section."""

    def __init__(self, pedb=None, data=None, **kwargs):
        """
        Initialize ``CfgGeneral``.

        Parameters
        ----------
        pedb : object, optional
            PyEDB ``Edb`` instance used to push settings into the open design.
        data : dict, optional
            Mapping of field names to values.  Merged with any extra *kwargs*.
        **kwargs : dict
            Additional field values passed directly to the Pydantic model.

        """
        data = dict(data or {})
        data.update(kwargs)
        super().__init__(**data)
        self._pedb = pedb

    model_config = {"arbitrary_types_allowed": True, "extra": "ignore"}

    spice_model_library: str = ""
    s_parameter_library: str = ""
    anti_pads_always_on: Optional[bool] = None
    suppress_pads: Optional[bool] = None

    @field_validator("spice_model_library", "s_parameter_library", mode="before")
    @staticmethod
    def _coerce_to_str(v):
        return "" if v is None else str(v)

    _pedb: Any = PrivateAttr(default=None)

    def set_parameters_to_edb(self):
        """Write general design-option settings into the open EDB design."""
        if self._pedb is None:
            return
        if self.anti_pads_always_on is not None:
            self._pedb.design_options.anti_pads_always_on = self.anti_pads_always_on
        if self.suppress_pads is not None:
            self._pedb.design_options.suppress_pads = self.suppress_pads

    def get_parameters_from_edb(self):
        """Read general design-option settings from EDB."""
        if self._pedb is None:
            return {k: v for k, v in self.model_dump(exclude_none=True).items() if v != ""}
        opts = self._pedb.design_options
        return {"anti_pads_always_on": opts.anti_pads_always_on, "suppress_pads": opts.suppress_pads}

    def apply(self):
        """Write general configuration into the open EDB design."""
        self.set_parameters_to_edb()

    def get_data_from_db(self):
        """Read general settings from EDB."""
        return self.get_parameters_from_edb()
