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

"""Via layer wrapper for the gRPC backend."""

from __future__ import absolute_import, annotations

from ansys.edb.core.layer.via_layer import ViaLayer as CoreViaLayer


class ViaLayer:
    """Represents a via layer in an overlapping stackup.

    A via layer defines the vertical extent of a via between two signal (reference)
    layers in an overlapping stackup. It is identified by its name, the lower and
    upper reference layer names, and the conductor material.

    Parameters
    ----------
    pedb : :class:`pyedb.Edb`
        EDB object.
    core : :class:`ansys.edb.core.layer.via_layer.ViaLayer`
        Core via layer object.
    """

    def __init__(self, pedb, core: CoreViaLayer):
        self._pedb = pedb
        self.core = core

    @classmethod
    def create(cls, pedb, name: str, lower_layer: str, upper_layer: str, material: str = "copper") -> "ViaLayer":
        """Create a via layer.

        Parameters
        ----------
        pedb : :class:`pyedb.Edb`
            EDB object.
        name : str
            Name of the via layer.
        lower_layer : str
            Name of the lower reference stackup layer.
        upper_layer : str
            Name of the upper reference stackup layer.
        material : str, optional
            Conductor material of the via layer. The default is ``"copper"``.

        Returns
        -------
        :class:`ViaLayer`
            Via layer object created.

        Examples
        --------
        >>> from pyedb.grpc.database.layers.via_layer import ViaLayer
        >>> via = ViaLayer.create(pedb, "Via1_2", "Layer1", "Layer2", material="copper")
        """
        core = CoreViaLayer.create(name=name, lr_layer=lower_layer, ur_layer=upper_layer, material=material)
        return cls(pedb, core)

    @property
    def name(self) -> str:
        """Via layer name.

        Returns
        -------
        str
            Name of the via layer.

        Examples
        --------
        >>> via = edb.stackup.via_layers["Via1_2"]
        >>> via.name
        'Via1_2'
        """
        return self.core.name

    @name.setter
    def name(self, value: str):
        """Set the via layer name.

        Parameters
        ----------
        value : str
            New name for the via layer.
        """
        self.core.name = value

    @property
    def lower_ref_layer_name(self) -> str:
        """Name of the lower reference layer.

        Returns
        -------
        str
            Name of the lower reference stackup layer.

        Examples
        --------
        >>> via = edb.stackup.via_layers["Via1_2"]
        >>> via.lower_ref_layer_name
        'Layer1'
        """
        return self.core.get_ref_layer_name(upper_ref=False)

    @lower_ref_layer_name.setter
    def lower_ref_layer_name(self, layer_name: str):
        """Set the lower reference layer by name.

        Parameters
        ----------
        layer_name : str
            Name of the stackup layer to use as the lower reference.
        """
        layers = self._pedb.stackup.layers
        if layer_name not in layers:
            raise ValueError(f"Layer '{layer_name}' not found in stackup.")
        self.core.set_ref_layer(layers[layer_name].core, upper_ref=False)

    @property
    def upper_ref_layer_name(self) -> str:
        """Name of the upper reference layer.

        Returns
        -------
        str
            Name of the upper reference stackup layer.

        Examples
        --------
        >>> via = edb.stackup.via_layers["Via1_2"]
        >>> via.upper_ref_layer_name
        'Layer2'
        """
        return self.core.get_ref_layer_name(upper_ref=True)

    @upper_ref_layer_name.setter
    def upper_ref_layer_name(self, layer_name: str):
        """Set the upper reference layer by name.

        Parameters
        ----------
        layer_name : str
            Name of the stackup layer to use as the upper reference.
        """
        layers = self._pedb.stackup.layers
        if layer_name not in layers:
            raise ValueError(f"Layer '{layer_name}' not found in stackup.")
        self.core.set_ref_layer(layers[layer_name].core, upper_ref=True)

    @property
    def material(self) -> str:
        """Conductor material of the via layer.

        Returns
        -------
        str
            Material name.

        Examples
        --------
        >>> via = edb.stackup.via_layers["Via1_2"]
        >>> via.material
        'copper'
        """
        return self.core.get_material()

    @material.setter
    def material(self, value: str):
        self.core.set_material(value)

    @property
    def is_tsv(self) -> bool:
        """Flag indicating whether the via layer is a through-silicon via (TSV).

        Returns
        -------
        bool
            ``True`` if the layer is a TSV layer.

        Examples
        --------
        >>> via = edb.stackup.via_layers["Via1_2"]
        >>> via.is_tsv
        False
        """
        return self.core.is_tsv

    @is_tsv.setter
    def is_tsv(self, value: bool):
        self.core.is_tsv = value

    def __repr__(self) -> str:
        return (
            f"ViaLayer(name={self.name!r}, lower={self.lower_ref_layer_name!r}, "
            f"upper={self.upper_ref_layer_name!r}, material={self.material!r})"
        )
