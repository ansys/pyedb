# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Build the ``variables`` configuration section.

The builder in this module wraps
:class:`pyedb.configuration.cfg_common.CfgVariables` and serializes design
variables into the list-based format expected by configuration files.
"""

from __future__ import annotations

from typing import List, Union

from pyedb.configuration.cfg_common import CfgVariables


class VariablesConfig:
    """Fluent builder for the ``variables`` configuration section.

    Wraps :class:`~pyedb.configuration.cfg_common.CfgVariables`.

    Examples
    --------
    >>> cfg.variables.add("trace_width", "100um", "Trace width for SI analysis")
    """

    def __init__(self):
        self._model = CfgVariables()

    def add(self, name: str, value: Union[str, int, float], description: str = ""):
        """Add a design variable.

        Parameters
        ----------
        name : str
            Variable name.
        value : str, int, or float
            Variable value or expression.
        description : str, optional
            Optional free-form description stored with the variable.
        """
        self._model.add_variable(name=name, value=value, description=description)

    def to_list(self) -> List[dict]:
        """Serialize configured design variables.

        Returns
        -------
        list[dict]
            Variables in the order they were added.
        """
        return [v.model_dump() for v in self._model.variables]
