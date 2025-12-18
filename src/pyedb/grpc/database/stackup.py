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

"""
This module contains the `EdbStackup` class.

"""

from __future__ import absolute_import, annotations

from collections import OrderedDict
import json
import logging
import math
from typing import Any, Dict, List, Optional, Tuple, Union
import warnings

from ansys.edb.core.definition.die_property import DieOrientation as GrpcDieOrientation
from ansys.edb.core.definition.solder_ball_property import (
    SolderballPlacement as GrpcSolderballPlacement,
)
from ansys.edb.core.geometry.point3d_data import Point3DData as GrpcPoint3DData
from ansys.edb.core.hierarchy.cell_instance import CellInstance as GrpcCellInstance
from ansys.edb.core.hierarchy.component_group import ComponentType as GrpcComponentType
from ansys.edb.core.layer.layer import LayerType as GrpcLayerType, TopBottomAssociation as GrpcTopBottomAssociation
from ansys.edb.core.layer.layer_collection import (
    LayerCollection as GrpcLayerCollection,
    LayerCollectionMode as GrpcLayerCollectionMode,
    LayerTypeSet as GrpcLayerTypeSet,
)
from ansys.edb.core.layer.stackup_layer import StackupLayer as GrpcStackupLayer
from ansys.edb.core.layout.mcad_model import McadModel as GrpcMcadModel
from defusedxml.ElementTree import parse as defused_parse
import matplotlib.colors as colors
import numpy as np
import pandas as pd

from pyedb.generic.general_methods import ET, generate_unique_name
from pyedb.grpc.database.layers.layer import Layer
from pyedb.grpc.database.layers.stackup_layer import StackupLayer
from pyedb.grpc.database.utility.value import Value
from pyedb.misc.aedtlib_personalib_install import write_pretty_xml
from pyedb.misc.decorators import deprecate_argument_name

logger = logging.getLogger(__name__)


class LayerCollection:
    """Manages layer collections in an EDB database.

    Parameters
    ----------
    pedb : :class:`pyedb.Edb`
        EDB object.
    edb_object : :class:`ansys.edb.core.layer.LayerCollection`
        EDB layer collection object.
    """

    def __init__(self, pedb=None, edb_object=None):
        self.core = edb_object
        self._pedb = pedb

    @classmethod
    def create(cls, mode: str = "laminate") -> LayerCollection:
        """Create layer collection.

        Parameters
        ----------
        mode : str, optional
            layer mode. Valid values, `"laminate"`, `"overlapping"`. Default value is `"laminate"`

        Returns
        -------
        LayerCollection
        """
        layer_collection = GrpcLayerCollection.create(mode=GrpcLayerCollectionMode.LAMINATE)
        return cls(None, layer_collection)

    def update_layout(self):
        """Update the layout with the current layer collection.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> edb.stackup.update_layout()
        """
        self._pedb.layout.layer_collection = self

    def add_layer_top(self, name: str, layer_type: str = "signal", **kwargs) -> Union["Layer", None]:
        """Add a layer on top of the stackup.

        Parameters
        ----------
        name : str
            Name of the layer.
        layer_type : str, optional
            Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
        **kwargs : dict, optional
            Additional keyword arguments. Possible keys are:
            - ``thickness`` : float, layer thickness.
            - ``material`` : str, layer material.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
            Layer object created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> top_layer = edb.stackup.add_layer_top(
        ...     "NewTopLayer", layer_type="signal", thickness="0.1mm", material="copper"
        ... )
        """
        thickness = Value(0.0)
        if "thickness" in kwargs:
            thickness = Value(kwargs["thickness"])
        elevation = Value(0.0)
        layer = StackupLayer.create(
            layout=self._pedb.layout,
            name=name,
            layer_type=layer_type,
            thickness=thickness,
            material="copper",
            elevation=elevation,
        )
        return self.core.add_layer_top(layer.core)

    def add_layer_bottom(self, name: str, layer_type: str = "signal", **kwargs) -> Union["Layer", None]:
        """Add a layer at the bottom of the stackup.

        Parameters
        ----------
        name : str
            Name of the layer.
        layer_type : str, optional
            Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
        **kwargs : dict, optional
            Additional keyword arguments. Possible keys are:
            - ``thickness`` : float, layer thickness.
            - ``material`` : str, layer material.
            - ``fill_material`` : str, fill material.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
            Layer object created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> bot_layer = edb.stackup.add_layer_bottom(
        ...     "NewBottomLayer", layer_type="signal", thickness="0.1mm", material="copper"
        ... )
        """
        thickness = Value(0.0)
        if "thickness" in kwargs:
            thickness = Value(kwargs["thickness"])
        elevation = Value(0.0)
        if "type" in kwargs:
            _layer_type = kwargs["type"]
        else:
            _layer_type = layer_type
        if "material" in kwargs:
            _material = kwargs["material"]
        else:
            _material = "copper"
        layer = StackupLayer.create(
            layout=self._pedb.layout,
            name=name,
            layer_type=_layer_type,
            thickness=thickness,
            material=_material,
            elevation=elevation,
        )
        if "fill_material" in kwargs:
            layer.core.set_fill_material(kwargs["fill_material"])
        return self.core.add_layer_bottom(layer.core)

    def add_layer_below(
        self, name: str, base_layer_name: str, layer_type: str = "signal", **kwargs
    ) -> Union["Layer", None]:
        """Add a layer below a specified layer.

        Parameters
        ----------
        name : str
            Name of the layer.
        base_layer_name : str
            Name of the base layer.
        layer_type : str, optional
            Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
        **kwargs : dict, optional
            Additional keyword arguments. Possible keys are:
            - ``thickness`` : float, layer thickness.
            - ``material`` : str, layer material.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
            Layer object created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> new_layer = edb.stackup.add_layer_below("NewLayer", "TopLayer", layer_type="dielectric", thickness="0.05mm")
        """
        thickness = Value(0.0)
        if "thickness" in kwargs:
            thickness = Value(kwargs["thickness"])
        elevation = Value(0.0)
        if "type" in kwargs:
            layer_type = kwargs["type"]
        if "material" in kwargs:
            material = kwargs["material"]
        else:
            material = "copper"
        layer = StackupLayer.create(
            layout=self._pedb.layout,
            name=name,
            layer_type=layer_type,
            thickness=thickness,
            material=material,
            elevation=elevation,
        )
        return self.core.add_layer_below(layer.core, base_layer_name)

    def add_layer_above(
        self, name: str, base_layer_name: str, layer_type: str = "signal", **kwargs
    ) -> Union["Layer", None]:
        """Add a layer above a specified layer.

        Parameters
        ----------
        name : str
            Name of the layer.
        base_layer_name : str
            Name of the base layer.
        layer_type : str, optional
            Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
        **kwargs : dict, optional
            Additional keyword arguments. Possible keys are:
            - ``thickness`` : float, layer thickness.
            - ``material`` : str, layer material.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
            Layer object created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> new_layer = edb.stackup.add_layer_above("NewLayer", "BottomLayer", layer_type="signal", thickness="0.05mm")
        """
        thickness = Value(0.0)
        if "thickness" in kwargs:
            thickness = Value(kwargs["thickness"])
        elevation = Value(0.0)
        layer = StackupLayer.create(
            layout=self._pedb.layout,
            name=name,
            layer_type=layer_type,
            thickness=thickness,
            material="copper",
            elevation=elevation,
        )
        return self.core.add_layer_above(layer.core, base_layer_name)

    def add_document_layer(self, name: str, layer_type: str = "user", **kwargs: Any) -> Optional["Layer"]:
        """Add a document layer.

        Parameters
        ----------
        name : str
            Name of the layer.
        layer_type : str, optional
            Type of the layer. The default is ``"user"``. Options are ``"user"`` and ``"outline"``.
        **kwargs : dict, optional
            Additional keyword arguments.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.layer.Layer`
            Layer object created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> outline_layer = edb.stackup.add_document_layer("Outline", layer_type="outline")
        """
        added_layer = self.add_layer_top(name)
        added_layer.type = GrpcLayerType.USER_LAYER
        return added_layer

    @property
    def stackup_layers(self):
        """Retrieve the dictionary of signal and dielectric layers.

        .. deprecated:: 0.6.61
            Use :func:`layers` instead.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
            Dictionary of stackup layers.
        """
        warnings.warn("Use new property :func:`layers` instead.", DeprecationWarning)
        return self.layers

    @property
    def non_stackup_layers(self) -> Dict[str, Layer]:
        """Retrieve the dictionary of non-stackup layers.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.layer.Layer`]
            Dictionary of non-stackup layers.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> non_stackup = edb.stackup.non_stackup_layers
        """
        return {
            layer.name: Layer(self._pedb, layer) for layer in self.get_layers(GrpcLayerTypeSet.NON_STACKUP_LAYER_SET)
        }

    @property
    def all_layers(self) -> Dict[str, Layer]:
        """Retrieve all layers.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.layer.Layer`]
            Dictionary of all layers.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> all_layers = edb.stackup.all_layers
        """
        return {layer.name: Layer(self._pedb, layer) for layer in self.get_layers(GrpcLayerTypeSet.ALL_LAYER_SET)}

    @property
    def signal_layers(self) -> Dict[str, StackupLayer]:
        """Retrieve the dictionary of signal layers.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
            Dictionary of signal layers.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> signal_layers = edb.stackup.signal_layers
        """
        return {
            layer.name: StackupLayer(self._pedb, layer)
            for layer in self.core.get_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)
        }

    @property
    def dielectric_layers(self) -> Dict[str, StackupLayer]:
        """Retrieve the dictionary of dielectric layers.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
            Dictionary of dielectric layers.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> dielectric_layers = edb.stackup.dielectric_layers
        """
        return {
            layer.name: StackupLayer(self._pedb, layer)
            for layer in self.core.get_layers(GrpcLayerTypeSet.DIELECTRIC_LAYER_SET)
        }

    @property
    def layers_by_id(self) -> List[List[Union[int, str]]]:
        """Retrieve the list of layers with their IDs.

        Returns
        -------
        list[list[int, str]]
            List of layers with their IDs and names.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> layers_by_id = edb.stackup.layers_by_id
        """
        return [[layer.id, layer.name] for layer in self.core.get_layers(GrpcLayerTypeSet.ALL_LAYER_SET)]

    @property
    def layers(self) -> Dict[str, StackupLayer]:
        """Retrieve the dictionary of stackup layers (signal and dielectric).

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
            Dictionary of stackup layers.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> layers = edb.stackup.layers
        """
        return {
            obj.name: StackupLayer(self._pedb, obj) for obj in self.core.get_layers(GrpcLayerTypeSet.STACKUP_LAYER_SET)
        }

    def find_layer_by_name(self, name: str):
        """Find a layer by its name.

        .. deprecated:: 0.29.0
            Use :func:`find_by_name` instead.

        Parameters
        ----------
        name : str
            Name of the layer.

        Returns
        -------
        :class:`ansys.edb.core.layer.Layer`
            Layer object found.

        Raises
        ------
        ValueError
            If no layer with the given name is found.
        """
        warnings.warn(
            "`find_layer_by_name` is deprecated and is now located here "
            "`pyedb.grpc.core.excitations.find_by_name` instead.",
            DeprecationWarning,
        )
        layer = self.core.find_by_name(name)
        if layer.is_null:
            raise ValueError(f"Layer with name '{name}' was not found.")
        return layer


