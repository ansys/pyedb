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

"""Shared base classes and variable models for configuration builders."""

from typing import List, Optional, Union

from pydantic import BaseModel


class CfgBase:
    """Provide common attribute export and assignment helpers."""

    protected_attributes = ["pedb", "pyedb_obj", "api"]

    def get_attributes(self, exclude=None):
        """Return a filtered dictionary of instance attributes.

        Parameters
        ----------
        exclude : str or list of str, optional
            Attribute names to exclude in addition to the built-in
            ``protected_attributes``.

        Returns
        -------
        dict
            Attribute name → value pairs, with ``None``, empty lists, and
            empty dicts omitted, and private (``_``-prefixed) names excluded.
        """
        attrs = {i: j for i, j in self.__dict__.items() if i not in self.protected_attributes}
        if exclude is not None:
            exclude = exclude if isinstance(exclude, list) else [exclude]
            attrs = {i: j for i, j in attrs.items() if i not in exclude}
        attrs = {i: j for i, j in attrs.items() if not i.startswith("_")}
        attrs = {i: j for i, j in attrs.items() if j not in [None, [], {}]}
        return attrs

    def set_attributes(self, pedb_object):
        """Set all non-protected attributes from this instance onto *pedb_object*.

        Parameters
        ----------
        pedb_object : object
            Target object that must already expose the same attribute names.

        Raises
        ------
        AttributeError
            If an attribute returned by :meth:`get_attributes` is not present
            on *pedb_object*.
        """
        attrs = self.get_attributes()
        for attr, value in attrs.items():
            if attr not in dir(pedb_object):
                raise AttributeError(f"Invalid attribute '{attr}' in '{pedb_object}'")
            setattr(pedb_object, attr, value)


class CfgVar(BaseModel):
    """Represent one design or project variable entry."""

    name: str
    value: Union[int, float, str]
    description: Optional[str] = ""


class CfgVariables(BaseModel):
    """Collect variable definitions for the ``variables`` section."""

    variables: List[CfgVar] = []

    def add_variable(self, name, value, description=""):
        """Append a raw :class:`CfgVar` entry.

        Parameters
        ----------
        name : str
            Variable name.  Prefix with ``$`` for project-scope.
        value : int, float, or str
            Variable value, e.g. ``"0.15mm"`` or ``25``.
        description : str, optional
            Human-readable description.  Default is ``""``.
        """
        self.variables.append(CfgVar(name=name, value=value, description=description))

    def add(self, name, value, description=""):
        """Add a design or project variable.

        Parameters
        ----------
        name : str
            Variable name.  Prefix with ``$`` for project-scope, e.g.
            ``"$project_temp"``; unprefixed names are design-scope.
        value : int, float, or str
            Variable value.
        description : str, optional
            Human-readable description.  Default is ``""``.

        Examples
        --------
        >>> cfg.variables.add("trace_width", "0.15mm", "Default trace width")
        >>> cfg.variables.add("$project_temp", "25cel")
        """
        self.add_variable(name=name, value=value, description=description)

    def to_list(self) -> List[dict]:
        """Serialize configured design variables."""
        return [v.model_dump(exclude_none=True) for v in self.variables]


class CfgBaseModel(BaseModel):
    """Base Pydantic model used by typed configuration payload classes."""

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
