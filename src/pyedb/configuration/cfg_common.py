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

"""Shared helpers, base classes, and variable models for configuration builders."""

from typing import Any, Iterable, List, Optional, Union

from pydantic import BaseModel, Field

_EMPTY_SERIALIZATION_VALUES = (None, [], {})


def compact_dict(
    data: Optional[dict] = None,
    /,
    *,
    exclude: tuple = _EMPTY_SERIALIZATION_VALUES,
    **kwargs,
) -> dict:
    """Return a copy of *data* with empty values removed.

    Parameters
    ----------
    data : dict, optional
        Base mapping to filter.
    exclude : tuple, optional
        Values to omit. Defaults to ``(None, [], {})``.
    **kwargs
        Extra key-value pairs merged into *data* before filtering.
    """
    raw = dict(data or {})
    raw.update(kwargs)
    return {key: value for key, value in raw.items() if value not in exclude}


def serialize_item(
    item: Any,
    export_methods: tuple[str, ...] = ("to_dict", "export_properties"),
) -> Any:
    """Serialize one configuration item using its first available export method.

    Parameters
    ----------
    item : Any
        The configuration object to serialize.
    export_methods : tuple of str, optional
        Ordered method names to try for serialization.
        Defaults to ``("to_dict", "export_properties")``.
    """
    for method_name in export_methods:
        method = getattr(item, method_name, None)
        if callable(method):
            return method()
    if hasattr(item, "model_dump"):
        return item.model_dump(exclude_none=True)
    return item


def serialize_list(
    items: Iterable[Any],
    export_methods: tuple[str, ...] = ("to_dict", "export_properties"),
) -> list:
    """Serialize an iterable of configuration items to plain Python objects.

    Parameters
    ----------
    items : iterable
        Configuration objects to serialize.
    export_methods : tuple of str, optional
        Ordered method names to try for serialization.
        Defaults to ``("to_dict", "export_properties")``.
    """
    return [serialize_item(item, export_methods=export_methods) for item in items]


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
        excluded = set(self.protected_attributes)
        if exclude is not None:
            excluded.update(exclude if isinstance(exclude, list) else [exclude])
        return {
            name: value
            for name, value in self.__dict__.items()
            if name not in excluded and not name.startswith("_") and value not in (None, [], {})
        }

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

    variables: List[CfgVar] = Field(default_factory=list)

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
        self.variables.append(CfgVar(name=name, value=value, description=description))

    def to_list(self) -> List[dict]:
        """Serialize configured design variables."""
        return [v.model_dump(exclude_none=True) for v in self.variables]


class CfgBaseModel(BaseModel):
    """Base Pydantic model used by typed configuration payload classes."""

    model_config = {
        "populate_by_name": True,
        "extra": "forbid",
    }
