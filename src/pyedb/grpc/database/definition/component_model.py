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

from typing import Union

from ansys.edb.core.definition.component_model import (
    ComponentModel as CoreComponentModel,
    NPortComponentModel as CoreNPortComponentModel,
)


class ComponentModel:
    """Class managing :class:`ComponentModel <pyedb.grpc.database.definition.component_model.ComponentModel>`."""

    def __init__(self, core):
        self.core = CoreComponentModel(core.msg)

    @property
    def is_null(self):
        """Check if the component model is null.

        Returns
        -------
        bool
            True if the component model is null, False otherwise.

        """
        return self.core.is_null

    @property
    def name(self):
        """Get the name of the component model.

        Returns
        -------
        str
            The name of the component model.

        """
        return self.core.name

    @property
    def reference_file(self):
        """Get the reference file of the component model.

        Returns
        -------
        str
            The reference file of the component model.

        """
        return self.core.reference_file


class NPortComponentModel:
    """Class managing :class:`NPortComponentModel <pyedb.grpc.database.definition.component_model.ComponentModel>`"""

    def __init__(self, core):
        self.core = CoreComponentModel(core.msg)

    @classmethod
    def create(cls, name: str) -> "NPortComponentModel":
        """Create an N-Port component model.

        Parameters
        ----------
        name : str
            Name of the N-Port component model.

        Returns
        -------
        NPortComponentModel
            The created N-Port component model object.

        """
        return cls(CoreNPortComponentModel.create(name))

    @classmethod
    def find_by_id(cls, component_definition, id: int) -> Union[None, "NPortComponentModel"]:
        """Find an N-Port component model by IO count in a given component definition.

        Parameters
        ----------
        component_definition : :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>`
            Component definition to search for the N-Port component model.
        id : int
            IO count of the N-Port component model.
        Returns
        -------
        NPortComponentModel
            N-Port component model that is found, ``None`` otherwise.
        """
        core_nport_model = CoreNPortComponentModel.find_by_id(component_definition.core, id)
        if not core_nport_model.is_null:
            return cls(core_nport_model)
        return None

    @classmethod
    def find_by_name(cls, component_definition, name: str) -> Union[None, "NPortComponentModel"]:
        """Find an N-Port component model by name in a given component definition.

        Parameters
        ----------
        component_definition : :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>`
            Component definition to search for the N-Port component model.
        name : str
            Name of the N-Port component model.

        Returns
        -------
        NPortComponentModel
            N-Port component model that is found, ``None`` otherwise.
        """
        core_nport_model = CoreNPortComponentModel.find_by_name(component_definition.core, name)
        if not core_nport_model.is_null:
            return cls(core_nport_model)
        return None

    @property
    def is_null(self):
        """Check if the N-Port component model is null.

        Returns
        -------
        bool
            True if the N-Port component model is null, False otherwise.

        """
        return self.core.is_null

    @property
    def name(self):
        """Get the name of the N-Port component model.

        Returns
        -------
        str
            The name of the N-Port component model.

        """
        return self.core.name

    @property
    def reference_file(self):
        """Get the reference file of the N-Port component model.

        Returns
        -------
        str
            The reference file of the N-Port component model.

        """
        return self.core.reference_file
