# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

from __future__ import absolute_import  # noreorder

from collections import OrderedDict
import json
import logging
import math
import warnings

from pyedb.dotnet.edb_core.edb_data.layer_data import (
    LayerEdbClass,
    StackupLayerEdbClass,
)
from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list
from pyedb.generic.general_methods import ET, generate_unique_name
from pyedb.misc.aedtlib_personalib_install import write_pretty_xml

colors = None
pd = None
np = None
try:
    import matplotlib.colors as colors
except ImportError:
    colors = None

try:
    import numpy as np
except ImportError:
    np = None

try:
    import pandas as pd
except ImportError:
    pd = None

logger = logging.getLogger(__name__)


class LayerCollection(object):
    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb

        if edb_object:
            self._edb_object = self._pedb.edb_api.cell._cell.LayerCollection(edb_object)
        else:
            self._edb_object = self._pedb.edb_api.cell._cell.LayerCollection()

        self._layer_type_set_mapping = {
            "stackup_layer_set": self._pedb.edb_api.cell.layer_type_set.StackupLayerSet,
            "signal_ayer_et": self._pedb.edb_api.cell.layer_type_set.SignalLayerSet,
            "non_stackup_layer_set": self._pedb.edb_api.cell.layer_type_set.NonStackupLayerSet,
            "all_layer_et": self._pedb.edb_api.cell.layer_type_set.AllLayerSet,
        }
        self._lc_mode_mapping = {
            "laminate": self._pedb.edb_api.cell._cell.LayerCollectionMode.Laminate,
            "overlapping": self._pedb.edb_api.cell._cell.LayerCollectionMode.Overlapping,
            "multizone": self._pedb.edb_api.cell._cell.LayerCollectionMode.MultiZone,
        }

    def update_layout(self):
        """Set layer collection into edb.

        Parameters
        ----------
        stackup
        """
        self._pedb.layout.layer_collection = self._edb_object

    def refresh_layer_collection(self):
        """Refresh layer collection from Edb. This method is run on demand after all edit operations on stackup."""
        self._edb_object = self._pedb.edb_api.cell._cell.LayerCollection(self._pedb.layout.layer_collection)
        self._lc = self._edb_object

    def _add_layer(self, add_method, base_layer_name="", **kwargs):
        """Add a layer to edb.

        Parameters
        ----------
        add_method
        base_layer_name
        """
        layer_clone = kwargs.get("layer_clone", None)
        if layer_clone:
            obj = layer_clone
        else:
            layer_type = kwargs.get("layer_type", None)
            if not layer_type:
                layer_type = kwargs["type"]
            if layer_type in ["signal", "dielectric"]:
                obj = StackupLayerEdbClass(self._pedb, edb_object=None, **kwargs)
            else:
                obj = LayerEdbClass(self._pedb, edb_object=None, **kwargs)
        method_top_bottom = None
        method_above_below = None
        if add_method == "add_layer_top":
            method_top_bottom = self._edb_object.AddLayerTop
        elif add_method == "add_layer_bottom":
            method_top_bottom = self._edb_object.AddLayerBottom
        elif add_method == "add_layer_above":
            method_above_below = self._edb_object.AddLayerAbove
        elif add_method == "add_layer_below":
            method_above_below = self._edb_object.AddLayerBelow
        else:  # pragma: no cover
            logger.error("The way of defining layer addition is not correct")
            return False

        if method_top_bottom:
            obj = obj if method_top_bottom(obj._edb_object) else False
        elif method_above_below:
            obj = obj if method_above_below(obj._edb_object, base_layer_name) else False
        self.update_layout()
        return obj

    def add_layer_top(self, name, layer_type="signal", **kwargs):
        """Add a layer on top of the stackup.

        Parameters
        ----------
        name : str
            Name of the layer.
        layer_type: str, optional
            Type of the layer. The default to ``"signal"``. Options are ``"signal"``, ``"dielectric"``
        kwargs

        Returns
        -------

        """
        kwargs["name"] = name
        kwargs["layer_type"] = layer_type
        return self._add_layer(add_method="add_layer_top", **kwargs)

    def add_layer_bottom(self, name, layer_type="signal", **kwargs):
        """Add a layer on bottom of the stackup.

        Parameters
        ----------
        name : str
            Name of the layer.
        layer_type: str, optional
            Type of the layer. The default to ``"signal"``. Options are ``"signal"``, ``"dielectric"``
        kwargs

        Returns
        -------

        """
        kwargs["name"] = name
        kwargs["layer_type"] = layer_type
        return self._add_layer(add_method="add_layer_bottom", **kwargs)

    def add_layer_below(self, name, base_layer_name, layer_type="signal", **kwargs):
        """Add a layer below a layer.

        Parameters
        ----------
        name : str
            Name of the layer.
        base_layer_name: str
            Name of the base layer.
        layer_type: str, optional
            Type of the layer. The default to ``"signal"``. Options are ``"signal"``, ``"dielectric"``
        kwargs

        Returns
        -------

        """
        kwargs["name"] = name
        kwargs["layer_type"] = layer_type
        return self._add_layer(add_method="add_layer_below", base_layer_name=base_layer_name, **kwargs)

    def add_layer_above(self, name, base_layer_name, layer_type="signal", **kwargs):
        """Add a layer above a layer.

        Parameters
        ----------
        name : str
            Name of the layer.
        base_layer_name: str
            Name of the base layer.
        layer_type: str, optional
            Type of the layer. The default to ``"signal"``. Options are ``"signal"``, ``"dielectric"``
        kwargs

        Returns
        -------

        """
        kwargs["name"] = name
        kwargs["layer_type"] = layer_type
        return self._add_layer(add_method="add_layer_above", base_layer_name=base_layer_name, **kwargs)

    def add_document_layer(self, name, layer_type="UndefinedLayerType", **kwargs):
        """Add a document layer.

        Parameters
        ----------
        name : str
            Name of the layer.
        layer_type: str, optional
            Type of the layer. The default to ``"signal"``. Options are ``"signal"``, ``"dielectric"``
        kwargs

        Returns
        -------

        """
        kwargs["name"] = name
        kwargs["layer_type"] = layer_type
        return self._add_layer(add_method="add_layer_bottom", **kwargs)

    def set_layer_clone(self, layer_clone):
        lc = self._pedb.edb_api.cell._cell.LayerCollection()  # empty layer collection
        lc.SetMode(self._edb_object.GetMode())
        if self.mode.lower() == "laminate":
            add_method = lc.AddLayerBottom
        else:
            add_method = lc.AddStackupLayerAtElevation

        obj = False
        # Add stackup layers
        for _, i in self.layers.items():
            if i.id == layer_clone.id:  # replace layer
                add_method(layer_clone._edb_object)
                obj = layer_clone
            else:  # keep existing layer
                add_method(i._edb_object)
        # Add non stackup layers
        for _, i in self.non_stackup_layers.items():
            if i.id == layer_clone.id:
                lc.AddLayerBottom(layer_clone._edb_object)
                obj = layer_clone
            else:
                lc.AddLayerBottom(i._edb_object)

        self._edb_object = lc
        self.update_layout()

        if not obj:
            logger.info("Layer clone was not found in stackup or non stackup layers.")
        return obj

    @property
    def stackup_layers(self):
        """Retrieve the dictionary of signal and dielectric layers."""
        warnings.warn("Use new property :func:`layers` instead.", DeprecationWarning)
        return self.layers

    @property
    def non_stackup_layers(self):
        """Retrieve the dictionary of signal layers."""
        return {name: obj for name, obj in self.all_layers.items() if not obj.is_stackup_layer}

    @property
    def all_layers(self):
        self.refresh_layer_collection()
        layer_list = list(self._edb_object.Layers(self._pedb.edb_api.cell.layer_type_set.AllLayerSet))
        temp = dict()
        for i in layer_list:
            if i.IsStackupLayer():
                obj = StackupLayerEdbClass(self._pedb, i.Clone(), name=i.GetName())
            else:
                obj = LayerEdbClass(self._pedb, i.Clone(), name=i.GetName())
            temp[obj.name] = obj
        return temp

    @property
    def layers_by_id(self):
        """Retrieve the list of layers with their ids."""
        return [[obj.id, name] for name, obj in self.all_layers.items()]

    @property
    def layers(self):
        """Retrieve the dictionary of layers.

        Returns
        -------
        Dict[str, :class:`pyedb.dotnet.edb_core.edb_data.layer_data.LayerEdbClass`]
        """
        return {name: obj for name, obj in self.all_layers.items() if obj.is_stackup_layer}