class Stackup:
    """Manages EDB methods for stackup operations.

    Parameters
    ----------
    pedb : :class:`pyedb.Edb`
        EDB object.
    edb_object : :class:`ansys.edb.core.layer.LayerCollection`, optional
        EDB layer collection object. The default is ``None``.
    """

    def __init__(self, pedb, edb_object=None):
        self.core = edb_object
        self._pedb = pedb
        self.layer_collection = LayerCollection(pedb, edb_object)

    def __getitem__(self, item):
        if item in self.non_stackup_layers:
            return Layer(edb_object=self.core.find_by_name(item))
        elif item in self.layers:
            return StackupLayer(self._pedb, edb_object=self.core.find_by_name(item))
        else:
            return None

    @property
    def _logger(self):
        return self._pedb.logger

    @property
    def signal_layers(self):
        """Retrieve the dictionary of signal layers.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
            Dictionary of signal layers.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> signal_layers = edb.stackup.signal_layers
        """
        return {
            layer.name: StackupLayer(self._pedb, layer)
            for layer in self.core.get_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)
        }

    @property
    def dielectric_layers(self):
        """Retrieve the dictionary of dielectric layers.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
            Dictionary of dielectric layers."""
        return {
            layer.name: StackupLayer(self._pedb, layer)
            for layer in self.core.get_layers(GrpcLayerTypeSet.DIELECTRIC_LAYER_SET)
        }

    @property
    def layers(self):
        """Retrieve the dictionary of stackup layers (signal and dielectric).

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
            Dictionary of stackup layers.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> layers = edb.stackup.layers
        """
        return {
            obj.name: StackupLayer(self._pedb, obj) for obj in self.core.get_layers(GrpcLayerTypeSet.STACKUP_LAYER_SET)
        }

    @property
    def non_stackup_layers(self):
        """Retrieve the dictionary of non-stackup layers.

        Returns
        -------
        dict[str, :class:`pyedb.grpc.database.layers.layer.Layer`]
            Dictionary of non-stackup layers.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> non_stackup = edb.stackup.non_stackup_layers
        """
        return {
            layer.name: Layer(layer)
            for layer in self._pedb.stackup.core.get_layers(GrpcLayerTypeSet.NON_STACKUP_LAYER_SET)
        }

    @property
    def thickness(self) -> float:
        """Retrieve the stackup thickness.

        Returns
        -------
        float
            Stackup thickness.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> thickness = edb.stackup.thickness
        """
        return self.get_layout_thickness()

    @property
    def num_layers(self) -> int:
        """Retrieve the number of layers in the stackup.

        Returns
        -------
        int
            Number of layers.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> num_layers = edb.stackup.num_layers
        """
        return len(self.layers)

    def create_symmetric_stackup(
        self,
        layer_count: int,
        inner_layer_thickness: str = "17um",
        outer_layer_thickness: str = "50um",
        dielectric_thickness: str = "100um",
        dielectric_material: str = "FR4_epoxy",
        soldermask: bool = True,
        soldermask_thickness: str = "20um",
    ) -> bool:
        """Create a symmetric stackup.

        Parameters
        ----------
        layer_count : int
            Number of layers. Must be even.
        inner_layer_thickness : str, float, optional
            Thickness of inner conductor layer.
        outer_layer_thickness : str, float, optional
            Thickness of outer conductor layer.
        dielectric_thickness : str, float, optional
            Thickness of dielectric layer.
        dielectric_material : str, optional
            Material of dielectric layer.
        soldermask : bool, optional
            Whether to create soldermask layers. The default is ``True``.
        soldermask_thickness : str, optional
            Thickness of soldermask layer.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> edb.stackup.create_symmetric_stackup(layer_count=4)
        """
        if not layer_count % 2 == 0:
            return False

        self.add_layer(
            "BOT",
            None,
            material="copper",
            thickness=outer_layer_thickness,
            fillMaterial=dielectric_material,
        )
        self.add_layer(
            "D" + str(int(layer_count / 2)),
            None,
            material="FR4_epoxy",
            thickness=dielectric_thickness,
            layer_type="dielectric",
            fillMaterial=dielectric_material,
        )
        self.add_layer(
            "TOP",
            None,
            material="copper",
            thickness=outer_layer_thickness,
            fillMaterial=dielectric_material,
        )
        if soldermask:
            self.add_layer(
                "SMT",
                None,
                material="SolderMask",
                thickness=soldermask_thickness,
                layer_type="dielectric",
                fillMaterial=dielectric_material,
            )
            self.add_layer(
                "SMB",
                None,
                material="SolderMask",
                thickness=soldermask_thickness,
                layer_type="dielectric",
                fillMaterial=dielectric_material,
                method="add_on_bottom",
            )
            self.layers["TOP"].dielectric_fill = "SolderMask"
            self.layers["BOT"].dielectric_fill = "SolderMask"

        for layer_num in np.arange(int(layer_count / 2), 1, -1):
            # Generate upper half
            self.add_layer(
                "L" + str(layer_num),
                "TOP",
                material="copper",
                thickness=inner_layer_thickness,
                fillMaterial=dielectric_material,
                method="insert_below",
            )
            self.add_layer(
                "D" + str(layer_num - 1),
                "TOP",
                material=dielectric_material,
                thickness=dielectric_thickness,
                layer_type="dielectric",
                fillMaterial=dielectric_material,
                method="insert_below",
            )

            # Generate lower half
            self.add_layer(
                "L" + str(layer_count - layer_num + 1),
                "BOT",
                material="copper",
                thickness=inner_layer_thickness,
                fillMaterial=dielectric_material,
                method="insert_above",
            )
            self.add_layer(
                "D" + str(layer_count - layer_num + 1),
                "BOT",
                material=dielectric_material,
                thickness=dielectric_thickness,
                layer_type="dielectric",
                fillMaterial=dielectric_material,
                method="insert_above",
            )
        return True

    @property
    def mode(self) -> str:
        """Stackup mode.

        Returns
        -------
        str
            Type of the stackup mode. Options are:
            - ``"laminate"``
            - ``"overlapping"``
            - ``"multizone"``

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> mode = edb.stackup.mode
        """
        return self.core.mode.name.lower()

    @mode.setter
    def mode(self, value):
        if value == 0 or value == GrpcLayerCollectionMode.LAMINATE or value == "laminate" or value == "Laminate":
            self.core.mode = GrpcLayerCollectionMode.LAMINATE
        elif (
            value == 1
            or value == GrpcLayerCollectionMode.OVERLAPPING
            or value == "overlapping"
            or value == "Overlapping"
        ):
            self.core.mode = GrpcLayerCollectionMode.OVERLAPPING
        elif value == 2 or value == GrpcLayerCollectionMode.MULTIZONE or value == "multizone" or value == "MultiZone":
            self.core.mode = GrpcLayerCollectionMode.MULTIZONE
        # self.core.update_layout()
        # TODO check if still needed with gRPC

    def _set_layout_stackup(
        self, layer_clone: GrpcStackupLayer, operation: str, base_layer: Optional[str] = None, method: int = 1
    ) -> bool:
        """Internal method. Apply stackup change into EDB.

        Parameters
        ----------
        layer_clone : :class:`ansys.edb.core.layer.StackupLayer`
            Layer object to apply.
        operation : str
            Operation to perform. Options are ``"change_attribute"``, ``"change_name"``, ``"change_position"``,
            ``"insert_below"``, ``"insert_above"``, ``"add_on_top"``, ``"add_on_bottom"``, ``"non_stackup"``,
            and ``"add_at_elevation"``.
        base_layer : str, optional
            Name of the base layer. The default value is ``None``.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        lc = self.core
        if operation in ["change_position", "change_attribute", "change_name"]:
            _lc = GrpcLayerCollection.create()

            layers = [i for i in lc.get_layers(GrpcLayerTypeSet.STACKUP_LAYER_SET)]
            non_stackup = [i for i in lc.get_layers(GrpcLayerTypeSet.NON_STACKUP_LAYER_SET)]
            _lc.mode = lc.mode
            if lc.mode.name.lower() == "overlapping":
                for layer in layers:
                    if layer.name == layer_clone.name or layer.name == base_layer:
                        _lc.add_stackup_layer_at_elevation(layer_clone.core)
                    else:
                        _lc.add_stackup_layer_at_elevation(layer.core)
            else:
                for layer in layers:
                    if layer.name == layer_clone.name or layer.name == base_layer:
                        _lc.add_layer_bottom(layer_clone.core)
                    else:
                        _lc.add_layer_bottom(layer.core)
            for layer in non_stackup:
                _lc.add_layer_bottom(layer.core)
        elif operation == "insert_below":
            lc.add_layer_below(layer_clone.core, base_layer)
        elif operation == "insert_above":
            lc.add_layer_above(layer_clone.core, base_layer)
        elif operation == "add_on_top":
            lc.add_layer_top(layer_clone.core)
        elif operation == "add_on_bottom":
            lc.add_layer_bottom(layer_clone.core)
        elif operation == "add_at_elevation":
            lc.add_stackup_layer_at_elevation(layer_clone.core)
        elif operation == "non_stackup":
            lc.add_layer_bottom(layer_clone.core)
        self.core = lc
        return True

    def _create_stackup_layer(
        self, layer_name: str, thickness: Union[str, float], layer_type: str = "signal", material: str = "copper"
    ) -> StackupLayer:
        if layer_type == "signal" and not material:
            material = "copper"
        elif layer_type == "dielectric":
            material = "FR4_epoxy"
        thickness = Value(thickness, self._pedb.active_db)
        layer = StackupLayer.create(
            layout=self._pedb.active_layout,
            name=layer_name,
            layer_type=layer_type,
            thickness=thickness,
            elevation=Value(0),
            material=material,
        )
        return layer

    def _create_nonstackup_layer(self, layer_name: str, layer_type: str):
        layer = Layer.create(layer_name, layer_type)
        self.core.add_layer_top(layer.core)
        return layer

    def add_outline_layer(self, name: str = "Outline") -> bool:
        """Add an outline layer named "Outline" if it is not present.

        Returns
        -------
        bool
            ``True`` when successful.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> edb.stackup.add_outline_layer()
        """
        return self.add_layer(layer_name="Outline", layer_type="outline")

    @deprecate_argument_name({"fillMaterial": "filling_material"})
    def add_layer(
        self,
        layer_name: str,
        base_layer: Optional[str] = None,
        method: str = "add_on_top",
        layer_type: str = "signal",
        material: str = "copper",
        filling_material: str = "FR4_epoxy",
        thickness: Union[str, float] = "35um",
        etch_factor: Optional[float] = None,
        is_negative: bool = False,
        enable_roughness: bool = False,
        elevation: Optional[float] = None,
    ) -> bool:
        """Insert a layer into stackup.

        Parameters
        ----------
        layer_name : str
            Name of the layer.
        base_layer : str, optional
            Name of the base layer.
        method : str, optional
            Where to insert the new layer. The default is ``"add_on_top"``. Options are:
            - ``"add_on_top"``
            - ``"add_on_bottom"``
            - ``"insert_above"``
            - ``"insert_below"``
            - ``"add_at_elevation"``
        layer_type : str, optional
            Type of layer. The default is ``"signal"``. Options are:
            - ``"signal"``
            - ``"dielectric"``
            - ``"conducting"``
            - ``"air_lines"``
            - ``"error"``
            - ``"symbol"``
            - ``"measure"``
            - ``"assembly"``
            - ``"silkscreen"``
            - ``"solder_mask"``
            - ``"solder_paste"``
            - ``"glue"``
            - ``"wirebond"``
            - ``"hfss_region"``
            - ``"user"``
        material : str, optional
            Material of the layer.
        filling_material : str, optional
            Fill material of the layer.
        thickness : str, float, optional
            Thickness of the layer.
        etch_factor : int, float, optional
            Etch factor of the layer.
        is_negative : bool, optional
            Whether the layer is negative.
        enable_roughness : bool, optional
            Whether roughness is enabled.
        elevation : float, optional
            Elevation of new layer. Only valid for Overlapping Stackup.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
            Layer object created.
        """
        if layer_name in self.layers:
            logger.error("layer {} exists.".format(layer_name))
            return False
        if not material:
            material = "copper" if layer_type == "signal" else "FR4_epoxy"
        if not filling_material:
            filling_material = "FR4_epoxy"

        materials = self._pedb.materials
        if material not in materials:
            material_properties = self._pedb.materials.read_syslib_material(material)
            if material_properties:
                logger.info(f"Material {material} found in syslib. Adding it to aedb project.")
                materials.add_material(material, **material_properties)
            else:
                logger.warning(f"Material {material} not found. Check the library and retry.")

        if layer_type != "dielectric" and filling_material not in materials:
            material_properties = self._pedb.materials.read_syslib_material(filling_material)
            if material_properties:
                logger.info(f"Material {filling_material} found in syslib. Adding it to aedb project.")
                materials.add_material(filling_material, **material_properties)
            else:
                logger.warning(f"Material {filling_material} not found. Check the library and retry.")

        if layer_type in ["signal", "dielectric"]:
            new_layer = self._create_stackup_layer(layer_name, thickness, layer_type)
            new_layer.core.set_material(material)
            if layer_type != "dielectric":
                new_layer.core.set_fill_material(filling_material)
            new_layer.negative = is_negative
            l1 = len(self.layers)
            if method == "add_at_elevation" and elevation:
                new_layer.lower_elevation = Value(elevation)
            if etch_factor:
                new_layer.etch_factor = etch_factor
            if enable_roughness:
                new_layer.roughness_enabled = True
            self._set_layout_stackup(new_layer, method, base_layer)
            if len(self.layers) == l1:
                self._set_layout_stackup(new_layer, method, base_layer, method=2)
            if layer_name in self.layers:
                return True
        else:
            self._create_nonstackup_layer(layer_name, layer_type)
            if layer_name in self.non_stackup_layers:
                return True
            return False
        return False

    def add_layer_top(self, name: str, layer_type: str = "signal", **kwargs) -> Union["Layer", None]:
        """Add a layer on top of the stackup.

        Parameters
        ----------
        name : str
            Name of the layer.
        layer_type : str, optional
            Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
        **kwargs : dict, optional
            Additional keyword arguments. Possible keys are:
            - ``thickness`` : float, layer thickness.
            - ``material`` : str, layer material.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
            Layer object created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> top_layer = edb.stackup.add_layer_top(
        ...     "NewTopLayer", layer_type="signal", thickness="0.1mm", material="copper"
        ... )
        """
        return self.layer_collection.add_layer_top(name, layer_type, **kwargs)

    def add_layer_bottom(self, name: str, layer_type: str = "signal", **kwargs) -> Union["Layer", None]:
        """Add a layer at the bottom of the stackup.

        Parameters
        ----------
        name : str
            Name of the layer.
        layer_type : str, optional
            Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
        **kwargs : dict, optional
            Additional keyword arguments. Possible keys are:
            - ``thickness`` : float, layer thickness.
            - ``material`` : str, layer material.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
            Layer object created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> bot_layer = edb.stackup.add_layer_bottom(
        ...     "NewBottomLayer", layer_type="signal", thickness="0.1mm", material="copper"
        ... )
        """
        return self.layer_collection.add_layer_bottom(name, layer_type, **kwargs)

    def add_layer_below(
        self, name: str, base_layer_name: str, layer_type: str = "signal", **kwargs
    ) -> Union["Layer", None]:
        """Add a layer below a specified layer.

        Parameters
        ----------
        name : str
            Name of the layer.
        base_layer_name : str
            Name of the base layer.
        layer_type : str, optional
            Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
        **kwargs : dict, optional
            Additional keyword arguments. Possible keys are:
            - ``thickness`` : float, layer thickness.
            - ``material`` : str, layer material.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
            Layer object created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> new_layer = edb.stackup.add_layer_below("NewLayer", "TopLayer", layer_type="dielectric", thickness="0.05mm")
        """
        return self.layer_collection.add_layer_below(name, base_layer_name, layer_type, **kwargs)

    def add_layer_above(
        self, name: str, base_layer_name: str, layer_type: str = "signal", **kwargs
    ) -> Union["Layer", None]:
        """Add a layer above a specified layer.

        Parameters
        ----------
        name : str
            Name of the layer.
        base_layer_name : str
            Name of the base layer.
        layer_type : str, optional
            Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
        **kwargs : dict, optional
            Additional keyword arguments. Possible keys are:
            - ``thickness`` : float, layer thickness.
            - ``material`` : str, layer material.

        Returns
        -------
        :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
            Layer object created.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> new_layer = edb.stackup.add_layer_above("NewLayer", "BottomLayer", layer_type="signal", thickness="0.05mm")
        """
        return self.layer_collection.add_layer_above(name, base_layer_name, layer_type, **kwargs)

    @property
    def layers_by_id(self) -> List[List[Union[int, str]]]:
        """Retrieve the list of layers with their IDs.

        Returns
        -------
        list[list[int, str]]
            List of layers with their IDs and names.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> layers_by_id = edb.stackup.layers_by_id
        """
        return self.layer_collection.layers_by_id

    def remove_layer(self, name: str) -> bool:
        """Remove a layer from stackup.

        Parameters
        ----------
        name : str
            Name of the layer to remove.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        new_layer_collection = LayerCollection.create()
        for layer_name, lyr in self.layers.items():
            if not (layer_name == name):
                new_layer_collection.core.add_layer_bottom(lyr.core)

        self._pedb.layout.core.layer_collection = new_layer_collection.core
        return True

    def export(self, fpath: str, file_format: str = "xml", include_material_with_layer: bool = False) -> bool:
        """Export stackup definition to a file.

        Parameters
        ----------
        fpath : str
            File path to export to.
        file_format : str, optional
            Format of the file to export. The default is ``"xml"``. Options are:
            - ``"csv"``
            - ``"xlsx"``
            - ``"json"``
            - ``"xml"``
        include_material_with_layer : bool, optional
            Whether to include the material definition inside layer objects. This parameter is only used
            when a JSON file is exported. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> edb.stackup.export("stackup.xml")
        """
        if len(fpath.split(".")) == 1:
            fpath = "{}.{}".format(fpath, file_format)

        if fpath.endswith(".csv"):
            return self._export_layer_stackup_to_csv_xlsx(fpath, file_format="csv")
        elif fpath.endswith(".xlsx"):
            return self._export_layer_stackup_to_csv_xlsx(fpath, file_format="xlsx")
        elif fpath.endswith(".json"):
            return self._export_layer_stackup_to_json(fpath, include_material_with_layer)
        elif fpath.endswith(".xml"):
            return self._export_xml(fpath)
        else:
            self._logger.warning("Layer stackup format is not supported. Skipping import.")
            return False

    def export_stackup(self, fpath, file_format="xml", include_material_with_layer=False):
        """Export stackup definition to a file.

        .. deprecated:: 0.6.61
           Use :func:`export` instead.

        Parameters
        ----------
        fpath : str
            File path to export to.
        file_format : str, optional
            Format of the file to export. The default is ``"xml"``. Options are:
            - ``"csv"``
            - ``"xlsx"``
            - ``"json"``
        include_material_with_layer : bool, optional
            Whether to include the material definition inside layer objects. This parameter is only used
            when a JSON file is exported. The default is ``False``.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> edb.stackup.export_stackup("stackup.xml")
        """

        self._logger.warning("Method export_stackup is deprecated. Use .export.")
        return self.export(fpath, file_format=file_format, include_material_with_layer=include_material_with_layer)

    def _export_layer_stackup_to_csv_xlsx(self, fpath: Optional[str] = None, file_format: Optional[str] = None) -> bool:
        data = {
            "Type": [],
            "Material": [],
            "Dielectric_Fill": [],
            "Thickness": [],
        }
        idx = []
        for lyr in self.layers.values():
            idx.append(lyr.name)
            data["Type"].append(lyr.type)
            data["Material"].append(lyr.material)
            data["Dielectric_Fill"].append(lyr.dielectric_fill)
            data["Thickness"].append(lyr.thickness)
        df = pd.DataFrame(data, index=idx, columns=["Type", "Material", "Dielectric_Fill", "Thickness"])
        if file_format == "csv":  # pragma: no cover
            if not fpath.endswith(".csv"):
                fpath = fpath + ".csv"
            df.to_csv(fpath)
        else:  # pragma: no cover
            if not fpath.endswith(".xlsx"):  # pragma: no cover
                fpath = fpath + ".xlsx"
            df.to_excel(fpath)
        return True

    def _export_layer_stackup_to_json(
        self, output_file: Optional[str] = None, include_material_with_layer: bool = False
    ) -> bool:
        if not include_material_with_layer:
            material_out = {}
            for material_name, material in self._pedb.materials.materials.items():
                material_out[material_name] = material.to_dict()
        layers_out = {}
        for k, v in self.layers.items():
            data = v._json_format()
            layers_out[k] = data
            if v.material in self._pedb.materials.materials:
                layer_material = self._pedb.materials.materials[v.material]
                if not v.dielectric_fill:
                    dielectric_fill = False
                else:
                    dielectric_fill = self._pedb.materials.materials[v.dielectric_fill]
                if include_material_with_layer:
                    layers_out[k]["material"] = layer_material.to_dict()
                    if dielectric_fill:
                        layers_out[k]["dielectric_fill"] = dielectric_fill.to_dict()
        if not include_material_with_layer:
            stackup_out = {"materials": material_out, "layers": layers_out}
        else:
            stackup_out = {"layers": layers_out}
        if output_file:
            with open(output_file, "w") as write_file:
                json.dump(stackup_out, write_file, indent=4)

            return True
        else:
            return False

    def limits(self, only_metals: bool = False) -> Tuple[str, str]:
        """Retrieve stackup limits.

        Parameters
        ----------
        only_metals : bool, optional
            Whether to retrieve only metals. The default is ``False``.

        Returns
        -------
        tuple
            Tuple containing:
            - Upper layer name
            - Upper layer top elevation
            - Lower layer name
            - Lower layer bottom elevation
        """
        if only_metals:
            input_layers = GrpcLayerTypeSet.SIGNAL_LAYER_SET
        else:
            input_layers = GrpcLayerTypeSet.STACKUP_LAYER_SET

        res = self.core.get_top_bottom_stackup_layers(input_layers)
        upper_layer = res[0]
        upper_layer_top_elevationm = res[1]
        lower_layer = res[2]
        lower_layer_lower_elevation = res[3]
        return upper_layer.name, upper_layer_top_elevationm, lower_layer.name, lower_layer_lower_elevation

    def flip_design(self) -> bool:
        """Flip the current design of a layout.

        Returns
        -------
        bool
            ``True`` when successful.

        Examples
        --------
        >>> edb = Edb(edbpath=targetfile, edbversion="2021.2")
        >>> edb.stackup.flip_design()
        >>> edb.save()
        >>> edb.close_edb()
        """
        try:
            lc = self._layer_collection
            new_lc = LayerCollection.create()
            new_lc.mode = lc.mode
            max_elevation = 0.0
            for layer in lc.get_layers(GrpcLayerTypeSet.STACKUP_LAYER_SET):
                if "RadBox" not in layer.name:  # Ignore RadBox
                    lower_elevation = Value(layer.clone().lower_elevation) * 1.0e6
                    upper_elevation = Value(layer.Clone().upper_elevation) * 1.0e6
                    max_elevation = max([max_elevation, lower_elevation, upper_elevation])

            non_stackup_layers = []
            for layer in lc.get_Layers():
                cloned_layer = layer.clone()
                if not cloned_layer.is_stackup_layer:
                    non_stackup_layers.append(cloned_layer)
                    continue
                if "RadBox" not in cloned_layer.name and not cloned_layer.is_via_layer:
                    upper_elevation = Value(cloned_layer.upper_elevation) * 1.0e6
                    updated_lower_el = max_elevation - upper_elevation
                    val = Value(f"{updated_lower_el}um")
                    cloned_layer.lower_elevation = val
                    if cloned_layer.top_bottom_association == GrpcTopBottomAssociation.TOP_ASSOCIATED:
                        cloned_layer.top_bottom_association = GrpcTopBottomAssociation.BOTTOM_ASSOCIATED
                    else:
                        cloned_layer.top_bottom_association = GrpcTopBottomAssociation.TOP_BOTTOM_ASSOCIATION_COUNT
                    new_lc.add_stackup_layer_at_elevation(cloned_layer)

            vialayers = [lay for lay in lc.get_layers(GrpcLayerTypeSet.STACKUP_LAYER_SET) if lay.clone().is_via_layer]
            for layer in vialayers:
                cloned_via_layer = layer.clone()
                upper_ref_name = cloned_via_layer.get_ref_layer_name(True)
                lower_ref_name = cloned_via_layer.get_ref_layer_name(False)
                upper_ref = [lay for lay in lc.Layers(GrpcLayerTypeSet.ALL_LAYER_SET) if lay.name == upper_ref_name][0]
                lower_ref = [lay for lay in lc.Layers(GrpcLayerTypeSet.ALL_LAYER_SET) if lay.name == lower_ref_name][0]
                cloned_via_layer.set_ref_layer(lower_ref, True)
                cloned_via_layer.set_ref_layer(upper_ref, False)
                ref_layer_in_flipped_stackup = [
                    lay for lay in new_lc.get_layers(GrpcLayerTypeSet.ALL_LAYER_SET) if lay.name == upper_ref_name
                ][0]
                via_layer_lower_elevation = (
                    ref_layer_in_flipped_stackup.lower_elevation + ref_layer_in_flipped_stackup.thickness
                )
                cloned_via_layer.lower_elevation = via_layer_lower_elevation
                new_lc.add_stackup_layer_at_elevation(cloned_via_layer)
            new_lc.add_layers(non_stackup_layers)
            self._pedb.layout.layer_collection = new_lc

            for pyaedt_cmp in list(self._pedb.components.instances.values()):
                cmp = pyaedt_cmp
                cmp_type = cmp.type
                cmp_prop = cmp.component_property
                try:
                    if cmp_prop.solder_ball_property.placement == GrpcSolderballPlacement.ABOVE_PADSTACK:
                        sball_prop = cmp_prop.solder_ball_property
                        sball_prop.placement = GrpcSolderballPlacement.BELOW_PADSTACK
                        cmp_prop.solder_ball_property = sball_prop
                    elif cmp_prop.solder_ball_property.placement == GrpcSolderballPlacement.BELOW_PADSTACK:
                        sball_prop = cmp_prop.solder_ball_property
                        sball_prop.placement = GrpcSolderballPlacement.ABOVE_PADSTACK
                        cmp_prop.solder_ball_property = sball_prop
                except Exception as e:
                    self._logger.warning(
                        f"A(n) {type(e).__name__} error occurred while attempting to update "
                        f"solder_ball_property for component {cmp}: {str(e)}"
                    )
                if cmp_type == GrpcComponentType.IC:
                    die_prop = cmp_prop.die_property
                    chip_orientation = die_prop.die_orientation
                    if chip_orientation == GrpcDieOrientation.CHIP_DOWN:
                        die_prop.die_orientation = GrpcDieOrientation.CHIP_UP
                        cmp_prop.die_property = die_prop
                    else:
                        die_prop.die_orientation = GrpcDieOrientation.CHIP_DOWN
                        cmp_prop.die_property = die_prop
                cmp.component_property = cmp_prop

            lay_list = new_lc.get_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)
            for padstack in list(self._pedb.padstacks.instances.values()):
                start_layer_id = [lay.id for lay in lay_list if lay.name == padstack.start_layer]
                stop_layer_id = [lay.id for lay in lay_list if lay.name == padstack.stop_layer]
                layer_map = padstack.get_layer_map()
                layer_map.set_mapping(stop_layer_id[0], start_layer_id[0])
                padstack.set_layer_map(layer_map)
            return True
        except:
            return False

    def get_layout_thickness(self) -> float:
        """Return the layout thickness.

        Returns
        -------
        float
            Thickness value.
        """
        layers = list(self.layers.values())
        layers.sort(key=lambda lay: lay.lower_elevation)
        thickness = 0
        if layers:
            top_layer = layers[-1]
            bottom_layer = layers[0]
            thickness = abs(top_layer.upper_elevation - bottom_layer.lower_elevation)
        return round(thickness, 7)

    def _get_solder_height(self, layer_name) -> float:
        height = 0.0
        for _, val in self._pedb.components.instances.items():
            try:
                if val.solder_ball_height and val.placement_layer == layer_name:
                    height = val.solder_ball_height
            except Exception as e:
                self._logger.error(
                    f"A(n) {type(e).__name__} error occurred while attempting to retrieve solder_height "
                    f"for layer {layer_name} - Default value of 0.0 is returned: {str(e)}"
                )
        return height

    def _remove_solder_pec(self, layer_name):
        for _, val in self._pedb.components.instances.items():
            if val.solder_ball_height and val.placement_layer == layer_name:
                comp_prop = val.component_property
                port_property = comp_prop.port_property
                port_property.reference_size_auto = False
                port_property.reference_size = (Value(0.0), Value(0.0))
                comp_prop.port_property = port_property
                val.component_property = comp_prop

    def adjust_solder_dielectrics(self) -> bool:
        """Adjust the stack-up by adding or modifying dielectric layers that contain solder balls.

        This method identifies the solder-ball height and adjusts the dielectric thickness on top (or bottom)
        to fit the thickness in order to merge another layout.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        for el, val in self._pedb.components.instances.items():
            if val.solder_ball_height:
                layer = val.placement_layer
                if layer == list(self.layers.keys())[0]:
                    self.add_layer(
                        "Bottom_air",
                        base_layer=list(self.layers.keys())[-1],
                        method="insert_below",
                        material="air",
                        thickness=val.solder_ball_height,
                        layer_type="dielectric",
                    )
                elif layer == list(self.layers.keys())[-1]:
                    self.add_layer(
                        "Top_Air",
                        base_layer=layer,
                        material="air",
                        thickness=val.solder_ball_height,
                        layer_type="dielectric",
                    )
                elif layer == list(self.signal_layers.keys())[-1]:
                    list(self.layers.values())[-1].thickness = val.solder_ball_height

                elif layer == list(self.signal_layers.keys())[0]:
                    list(self.layers.values())[0].thickness = val.solder_ball_height
        return True

    def place_in_layout(
        self,
        edb: "Edb",
        angle: float = 0.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        flipped_stackup: bool = True,
        place_on_top: bool = True,
    ) -> bool:
        """Place current cell into another cell using layer placement method.

        Flip the current layer stackup of a layout if requested.

        Parameters
        ----------
        edb : :class:`pyedb.Edb`
            Target Edb object.
        angle : float, optional
            Rotation angle in degrees. The default is ``0.0``.
        offset_x : float, optional
            X offset value. The default is ``0.0``.
        offset_y : float, optional
            Y offset value. The default is ``0.0``.
        flipped_stackup : bool, optional
            Whether to flip the current layout. The default is ``True``.
        place_on_top : bool, optional
            Whether to place the current layout on top of the destination layout. The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1, edbversion="2021.2")
        >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")

        >>> hosting_cmp = edb1.components.get_component_by_name("U100")
        >>> mounted_cmp = edb2.components.get_component_by_name("BGA")

        >>> vector, rotation, solder_ball_height = edb1.components.get_component_placement_vector(
        ...     mounted_component=mounted_cmp,
        ...     hosting_component=hosting_cmp,
        ...     mounted_component_pin1="A12",
        ...     mounted_component_pin2="A14",
        ...     hosting_component_pin1="A12",
        ...     hosting_component_pin2="A14",
        ... )
        >>> edb2.stackup.place_in_layout(
        ...     edb1.active_cell,
        ...     angle=0.0,
        ...     offset_x=vector[0],
        ...     offset_y=vector[1],
        ...     flipped_stackup=False,
        ...     place_on_top=True,
        ... )
        """
        # if flipped_stackup and place_on_top or (not flipped_stackup and not place_on_top):
        self.adjust_solder_dielectrics()
        if not place_on_top:
            edb.stackup.flip_design()
            place_on_top = True
            if not flipped_stackup:
                self.flip_design()
        elif flipped_stackup:
            self.flip_design()
        edb_cell = edb.active_cell
        _angle = Value(angle * math.pi / 180.0)
        _offset_x = Value(offset_x)
        _offset_y = Value(offset_y)

        if edb_cell.name not in self._pedb.cell_names:
            list_cells = self._pedb.copy_cells([edb_cell])
            edb_cell = list_cells[0]
        self._pedb.layout.cell.is_blackbox = True
        cell_inst2 = GrpcCellInstance.create(
            layout=edb_cell.layout, name=self._pedb.layout.cell.name, ref=self._pedb.active_layout
        )
        cell_trans = cell_inst2.transform
        cell_trans.rotation = _angle
        cell_trans.offset_x = _offset_x
        cell_trans.offset_y = _offset_y
        cell_trans.mirror = flipped_stackup
        cell_inst2.transform = cell_trans
        cell_inst2.solve_independent_preference = False
        stackup_target = edb_cell.layout.layer_collection

        if place_on_top:
            cell_inst2.placement_layer = stackup_target.get_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)[0]
        else:
            cell_inst2.placement_layer = stackup_target.get_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)[-1]
        return True

    def place_in_layout_3d_placement(
        self,
        edb: "Edb",
        angle: float = 0.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        flipped_stackup: bool = True,
        place_on_top: bool = True,
        solder_height: float = 0,
    ) -> bool:
        """Place current cell into another cell using 3D placement method.

        Flip the current layer stackup of a layout if requested.

        Parameters
        ----------
        edb : :class:`pyedb.Edb`
            Target Edb object.
        angle : float, optional
            Rotation angle in degrees. The default is ``0.0``.
        offset_x : float, optional
            X offset value. The default is ``0.0``.
        offset_y : float, optional
            Y offset value. The default is ``0.0``.
        flipped_stackup : bool, optional
            Whether to flip the current layout. The default is ``True``.
        place_on_top : bool, optional
            Whether to place the current layout on top of the destination layout. The default is ``True``.
        solder_height : float, optional
            Solder ball or bumps height. This value will be added to the elevation to align the two layouts.

        Returns
        -------
        bool
            ``True`` when successful.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1, edbversion="2021.2")
        >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")
        >>> hosting_cmp = edb1.components.get_component_by_name("U100")
        >>> mounted_cmp = edb2.components.get_component_by_name("BGA")
        >>> edb2.stackup.place_in_layout(
        ...     edb1.active_cell,
        ...     angle=0.0,
        ...     offset_x="1mm",
        ...     offset_y="2mm",
        ...     flipped_stackup=False,
        ...     place_on_top=True,
        ... )
        """
        _angle = angle * math.pi / 180.0

        if solder_height <= 0:
            if flipped_stackup and not place_on_top or (place_on_top and not flipped_stackup):
                minimum_elevation = None
                layers_from_the_bottom = sorted(self.layers.values(), key=lambda lay: lay.upper_elevation)
                for lay in layers_from_the_bottom:
                    if minimum_elevation is None:
                        minimum_elevation = lay.lower_elevation
                    elif lay.lower_elevation > minimum_elevation:
                        break
                    lay_solder_height = self._get_solder_height(lay.name)
                    solder_height = max(lay_solder_height, solder_height)
                    self._remove_solder_pec(lay.name)
            else:
                maximum_elevation = None
                layers_from_the_top = sorted(self.layers.values(), key=lambda lay: -lay.upper_elevation)
                for lay in layers_from_the_top:
                    if maximum_elevation is None:
                        maximum_elevation = lay.upper_elevation
                    elif lay.upper_elevation < maximum_elevation:
                        break
                    lay_solder_height = self._get_solder_height(lay.name)
                    solder_height = max(lay_solder_height, solder_height)
                    self._remove_solder_pec(lay.name)

        rotation = Value(0.0)
        if flipped_stackup:
            rotation = Value(math.pi)

        edb_cell = edb.active_cell
        _offset_x = Value(offset_x)
        _offset_y = Value(offset_y)

        if edb_cell.name not in self._pedb.cell_names:
            list_cells = self._pedb.copy_cells(edb_cell)
            edb_cell = list_cells[0]
        self._pedb.layout.cell.is_blackbox = True
        cell_inst2 = GrpcCellInstance.create(
            layout=edb_cell.layout, name=self._pedb.layout.cell.name, ref=self._pedb.active_layout.core
        )

        stackup_target = edb_cell.layout.layer_collection
        stackup_source = self._pedb.layout.core.layer_collection
        if place_on_top:
            cell_inst2.placement_layer = list(LayerCollection(self._pedb, stackup_target).layers.values())[0].core
        else:
            cell_inst2.placement_layer = list(LayerCollection(self._pedb, stackup_target).layers.values())[-1].core
        cell_inst2.placement_3d = True
        res = stackup_target.get_top_bottom_stackup_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)
        target_top_elevation = res[1]
        target_bottom_elevation = res[3]
        res_s = stackup_source.get_top_bottom_stackup_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)
        source_stack_top_elevation = res_s[1]
        source_stack_bot_elevation = res_s[3]

        if place_on_top and flipped_stackup:
            elevation = target_top_elevation + source_stack_top_elevation
        elif place_on_top:
            elevation = target_top_elevation - source_stack_bot_elevation
        elif flipped_stackup:
            elevation = target_bottom_elevation + source_stack_bot_elevation
            solder_height = -solder_height
        else:
            elevation = target_bottom_elevation - source_stack_top_elevation
            solder_height = -solder_height

        h_stackup = Value(elevation + solder_height)

        zero_data = Value(0.0)
        one_data = Value(1.0)
        point3d_t = GrpcPoint3DData(_offset_x, _offset_y, h_stackup)
        point_loc = GrpcPoint3DData(zero_data, zero_data, zero_data)
        point_from = GrpcPoint3DData(one_data, zero_data, zero_data)
        point_to = GrpcPoint3DData(math.cos(_angle), -1 * math.sin(_angle), zero_data)
        transform = cell_inst2.transform3d.create_from_one_axis_to_another(from_axis=point_from, to_axis=point_to)
        cell_inst2.transform3d = transform
        transform = cell_inst2.transform3d.create_from_axis_and_angle(axis=point_loc, angle=angle)
        cell_inst2.transform3d = transform
        transform = cell_inst2.transform3d.create_from_offset(offset=point3d_t)
        cell_inst2.transform3d = transform
        # TODO check if component is properly placed.
        return True

    def place_instance(
        self,
        component_edb: "Edb",
        angle: float = 0.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        offset_z: float = 0.0,
        flipped_stackup: bool = True,
        place_on_top: bool = True,
        solder_height: float = 0,
    ) -> GrpcCellInstance:
        """Place a component instance in the layout using 3D placement.

        Parameters
        ----------
        component_edb : :class:`pyedb.Edb`
            Component Edb object to place.
        angle : float, optional
            Rotation angle in degrees. The default is ``0.0``.
        offset_x : float, optional
            X offset value. The default is ``0.0``.
        offset_y : float, optional
            Y offset value. The default is ``0.0``.
        offset_z : float, optional
            Z offset value (elevation offset). The default is ``0.0``.
        flipped_stackup : bool, optional
            Whether to flip the component stackup. The default is ``True``.
        place_on_top : bool, optional
            Whether to place the component on top of the target layout. The default is ``True``.
        solder_height : float, optional
            Solder ball or bumps height. The default is ``0``.

        Returns
        -------
        :class:`ansys.edb.core.hierarchy.CellInstance`
            Cell instance created.
        """
        _angle = angle * math.pi / 180.0

        if solder_height <= 0:
            if flipped_stackup and not place_on_top or (place_on_top and not flipped_stackup):
                minimum_elevation = None
                layers_from_the_bottom = sorted(
                    component_edb.stackup.layers.values(), key=lambda lay: lay.upper_elevation
                )
                for lay in layers_from_the_bottom:
                    if minimum_elevation is None:
                        minimum_elevation = lay.lower_elevation
                    elif lay.lower_elevation > minimum_elevation:
                        break
                    lay_solder_height = component_edb.stackup._get_solder_height(lay.name)
                    solder_height = max(lay_solder_height, solder_height)
                    component_edb.stackup._remove_solder_pec(lay.name)
            else:
                maximum_elevation = None
                layers_from_the_top = sorted(
                    component_edb.stackup.layers.values(), key=lambda lay: -lay.upper_elevation
                )
                for lay in layers_from_the_top:
                    if maximum_elevation is None:
                        maximum_elevation = lay.upper_elevation
                    elif lay.upper_elevation < maximum_elevation:
                        break
                    lay_solder_height = component_edb.stackup._get_solder_height(lay.name)
                    solder_height = max(lay_solder_height, solder_height)
                    component_edb.stackup._remove_solder_pec(lay.name)
        edb_cell = component_edb.active_cell
        _offset_x = Value(offset_x)
        _offset_y = Value(offset_y)

        if edb_cell.name not in self._pedb.cell_names:
            list_cells = self._pedb.copy_cells(edb_cell)
            edb_cell = list_cells[0]
        for cell in self._pedb.active_db.top_circuit_cells:
            if cell.name == edb_cell.name:
                edb_cell = cell
        # Keep Cell Independent
        edb_cell.is_black_box = True
        rotation = Value(0.0)
        if flipped_stackup:
            rotation = Value(math.pi)

        _offset_x = Value(offset_x)
        _offset_y = Value(offset_y)

        instance_name = generate_unique_name(edb_cell.name, n=2)

        cell_inst2 = GrpcCellInstance.create(
            layout=self._pedb.active_layout.core, name=instance_name, ref=edb_cell.layout
        )

        stackup_source = edb_cell.layout.layer_collection
        stackup_target = self._pedb.layout.core.layer_collection

        if place_on_top:
            cell_inst2.placement_layer = stackup_target.get_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)[0]
        else:
            cell_inst2.placement_layer = stackup_target.get_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)[-1]
        cell_inst2.placement_3d = True
        res = stackup_target.get_top_bottom_stackup_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)
        target_top_elevation = res[1]
        target_bottom_elevation = res[3]
        res_s = stackup_source.get_top_bottom_stackup_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)
        source_stack_top_elevation = res_s[1]
        source_stack_bot_elevation = res_s[3]

        if place_on_top and flipped_stackup:
            elevation = target_top_elevation + source_stack_top_elevation + offset_z
        elif place_on_top:
            elevation = target_top_elevation - source_stack_bot_elevation + offset_z
        elif flipped_stackup:
            elevation = target_bottom_elevation + source_stack_bot_elevation - offset_z
            solder_height = -solder_height
        else:
            elevation = target_bottom_elevation - source_stack_top_elevation - offset_z
            solder_height = -solder_height

        h_stackup = elevation + solder_height

        zero_data = Value(0.0)
        one_data = Value(1.0)
        point3d_t = GrpcPoint3DData(_offset_x, _offset_y, h_stackup)
        point_loc = GrpcPoint3DData(zero_data, zero_data, zero_data)
        point_from = GrpcPoint3DData(one_data, zero_data, zero_data)
        point_to = GrpcPoint3DData(math.cos(_angle), -1 * math.sin(_angle), zero_data)
        transform = cell_inst2.transform3d.create_from_axis_and_angle(axis=point_loc, angle=angle)
        cell_inst2.transform3d = transform
        transform = cell_inst2.transform3d.create_from_one_axis_to_another(point_from, point_to)
        cell_inst2.transform3d = transform
        transform = cell_inst2.transform3d.create_from_offset(point3d_t)
        cell_inst2.transform3d = transform
        # TODO check is position is correct.
        return cell_inst2

    def place_a3dcomp_3d_placement(
        self,
        a3dcomp_path: str,
        angle: float = 0.0,
        offset_x: float = 0.0,
        offset_y: float = 0.0,
        offset_z: float = 0.0,
        place_on_top: bool = True,
    ) -> bool:
        """Place a 3D component into the current layout.

        3D Component ports are not visible via EDB. They will be visible after the EDB has been opened in Ansys
        Electronics Desktop as a project.

        Parameters
        ----------
        a3dcomp_path : str
            Path to the 3D Component file (``*.a3dcomp``) to place.
        angle : float, optional
            Clockwise rotation angle applied to the a3dcomp.
        offset_x : float, optional
            X offset value. The default is ``0.0``.
        offset_y : float, optional
            Y offset value. The default is ``0.0``.
        offset_z : float, optional
            Z offset value (elevation). The default is ``0.0``.
        place_on_top : bool, optional
            Whether to place the 3D component on the top or the bottom of this layout. If ``False``, the 3D component
            will be flipped over around its X axis.

        Returns
        -------
        bool
            ``True`` if successful, ``False`` if not.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1, edbversion="2021.2")
        >>> a3dcomp_path = "connector.a3dcomp"
        >>> edb1.stackup.place_a3dcomp_3d_placement(
        ...     a3dcomp_path,
        ...     angle=0.0,
        ...     offset_x="1mm",
        ...     offset_y="2mm",
        ...     flipped_stackup=False,
        ...     place_on_top=True,
        ... )
        """
        rotation_axis_from = GrpcPoint3DData(1.0, 0.0, 0.0)
        _angle = angle * math.pi / 180.0
        rotation_axis_to = GrpcPoint3DData(math.cos(_angle), -1 * math.sin(_angle), 0.0)

        stackup_target = LayerCollection(self._pedb, self._pedb.layout.core.layer_collection)
        res = stackup_target.core.get_top_bottom_stackup_layers(GrpcLayerTypeSet.SIGNAL_LAYER_SET)
        target_top_elevation = res[1]
        target_bottom_elevation = res[3]
        flip_angle = Value("0deg")
        if place_on_top:
            elevation = target_top_elevation + offset_z
        else:
            flip_angle = Value("180deg")
            elevation = target_bottom_elevation - offset_z
        h_stackup = Value(elevation)
        location = GrpcPoint3DData(offset_x, offset_y, h_stackup)
        mcad_model = GrpcMcadModel.create_3d_comp(layout=self._pedb.active_layout.core, filename=a3dcomp_path)
        if mcad_model.is_null:  # pragma: no cover
            logger.error("Failed to create MCAD model from a3dcomp")
            return False

        if mcad_model.cell_instance.is_null:  # pragma: no cover
            logger.error("Cell instance of a3dcomp is null")
            return False

        mcad_model.cell_instance.placement_3d = True
        transform_rotation = mcad_model.cell_instance.transform3d.create_from_axis_and_angle(
            axis=rotation_axis_from, angle=Value(flip_angle)
        )
        mcad_model.cell_instance.transform3d = transform_rotation
        transform_translation = mcad_model.cell_instance.transform3d.create_from_offset(offset=location)
        mcad_model.cell_instance.transform3d = transform_translation
        return True

    def residual_copper_area_per_layer(self) -> Dict[str, float]:
        """Report residual copper area per layer in percentage.

        Returns
        -------
        dict
            Dictionary of copper area per layer.

        Examples
        --------
        >>> edb = Edb(edbpath=targetfile1, edbversion="2021.2")
        >>> edb.stackup.residual_copper_area_per_layer()
        """
        temp_data = {name: 0 for name, _ in self.signal_layers.items()}
        outline_area = 0
        for i in self._pedb.modeler.primitives:
            layer_name = i.layer.name
            if layer_name.lower() == "outline":
                if i.area() > outline_area:
                    outline_area = i.area()
            elif layer_name not in temp_data:
                continue
            elif not i.is_void:
                temp_data[layer_name] = temp_data[layer_name] + i.area()
            else:
                pass
        temp_data = {name: area / outline_area * 100 for name, area in temp_data.items()}
        return temp_data

    def _import_dict(self, json_dict: Dict[str, Any], rename: bool = False) -> bool:
        """Import stackup from a dictionary.

        Parameters
        ----------
        json_dict : dict
            Dictionary containing stackup information.
        rename : bool, optional
            Whether to rename layers. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        if not "materials" in json_dict:
            self._logger.info("Configuration file does not have material definition. Using aedb and syslib materials.")
        else:
            mats = json_dict["materials"]
            for name, material in mats.items():
                try:
                    material_name = material["name"]
                    del material["name"]
                except KeyError:
                    material_name = name
                if material_name not in self._pedb.materials:
                    self._pedb.materials.add_material(material_name, **material)
                else:
                    self._pedb.materials.update_material(material_name, material)
        temp = json_dict
        if "layers" in json_dict:
            temp = {i: j for i, j in json_dict["layers"].items() if j["type"] in ["signal", "dielectric"]}
        config_file_layers = list(temp.keys())
        layout_layers = list(self.layers.keys())
        renamed_layers = {}
        if rename and len(config_file_layers) == len(layout_layers):
            for lay_ind in range(len(list(temp.keys()))):
                if not config_file_layers[lay_ind] == layout_layers[lay_ind]:
                    renamed_layers[layout_layers[lay_ind]] = config_file_layers[lay_ind]
        layers_names = list(self.layers.keys())[::]
        for name in layers_names:
            layer = None
            if name in temp:
                layer = temp[name]
            elif name in renamed_layers:
                layer = temp[renamed_layers[name]]
                self.layers[name].name = renamed_layers[name]
                name = renamed_layers[name]
            else:  # Remove layers not in config file.
                self.remove_layer(name)
                self._logger.warning(f"Layer {name} were not found in configuration file, removing layer")
            default_layer = {
                "name": "default",
                "type": "signal",
                "material": "copper",
                "dielectric_fill": "FR4_epoxy",
                "thickness": 3.5e-05,
                "etch_factor": 0.0,
                "roughness_enabled": False,
                "top_hallhuray_nodule_radius": 0.0,
                "top_hallhuray_surface_ratio": 0.0,
                "bottom_hallhuray_nodule_radius": 0.0,
                "bottom_hallhuray_surface_ratio": 0.0,
                "side_hallhuray_nodule_radius": 0.0,
                "side_hallhuray_surface_ratio": 0.0,
                "upper_elevation": 0.0,
                "lower_elevation": 0.0,
                "color": [242, 140, 102],
            }
            if layer:
                if "color" in layer:
                    default_layer["color"] = layer["color"]
                elif not layer["type"] == "signal":
                    default_layer["color"] = [27, 110, 76]

                for k, v in layer.items():
                    default_layer[k] = v
                self.layers[name]._load_layer(default_layer)
        for layer_name, layer in temp.items():  # looping over potential new layers to add
            if layer_name in self.layers:
                continue  # if layer exist, skip
            # adding layer
            default_layer = {
                "name": "default",
                "type": "signal",
                "material": "copper",
                "dielectric_fill": "FR4_epoxy",
                "thickness": 3.5e-05,
                "etch_factor": 0.0,
                "roughness_enabled": False,
                "top_hallhuray_nodule_radius": 0.0,
                "top_hallhuray_surface_ratio": 0.0,
                "bottom_hallhuray_nodule_radius": 0.0,
                "bottom_hallhuray_surface_ratio": 0.0,
                "side_hallhuray_nodule_radius": 0.0,
                "side_hallhuray_surface_ratio": 0.0,
                "upper_elevation": 0.0,
                "lower_elevation": 0.0,
                "color": [242, 140, 102],
            }

            if "color" in layer:
                default_layer["color"] = layer["color"]
            elif not layer["type"] == "signal":
                default_layer["color"] = [27, 110, 76]

            for k, v in layer.items():
                default_layer[k] = v

            temp_2 = list(temp.keys())
            if temp_2.index(layer_name) == 0:
                new_layer = self.add_layer(
                    layer_name,
                    method="add_on_top",
                    layer_type=default_layer["type"],
                    material=default_layer["material"],
                    fillMaterial=default_layer["dielectric_fill"],
                    thickness=default_layer["thickness"],
                )

            elif temp_2.index(layer_name) == len(temp_2):
                new_layer = self.add_layer(
                    layer_name,
                    base_layer=layer_name,
                    method="add_on_bottom",
                    layer_type=default_layer["type"],
                    material=default_layer["material"],
                    fillMaterial=default_layer["dielectric_fill"],
                    thickness=default_layer["thickness"],
                )
            else:
                new_layer = self.add_layer(
                    layer_name,
                    base_layer=temp_2[temp_2.index(layer_name) - 1],
                    method="insert_below",
                    layer_type=default_layer["type"],
                    material=default_layer["material"],
                    fillMaterial=default_layer["dielectric_fill"],
                    thickness=default_layer["thickness"],
                )
            new_layer = self.layers[layer_name]
            new_layer.color = tuple(default_layer["color"])
            new_layer.etch_factor = default_layer["etch_factor"]
            new_layer.roughness_enabled = default_layer["roughness_enabled"]
            new_layer.top_hallhuray_nodule_radius = default_layer["top_hallhuray_nodule_radius"]
            new_layer.top_hallhuray_surface_ratio = default_layer["top_hallhuray_surface_ratio"]
            new_layer.bottom_hallhuray_nodule_radius = default_layer["bottom_hallhuray_nodule_radius"]
            new_layer.bottom_hallhuray_surface_ratio = default_layer["bottom_hallhuray_surface_ratio"]
            new_layer.side_hallhuray_nodule_radius = default_layer["side_hallhuray_nodule_radius"]
            new_layer.side_hallhuray_surface_ratio = default_layer["side_hallhuray_surface_ratio"]
        return True

    def _import_json(self, file_path: str, rename: bool = False) -> bool:
        """Import stackup from a JSON file.

        Parameters
        ----------
        file_path : str
            Path to the JSON file.
        rename : bool, optional
            Whether to rename layers. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        if file_path:
            f = open(file_path)
            json_dict = json.load(f)  # pragma: no cover
            return self._import_dict(json_dict, rename)

    def _import_csv(self, file_path: str) -> bool:
        """Import stackup definition from a CSV file.

        Parameters
        ----------
        file_path : str
            File path to the CSV file.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        df = pd.read_csv(file_path, index_col=0)

        for name in self.layers.keys():  # pragma: no cover
            if not name in df.index:
                logger.error(f"{name} doesn't exist in csv")
                return False

        for name, layer_info in df.iterrows():
            layer_type = layer_info.Type
            if name in self.layers:
                layer = self.layers[name]
                layer.type = layer_type
            else:
                layer = self.add_layer(name, layer_type=layer_type, material="copper", fillMaterial="copper")
            layer = self.layers[name]
            layer.material = layer_info.Material
            layer.thickness = layer_info.Thickness
            if not str(layer_info.Dielectric_Fill) == "nan":
                layer.dielectric_fill = layer_info.Dielectric_Fill

        lc_new = GrpcLayerCollection.create()
        for name, _ in df.iterrows():
            layer = self.layers[name]
            lc_new.add_layer_bottom(layer.core)

        for name, layer in self.non_stackup_layers.items():
            lc_new.add_layer_bottom(layer.core)

        self._pedb.layout.layer_collection = lc_new
        return True

    def _set(
        self,
        layers: Optional[Dict] = None,
        materials: Optional[Dict] = None,
        roughness: Optional[Dict] = None,
        non_stackup_layers: Optional[Dict] = None,
    ) -> bool:
        """Update stackup information.

        Parameters
        ----------
        layers : dict, optional
            Dictionary containing layer information.
        materials : dict, optional
            Dictionary containing material information.
        roughness : dict, optional
            Dictionary containing roughness information.
        non_stackup_layers : dict, optional
            Dictionary containing non-stackup layer information.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        if materials:
            self._add_materials_from_dictionary(materials)

        if layers:
            prev_layer = None
            for name, val in layers.items():
                etching_factor = float(val["EtchFactor"]) if "EtchFactor" in val else None

                if not self.layers:
                    self.add_layer(
                        name,
                        None,
                        "add_on_top",
                        val["Type"],
                        val["Material"],
                        val["FillMaterial"] if val["Type"] == "signal" else "",
                        val["Thickness"],
                        etching_factor,
                    )
                else:
                    if name in self.layers.keys():
                        lyr = self.layers[name]
                        lyr.type = val["Type"]
                        lyr.material = val["Material"]
                        lyr.dielectric_fill = val["FillMaterial"] if val["Type"] == "signal" else ""
                        lyr.thickness = val["Thickness"]
                        if prev_layer:
                            self._set_layout_stackup(lyr._edb_layer, "change_position", prev_layer)
                    else:
                        if prev_layer and prev_layer in self.layers:
                            layer_name = prev_layer
                        else:
                            layer_name = list(self.layers.keys())[-1] if self.layers else None
                        self.add_layer(
                            name,
                            layer_name,
                            "insert_above",
                            val["Type"],
                            val["Material"],
                            val["FillMaterial"] if val["Type"] == "signal" else "",
                            val["Thickness"],
                            etching_factor,
                        )
                    prev_layer = name
            for name in self.layers:
                if name not in layers:
                    self.remove_layer(name)

        if roughness:
            for name, attr in roughness.items():
                layer = self.signal_layers[name]
                layer.roughness_enabled = True

                attr_name = "HuraySurfaceRoughness"
                if attr_name in attr:
                    on_surface = "top"
                    layer.assign_roughness_model(
                        "huray",
                        attr[attr_name]["NoduleRadius"],
                        attr[attr_name]["HallHuraySurfaceRatio"],
                        apply_on_surface=on_surface,
                    )

                attr_name = "HurayBottomSurfaceRoughness"
                if attr_name in attr:
                    on_surface = "bottom"
                    layer.assign_roughness_model(
                        "huray",
                        attr[attr_name]["NoduleRadius"],
                        attr[attr_name]["HallHuraySurfaceRatio"],
                        apply_on_surface=on_surface,
                    )
                attr_name = "HuraySideSurfaceRoughness"
                if attr_name in attr:
                    on_surface = "side"
                    layer.assign_roughness_model(
                        "huray",
                        attr[attr_name]["NoduleRadius"],
                        attr[attr_name]["HallHuraySurfaceRatio"],
                        apply_on_surface=on_surface,
                    )

                attr_name = "GroissSurfaceRoughness"
                if attr_name in attr:
                    on_surface = "top"
                    layer.assign_roughness_model(
                        "groisse", groisse_roughness=attr[attr_name]["Roughness"], apply_on_surface=on_surface
                    )

                attr_name = "GroissBottomSurfaceRoughness"
                if attr_name in attr:
                    on_surface = "bottom"
                    layer.assign_roughness_model(
                        "groisse", groisse_roughness=attr[attr_name]["Roughness"], apply_on_surface=on_surface
                    )

                attr_name = "GroissSideSurfaceRoughness"
                if attr_name in attr:
                    on_surface = "side"
                    layer.assign_roughness_model(
                        "groisse", groisse_roughness=attr[attr_name]["Roughness"], apply_on_surface=on_surface
                    )

        if non_stackup_layers:
            for name, val in non_stackup_layers.items():
                if name in self.non_stackup_layers:
                    continue
                else:
                    self.add_layer(name, layer_type=val["Type"])

        return True

    def _get(self) -> Tuple[Dict, Dict, Dict, Dict]:
        """Get stackup information from layout.

        Returns
        -------
        tuple
            Tuple containing:
            - layers (dict)
            - materials (dict)
            - roughness_models (dict)
            - non_stackup_layers (dict)
        """
        layers = OrderedDict()
        roughness_models = OrderedDict()
        for name, val in self.layers.items():
            layer = dict()
            layer["Material"] = val.material
            layer["Name"] = val.name
            layer["Thickness"] = val.thickness
            layer["Type"] = val.type
            if not val.type == "dielectric":
                layer["FillMaterial"] = val.dielectric_fill
                layer["EtchFactor"] = val.etch_factor
            layers[name] = layer

            if val.roughness_enabled:
                roughness_models[name] = {}
                model = val.get_roughness_model("top")
                if model.type.name.endswith("GroissRoughnessModel"):
                    roughness_models[name]["GroissSurfaceRoughness"] = {"Roughness": Value(model.get_Roughness)}
                else:
                    roughness_models[name]["HuraySurfaceRoughness"] = {
                        "HallHuraySurfaceRatio": Value(model.get_nodule_radius()),
                        "NoduleRadius": Value(model.get_surface_ratio()),
                    }
                model = val.get_roughness_model("bottom")
                if model.type.name.endswith("GroissRoughnessModel"):
                    roughness_models[name]["GroissBottomSurfaceRoughness"] = {"Roughness": Value(model.get_roughness())}
                else:
                    roughness_models[name]["HurayBottomSurfaceRoughness"] = {
                        "HallHuraySurfaceRatio": Value(model.get_nodule_radius()),
                        "NoduleRadius": Value(model.get_surface_ratio()),
                    }
                model = val.get_roughness_model("side")
                if model.ToString().endswith("GroissRoughnessModel"):
                    roughness_models[name]["GroissSideSurfaceRoughness"] = {"Roughness": Value(model.get_roughness())}
                else:
                    roughness_models[name]["HuraySideSurfaceRoughness"] = {
                        "HallHuraySurfaceRatio": Value(model.get_nodule_radius()),
                        "NoduleRadius": Value(model.get_surface_ratio()),
                    }

        non_stackup_layers = OrderedDict()
        for name, val in self.non_stackup_layers.items():
            layer = dict()
            layer["Name"] = val.name
            layer["Type"] = val.type
            non_stackup_layers[name] = layer

        materials = {}
        for name, val in self._pedb.materials.materials.items():
            material = {}
            if val.conductivity:
                if val.conductivity > 4e7:
                    material["Conductivity"] = val.conductivity
            else:
                material["Permittivity"] = val.permittivity
                material["DielectricLossTangent"] = val.dielectric_loss_tangent
            materials[name] = material

        return layers, materials, roughness_models, non_stackup_layers

    def _add_materials_from_dictionary(self, material_dict: Dict[str, Dict]) -> bool:
        materials = self.self._pedb.materials.materials
        for name, material_properties in material_dict.items():
            if "Conductivity" in material_properties:
                materials.add_conductor_material(name, material_properties["Conductivity"])
            else:
                materials.add_dielectric_material(
                    name,
                    material_properties["Permittivity"],
                    material_properties["DielectricLossTangent"],
                )
        return True

    def _import_xml(self, file_path: str, rename: bool = False) -> bool:
        """Read external XML file and convert into JSON format.

        Parameters
        ----------
        file_path : str
            Path to external XML file.
        rename : bool, optional
            Whether to rename layers. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        tree = defused_parse(file_path)
        root = tree.getroot()
        stackup = root.find("Stackup")
        stackup_dict = {}
        if stackup.find("Materials"):
            mats = []
            for m in stackup.find("Materials").findall("Material"):
                temp = dict()
                for i in list(m):
                    value = list(i)[0].text
                    temp[i.tag] = value
                mat = {"name": m.attrib["Name"]}
                temp_dict = {
                    "Permittivity": "permittivity",
                    "Conductivity": "conductivity",
                    "DielectricLossTangent": "dielectric_loss_tangent",
                }
                for i in temp_dict.keys():
                    value = temp.get(i, None)
                    if value:
                        mat[temp_dict[i]] = value
                mats.append(mat)
            stackup_dict["materials"] = mats

        stackup_section = stackup.find("Layers")
        if stackup_section:
            length_unit = stackup_section.attrib["LengthUnit"]
            layers = []
            for l in stackup.find("Layers").findall("Layer"):
                temp = l.attrib
                layer = dict()
                temp_dict = {
                    "Name": "name",
                    "Color": "color",
                    "Material": "material",
                    "Thickness": "thickness",
                    "Type": "type",
                    "FillMaterial": "fill_material",
                }
                for i in temp_dict.keys():
                    value = temp.get(i, None)
                    if value:
                        if i == "Thickness":
                            value = str(round(float(value), 6)) + length_unit
                        value = "signal" if value == "conductor" else value
                        if i == "Color":
                            value = [int(x * 255) for x in list(colors.to_rgb(value))]
                        layer[temp_dict[i]] = value
                layers.append(layer)
            stackup_dict["layers"] = layers
        cfg = {"stackup": stackup_dict}
        return self._pedb.configuration.load(cfg, apply_file=True)

    def _export_xml(self, file_path: str) -> bool:
        """Export stackup information to an external XML file.

        Parameters
        ----------
        file_path : str
            Path to external XML file.

        Returns
        -------
        bool
            ``True`` when successful.
        """
        layers, materials, roughness, non_stackup_layers = self._get()

        root = ET.Element("{http://www.ansys.com/control}Control", attrib={"schemaVersion": "1.0"})

        el_stackup = ET.SubElement(root, "Stackup", {"schemaVersion": "1.0"})

        el_materials = ET.SubElement(el_stackup, "Materials")
        for mat, val in materials.items():
            material = ET.SubElement(el_materials, "Material")
            material.set("Name", mat)
            for pname, pval in val.items():
                mat_prop = ET.SubElement(material, pname)
                value = ET.SubElement(mat_prop, "Double")
                value.text = str(pval)

        el_layers = ET.SubElement(el_stackup, "Layers", {"LengthUnit": "meter"})
        for lyr, val in layers.items():
            layer = ET.SubElement(el_layers, "Layer")
            val = {i: str(j) for i, j in val.items()}
            if val["Type"] == "signal":
                val["Type"] = "conductor"
            layer.attrib.update(val)

        for lyr, val in non_stackup_layers.items():
            layer = ET.SubElement(el_layers, "Layer")
            val = {i: str(j) for i, j in val.items()}
            layer.attrib.update(val)

        for lyr, val in roughness.items():
            el = el_layers.find("./Layer[@Name='{}']".format(lyr))
            for pname, pval in val.items():
                pval = {i: str(j) for i, j in pval.items()}
                ET.SubElement(el, pname, pval)

        write_pretty_xml(root, file_path)
        return True

    def load(self, file_path: Union[str, Dict], rename: bool = False) -> bool:
        """Import stackup from a file.

        Supported formats: XML, CSV, JSON.

        Parameters
        ----------
        file_path : str or dict
            Path to stackup file or dictionary with stackup details.
        rename : bool, optional
            If ``False``, layers in layout not found in the stackup file are deleted.
            If ``True`` and the number of layers in the stackup file equals the number of stackup layers
            in the layout, layers are renamed according to the file.

        Returns
        -------
        bool
            ``True`` when successful.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> edb.stackup.load("stackup.xml")
        """

        if isinstance(file_path, dict):
            return self._import_dict(file_path)
        elif file_path.endswith(".csv"):
            return self._import_csv(file_path)
        elif file_path.endswith(".json"):
            return self._import_json(file_path, rename=rename)
        elif file_path.endswith(".xml"):
            return self._import_xml(file_path, rename=rename)
        else:
            return False

    def plot(
        self,
        save_plot: Optional[str] = None,
        size: Tuple[int, int] = (2000, 1500),
        plot_definitions: Optional[Union[str, List[str]]] = None,
        first_layer: Optional[Union[str, "Layer"]] = None,
        last_layer: Optional[Union[str, "Layer"]] = None,
        scale_elevation: bool = True,
        show: bool = True,
    ) -> Any:
        """Plot the current stackup and optionally overlap padstack definitions.

        Only supports 'Laminate' and 'Overlapping' stackup types.

        Parameters
        ----------
        save_plot : str, optional
            Path to save the plot image. If provided, ``show`` is ignored.
        size : tuple, optional
            Image size in pixels (width, height). Default is ``(2000, 1500)``.
        plot_definitions : str or list, optional
            List of padstack definitions to plot on the stackup. Only supported for Laminate mode.
        first_layer : str or :class:`pyedb.grpc.database.layers.layer.Layer`, optional
            First layer to plot from the bottom. Default is ``None`` (start from bottom).
        last_layer : str or :class:`pyedb.grpc.database.layers.layer.Layer`, optional
            Last layer to plot from the bottom. Default is ``None`` (plot up to top layer).
        scale_elevation : bool, optional
            Scale real layer thickness so that max_thickness = 3 * min_thickness. Default is ``True``.
        show : bool, optional
            Whether to show the plot. Default is ``True``.

        Returns
        -------
        :class:`matplotlib.pyplot`
            Matplotlib plot object.
        """

        from pyedb.generic.constants import CSS4_COLORS
        from pyedb.generic.plot import plot_matplotlib

        layer_names = list(self.layers.keys())
        if first_layer is None or first_layer not in layer_names:
            bottom_layer = layer_names[-1]
        elif isinstance(first_layer, str):
            bottom_layer = first_layer
        elif isinstance(first_layer, Layer):
            bottom_layer = first_layer.name
        else:
            raise AttributeError("first_layer must be str or class `dotnet.database.edb_data.layer_data.LayerEdbClass`")
        if last_layer is None or last_layer not in layer_names:
            top_layer = layer_names[0]
        elif isinstance(last_layer, str):
            top_layer = last_layer
        elif isinstance(last_layer, Layer):
            top_layer = last_layer.name
        else:
            raise AttributeError("last_layer must be str or class `dotnet.database.edb_data.layer_data.LayerEdbClass`")

        stackup_mode = self.mode
        if stackup_mode not in ["laminate", "overlapping"]:
            raise AttributeError("stackup plot supports only 'laminate' and 'overlapping' stackup types.")

        # build the layers data
        layers_data = []
        skip_flag = True
        for layer in self.layers.values():  # start from top
            if layer.name != top_layer and skip_flag:
                continue
            else:
                skip_flag = False
            layers_data.append([layer, layer.lower_elevation, layer.upper_elevation, layer.thickness])
            if layer.name == bottom_layer:
                break
        layers_data.reverse()  # let's start from the bottom

        # separate dielectric and signal if overlapping stackup
        if stackup_mode == "overlapping":
            dielectric_layers = [l for l in layers_data if l[0].type == "dielectric"]
            signal_layers = [l for l in layers_data if l[0].type == "signal"]

        # compress the thicknesses if required
        if scale_elevation:
            min_thickness = min([i[3] for i in layers_data if i[3] != 0])
            max_thickness = max([i[3] for i in layers_data])
            c = 3  # max_thickness = c * min_thickness

            def _compress_t(y):
                m = min_thickness
                M = max_thickness
                k = (c - 1) * m / (M - m)
                if y > 0:
                    return (y - m) * k + m
                else:
                    return 0.0

            if stackup_mode == "laminate":
                l0 = layers_data[0]
                compressed_layers_data = [[l0[0], l0[1], _compress_t(l0[3]), _compress_t(l0[3])]]  # the first row
                lp = compressed_layers_data[0]
                for li in layers_data[1:]:  # the other rows
                    ct = _compress_t(li[3])
                    compressed_layers_data.append([li[0], lp[2], lp[2] + ct, ct])
                    lp = compressed_layers_data[-1]
                layers_data = compressed_layers_data

            elif stackup_mode == "overlapping":
                compressed_diels = []
                first_diel = True
                for li in dielectric_layers:
                    ct = _compress_t(li[3])
                    if first_diel:
                        if li[1] > 0:
                            l0le = _compress_t(li[1])
                        else:
                            l0le = li[1]
                        compressed_diels.append([li[0], l0le, l0le + ct, ct])
                        first_diel = False
                    else:
                        lp = compressed_diels[-1]
                        compressed_diels.append([li[0], lp[2], lp[2] + ct, ct])

                def _convert_elevation(el):
                    inside = False
                    for i, li in enumerate(dielectric_layers):
                        if li[1] <= el <= li[2]:
                            inside = True
                            break
                    if inside:
                        u = (el - li[1]) / (li[2] - li[1])
                        cli = compressed_diels[i]
                        cel = cli[1] + u * (cli[2] - cli[1])
                    else:
                        cel = el
                    return cel

                compressed_signals = []
                for li in signal_layers:
                    cle = _convert_elevation(li[1])
                    cue = _convert_elevation(li[2])
                    ct = cue - cle
                    compressed_signals.append([li[0], cle, cue, ct])

                dielectric_layers = compressed_diels
                signal_layers = compressed_signals

        # create the data for the plot
        diel_alpha = 0.4
        signal_alpha = 0.6
        zero_thickness_alpha = 1.0
        annotation_fontsize = 14
        annotation_x_margin = 0.01
        annotations = []
        plot_data = []
        if stackup_mode == "laminate":
            min_thickness = min([i[3] for i in layers_data if i[3] != 0])
            for ly in layers_data:
                layer = ly[0]

                # set color and label
                color = [float(i) / 256 for i in layer.color]
                if color == [1.0, 1.0, 1.0]:
                    color = [0.9, 0.9, 0.9]
                label = "{}, {}, thick: {:.3f}um, elev: {:.3f}um".format(
                    layer.name, layer.material, layer.thickness * 1e6, layer.lower_elevation * 1e6
                )

                # create patch
                x = [0, 0, 1, 1]
                if ly[3] > 0:
                    lower_elevation = ly[1]
                    upper_elevation = ly[2]
                    y = [lower_elevation, upper_elevation, upper_elevation, lower_elevation]
                    plot_data.insert(0, [x, y, color, label, signal_alpha, "fill"])
                else:
                    lower_elevation = ly[1] - min_thickness * 0.1  # make the zero thickness layers more visible
                    upper_elevation = ly[2] + min_thickness * 0.1
                    y = [lower_elevation, upper_elevation, upper_elevation, lower_elevation]
                    # put the zero thickness layers on top
                    plot_data.append([x, y, color, label, zero_thickness_alpha, "fill"])

                # create annotation
                y_pos = (lower_elevation + upper_elevation) / 2
                if layer.type == "dielectric":
                    x_pos = -annotation_x_margin
                    annotations.append(
                        [x_pos, y_pos, layer.name, {"fontsize": annotation_fontsize, "horizontalalignment": "right"}]
                    )
                elif layer.type == "signal":
                    x_pos = 1.0 + annotation_x_margin
                    annotations.append([x_pos, y_pos, layer.name, {"fontsize": annotation_fontsize}])

            # evaluate the legend reorder
            legend_order = []
            for ly in layers_data:
                name = ly[0].name
                for i, a in enumerate(plot_data):
                    iname = a[3].split(",")[0]
                    if name == iname:
                        legend_order.append(i)
                        break

        elif stackup_mode == "overlapping":
            min_thickness = min([i[3] for i in signal_layers if i[3] != 0])
            columns = []  # first column is x=[0,1], second column is x=[1,2] and so on...
            for ly in signal_layers:
                lower_elevation = ly[1]  # lower elevation
                t = ly[3]  # thickness
                put_in_column = 0
                cell_position = 0
                for c in columns:
                    uep = c[-1][0][2]  # upper elevation of the last entry of that column
                    tp = c[-1][0][3]  # thickness of the last entry of that column
                    if lower_elevation < uep or (abs(lower_elevation - uep) < 1e-15 and tp == 0 and t == 0):
                        put_in_column += 1
                        cell_position = len(c)
                    else:
                        break
                if len(columns) < put_in_column + 1:  # add a new column if required
                    columns.append([])
                # put zeros at the beginning of the column until there is the first layer
                if cell_position != 0:
                    fill_cells = cell_position - 1 - len(columns[put_in_column])
                    for i in range(fill_cells):
                        columns[put_in_column].append(0)
                # append the layer to the proper column and row
                x = [put_in_column + 1, put_in_column + 1, put_in_column + 2, put_in_column + 2]
                columns[put_in_column].append([ly, x])

            # fill the columns matrix with zeros on top
            n_rows = max([len(i) for i in columns])
            for c in columns:
                while len(c) < n_rows:
                    c.append(0)
            # expand to the right the fill for the signals that have no overlap on the right
            width = len(columns) + 1
            for i, c in enumerate(columns[:-1]):
                for j, r in enumerate(c):
                    if r != 0:  # and dname == r[0].name
                        if columns[i + 1][j] == 0:
                            # nothing on the right, so expand the fill
                            x = r[1]
                            r[1] = [x[0], x[0], width, width]

            for c in columns:
                for r in c:
                    if r != 0:
                        ly = r[0]
                        layer = ly[0]
                        x = r[1]

                        # set color and label
                        color = [float(i) / 256 for i in layer.color]
                        if color == [1.0, 1.0, 1.0]:
                            color = [0.9, 0.9, 0.9]
                        label = "{}, {}, thick: {:.3f}um, elev: {:.3f}um".format(
                            layer.name, layer.material, layer.thickness * 1e6, layer.lower_elevation * 1e6
                        )

                        if ly[3] > 0:
                            lower_elevation = ly[1]
                            upper_elevation = ly[2]
                            y = [lower_elevation, upper_elevation, upper_elevation, lower_elevation]
                            plot_data.insert(0, [x, y, color, label, signal_alpha, "fill"])
                        else:
                            lower_elevation = ly[1] - min_thickness * 0.1  # make the zero thickness layers more visible
                            upper_elevation = ly[2] + min_thickness * 0.1
                            y = [lower_elevation, upper_elevation, upper_elevation, lower_elevation]
                            # put the zero thickness layers on top
                            plot_data.append([x, y, color, label, zero_thickness_alpha, "fill"])

                        # create annotation
                        x_pos = 1.0
                        y_pos = (lower_elevation + upper_elevation) / 2
                        annotations.append([x_pos, y_pos, layer.name, {"fontsize": annotation_fontsize}])

            # order the annotations based on y_pos (it is necessary later to move them to avoid text overlapping)
            annotations.sort(key=lambda e: e[1])
            # move all the annotations to the final x (it could be larger than 1 due to additional columns)
            width = len(columns) + 1
            for i, a in enumerate(annotations):
                a[0] = width + annotation_x_margin * width

            for ly in dielectric_layers:
                layer = ly[0]
                # set color and label
                color = [float(i) / 256 for i in layer.color]
                if color == [1.0, 1.0, 1.0]:
                    color = [0.9, 0.9, 0.9]
                label = "{}, {}, thick: {:.3f}um, elev: {:.3f}um".format(
                    layer.name, layer.material, layer.thickness * 1e6, layer.lower_elevation * 1e6
                )
                # create the patch
                lower_elevation = ly[1]
                upper_elevation = ly[2]
                y = [lower_elevation, upper_elevation, upper_elevation, lower_elevation]
                x = [0, 0, width, width]
                plot_data.insert(0, [x, y, color, label, diel_alpha, "fill"])

                # create annotation
                x_pos = -annotation_x_margin * width
                y_pos = (lower_elevation + upper_elevation) / 2
                annotations.append(
                    [x_pos, y_pos, layer.name, {"fontsize": annotation_fontsize, "horizontalalignment": "right"}]
                )

            # evaluate the legend reorder
            legend_order = []
            for ly in dielectric_layers:
                name = ly[0].name
                for i, a in enumerate(plot_data):
                    iname = a[3].split(",")[0]
                    if name == iname:
                        legend_order.append(i)
                        break
            for ly in signal_layers:
                name = ly[0].name
                for i, a in enumerate(plot_data):
                    iname = a[3].split(",")[0]
                    if name == iname:
                        legend_order.append(i)
                        break

        # calculate the extremities of the plot
        x_min = 0.0
        x_max = max([max(i[0]) for i in plot_data])
        if stackup_mode == "laminate":
            y_min = layers_data[0][1]
            y_max = layers_data[-1][2]
        elif stackup_mode == "overlapping":
            y_min = min(dielectric_layers[0][1], signal_layers[0][1])
            y_max = max(dielectric_layers[-1][2], signal_layers[-1][2])

        # move the annotations to avoid text overlapping
        new_annotations = []
        for i, a in enumerate(annotations):
            if i > 0 and abs(a[1] - annotations[i - 1][1]) < (y_max - y_min) / 75:
                new_annotations[-1][2] = str(new_annotations[-1][2]) + ", " + str(a[2])
            else:
                new_annotations.append(a)
        annotations = new_annotations

        if plot_definitions:
            if stackup_mode == "overlapping":
                self._logger.warning("Plot of padstacks are supported only for Laminate mode.")

            max_plots = 10

            if not isinstance(plot_definitions, list):
                plot_definitions = [plot_definitions]
            color_index = 0
            color_keys = list(CSS4_COLORS.keys())
            delta = 1 / (max_plots + 1)  # padstack spacing in plot coordinates
            x_start = delta

            # find the max padstack size to calculate the scaling factor
            max_padstak_size = 0.0
            for definition in plot_definitions:
                if isinstance(definition, str):
                    definition = self._pedb.padstacks.definitions[definition]
                for layer, defs in definition.pad_by_layer.items():
                    pad_shape = defs.shape
                    params = defs.parameters_values
                    pad_size = max([p for p in params])
                    if pad_size > max_padstak_size:
                        max_padstak_size = pad_size
                if not definition.is_null:
                    hole_d = definition.hole_diameter
                    max_padstak_size = max(hole_d, max_padstak_size)
            scaling_f_pad = (2 / ((max_plots + 1) * 3)) / max_padstak_size

            for definition in plot_definitions:
                if isinstance(definition, str):
                    definition = self._pedb.padstacks.definitions[definition]
                min_le = 1e12
                max_ue = -1e12
                max_x = 0
                padstack_name = definition.name
                annotations.append([x_start, y_max, padstack_name, {"rotation": 45}])

                via_start_layer = definition.start_layer
                via_stop_layer = definition.stop_layer

                if stackup_mode == "overlapping":
                    # here search the column using the first and last layer. Pick the column with max index.
                    pass

                for layer, defs in definition.pad_by_layer.items():
                    pad_shape = defs.shape
                    params = defs.parameters_values
                    pad_size = max([p for p in params])
                    if stackup_mode == "laminate":
                        x = [
                            x_start - pad_size / 2 * scaling_f_pad,
                            x_start - pad_size / 2 * scaling_f_pad,
                            x_start + pad_size / 2 * scaling_f_pad,
                            x_start + pad_size / 2 * scaling_f_pad,
                        ]
                        lower_elevation = [e[1] for e in layers_data if e[0].name == layer or layer == "Default"][0]
                        upper_elevation = [e[2] for e in layers_data if e[0].name == layer or layer == "Default"][0]
                        y = [lower_elevation, upper_elevation, upper_elevation, lower_elevation]
                        # create the patch for that signal layer
                        plot_data.append([x, y, color_keys[color_index], None, 1.0, "fill"])
                    elif stackup_mode == "overlapping":
                        # here evaluate the x based on the column evaluated before and the pad size
                        pass

                    min_le = min(lower_elevation, min_le)
                    max_ue = max(upper_elevation, max_ue)
                if not definition.is_null:
                    # create patch for the hole
                    hole_radius = definition.hole_diameter / 2 * scaling_f_pad
                    x = [x_start - hole_radius, x_start - hole_radius, x_start + hole_radius, x_start + hole_radius]
                    y = [min_le, max_ue, max_ue, min_le]
                    plot_data.append([x, y, color_keys[color_index], None, 0.7, "fill"])
                    # create patch for the dielectric
                    max_x = max(max_x, hole_radius)
                    rad = hole_radius * (100 - definition.hole_plating_ratio) / 100
                    x = [x_start - rad, x_start - rad, x_start + rad, x_start + rad]
                    plot_data.append([x, y, color_keys[color_index], None, 1.0, "fill"])

                color_index += 1
                if color_index == max_plots:
                    self._logger.warning("Maximum number of definitions plotted.")
                    break
                x_start += delta

        # plot the stackup
        plt = plot_matplotlib(
            plot_data,
            size=size,
            show_legend=False,
            xlabel="",
            ylabel="",
            title="",
            save_plot=None,
            x_limits=[x_min, x_max],
            y_limits=[y_min, y_max],
            axis_equal=False,
            annotations=annotations,
            show=False,
        )
        # we have to customize some defaults, so we plot or save the figure here
        plt.axis("off")
        plt.box(False)
        plt.title("Stackup\n ", fontsize=28)
        # evaluates the number of legend column based on the layer name max length
        ncol = 3 if max([len(n) for n in layer_names]) < 15 else 2
        handles, labels = plt.gca().get_legend_handles_labels()
        plt.legend(
            [handles[idx] for idx in legend_order],
            [labels[idx] for idx in legend_order],
            bbox_to_anchor=(0, -0.05),
            loc="upper left",
            borderaxespad=0,
            ncol=ncol,
        )
        plt.tight_layout()
        if save_plot:
            plt.savefig(save_plot)
        elif show:
            plt.show()
        return plt
