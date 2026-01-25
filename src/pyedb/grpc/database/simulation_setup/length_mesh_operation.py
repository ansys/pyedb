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
# FITNE SS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ansys.edb.core.simulation_setup.mesh_operation import LengthMeshOperation as GrpcLengthMeshOperation


class LengthMeshOperation:
    """PyEDB Length Mesh Operation class."""

    def __init__(
        self,
        core=None,
        name="",
        net_layer_info=None,
        enabled=True,
        refine_inside=False,
        mesh_region="",
        solve_inside=False,
        max_length: str = "1mm",
        restrict_max_length: bool = True,
        max_elements: str = "1000",
        restrict_max_elements: bool = False,
    ):
        if not core:
            self.core = self.create(
                name=name,
                net_layer_info=net_layer_info,
                enabled=enabled,
                refine_inside=refine_inside,
                mesh_region=mesh_region,
                solve_inside=solve_inside,
                max_length=max_length,
                restrict_max_length=restrict_max_length,
                max_elements=max_elements,
                restrict_max_elements=restrict_max_elements,
            )
        else:
            self.core = core

    @classmethod
    def create(
        cls,
        name: str = "",
        net_layer_info: tuple[str, str, bool] = None,
        enabled: bool = True,
        refine_inside: bool = False,
        mesh_region: str = "",
        solve_inside: bool = False,
        max_length: str = "1mm",
        restrict_max_length: bool = True,
        max_elements: str = "1000",
        restrict_max_elements: bool = False,
    ) -> "LengthMeshOperation":
        """Create a Length Mesh Operation.
        Parameters
        ----------
        name : str
            Name of the mesh operation.
        net_layer_info : tuple[str, str, bool]
            A tuple containing the net name, layer name, and a boolean indicating whether to include
            child layers.
        enabled : bool
            Whether the mesh operation is enabled.
        refine_inside : bool
            Whether to refine the mesh inside the specified region.
        mesh_region : str
            The name of the mesh region.
        solve_inside : bool
            Whether to solve inside the specified region.
        max_length : str
            The maximum length for the mesh operation.
        restrict_max_length : bool
            Whether to restrict the maximum length.
        max_elements : str
            The maximum number of elements for the mesh operation.
        restrict_max_elements : bool
            Whether to restrict the maximum number of elements.
        Returns
        -------
        LengthMeshOperation : LengthMeshOperation
            The Length Mesh Operation object.
        """
        core_op = GrpcLengthMeshOperation(
            name=name,
            net_layer_info=net_layer_info,
            enabled=enabled,
            refine_inside=refine_inside,
            mesh_region=mesh_region,
            solve_inside=solve_inside,
            max_length=max_length,
            restrict_max_length=restrict_max_length,
            max_elements=max_elements,
            restrict_max_elements=restrict_max_elements,
        )
        return cls(core=core_op)

    @property
    def name(self) -> str:
        """Get the name of the mesh operation.

        Returns
        -------
        str
            Name of the mesh operation.
        """
        return self.core.name

    @name.setter
    def name(self, value: str):
        self.core.name = value

    @property
    def enabled(self) -> bool:
        """Get the enabled status of the mesh operation.

        Returns
        -------
        bool
            True if the mesh operation is enabled, False otherwise.
        """
        return self.core.enabled

    @enabled.setter
    def enabled(self, value: bool):
        self.core.enabled = value

    @property
    def mesh_region(self) -> str:
        """Get the mesh region name.

        Returns
        -------
        str
            Name of the mesh region.
        """
        return self.core.mesh_region

    @mesh_region.setter
    def mesh_region(self, value: str):
        self.core.mesh_region = value

    @property
    def net_layer_info(self) -> list[tuple[str, str, bool]]:
        """Get the net layer information list.

        Returns
        -------
        list[tuple(str, str, bool)]
            List of net layer information for the mesh operation.
        """
        return list(self.core.net_layer_info)

    @net_layer_info.setter
    def net_layer_info(self, value: list[tuple[str, str, bool]]):
        self.core.net_layer_info.clear()
        for info in value:
            self.core.net_layer_info.append(info)

    @property
    def refine_inside(self) -> bool:
        """Get the refine inside status of the mesh operation.

        Returns
        -------
        bool
            True if refining inside is enabled, False otherwise.
        """
        return self.core.refine_inside

    @refine_inside.setter
    def refine_inside(self, value: bool):
        self.core.refine_inside = value

    @property
    def solve_inside(self) -> bool:
        """Get the solve inside status of the mesh operation.

        Returns
        -------
        bool
            True if solving inside is enabled, False otherwise.
        """
        return self.core.solve_inside

    @solve_inside.setter
    def solve_inside(self, value: bool):
        self.core.solve_inside = value

    @property
    def max_length(self) -> float:
        """Get the length for the length mesh operation.

        Returns
        -------
        float
            The length value.

        """
        return self.core.max_length

    @max_length.setter
    def max_length(self, value: float):
        """Set the length for the length mesh operation.

        Parameters
        ----------
        value : float
            The length value to set.

        """
        self.core.max_length = value

    @property
    def restrict_max_length(self) -> bool:
        """Get the restrict max length status of the mesh operation.

        Returns
        -------
        bool
            True if restricting max length is enabled, False otherwise.
        """
        return self.core.restrict_max_length

    @restrict_max_length.setter
    def restrict_max_length(self, value: bool):
        self.core.restrict_max_length = value

    @property
    def max_elements(self) -> str:
        """Get the maximum number of elements for the length mesh operation.

        Returns
        -------
        str
            The maximum number of elements.

        """
        return self.core.max_elements

    @max_elements.setter
    def max_elements(self, value: str):
        self.core.max_elements = value

    @property
    def restrict_max_elements(self) -> bool:
        """Get the restrict max elements status of the mesh operation.

        Returns
        -------
        bool
            True if restricting max elements is enabled, False otherwise.
        """
        return self.core.restrict_max_elements

    @restrict_max_elements.setter
    def restrict_max_elements(self, value: bool):
        self.core.restrict_max_elements = value
