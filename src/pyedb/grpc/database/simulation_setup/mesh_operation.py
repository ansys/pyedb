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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ansys.edb.core.simulation_setup.mesh_operation import (
        MeshOperation as GrpcMeshOperation,
    )


class MeshOperation:
    """Mesh operation class.

    Attributes:
    name : str, default: “”
        Name of the mesh operation.

    net_layer_infolist[tuple(str, str, bool)], default: None
        list of tuple of (str, str, bool): List of net layer information for the mesh operation.

    enabled : bool, default: True
        Flag indicating if the mesh operation is enabled.

    refine_inside : bool, default: False
        Flag indicating if refining inside is enabled.

    mesh_region : str, default: “”
        Name of the mesh region.

    solve_inside : bool, default: False
        Flag indicating if solve inside is enabled.
    """

    def __init__(
        self,
        core: "GrpcMeshOperation" = None,
        name="",
        net_layer_info=None,
        enabled=True,
        refine_inside=False,
        mesh_region="",
        solve_inside=False,
    ):
        if core:
            self.core = core
        else:
            self.core = GrpcMeshOperation()
            self.core.name = name
            self.core.enabled = enabled
            self.core.refine_inside = refine_inside
            self.core.mesh_region = mesh_region
            self.core.solve_inside = solve_inside
            if net_layer_info:
                for info in net_layer_info:
                    self.core.net_layer_info.append(info)

    @classmethod
    def create(
        cls,
        name: str,
        net_layer_info: list[tuple[str, str, bool]],
        enabled: bool,
        refine_inside: bool,
        mesh_region: str,
        solve_inside: bool,
    ):
        """Create a mesh operation.

        Parameters
        ----------
        name : str
            Name of the mesh operation.
        net_layer_info : list[tuple(str, str, bool)]
            List of net layer information for the mesh operation.
        enabled : bool
            Flag indicating if the mesh operation is enabled.
        refine_inside : bool
            Flag indicating if refining inside is enabled.
        mesh_region : str
            Name of the mesh region.
        solve_inside : bool
            Flag indicating if solve inside is enabled.

        Returns
        -------
        MeshOperation
            The created MeshOperation object.
        """
        core = GrpcMeshOperation()
        core.name = name
        core.enabled = enabled
        core.refine_inside = refine_inside
        core.mesh_region = mesh_region
        core.solve_inside = solve_inside
        for info in net_layer_info:
            core.net_layer_info.append(info)
        return cls(core)

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