class Stackup(LayerCollection):
    """Manages EDB methods for stackup accessible from `Edb.stackup` property."""

    def __getitem__(self, item):
        return self.all_layers[item]

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)
        # parent caller class
        self._lc = self._edb_object

    @property
    def _logger(self):
        return self._pedb.logger

    @property
    def layer_types(self):
        """Layer types.

        Returns
        -------
        type
            Types of layers.
        """
        return self._pedb.edb_api.cell.layer_type

    @property
    def thickness(self):
        """Retrieve Stackup thickness.

        Returns
        -------
        float
            Layout stackup thickness.

        """
        return self.get_layout_thickness()

    @property
    def num_layers(self):
        """Retrieve the stackup layer number.

        Returns
        -------
        int
            layer number.

        """
        return len(list(self.layers.keys()))

    def _int_to_layer_types(self, val):
        if int(val) == 0:
            return self.layer_types.SignalLayer
        elif int(val) == 1:
            return self.layer_types.DielectricLayer
        elif int(val) == 2:
            return self.layer_types.ConductingLayer
        elif int(val) == 3:
            return self.layer_types.AirlinesLayer
        elif int(val) == 4:
            return self.layer_types.ErrorsLayer
        elif int(val) == 5:
            return self.layer_types.SymbolLayer
        elif int(val) == 6:
            return self.layer_types.MeasureLayer
        elif int(val) == 8:
            return self.layer_types.AssemblyLayer
        elif int(val) == 9:
            return self.layer_types.SilkscreenLayer
        elif int(val) == 10:
            return self.layer_types.SolderMaskLayer
        elif int(val) == 11:
            return self.layer_types.SolderPasteLayer
        elif int(val) == 12:
            return self.layer_types.GlueLayer
        elif int(val) == 13:
            return self.layer_types.WirebondLayer
        elif int(val) == 14:
            return self.layer_types.UserLayer
        elif int(val) == 16:
            return self.layer_types.SIwaveHFSSSolverRegions
        elif int(val) == 17:
            return self.layer_types.PostprocessingLayer
        elif int(val) == 18:
            return self.layer_types.OutlineLayer
        elif int(val) == 16:
            return self.layer_types.LayerTypesCount
        elif int(val) == -1:
            return self.layer_types.UndefinedLayerType

    def _layer_types_to_int(self, layer_type):
        if not isinstance(layer_type, int):
            if layer_type == self.layer_types.SignalLayer:
                return 0
            elif layer_type == self.layer_types.DielectricLayer:
                return 1
            elif layer_type == self.layer_types.ConductingLayer:
                return 2
            elif layer_type == self.layer_types.AirlinesLayer:
                return 3
            elif layer_type == self.layer_types.ErrorsLayer:
                return 4
            elif layer_type == self.layer_types.SymbolLayer:
                return 5
            elif layer_type == self.layer_types.MeasureLayer:
                return 6
            elif layer_type == self.layer_types.AssemblyLayer:
                return 8
            elif layer_type == self.layer_types.SilkscreenLayer:
                return 9
            elif layer_type == self.layer_types.SolderMaskLayer:
                return 10
            elif layer_type == self.layer_types.SolderPasteLayer:
                return 11
            elif layer_type == self.layer_types.GlueLayer:
                return 12
            elif layer_type == self.layer_types.WirebondLayer:
                return 13
            elif layer_type == self.layer_types.UserLayer:
                return 14
            elif layer_type == self.layer_types.SIwaveHFSSSolverRegions:
                return 16
            elif layer_type == self.layer_types.OutlineLayer:
                return 18
        elif isinstance(layer_type, int):
            return

    def create_symmetric_stackup(
        self,
        layer_count,
        inner_layer_thickness="17um",
        outer_layer_thickness="50um",
        dielectric_thickness="100um",
        dielectric_material="FR4_epoxy",
        soldermask=True,
        soldermask_thickness="20um",
    ):  # pragma: no cover
        """Create a symmetric stackup.

        Parameters
        ----------
        layer_count : int
            Number of layer count.
        inner_layer_thickness : str, float, optional
            Thickness of inner conductor layer.
        outer_layer_thickness : str, float, optional
            Thickness of outer conductor layer.
        dielectric_thickness : str, float, optional
            Thickness of dielectric layer.
        dielectric_material : str, optional
            Material of dielectric layer.
        soldermask : bool, optional
            Whether to create soldermask layers. The default is``True``.
        soldermask_thickness : str, optional
            Thickness of soldermask layer.

        Returns
        -------
        bool
        """
        if not np:
            self._pedb.logger.error("Numpy is needed. Please, install it first.")
            return False
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
    def _layer_collection(self):
        """Copy of EDB layer collection.

        Returns
        -------
        :class:`Ansys.Ansoft.Edb.Cell.LayerCollection`
            Collection of layers.
        """
        self.refresh_layer_collection()
        return self._lc

    @property
    def mode(self):
        """Stackup mode.

        Returns
        -------
        int, str
            Type of the stackup mode, where:

            * 0 - Laminate
            * 1 - Overlapping
            * 2 - MultiZone
        """
        self._stackup_mode = self._layer_collection.GetMode()
        return str(self._stackup_mode)

    @mode.setter
    def mode(self, value):
        mode = self._pedb.edb_api.Cell.LayerCollectionMode
        if value == 0 or value == mode.Laminate or value == "Laminate":
            self._layer_collection.SetMode(mode.Laminate)
        elif value == 1 or value == mode.Overlapping or value == "Overlapping":
            self._layer_collection.SetMode(mode.Overlapping)
        elif value == 2 or value == mode.MultiZone or value == "MultiZone":
            self._layer_collection.SetMode(mode.MultiZone)
        self.update_layout()

    @property
    def stackup_mode(self):
        """Stackup mode.

        .. deprecated:: 0.6.52
           Use :func:`mode` method instead.

        Returns
        -------
        int, str
            Type of the stackup mode, where:

            * 0 - Laminate
            * 1 - Overlapping
            * 2 - MultiZone
        """
        warnings.warn("`stackup_mode` is deprecated. Use `mode` method instead.", DeprecationWarning)
        return self.mode

    @stackup_mode.setter
    def stackup_mode(self, value):
        warnings.warn("`stackup_mode` is deprecated. Use `mode` method instead.", DeprecationWarning)
        self.mode = value

    @property
    def _edb_layer_list(self):
        layer_list = list(self._layer_collection.Layers(self._pedb.edb_api.cell.layer_type_set.AllLayerSet))
        return [i.Clone() for i in layer_list]

    @property
    def signal_layers(self):
        """Retrieve the dictionary of signal layers.

        Returns
        -------
        Dict[str, :class:`pyedb.dotnet.edb_core.edb_data.layer_data.LayerEdbClass`]
        """
        layer_type = self._pedb.edb_api.cell.layer_type.SignalLayer
        _lays = OrderedDict()
        for name, obj in self.layers.items():
            if obj._edb_layer.GetLayerType() == layer_type:
                _lays[name] = obj
        return _lays

    @property
    def dielectric_layers(self):
        """Dielectric layers.

        Returns
        -------
        dict[str, :class:`dotnet.edb_core.edb_data.layer_data.EDBLayer`]
            Dictionary of dielectric layers.
        """
        layer_type = self._pedb.edb_api.cell.layer_type.DielectricLayer
        _lays = OrderedDict()
        for name, obj in self.layers.items():
            if obj._edb_layer.GetLayerType() == layer_type:
                _lays[name] = obj
        return _lays

    def _edb_value(self, value):
        return self._pedb.edb_value(value)

    def _set_layout_stackup(self, layer_clone, operation, base_layer=None, method=1):
        """Internal method. Apply stackup change into EDB.

        Parameters
        ----------
        layer_clone : :class:`dotnet.edb_core.EDB_Data.EDBLayer`
        operation : str
            Options are ``"change_attribute"``, ``"change_name"``,``"change_position"``, ``"insert_below"``,
             ``"insert_above"``, ``"add_on_top"``, ``"add_on_bottom"``, ``"non_stackup"``,  ``"add_at_elevation"``.
        base_layer : str, optional
            Name of the base layer. The default value is ``None``.

        Returns
        -------

        """
        _lc = self._layer_collection
        if operation in ["change_position", "change_attribute", "change_name"]:
            lc_readonly = self._pedb.layout.layer_collection
            layers = [
                i.Clone()
                for i in list(list(lc_readonly.Layers(self._pedb.edb_api.cell.layer_type_set.StackupLayerSet)))
            ]
            non_stackup = [
                i.Clone()
                for i in list(list(lc_readonly.Layers(self._pedb.edb_api.cell.layer_type_set.NonStackupLayerSet)))
            ]
            _lc = self._pedb.edb_api.cell._cell.LayerCollection()
            mode = lc_readonly.GetMode()
            _lc.SetMode(lc_readonly.GetMode())
            if str(mode) == "Overlapping":
                for layer in layers:
                    if layer.GetName() == layer_clone.GetName() or layer.GetName() == base_layer:
                        _lc.AddStackupLayerAtElevation(layer_clone)
                    else:
                        _lc.AddStackupLayerAtElevation(layer)
            else:
                for layer in layers:
                    if layer.GetName() == layer_clone.GetName() or layer.GetName() == base_layer:
                        _lc.AddLayerBottom(layer_clone)
                    else:
                        _lc.AddLayerBottom(layer)
            for layer in non_stackup:
                _lc.AddLayerBottom(layer)
            _lc.SetMode(lc_readonly.GetMode())
        elif operation == "insert_below":
            _lc.AddLayerBelow(layer_clone, base_layer)
        elif operation == "insert_above":
            _lc.AddLayerAbove(layer_clone, base_layer)
        elif operation == "add_on_top":
            _lc.AddLayerTop(layer_clone)
        elif operation == "add_on_bottom":
            _lc.AddLayerBottom(layer_clone)
        elif operation == "add_at_elevation":
            _lc.AddStackupLayerAtElevation(layer_clone)
        elif operation == "non_stackup":
            _lc.AddLayerBottom(layer_clone)
        self._pedb.layout.layer_collection = _lc
        self.refresh_layer_collection()
        return True

    def _create_stackup_layer(self, layer_name, thickness, layer_type="signal"):
        if layer_type == "signal":
            _layer_type = self._pedb.edb_api.cell.layer_type.SignalLayer
        else:
            _layer_type = self._pedb.edb_api.cell.layer_type.DielectricLayer

        result = self._pedb.edb_api.cell._cell.StackupLayer(
            layer_name,
            _layer_type,
            self._edb_value(thickness),
            self._edb_value(0),
            "",
        )
        self.refresh_layer_collection()
        return result

    def _create_nonstackup_layer(self, layer_name, layer_type):
        if layer_type == "conducting":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.ConductingLayer
        elif layer_type == "airlines":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.AirlinesLayer
        elif layer_type == "error":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.ErrorsLayer
        elif layer_type == "symbol":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.SymbolLayer
        elif layer_type == "measure":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.MeasureLayer
        elif layer_type == "assembly":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.AssemblyLayer
        elif layer_type == "silkscreen":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.SilkscreenLayer
        elif layer_type == "soldermask":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.SolderMaskLayer
        elif layer_type == "solderpaste":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.SolderPasteLayer
        elif layer_type == "glue":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.GlueLayer
        elif layer_type == "wirebond":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.WirebondLayer
        elif layer_type == "user":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.UserLayer
        elif layer_type == "siwavehfsssolverregions":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.SIwaveHFSSSolverRegions
        elif layer_type == "outline":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.OutlineLayer
        elif layer_type == "postprocessing":  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.PostprocessingLayer
        else:  # pragma: no cover
            _layer_type = self._pedb.edb_api.cell.layer_type.UndefinedLayerType

        result = self._pedb.edb_api.cell.layer(layer_name, _layer_type)
        self.refresh_layer_collection()
        return result

    def add_outline_layer(self, outline_name="Outline"):
        """Add an outline layer named ``"Outline"`` if it is not present.

        Returns
        -------
        bool
            "True" if successful, ``False`` if failed.
        """
        return self.add_document_layer(name="Outline", layer_type="outline")

    # TODO: Update optional argument material into material_name and fillMaterial into fill_material_name

    def add_layer(
        self,
        layer_name,
        base_layer=None,
        method="add_on_top",
        layer_type="signal",
        material="copper",
        fillMaterial="FR4_epoxy",
        thickness="35um",
        etch_factor=None,
        is_negative=False,
        enable_roughness=False,
        elevation=None,
    ):
        """Insert a layer into stackup.

        Parameters
        ----------
        layer_name : str
            Name of the layer.
        base_layer : str, optional
            Name of the base layer.
        method : str, optional
            Where to insert the new layer. The default is ``"add_on_top"``. Options are ``"add_on_top"``,
            ``"add_on_bottom"``, ``"insert_above"``, ``"insert_below"``, ``"add_at_elevation"``,.
        layer_type : str, optional
            Type of layer. The default is ``"signal"``. Options are ``"signal"``, ``"dielectric"``, ``"conducting"``,
             ``"air_lines"``, ``"error"``, ``"symbol"``, ``"measure"``, ``"assembly"``, ``"silkscreen"``,
             ``"solder_mask"``, ``"solder_paste"``, ``"glue"``, ``"wirebond"``, ``"hfss_region"``, ``"user"``.
        material : str, optional
            Material of the layer.
        fillMaterial : str, optional
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
        :class:`pyedb.dotnet.edb_core.edb_data.layer_data.LayerEdbClass`
        """
        if layer_name in self.layers:
            logger.error("layer {} exists.".format(layer_name))
            return False
        if not material:
            material = "copper" if layer_type == "signal" else "FR4_epoxy"
        if not fillMaterial:
            fillMaterial = "FR4_epoxy"

        materials = self._pedb.materials
        if material not in materials:
            material_properties = self._pedb.materials.read_syslib_material(material)
            if material_properties:
                logger.info(f"Material {material} found in syslib. Adding it to aedb project.")
                materials.add_material(material, **material_properties)
            else:
                logger.warning(f"Material {material} not found. Check the library and retry.")

        if layer_type != "dielectric" and fillMaterial not in materials:
            material_properties = self._pedb.materials.read_syslib_material(fillMaterial)
            if material_properties:
                logger.info(f"Material {fillMaterial} found in syslib. Adding it to aedb project.")
                materials.add_material(fillMaterial, **material_properties)
            else:
                logger.warning(f"Material {fillMaterial} not found. Check the library and retry.")

        if layer_type in ["signal", "dielectric"]:
            new_layer = self._create_stackup_layer(layer_name, thickness, layer_type)
            new_layer.SetMaterial(material)
            if layer_type != "dielectric":
                new_layer.SetFillMaterial(fillMaterial)
            new_layer.SetNegative(is_negative)
            l1 = len(self.layers)
            if method == "add_at_elevation" and elevation:
                new_layer.SetLowerElevation(self._pedb.edb_value(elevation))
            self._set_layout_stackup(new_layer, method, base_layer)
            if len(self.layers) == l1:
                self._set_layout_stackup(new_layer, method, base_layer, method=2)
            if etch_factor:
                new_layer = self.layers[layer_name]
                new_layer.etch_factor = etch_factor
            if enable_roughness:
                new_layer = self.layers[layer_name]
                new_layer.roughness_enabled = True
        else:
            new_layer = self._create_nonstackup_layer(layer_name, layer_type)
            self._set_layout_stackup(new_layer, "non_stackup")
        self.refresh_layer_collection()
        return self.layers[layer_name]

    def remove_layer(self, name):
        """Remove a layer from stackup.

        Parameters
        ----------
        name : str
            Name of the layer to remove.

        Returns
        -------

        """
        new_layer_collection = self._pedb.edb_api.Cell.LayerCollection()
        for lyr in self._edb_layer_list:
            if not (lyr.GetName() == name):
                new_layer_collection.AddLayerBottom(lyr)

        self._pedb.layout.layer_collection = new_layer_collection
        self.refresh_layer_collection()
        return True

    def export(self, fpath, file_format="xml", include_material_with_layer=False):
        """Export stackup definition to a CSV or JSON file.

        Parameters
        ----------
        fpath : str
            File path to csv or json file.
        file_format : str, optional
            Format of the file to export. The default is ``"csv"``. Options are ``"csv"``, ``"xlsx"``,
            ``"json"``.
        include_material_with_layer : bool, optional.
            Whether to include the material definition inside layer ones. This parameter is only used
            when a JSON file is exported. The default is ``False``, which keeps the material definition
            section in the JSON file. If ``True``, the material definition is included inside the layer ones.

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
        """Export stackup definition to a CSV or JSON file.

        .. deprecated:: 0.6.61
           Use :func:`export` instead.

        Parameters
        ----------
        fpath : str
            File path to CSV or JSON file.
        file_format : str, optional
            Format of the file to export. The default is ``"csv"``. Options are ``"csv"``, ``"xlsx"``
            and ``"json"``.
        include_material_with_layer : bool, optional.
            Whether to include the material definition inside layer objects. This parameter is only used
            when a JSON file is exported. The default is ``False``, which keeps the material definition
            section in the JSON file. If ``True``, the material definition is included inside the layer ones.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edb = Edb()
        >>> edb.stackup.export_stackup("stackup.xml")
        """

        self._logger.warning("Method export_stackup is deprecated. Use .export.")
        return self.export(fpath, file_format=file_format, include_material_with_layer=include_material_with_layer)

    def _export_layer_stackup_to_csv_xlsx(self, fpath=None, file_format=None):
        if not pd:
            self._pedb.logger.error("Pandas is needed. Please, install it first.")
            return False

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

    def _export_layer_stackup_to_json(self, output_file=None, include_material_with_layer=False):
        if not include_material_with_layer:
            material_out = {}
            for material_name, material in self._pedb.materials.materials.items():
                material_out[material_name] = material.to_dict()
        layers_out = {}
        for k, v in self.layers.items():
            data = v._json_format()
            # FIXME: Update the API to avoid providing following information to our users
            del data["pedb"]
            del data["edb_object"]
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

    # TODO: This method might need some refactoring

    def _import_layer_stackup(self, input_file=None):
        if input_file:
            f = open(input_file)
            json_dict = json.load(f)  # pragma: no cover
            for k, v in json_dict.items():
                if k == "materials":
                    for material in v.values():
                        material_name = material["name"]
                        del material["name"]
                        if material_name not in self._pedb.materials:
                            self._pedb.materials.add_material(material_name, **material)
                        else:
                            self._pedb.materials.update_material(material_name, material)
                if k == "layers":
                    if len(list(v.values())) == len(list(self.layers.values())):
                        imported_layers_list = [l_dict["name"] for l_dict in list(v.values())]
                        layout_layer_list = list(self.layers.keys())
                        for layer_name in imported_layers_list:
                            layer_index = imported_layers_list.index(layer_name)
                            if layout_layer_list[layer_index] != layer_name:
                                self.layers[layout_layer_list[layer_index]].name = layer_name
                    prev_layer = None
                    for layer_name, layer in v.items():
                        if layer["name"] not in self.layers:
                            if not prev_layer:
                                self.add_layer(
                                    layer_name,
                                    method="add_on_top",
                                    layer_type=layer["type"],
                                    material=layer["material"],
                                    fillMaterial=layer["dielectric_fill"],
                                    thickness=layer["thickness"],
                                )
                                prev_layer = layer_name
                            else:
                                self.add_layer(
                                    layer_name,
                                    base_layer=layer_name,
                                    method="insert_below",
                                    layer_type=layer["type"],
                                    material=layer["material"],
                                    fillMaterial=layer["dielectric_fill"],
                                    thickness=layer["thickness"],
                                )
                                prev_layer = layer_name
                        if layer_name in self.layers:
                            self.layers[layer["name"]]._load_layer(layer)
            self.refresh_layer_collection()
            return True

    def stackup_limits(self, only_metals=False):
        """Retrieve stackup limits.

        .. deprecated:: 0.6.62
           Use :func:`Edb.stackup.limits` function instead.

        Parameters
        ----------
        only_metals : bool, optional
            Whether to retrieve only metals. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        warnings.warn("`stackup_limits` is deprecated. Use `limits` property instead.", DeprecationWarning)
        return self.limits(only_metals=only_metals)

    def limits(self, only_metals=False):
        """Retrieve stackup limits.

        Parameters
        ----------
        only_metals : bool, optional
            Whether to retrieve only metals. The default is ``False``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if only_metals:
            input_layers = self._pedb.edb_api.cell.layer_type_set.SignalLayerSet
        else:
            input_layers = self._pedb.edb_api.cell.layer_type_set.StackupLayerSet

        res, topl, topz, bottoml, bottomz = self._layer_collection.GetTopBottomStackupLayers(input_layers)
        return topl.GetName(), topz, bottoml.GetName(), bottomz

    def flip_design(self):
        """Flip the current design of a layout.

        Returns
        -------
        bool
            ``True`` when succeed ``False`` if not.

        Examples
        --------
        >>> edb = Edb(edbpath=targetfile,  edbversion="2021.2")
        >>> edb.stackup.flip_design()
        >>> edb.save()
        >>> edb.close_edb()
        """
        try:
            lc = self._layer_collection
            new_lc = self._pedb.edb_api.Cell.LayerCollection()
            lc_mode = lc.GetMode()
            new_lc.SetMode(lc_mode)
            max_elevation = 0.0
            for layer in lc.Layers(self._pedb.edb_api.cell.layer_type_set.StackupLayerSet):
                if "RadBox" not in layer.GetName():  # Ignore RadBox
                    lower_elevation = layer.Clone().GetLowerElevation() * 1.0e6
                    upper_elevation = layer.Clone().GetUpperElevation() * 1.0e6
                    max_elevation = max([max_elevation, lower_elevation, upper_elevation])

            non_stackup_layers = []
            for layer in lc.Layers(self._pedb.edb_api.cell.layer_type_set.AllLayerSet):
                cloned_layer = layer.Clone()
                if not cloned_layer.IsStackupLayer():
                    non_stackup_layers.append(cloned_layer)
                    continue
                if "RadBox" not in cloned_layer.GetName() and not cloned_layer.IsViaLayer():
                    upper_elevation = cloned_layer.GetUpperElevation() * 1.0e6
                    updated_lower_el = max_elevation - upper_elevation
                    val = self._edb_value("{}um".format(updated_lower_el))
                    cloned_layer.SetLowerElevation(val)
                    if (
                        cloned_layer.GetTopBottomAssociation()
                        == self._pedb.edb_api.Cell.TopBottomAssociation.TopAssociated
                    ):
                        cloned_layer.SetTopBottomAssociation(
                            self._pedb.edb_api.Cell.TopBottomAssociation.BottomAssociated
                        )
                    else:
                        cloned_layer.SetTopBottomAssociation(self._pedb.edb_api.Cell.TopBottomAssociation.TopAssociated)
                    new_lc.AddStackupLayerAtElevation(cloned_layer)

            vialayers = [
                lay
                for lay in lc.Layers(self._pedb.edb_api.cell.layer_type_set.StackupLayerSet)
                if lay.Clone().IsViaLayer()
            ]
            for layer in vialayers:
                cloned_via_layer = layer.Clone()
                upper_ref_name = cloned_via_layer.GetRefLayerName(True)
                lower_ref_name = cloned_via_layer.GetRefLayerName(False)
                upper_ref = [
                    lay
                    for lay in lc.Layers(self._pedb.edb_api.cell.layer_type_set.AllLayerSet)
                    if lay.GetName() == upper_ref_name
                ][0]
                lower_ref = [
                    lay
                    for lay in lc.Layers(self._pedb.edb_api.cell.layer_type_set.AllLayerSet)
                    if lay.GetName() == lower_ref_name
                ][0]
                cloned_via_layer.SetRefLayer(lower_ref, True)
                cloned_via_layer.SetRefLayer(upper_ref, False)
                ref_layer_in_flipped_stackup = [
                    lay
                    for lay in new_lc.Layers(self._pedb.edb_api.cell.layer_type_set.AllLayerSet)
                    if lay.GetName() == upper_ref_name
                ][0]
                via_layer_lower_elevation = (
                    ref_layer_in_flipped_stackup.GetLowerElevation() + ref_layer_in_flipped_stackup.GetThickness()
                )
                cloned_via_layer.SetLowerElevation(self._edb_value(via_layer_lower_elevation))
                new_lc.AddStackupLayerAtElevation(cloned_via_layer)

            layer_list = convert_py_list_to_net_list(non_stackup_layers)
            new_lc.AddLayers(layer_list)
            self._pedb.layout.layer_collection = new_lc

            for pyaedt_cmp in list(self._pedb.components.instances.values()):
                cmp = pyaedt_cmp.edbcomponent
                cmp_type = cmp.GetComponentType()
                cmp_prop = cmp.GetComponentProperty().Clone()
                try:
                    if (
                        cmp_prop.GetSolderBallProperty().GetPlacement()
                        == self._pedb.definition.SolderballPlacement.AbovePadstack
                    ):
                        sball_prop = cmp_prop.GetSolderBallProperty().Clone()
                        sball_prop.SetPlacement(self._pedb.definition.SolderballPlacement.BelowPadstack)
                        cmp_prop.SetSolderBallProperty(sball_prop)
                    elif (
                        cmp_prop.GetSolderBallProperty().GetPlacement()
                        == self._pedb.definition.SolderballPlacement.BelowPadstack
                    ):
                        sball_prop = cmp_prop.GetSolderBallProperty().Clone()
                        sball_prop.SetPlacement(self._pedb.definition.SolderballPlacement.AbovePadstack)
                        cmp_prop.SetSolderBallProperty(sball_prop)
                except:
                    pass
                if cmp_type == self._pedb.definition.ComponentType.IC:
                    die_prop = cmp_prop.GetDieProperty().Clone()
                    chip_orientation = die_prop.GetOrientation()
                    if chip_orientation == self._pedb.definition.DieOrientation.ChipDown:
                        die_prop.SetOrientation(self._pedb.definition.DieOrientation.ChipUp)
                        cmp_prop.SetDieProperty(die_prop)
                    else:
                        die_prop.SetOrientation(self._pedb.definition.DieOrientation.ChipDown)
                        cmp_prop.SetDieProperty(die_prop)
                cmp.SetComponentProperty(cmp_prop)

            lay_list = list(new_lc.Layers(self._pedb.edb_api.cell.layer_type_set.SignalLayerSet))
            for padstack in list(self._pedb.padstacks.instances.values()):
                start_layer_id = [lay.GetLayerId() for lay in list(lay_list) if lay.GetName() == padstack.start_layer]
                stop_layer_id = [lay.GetLayerId() for lay in list(lay_list) if lay.GetName() == padstack.stop_layer]
                layer_map = padstack._edb_padstackinstance.GetLayerMap()
                layer_map.SetMapping(stop_layer_id[0], start_layer_id[0])
                padstack._edb_padstackinstance.SetLayerMap(layer_map)
            self.refresh_layer_collection()
            return True
        except:
            return False

    def get_layout_thickness(self):
        """Return the layout thickness.

        Returns
        -------
        float
            The thickness value.
        """
        layers = list(self.layers.values())
        layers.sort(key=lambda lay: lay.lower_elevation)
        thickness = 0
        if layers:
            top_layer = layers[-1]
            bottom_layer = layers[0]
            thickness = abs(top_layer.upper_elevation - bottom_layer.lower_elevation)
        return round(thickness, 7)

    def _get_solder_height(self, layer_name):
        for _, val in self._pedb.components.instances.items():
            if val.solder_ball_height and val.placement_layer == layer_name:
                return val.solder_ball_height
        return 0

    def _remove_solder_pec(self, layer_name):
        for _, val in self._pedb.components.instances.items():
            if val.solder_ball_height and val.placement_layer == layer_name:
                comp_prop = val.component_property
                port_property = comp_prop.GetPortProperty().Clone()
                port_property.SetReferenceSizeAuto(False)
                port_property.SetReferenceSize(self._edb_value(0.0), self._edb_value(0.0))
                comp_prop.SetPortProperty(port_property)
                val.edbcomponent.SetComponentProperty(comp_prop)

    def adjust_solder_dielectrics(self):
        """Adjust the stack-up by adding or modifying dielectric layers that contains Solder Balls.
        This method identifies the solder-ball height and adjust the dielectric thickness on top (or bottom) to fit
        the thickness in order to merge another layout.

        Returns
        -------
        bool
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
        edb,
        angle=0.0,
        offset_x=0.0,
        offset_y=0.0,
        flipped_stackup=True,
        place_on_top=True,
    ):
        """Place current Cell into another cell using layer placement method.
        Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

        Parameters
        ----------
        edb : Edb
            Cell on which to place the current layout. If None the Cell will be applied on an empty new Cell.
        angle : double, optional
            The rotation angle applied on the design.
        offset_x : double, optional
            The x offset value.
        offset_y : double, optional
            The y offset value.
        flipped_stackup : bool, optional
            Either if the current layout is inverted.
            If `True` and place_on_top is `True` the stackup will be flipped before the merge.
        place_on_top : bool, optional
            Either if place the current layout on Top or Bottom of destination Layout.

        Returns
        -------
        bool
            ``True`` when succeed ``False`` if not.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")

        >>> hosting_cmp = edb1.components.get_component_by_name("U100")
        >>> mounted_cmp = edb2.components.get_component_by_name("BGA")

        >>> vector, rotation, solder_ball_height = edb1.components.get_component_placement_vector(
        ...                                                     mounted_component=mounted_cmp,
        ...                                                     hosting_component=hosting_cmp,
        ...                                                     mounted_component_pin1="A12",
        ...                                                     mounted_component_pin2="A14",
        ...                                                     hosting_component_pin1="A12",
        ...                                                     hosting_component_pin2="A14")
        >>> edb2.stackup.place_in_layout(edb1.active_cell, angle=0.0, offset_x=vector[0],
        ...                              offset_y=vector[1], flipped_stackup=False, place_on_top=True,
        ...                              )
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
        _angle = self._edb_value(angle * math.pi / 180.0)
        _offset_x = self._edb_value(offset_x)
        _offset_y = self._edb_value(offset_y)

        if edb_cell.GetName() not in self._pedb.cell_names:
            list_cells = self._pedb.copy_cells([edb_cell.api_object])
            edb_cell = list_cells[0]
        self._pedb.layout.cell.SetBlackBox(True)
        cell_inst2 = self._pedb.edb_api.cell.hierarchy.cell_instance.Create(
            edb_cell.GetLayout(), self._pedb.layout.cell.GetName(), self._pedb.active_layout
        )
        cell_trans = cell_inst2.GetTransform()
        cell_trans.SetRotationValue(_angle)
        cell_trans.SetXOffsetValue(_offset_x)
        cell_trans.SetYOffsetValue(_offset_y)
        cell_trans.SetMirror(flipped_stackup)
        cell_inst2.SetTransform(cell_trans)
        cell_inst2.SetSolveIndependentPreference(False)
        stackup_target = edb_cell.GetLayout().GetLayerCollection()

        if place_on_top:
            cell_inst2.SetPlacementLayer(
                list(stackup_target.Layers(self._pedb.edb_api.cell.layer_type_set.SignalLayerSet))[0]
            )
        else:
            cell_inst2.SetPlacementLayer(
                list(stackup_target.Layers(self._pedb.edb_api.cell.layer_type_set.SignalLayerSet))[-1]
            )
        self.refresh_layer_collection()
        return True

    def place_in_layout_3d_placement(
        self,
        edb,
        angle=0.0,
        offset_x=0.0,
        offset_y=0.0,
        flipped_stackup=True,
        place_on_top=True,
        solder_height=0,
    ):
        """Place current Cell into another cell using 3d placement method.
        Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

        Parameters
        ----------
        edb : Edb
            Cell on which to place the current layout. If None the Cell will be applied on an empty new Cell.
        angle : double, optional
            The rotation angle applied on the design.
        offset_x : double, optional
            The x offset value.
        offset_y : double, optional
            The y offset value.
        flipped_stackup : bool, optional
            Either if the current layout is inverted.
            If `True` and place_on_top is `True` the stackup will be flipped before the merge.
        place_on_top : bool, optional
            Either if place the current layout on Top or Bottom of destination Layout.
        solder_height : float, optional
            Solder Ball or Bumps eight.
            This value will be added to the elevation to align the two layouts.

        Returns
        -------
        bool
            ``True`` when succeed ``False`` if not.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")
        >>> hosting_cmp = edb1.components.get_component_by_name("U100")
        >>> mounted_cmp = edb2.components.get_component_by_name("BGA")
        >>> edb2.stackup.place_in_layout(edb1.active_cell, angle=0.0, offset_x="1mm",
        ...                                   offset_y="2mm", flipped_stackup=False, place_on_top=True,
        ...                                   )
        """
        _angle = angle * math.pi / 180.0

        if solder_height <= 0:
            if flipped_stackup and not place_on_top or (place_on_top and not flipped_stackup):
                minimum_elevation = None
                layers_from_the_bottom = sorted(self.signal_layers.values(), key=lambda lay: lay.upper_elevation)
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
                layers_from_the_top = sorted(self.signal_layers.values(), key=lambda lay: -lay.upper_elevation)
                for lay in layers_from_the_top:
                    if maximum_elevation is None:
                        maximum_elevation = lay.upper_elevation
                    elif lay.upper_elevation < maximum_elevation:
                        break
                    lay_solder_height = self._get_solder_height(lay.name)
                    solder_height = max(lay_solder_height, solder_height)
                    self._remove_solder_pec(lay.name)

        rotation = self._edb_value(0.0)
        if flipped_stackup:
            rotation = self._edb_value(math.pi)

        edb_cell = edb.active_cell
        _offset_x = self._edb_value(offset_x)
        _offset_y = self._edb_value(offset_y)

        if edb_cell.GetName() not in self._pedb.cell_names:
            list_cells = self._pedb.copy_cells(edb_cell.api_object)
            edb_cell = list_cells[0]
        self._pedb.layout.cell.SetBlackBox(True)
        cell_inst2 = self._pedb.edb_api.cell.hierarchy.cell_instance.Create(
            edb_cell.GetLayout(), self._pedb.layout.cell.GetName(), self._pedb.active_layout
        )

        stackup_target = self._pedb.edb_api.Cell.LayerCollection(edb_cell.GetLayout().GetLayerCollection())
        stackup_source = self._pedb.edb_api.Cell.LayerCollection(self._pedb.layout.layer_collection)

        if place_on_top:
            cell_inst2.SetPlacementLayer(
                list(stackup_target.Layers(self._pedb.edb_api.cell.layer_type_set.SignalLayerSet))[0]
            )
        else:
            cell_inst2.SetPlacementLayer(
                list(stackup_target.Layers(self._pedb.edb_api.cell.layer_type_set.SignalLayerSet))[-1]
            )
        cell_inst2.SetIs3DPlacement(True)
        sig_set = self._pedb.edb_api.cell.layer_type_set.SignalLayerSet
        res = stackup_target.GetTopBottomStackupLayers(sig_set)
        target_top_elevation = res[2]
        target_bottom_elevation = res[4]
        res_s = stackup_source.GetTopBottomStackupLayers(sig_set)
        source_stack_top_elevation = res_s[2]
        source_stack_bot_elevation = res_s[4]

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

        h_stackup = self._edb_value(elevation + solder_height)

        zero_data = self._edb_value(0.0)
        one_data = self._edb_value(1.0)
        point3d_t = self._pedb.point_3d(_offset_x, _offset_y, h_stackup)
        point_loc = self._pedb.point_3d(zero_data, zero_data, zero_data)
        point_from = self._pedb.point_3d(one_data, zero_data, zero_data)
        point_to = self._pedb.point_3d(math.cos(_angle), -1 * math.sin(_angle), zero_data)
        cell_inst2.Set3DTransformation(point_loc, point_from, point_to, rotation, point3d_t)
        self.refresh_layer_collection()
        return True

    def place_instance(
        self,
        component_edb,
        angle=0.0,
        offset_x=0.0,
        offset_y=0.0,
        offset_z=0.0,
        flipped_stackup=True,
        place_on_top=True,
        solder_height=0,
    ):
        """Place current Cell into another cell using 3d placement method.
        Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

        Parameters
        ----------
        component_edb : Edb
            Cell to place in the current layout.
        angle : double, optional
            The rotation angle applied on the design.
        offset_x : double, optional
            The x offset value.
            The default value is ``0.0``.
        offset_y : double, optional
            The y offset value.
            The default value is ``0.0``.
        offset_z : double, optional
            The z offset value. (i.e. elevation offset for placement relative to the top layer conductor).
            The default value is ``0.0``, which places the cell layout on top of the top conductor
            layer of the target EDB.
        flipped_stackup : bool, optional
            Either if the current layout is inverted.
            If `True` and place_on_top is `True` the stackup will be flipped before the merge.
        place_on_top : bool, optional
            Either if place the component_edb layout on Top or Bottom of destination Layout.
        solder_height : float, optional
            Solder Ball or Bumps eight.
            This value will be added to the elevation to align the two layouts.

        Returns
        -------
        bool
            ``True`` when succeed ``False`` if not.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")
        >>> hosting_cmp = edb1.components.get_component_by_name("U100")
        >>> mounted_cmp = edb2.components.get_component_by_name("BGA")
        >>> edb1.stackup.place_instance(edb2, angle=0.0, offset_x="1mm",
        ...                                   offset_y="2mm", flipped_stackup=False, place_on_top=True,
        ...                                   )
        """
        _angle = angle * math.pi / 180.0

        if solder_height <= 0:
            if flipped_stackup and not place_on_top or (place_on_top and not flipped_stackup):
                minimum_elevation = None
                layers_from_the_bottom = sorted(
                    component_edb.stackup.signal_layers.values(), key=lambda lay: lay.upper_elevation
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
                    component_edb.stackup.signal_layers.values(), key=lambda lay: -lay.upper_elevation
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
        _offset_x = self._edb_value(offset_x)
        _offset_y = self._edb_value(offset_y)

        if edb_cell.GetName() not in self._pedb.cell_names:
            list_cells = self._pedb.copy_cells(edb_cell.api_object)
            edb_cell = list_cells[0]
        for cell in list(self._pedb.active_db.CircuitCells):
            if cell.GetName() == edb_cell.GetName():
                edb_cell = cell
        # Keep Cell Independent
        edb_cell.SetBlackBox(True)
        rotation = self._edb_value(0.0)
        if flipped_stackup:
            rotation = self._edb_value(math.pi)

        _offset_x = self._edb_value(offset_x)
        _offset_y = self._edb_value(offset_y)

        instance_name = generate_unique_name(edb_cell.GetName(), n=2)

        cell_inst2 = self._pedb.edb_api.cell.hierarchy.cell_instance.Create(
            self._pedb.active_layout, instance_name, edb_cell.GetLayout()
        )

        stackup_source = self._pedb.edb_api.Cell.LayerCollection(edb_cell.GetLayout().GetLayerCollection())
        stackup_target = self._pedb.edb_api.Cell.LayerCollection(self._pedb.layout.layer_collection)

        if place_on_top:
            cell_inst2.SetPlacementLayer(
                list(stackup_target.Layers(self._pedb.edb_api.cell.layer_type_set.SignalLayerSet))[0]
            )
        else:
            cell_inst2.SetPlacementLayer(
                list(stackup_target.Layers(self._pedb.edb_api.cell.layer_type_set.SignalLayerSet))[-1]
            )
        cell_inst2.SetIs3DPlacement(True)
        sig_set = self._pedb.edb_api.cell.layer_type_set.SignalLayerSet
        res = stackup_target.GetTopBottomStackupLayers(sig_set)
        target_top_elevation = res[2]
        target_bottom_elevation = res[4]
        res_s = stackup_source.GetTopBottomStackupLayers(sig_set)
        source_stack_top_elevation = res_s[2]
        source_stack_bot_elevation = res_s[4]

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

        h_stackup = self._edb_value(elevation + solder_height)

        zero_data = self._edb_value(0.0)
        one_data = self._edb_value(1.0)
        point3d_t = self._pedb.point_3d(_offset_x, _offset_y, h_stackup)
        point_loc = self._pedb.point_3d(zero_data, zero_data, zero_data)
        point_from = self._pedb.point_3d(one_data, zero_data, zero_data)
        point_to = self._pedb.point_3d(math.cos(_angle), -1 * math.sin(_angle), zero_data)
        cell_inst2.Set3DTransformation(point_loc, point_from, point_to, rotation, point3d_t)
        self.refresh_layer_collection()
        return cell_inst2

    def place_a3dcomp_3d_placement(
        self,
        a3dcomp_path,
        angle=0.0,
        offset_x=0.0,
        offset_y=0.0,
        offset_z=0.0,
        place_on_top=True,
    ):
        """Place a 3D Component into current layout.
         3D Component ports are not visible via EDB. They will be visible after the EDB has been opened in Ansys
         Electronics Desktop as a project.

        Parameters
        ----------
        a3dcomp_path : str
            Path to the 3D Component file (\\*.a3dcomp) to place.
        angle : double, optional
            Clockwise rotation angle applied to the a3dcomp.
        offset_x : double, optional
            The x offset value.
            The default value is ``0.0``.
        offset_y : double, optional
            The y offset value.
            The default value is ``0.0``.
        offset_z : double, optional
            The z offset value. (i.e. elevation)
            The default value is ``0.0``.
        place_on_top : bool, optional
            Whether to place the 3D Component on the top or the bottom of this layout.
            If ``False`` then the 3D Component will also be flipped over around its X axis.

        Returns
        -------
        bool
            ``True`` if successful and ``False`` if not.

        Examples
        --------
        >>> edb1 = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> a3dcomp_path = "connector.a3dcomp"
        >>> edb1.stackup.place_a3dcomp_3d_placement(a3dcomp_path, angle=0.0, offset_x="1mm",
        ...                                   offset_y="2mm", flipped_stackup=False, place_on_top=True,
        ...                                   )
        """
        zero_data = self._edb_value(0.0)
        one_data = self._edb_value(1.0)
        local_origin = self._pedb.point_3d(0.0, 0.0, 0.0)
        rotation_axis_from = self._pedb.point_3d(1.0, 0.0, 0.0)
        _angle = angle * math.pi / 180.0
        rotation_axis_to = self._pedb.point_3d(math.cos(_angle), -1 * math.sin(_angle), 0.0)

        stackup_target = self._pedb.edb_api.cell._cell.LayerCollection(self._pedb.layout.layer_collection)
        sig_set = self._pedb.edb_api.cell.layer_type_set.SignalLayerSet
        res = stackup_target.GetTopBottomStackupLayers(sig_set)
        target_top_elevation = res[2]
        target_bottom_elevation = res[4]
        flip_angle = self._edb_value("0deg")
        if place_on_top:
            elevation = target_top_elevation + offset_z
        else:
            flip_angle = self._edb_value("180deg")
            elevation = target_bottom_elevation - offset_z
        h_stackup = self._edb_value(elevation)
        location = self._pedb.point_3d(offset_x, offset_y, h_stackup)

        mcad_model = self._pedb.edb_api.McadModel.Create3DComp(self._pedb.active_layout, a3dcomp_path)
        if mcad_model.IsNull():  # pragma: no cover
            logger.error("Failed to create MCAD model from a3dcomp")
            return False

        cell_instance = mcad_model.GetCellInstance()
        if cell_instance.IsNull():  # pragma: no cover
            logger.error("Cell instance of a3dcomp is null")
            return False

        if not cell_instance.SetIs3DPlacement(True):  # pragma: no cover
            logger.error("Failed to set 3D placement on a3dcomp cell instance")
            return False

        if not cell_instance.Set3DTransformation(
            local_origin, rotation_axis_from, rotation_axis_to, flip_angle, location
        ):  # pragma: no cover
            logger.error("Failed to set 3D transform on a3dcomp cell instance")
            return False
        self.refresh_layer_collection()
        return True

    def residual_copper_area_per_layer(self):
        """Report residual copper area per layer in percentage.

        Returns
        -------
        dict
            Copper area per layer.

        Examples
        --------
        >>> edb = Edb(edbpath=targetfile1,  edbversion="2021.2")
        >>> edb.stackup.residual_copper_area_per_layer()
        """
        temp_data = {name: 0 for name, _ in self.signal_layers.items()}
        outline_area = 0
        for i in self._pedb.modeler.primitives:
            layer_name = i.GetLayer().GetName()
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

    # TODO: This method might need some refactoring

    def _import_dict(self, json_dict, rename=False):
        """Import stackup from a dictionary."""
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

            new_layer.color = default_layer["color"]
            new_layer.etch_factor = default_layer["etch_factor"]

            new_layer.roughness_enabled = default_layer["roughness_enabled"]
            new_layer.top_hallhuray_nodule_radius = default_layer["top_hallhuray_nodule_radius"]
            new_layer.top_hallhuray_surface_ratio = default_layer["top_hallhuray_surface_ratio"]
            new_layer.bottom_hallhuray_nodule_radius = default_layer["bottom_hallhuray_nodule_radius"]
            new_layer.bottom_hallhuray_surface_ratio = default_layer["bottom_hallhuray_surface_ratio"]
            new_layer.side_hallhuray_nodule_radius = default_layer["side_hallhuray_nodule_radius"]
            new_layer.side_hallhuray_surface_ratio = default_layer["side_hallhuray_surface_ratio"]

        return True

    def _import_json(self, file_path, rename=False):
        """Import stackup from a json file."""
        if file_path:
            f = open(file_path)
            json_dict = json.load(f)  # pragma: no cover
            return self._import_dict(json_dict, rename)

    def _import_csv(self, file_path):
        """Import stackup definition from a CSV file.

        Parameters
        ----------
        file_path : str
            File path to the CSV file.
        """
        if not pd:
            self._pedb.logger.error("Pandas is needed. You must install it first.")
            return False

        df = pd.read_csv(file_path, index_col=0)

        for name in self.layers.keys():  # pragma: no cover
            if not name in df.index:
                logger.error("{} doesn't exist in csv".format(name))
                return False

        for name, layer_info in df.iterrows():
            layer_type = layer_info.Type
            if name in self.layers:
                layer = self.layers[name]
                layer.type = layer_type
            else:
                layer = self.add_layer(name, layer_type=layer_type, material="copper", fillMaterial="copper")

            layer.material = layer_info.Material
            layer.thickness = layer_info.Thickness
            if not str(layer_info.Dielectric_Fill) == "nan":
                layer.dielectric_fill = layer_info.Dielectric_Fill

        lc_new = self._pedb.edb_api.Cell.LayerCollection()
        for name, _ in df.iterrows():
            layer = self.layers[name]
            lc_new.AddLayerBottom(layer._edb_layer)

        for name, layer in self.non_stackup_layers.items():
            lc_new.AddLayerBottom(layer._edb_layer)

        self._pedb.layout.layer_collection = lc_new
        self.refresh_layer_collection()
        return True

    def _set(self, layers=None, materials=None, roughness=None, non_stackup_layers=None):
        """Update stackup information.

        Parameters
        ----------
        layers: dict
            Dictionary containing layer information.
        materials: dict
            Dictionary containing material information.
        roughness: dict
            Dictionary containing roughness information.

        Returns
        -------

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

    def _get(self):
        """Get stackup information from layout.

        Returns:
        tuple: (dict, dict, dict)
            layers, materials, roughness_models
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
                if model.ToString().endswith("GroissRoughnessModel"):
                    roughness_models[name]["GroissSurfaceRoughness"] = {"Roughness": model.get_Roughness().ToDouble()}
                else:
                    roughness_models[name]["HuraySurfaceRoughness"] = {
                        "HallHuraySurfaceRatio": model.get_NoduleRadius().ToDouble(),
                        "NoduleRadius": model.get_SurfaceRatio().ToDouble(),
                    }
                model = val.get_roughness_model("bottom")
                if model.ToString().endswith("GroissRoughnessModel"):
                    roughness_models[name]["GroissBottomSurfaceRoughness"] = {
                        "Roughness": model.get_Roughness().ToDouble()
                    }
                else:
                    roughness_models[name]["HurayBottomSurfaceRoughness"] = {
                        "HallHuraySurfaceRatio": model.get_NoduleRadius().ToDouble(),
                        "NoduleRadius": model.get_SurfaceRatio().ToDouble(),
                    }
                model = val.get_roughness_model("side")
                if model.ToString().endswith("GroissRoughnessModel"):
                    roughness_models[name]["GroissSideSurfaceRoughness"] = {
                        "Roughness": model.get_Roughness().ToDouble()
                    }
                else:
                    roughness_models[name]["HuraySideSurfaceRoughness"] = {
                        "HallHuraySurfaceRatio": model.get_NoduleRadius().ToDouble(),
                        "NoduleRadius": model.get_SurfaceRatio().ToDouble(),
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

    def _add_materials_from_dictionary(self, material_dict):
        materials = self.self._pedb.materials.materials
        for name, material_properties in material_dict.items():
            if not name in materials:
                if "Conductivity" in material_properties:
                    materials.add_conductor_material(name, material_properties["Conductivity"])
                else:
                    materials.add_dielectric_material(
                        name,
                        material_properties["Permittivity"],
                        material_properties["DielectricLossTangent"],
                    )
            else:
                material = materials[name]
                if "Conductivity" in material_properties:
                    material.conductivity = material_properties["Conductivity"]
                else:
                    material.permittivity = material_properties["Permittivity"]
                    material.loss_tanget = material_properties["DielectricLossTangent"]
        return True

    def _import_xml(self, file_path, rename=False):
        """Read external xml file and convert into json file.
        You can use xml file to import layer stackup but using json file is recommended.
        see :class:`pyedb.dotnet.edb_core.edb_data.simulation_configuration.SimulationConfiguration´ class to
        generate files`.

        Parameters
        ----------
        file_path: str
            Path to external XML file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if not colors:
            self._pedb.logger.error("Matplotlib is needed. Please, install it first.")
            return False
        tree = ET.parse(file_path)
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

    def _export_xml(self, file_path):
        """Export stackup information to an external XMLfile.

        Parameters
        ----------
        file_path: str
            Path to external XML file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
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

    def load(self, file_path, rename=False):
        """Import stackup from a file. The file format can be XML, CSV, or JSON. Valid control file must
        have the same number of signal layers. Signals layers can be renamed. Dielectric layers can be
        added and deleted.


        Parameters
        ----------
        file_path : str, dict
            Path to stackup file or dict with stackup details.
        rename : bool
            If rename is ``False`` then layer in layout not found in the stackup file are deleted.
            Otherwise, if the number of layer in the stackup file equals the number of stackup layer
            in the layout, layers are renamed according the file.
            Note that layer order matters, and has to be writtent from top to bottom layer in the file.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

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
        save_plot=None,
        size=(2000, 1500),
        plot_definitions=None,
        first_layer=None,
        last_layer=None,
        scale_elevation=True,
        show=True,
    ):
        """Plot current stackup and, optionally, overlap padstack definitions.
        Plot supports only 'Laminate' and 'Overlapping' stackup types.

        Parameters
        ----------
        save_plot : str, optional
            If a path is specified the plot will be saved in this location.
            If ``save_plot`` is provided, the ``show`` parameter is ignored.
        size : tuple, optional
            Image size in pixel (width, height). Default value is ``(2000, 1500)``
        plot_definitions : str, list, optional
            List of padstack definitions to plot on the stackup.
            It is supported only for Laminate mode.
        first_layer : str or :class:`pyedb.dotnet.edb_core.edb_data.layer_data.LayerEdbClass`
            First layer to plot from the bottom. Default is `None` to start plotting from bottom.
        last_layer : str or :class:`pyedb.dotnet.edb_core.edb_data.layer_data.LayerEdbClass`
            Last layer to plot from the bottom. Default is `None` to plot up to top layer.
        scale_elevation : bool, optional
            The real layer thickness is scaled so that max_thickness = 3 * min_thickness.
            Default is `True`.
        show : bool, optional
            Whether to show the plot or not. Default is `True`.

        Returns
        -------
        :class:`matplotlib.plt`
        """

        from pyedb.generic.constants import CSS4_COLORS
        from pyedb.generic.plot import plot_matplotlib

        layer_names = list(self.layers.keys())
        if first_layer is None or first_layer not in layer_names:
            bottom_layer = layer_names[-1]
        elif isinstance(first_layer, str):
            bottom_layer = first_layer
        elif isinstance(first_layer, LayerEdbClass):
            bottom_layer = first_layer.name
        else:
            raise AttributeError("first_layer must be str or class `dotnet.edb_core.edb_data.layer_data.LayerEdbClass`")
        if last_layer is None or last_layer not in layer_names:
            top_layer = layer_names[0]
        elif isinstance(last_layer, str):
            top_layer = last_layer
        elif isinstance(last_layer, LayerEdbClass):
            top_layer = last_layer.name
        else:
            raise AttributeError("last_layer must be str or class `dotnet.edb_core.edb_data.layer_data.LayerEdbClass`")

        stackup_mode = self.mode
        if stackup_mode not in ["Laminate", "Overlapping"]:
            raise AttributeError("stackup plot supports only 'Laminate' and 'Overlapping' stackup types.")

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
        if stackup_mode == "Overlapping":
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

            if stackup_mode == "Laminate":
                l0 = layers_data[0]
                compressed_layers_data = [[l0[0], l0[1], _compress_t(l0[3]), _compress_t(l0[3])]]  # the first row
                lp = compressed_layers_data[0]
                for li in layers_data[1:]:  # the other rows
                    ct = _compress_t(li[3])
                    compressed_layers_data.append([li[0], lp[2], lp[2] + ct, ct])
                    lp = compressed_layers_data[-1]
                layers_data = compressed_layers_data

            elif stackup_mode == "Overlapping":
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
        if stackup_mode == "Laminate":
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

        elif stackup_mode == "Overlapping":
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
                    if r != 0:  # and dname == r[0].name:
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
        if stackup_mode == "Laminate":
            y_min = layers_data[0][1]
            y_max = layers_data[-1][2]
        elif stackup_mode == "Overlapping":
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
            if stackup_mode == "Overlapping":
                self._logger.warning("Plot of padstacks are supported only for Laminate mode.")

            max_plots = 10

            if not isinstance(plot_definitions, list):
                plot_definitions = [plot_definitions]
            color_index = 0
            color_keys = list(CSS4_COLORS.keys())
            delta = 1 / (max_plots + 1)  # padstack spacing in plot coordinates
            x_start = delta

            # find the max padstack size to calculate the scaling factor
            max_padstak_size = 0
            for definition in plot_definitions:
                if isinstance(definition, str):
                    definition = self._pedb.padstacks.definitions[definition]
                for layer, defs in definition.pad_by_layer.items():
                    pad_shape = defs.geometry_type
                    params = defs.parameters_values
                    if pad_shape in [1, 2, 6]:
                        pad_size = params[0]
                    elif pad_shape in [3, 4, 5]:
                        pad_size = max(params[0], params[1])
                    else:
                        pad_size = 1e-4
                    max_padstak_size = max(pad_size, max_padstak_size)
                if definition.hole_properties:
                    hole_d = definition.hole_properties[0]
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

                via_start_layer = definition.via_start_layer
                via_stop_layer = definition.via_stop_layer

                if stackup_mode == "Overlapping":
                    # here search the column using the first and last layer. Pick the column with max index.
                    pass

                for layer, defs in definition.pad_by_layer.items():
                    pad_shape = defs.geometry_type
                    params = defs.parameters_values
                    if pad_shape in [1, 2, 6]:
                        pad_size = params[0]
                    elif pad_shape in [3, 4, 5]:
                        pad_size = max(params[0], params[1])
                    else:
                        pad_size = 1e-4

                    if stackup_mode == "Laminate":
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
                    elif stackup_mode == "Overlapping":
                        # here evaluate the x based on the column evaluated before and the pad size
                        pass

                    min_le = min(lower_elevation, min_le)
                    max_ue = max(upper_elevation, max_ue)
                if definition.hole_properties:
                    # create patch for the hole
                    hole_radius = definition.hole_properties[0] / 2 * scaling_f_pad
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
