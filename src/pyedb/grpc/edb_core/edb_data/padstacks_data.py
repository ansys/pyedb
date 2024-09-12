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

from collections import OrderedDict
import math
import re
import warnings

from pyedb.dotnet.clr_module import String
from pyedb.dotnet.edb_core.cell.primitive.primitive import Primitive
from pyedb.dotnet.edb_core.dotnet.database import PolygonDataDotNet
from pyedb.dotnet.edb_core.edb_data.edbvalue import EdbValue
from pyedb.dotnet.edb_core.general import PadGeometryTpe, convert_py_list_to_net_list
from pyedb.modeler.geometry_operators import GeometryOperators


class EDBPadProperties(object):
    """Manages EDB functionalities for pad properties.

    Parameters
    ----------
    edb_padstack :

    layer_name : str
        Name of the layer.
    pad_type :
        Type of the pad.
    pedbpadstack : str
        Inherited AEDT object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_pad_properties = edb.padstacks.definitions["MyPad"].pad_by_layer["TOP"]
    """

    def __init__(self, edb_padstack, layer_name, pad_type, p_edb_padstack):
        self._edb_object = edb_padstack
        self._pedbpadstack = p_edb_padstack
        self.layer_name = layer_name
        self.pad_type = pad_type

        self._edb_padstack = self._edb_object

    @property
    def _padstack_methods(self):
        return self._pedbpadstack._padstack_methods

    @property
    def _stackup_layers(self):
        return self._pedbpadstack._stackup_layers

    @property
    def _edb(self):
        return self._pedbpadstack._edb

    def _get_edb_value(self, value):
        return self._pedbpadstack._get_edb_value(value)

    @property
    def _pad_parameter_value(self):
        pad_params = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_params

    @property
    def geometry_type(self):
        """Geometry type.

        Returns
        -------
        int
            Type of the geometry.
        """

        padparams = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return int(padparams[1])

    @geometry_type.setter
    def geometry_type(self, geom_type):
        """0, NoGeometry. 1, Circle. 2 Square. 3, Rectangle. 4, Oval. 5, Bullet. 6, N-sided polygon. 7, Polygonal
        shape.8, Round gap with 45 degree thermal ties. 9, Round gap with 90 degree thermal ties.10, Square gap
        with 45 degree thermal ties. 11, Square gap with 90 degree thermal ties.
        """
        val = self._get_edb_value(0)
        params = []
        if geom_type == 0:
            pass
        elif geom_type == 1:
            params = [val]
        elif geom_type == 2:
            params = [val]
        elif geom_type == 3:
            params = [val, val]
        elif geom_type == 4:
            params = [val, val, val]
        elif geom_type == 5:
            params = [val, val, val]
        self._update_pad_parameters_parameters(geom_type=geom_type, params=params)

    @property
    def shape(self):
        """Get the shape of the pad."""
        return self._pad_parameter_value[1].ToString()

    @shape.setter
    def shape(self, value):
        self._update_pad_parameters_parameters(geom_type=PadGeometryTpe[value].value)

    @property
    def parameters_values(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        return [i.tofloat for i in self.parameters.values()]

    @property
    def parameters_values_string(self):
        """Parameters value in string format."""
        return [i.tostring for i in self.parameters.values()]

    @property
    def polygon_data(self):
        """Parameters.

        Returns
        -------
        list
            List of parameters.
        """
        try:
            pad_values = self._edb_padstack.GetData().GetPolygonalPadParameters(
                self.layer_name, self.int_to_pad_type(self.pad_type)
            )
            if pad_values[1]:
                return PolygonDataDotNet(self._edb._app, pad_values[1])
            else:
                return
        except:
            return

    @property
    def parameters(self):
        """Get parameters.

        Returns
        -------
        dict
        """
        value = list(self._pad_parameter_value[2])
        if self.shape == PadGeometryTpe.Circle.name:
            return OrderedDict({"Diameter": EdbValue(value[0])})
        elif self.shape == PadGeometryTpe.Square.name:
            return OrderedDict({"Size": EdbValue(value[0])})
        elif self.shape == PadGeometryTpe.Rectangle.name:
            return OrderedDict({"XSize": EdbValue(value[0]), "YSize": EdbValue(value[1])})
        elif self.shape in [PadGeometryTpe.Oval.name, PadGeometryTpe.Bullet.name]:
            return OrderedDict(
                {"XSize": EdbValue(value[0]), "YSize": EdbValue(value[1]), "CornerRadius": EdbValue(value[2])}
            )
        elif self.shape == PadGeometryTpe.NSidedPolygon.name:
            return OrderedDict({"Size": EdbValue(value[0]), "NumSides": EdbValue(value[1])})
        elif self.shape in [PadGeometryTpe.Round45.name, PadGeometryTpe.Round90.name]:  # pragma: no cover
            return OrderedDict(
                {"Inner": EdbValue(value[0]), "ChannelWidth": EdbValue(value[1]), "IsolationGap": EdbValue(value[2])}
            )
        else:
            return OrderedDict()  # pragma: no cover

    @parameters.setter
    def parameters(self, value):
        """Set parameters.
        "Circle", {"Diameter": "0.5mm"}

        Parameters
        ----------
        value : dict
            Pad parameters in dictionary.
        >>> pad = Edb.padstacks["PlanarEMVia"]["TOP"]
        >>> pad.shape = "Circle"
        >>> pad.pad_parameters{"Diameter": "0.5mm"}
        >>> pad.shape = "Bullet"
        >>> pad.pad_parameters{"XSize": "0.5mm", "YSize": "0.5mm"}
        """

        if isinstance(value, dict):
            value = {k: v.tostring if isinstance(v, EdbValue) else v for k, v in value.items()}
            if self.shape == PadGeometryTpe.Circle.name:
                params = [self._get_edb_value(value["Diameter"])]
            elif self.shape == PadGeometryTpe.Square.name:
                params = [self._get_edb_value(value["Size"])]
            elif self.shape == PadGeometryTpe.Rectangle.name:
                params = [self._get_edb_value(value["XSize"]), self._get_edb_value(value["YSize"])]
            elif self.shape == [PadGeometryTpe.Oval.name, PadGeometryTpe.Bullet.name]:
                params = [
                    self._get_edb_value(value["XSize"]),
                    self._get_edb_value(value["YSize"]),
                    self._get_edb_value(value["CornerRadius"]),
                ]
            elif self.shape in [PadGeometryTpe.Round45.name, PadGeometryTpe.Round90.name]:  # pragma: no cover
                params = [
                    self._get_edb_value(value["Inner"]),
                    self._get_edb_value(value["ChannelWidth"]),
                    self._get_edb_value(value["IsolationGap"]),
                ]
            else:  # pragma: no cover
                params = None
        elif isinstance(value, list):
            params = [self._get_edb_value(i) for i in value]
        else:
            params = [self._get_edb_value(value)]
        self._update_pad_parameters_parameters(params=params)

    @property
    def offset_x(self):
        """Offset for the X axis.

        Returns
        -------
        str
            Offset for the X axis.
        """

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_values[3].ToString()

    @offset_x.setter
    def offset_x(self, offset_value):
        self._update_pad_parameters_parameters(offsetx=offset_value)

    @property
    def offset_y(self):
        """Offset for the Y axis.

        Returns
        -------
        str
            Offset for the Y axis.
        """

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_values[4].ToString()

    @offset_y.setter
    def offset_y(self, offset_value):
        self._update_pad_parameters_parameters(offsety=offset_value)

    @property
    def rotation(self):
        """Rotation.

        Returns
        -------
        str
            Value for the rotation.
        """

        pad_values = self._edb_padstack.GetData().GetPadParametersValue(
            self.layer_name, self.int_to_pad_type(self.pad_type)
        )
        return pad_values[5].ToString()

    @rotation.setter
    def rotation(self, rotation_value):
        self._update_pad_parameters_parameters(rotation=rotation_value)

    def int_to_pad_type(self, val=0):
        """Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadType enumerator value.
        """
        return self._pedbpadstack._ppadstack.int_to_pad_type(val)

    def int_to_geometry_type(self, val=0):
        """Convert an integer to an EDB.PadGeometryType.

        Parameters
        ----------
        val : int

        Returns
        -------
        object
            EDB.PadGeometryType enumerator value.
        """
        return self._pedbpadstack._ppadstack.int_to_geometry_type(val)

    def _update_pad_parameters_parameters(
        self,
        layer_name=None,
        pad_type=None,
        geom_type=None,
        params=None,
        offsetx=None,
        offsety=None,
        rotation=None,
    ):
        """Update padstack parameters.

        Parameters
        ----------
        layer_name : str, optional
            Name of the layer. The default is ``None``.
        pad_type : int, optional
            Type of the pad. The default is ``None``.
        geom_type : int, optional
            Type of the geometry. The default is ``None``.
        params : list, optional
            The default is ``None``.
        offsetx : float, optional
            Offset value for the X axis. The default is ``None``.
        offsety :  float, optional
            Offset value for the Y axis. The default is ``None``.
        rotation : float, optional
            Rotation value. The default is ``None``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        originalPadstackDefinitionData = self._edb_padstack.GetData()
        newPadstackDefinitionData = self._edb.definition.PadstackDefData(originalPadstackDefinitionData)
        if not pad_type:
            pad_type = self.pad_type
        if not geom_type:
            geom_type = self.geometry_type
        if params:
            params = convert_py_list_to_net_list(params)
        else:
            params = self._pad_parameter_value[2]
        if not offsetx:
            offsetx = self.offset_x
        if not offsety:
            offsety = self.offset_y
        if not rotation:
            rotation = self.rotation
        if not layer_name:
            layer_name = self.layer_name

        newPadstackDefinitionData.SetPadParameters(
            layer_name,
            self.int_to_pad_type(pad_type),
            self.int_to_geometry_type(geom_type),
            params,
            self._get_edb_value(offsetx),
            self._get_edb_value(offsety),
            self._get_edb_value(rotation),
        )
        self._edb_padstack.SetData(newPadstackDefinitionData)


class EDBPadstackInstance(Primitive):
    """Manages EDB functionalities for a padstack.

    Parameters
    ----------
    edb_padstackinstance :

    _pedb :
        Inherited AEDT object.

    Examples
    --------
    >>> from pyedb import Edb
    >>> edb = Edb(myedb, edbversion="2021.2")
    >>> edb_padstack_instance = edb.padstacks.instances[0]
    """

    def __init__(self, edb_padstackinstance, _pedb):
        super().__init__(_pedb, edb_padstackinstance)
        self._edb_padstackinstance = self._edb_object
        self._bounding_box = []
        self._object_instance = None
        self._position = []
        self._pdef = None

    def get_terminal(self, name=None, create_new_terminal=False):
        """Get PadstackInstanceTerminal object.

        Parameters
        ----------
        name : str, optional
            Name of the terminal. Only applicable when create_new_terminal is True.
        create_new_terminal : bool, optional
            Whether to create a new terminal.

        Returns
        -------
        :class:`pyedb.dotnet.edb_core.edb_data.terminals`
        """
        warnings.warn("Use new property :func:`terminal` instead.", DeprecationWarning)
        if create_new_terminal:
            term = self._create_terminal(name)
        else:
            from pyedb.dotnet.edb_core.cell.terminal.padstack_instance_terminal import (
                PadstackInstanceTerminal,
            )

            term = PadstackInstanceTerminal(self._pedb, self._edb_object.GetPadstackInstanceTerminal())
        if not term.is_null:
            return term

    @property
    def terminal(self):
        """Terminal."""
        from pyedb.dotnet.edb_core.cell.terminal.padstack_instance_terminal import (
            PadstackInstanceTerminal,
        )

        term = PadstackInstanceTerminal(self._pedb, self._edb_object.GetPadstackInstanceTerminal())
        return term if not term.is_null else None

    def _create_terminal(self, name=None):
        """Create a padstack instance terminal"""
        warnings.warn("`_create_terminal` is deprecated. Use `create_terminal` instead.", DeprecationWarning)
        return self.create_terminal(name)

    def create_terminal(self, name=None):
        """Create a padstack instance terminal"""
        from pyedb.dotnet.edb_core.cell.terminal.padstack_instance_terminal import (
            PadstackInstanceTerminal,
        )

        term = PadstackInstanceTerminal(self._pedb, self._edb_object.GetPadstackInstanceTerminal())
        return term.create(self, name)

    def create_coax_port(self, name=None, radial_extent_factor=0):
        """Create a coax port."""
        port = self.create_port(name)
        port.radial_extent_factor = radial_extent_factor
        return port

    def create_port(self, name=None, reference=None, is_circuit_port=False):
        """Create a port on the padstack.

        Parameters
        ----------
        name : str, optional
            Name of the port. The default is ``None``, in which case a name is automatically assigned.
        reference : class:`pyedb.dotnet.edb_core.edb_data.nets_data.EDBNetsData`, \
            class:`pyedb.dotnet.edb_core.edb_data.padstacks_data.EDBPadstackInstance`, \
            class:`pyedb.dotnet.edb_core.edb_data.sources.PinGroup`, optional
            Negative terminal of the port.
        is_circuit_port : bool, optional
            Whether it is a circuit port.
        """
        terminal = self.create_terminal(name)
        if reference:
            ref_terminal = reference.create_terminal(terminal.name + "_ref")
            if reference._edb_object.ToString() == "PinGroup":
                is_circuit_port = True
        else:
            ref_terminal = None

        return self._pedb.create_port(terminal, ref_terminal, is_circuit_port)

    @property
    def _em_properties(self):
        """Get EM properties."""
        default = (
            r"$begin 'EM properties'\n"
            r"\tType('Mesh')\n"
            r"\tDataId='EM properties1'\n"
            r"\t$begin 'Properties'\n"
            r"\t\tGeneral=''\n"
            r"\t\tModeled='true'\n"
            r"\t\tUnion='true'\n"
            r"\t\t'Use Precedence'='false'\n"
            r"\t\t'Precedence Value'='1'\n"
            r"\t\tPlanarEM=''\n"
            r"\t\tRefined='true'\n"
            r"\t\tRefineFactor='1'\n"
            r"\t\tNoEdgeMesh='false'\n"
            r"\t\tHFSS=''\n"
            r"\t\t'Solve Inside'='false'\n"
            r"\t\tSIwave=''\n"
            r"\t\t'DCIR Equipotential Region'='false'\n"
            r"\t$end 'Properties'\n"
            r"$end 'EM properties'\n"
        )

        pid = self._pedb.edb_api.ProductId.Designer
        _, p = self._edb_padstackinstance.GetProductProperty(pid, 18, "")
        if p:
            return p
        else:
            return default

    @_em_properties.setter
    def _em_properties(self, em_prop):
        """Set EM properties"""
        pid = self._pedb.edb_api.ProductId.Designer
        self._edb_padstackinstance.SetProductProperty(pid, 18, em_prop)

    @property
    def dcir_equipotential_region(self):
        """Check whether dcir equipotential region is enabled.

        Returns
        -------
        bool
        """
        pattern = r"'DCIR Equipotential Region'='([^']+)'"
        em_pp = self._em_properties
        result = re.search(pattern, em_pp).group(1)
        if result == "true":
            return True
        else:
            return False

    @dcir_equipotential_region.setter
    def dcir_equipotential_region(self, value):
        """Set dcir equipotential region."""
        pp = r"'DCIR Equipotential Region'='true'" if value else r"'DCIR Equipotential Region'='false'"
        em_pp = self._em_properties
        pattern = r"'DCIR Equipotential Region'='([^']+)'"
        new_em_pp = re.sub(pattern, pp, em_pp)
        self._em_properties = new_em_pp

    @property
    def object_instance(self):
        """Return Ansys.Ansoft.Edb.LayoutInstance.LayoutObjInstance object."""
        if not self._object_instance:
            self._object_instance = (
                self._edb_padstackinstance.GetLayout()
                .GetLayoutInstance()
                .GetLayoutObjInstance(self._edb_padstackinstance, None)
            )
        return self._object_instance

    @property
    def bounding_box(self):
        """Get bounding box of the padstack instance.
        Because this method is slow, the bounding box is stored in a variable and reused.

        Returns
        -------
        list of float
        """
        if self._bounding_box:
            return self._bounding_box
        bbox = self.object_instance.GetBBox()
        self._bounding_box = [
            [bbox.Item1.X.ToDouble(), bbox.Item1.Y.ToDouble()],
            [bbox.Item2.X.ToDouble(), bbox.Item2.Y.ToDouble()],
        ]
        return self._bounding_box

    def in_polygon(self, polygon_data, include_partial=True, simple_check=False):
        """Check if padstack Instance is in given polygon data.

        Parameters
        ----------
        polygon_data : PolygonData Object
        include_partial : bool, optional
            Whether to include partial intersecting instances. The default is ``True``.
        simple_check : bool, optional
            Whether to perform a single check based on the padstack center or check the padstack bounding box.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        pos = [i for i in self.position]
        int_val = 1 if polygon_data.PointInPolygon(self._pedb.point_data(*pos)) else 0
        if int_val == 0:
            return False

        if simple_check:
            # pos = [i for i in self.position]
            # int_val = 1 if polygon_data.PointInPolygon(self._pedb.point_data(*pos)) else 0
            return True
        else:
            plane = self._pedb.modeler.Shape("rectangle", pointA=self.bounding_box[0], pointB=self.bounding_box[1])
            rectangle_data = self._pedb.modeler.shape_to_polygon_data(plane)
            int_val = polygon_data.GetIntersectionType(rectangle_data)
        # Intersection type:
        # 0 = objects do not intersect
        # 1 = this object fully inside other (no common contour points)
        # 2 = other object fully inside this
        # 3 = common contour points 4 = undefined intersection
        if int_val == 0:
            return False
        elif include_partial:
            return True
        elif int_val < 3:
            return True
        else:
            return False

    @property
    def pin(self):
        """EDB padstack object."""
        warnings.warn("`pin` is deprecated.", DeprecationWarning)
        return self._edb_padstackinstance

    @property
    def padstack_definition(self):
        """Padstack definition.

        Returns
        -------
        str
            Name of the padstack definition.
        """
        self._pdef = self._edb_padstackinstance.GetPadstackDef().GetName()
        return self._pdef

    @property
    def backdrill_top(self):
        """Backdrill layer from top.

        Returns
        -------
        tuple
            Tuple of the layer name, drill diameter, and offset if it exists.
        """
        layer = self._pedb.edb_api.cell.layer("", self._pedb.edb_api.cell.layer_type.SignalLayer)
        val = self._pedb.edb_value(0)
        offset = self._pedb.edb_value(0.0)
        (
            flag,
            drill_to_layer,
            offset,
            diameter,
        ) = self._edb_padstackinstance.GetBackDrillParametersLayerValue(layer, offset, val, False)
        if flag:
            if offset.ToDouble():
                return drill_to_layer.GetName(), diameter.ToString(), offset.ToString()
            else:
                return drill_to_layer.GetName(), diameter.ToString()
        else:
            return

    def set_backdrill_top(self, drill_depth, drill_diameter, offset=0.0):
        """Set backdrill from top.

        Parameters
        ----------
        drill_depth : str
            Name of the drill to layer.
        drill_diameter : float, str
            Diameter of backdrill size.
        offset : float, str
            Offset for the backdrill. The default is ``0.0``. If the value is other than the
            default, the stub does not stop at the layer. In AEDT, this parameter is called
            "Mfg stub length".

        Returns
        -------
        bool
            True if success, False otherwise.
        """
        layer = self._pedb.stackup.layers[drill_depth]._edb_layer
        val = self._pedb.edb_value(drill_diameter)
        offset = self._pedb.edb_value(offset)
        if offset.ToDouble():
            return self._edb_padstackinstance.SetBackDrillParameters(layer, offset, val, False)
        else:
            return self._edb_padstackinstance.SetBackDrillParameters(layer, val, False)

    @property
    def backdrill_bottom(self):
        """Backdrill layer from bottom.

        Returns
        -------
        tuple
            Tuple of the layer name, drill diameter, and drill offset if it exists.
        """
        layer = self._pedb.edb_api.cell.layer("", self._pedb.edb_api.cell.layer_type.SignalLayer)
        val = self._pedb.edb_value(0)
        offset = self._pedb.edb_value(0.0)
        (
            flag,
            drill_to_layer,
            offset,
            diameter,
        ) = self._edb_padstackinstance.GetBackDrillParametersLayerValue(layer, offset, val, True)
        if flag:
            if offset.ToDouble():
                return drill_to_layer.GetName(), diameter.ToString(), offset.ToString()
            else:
                return drill_to_layer.GetName(), diameter.ToString()
        else:
            return

    def set_backdrill_bottom(self, drill_depth, drill_diameter, offset=0.0):
        """Set backdrill from bottom.

        Parameters
        ----------
        drill_depth : str
            Name of the drill to layer.
        drill_diameter : float, str
            Diameter of the backdrill size.
        offset : float, str, optional
            Offset for the backdrill. The default is ``0.0``. If the value is other than the
            default, the stub does not stop at the layer. In AEDT, this parameter is called
            "Mfg stub length".

        Returns
        -------
        bool
            True if success, False otherwise.
        """
        layer = self._pedb.stackup.layers[drill_depth]._edb_layer
        val = self._pedb.edb_value(drill_diameter)
        offset = self._pedb.edb_value(offset)
        if offset.ToDouble():
            return self._edb_object.SetBackDrillParameters(layer, offset, val, True)
        else:
            return self._edb_object.SetBackDrillParameters(layer, val, True)

    @property
    def start_layer(self):
        """Starting layer.

        Returns
        -------
        str
            Name of the starting layer.
        """
        layer = self._pedb.edb_api.cell.layer("", self._pedb.edb_api.cell.layer_type.SignalLayer)
        _, start_layer, stop_layer = self._edb_object.GetLayerRange()

        if start_layer:
            return start_layer.GetName()
        return None

    @start_layer.setter
    def start_layer(self, layer_name):
        stop_layer = self._pedb.stackup.signal_layers[self.stop_layer]._edb_layer
        layer = self._pedb.stackup.signal_layers[layer_name]._edb_layer
        self._edb_padstackinstance.SetLayerRange(layer, stop_layer)

    @property
    def stop_layer(self):
        """Stopping layer.

        Returns
        -------
        str
            Name of the stopping layer.
        """
        layer = self._pedb.edb_api.cell.layer("", self._pedb.edb_api.cell.layer_type.SignalLayer)
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange()

        if stop_layer:
            return stop_layer.GetName()
        return None

    @stop_layer.setter
    def stop_layer(self, layer_name):
        start_layer = self._pedb.stackup.signal_layers[self.start_layer]._edb_layer
        layer = self._pedb.stackup.signal_layers[layer_name]._edb_layer
        self._edb_padstackinstance.SetLayerRange(start_layer, layer)

    @property
    def layer_range_names(self):
        """List of all layers to which the padstack instance belongs."""
        _, start_layer, stop_layer = self._edb_padstackinstance.GetLayerRange()
        started = False
        layer_list = []
        start_layer_name = start_layer.GetName()
        stop_layer_name = stop_layer.GetName()
        for layer_name in list(self._pedb.stackup.layers.keys()):
            if started:
                layer_list.append(layer_name)
                if layer_name == stop_layer_name or layer_name == start_layer_name:
                    break
            elif layer_name == start_layer_name:
                started = True
                layer_list.append(layer_name)
                if layer_name == stop_layer_name:
                    break
            elif layer_name == stop_layer_name:
                started = True
                layer_list.append(layer_name)
                if layer_name == start_layer_name:
                    break
        return layer_list

    @property
    def net_name(self):
        """Net name.

        Returns
        -------
        str
            Name of the net.
        """
        return self._edb_padstackinstance.GetNet().GetName()

    @net_name.setter
    def net_name(self, val):
        if not isinstance(val, str):
            try:
                self._edb_padstackinstance.SetNet(val.net_obj)
            except:
                raise AttributeError("Value inserted not found. Input has to be net name or net object.")
        elif val in self._pedb.nets.netlist:
            net = self._pedb.nets.nets[val].net_object
            self._edb_padstackinstance.SetNet(net)
        else:
            raise AttributeError("Value inserted not found. Input has to be net name or net object.")

    @property
    def is_pin(self):
        """Determines whether this padstack instance is a layout pin.

        Returns
        -------
        bool
            True if this padstack type is a layout pin, False otherwise.
        """
        return self._edb_padstackinstance.IsLayoutPin()

    @is_pin.setter
    def is_pin(self, pin):
        """Set padstack type

        Parameters
        ----------
        pin : bool
            True if set this padstack instance as pin, False otherwise
        """
        self._edb_padstackinstance.SetIsLayoutPin(pin)

    @property
    def component(self):
        """Component."""
        from pyedb.dotnet.edb_core.cell.hierarchy.component import EDBComponent

        comp = EDBComponent(self._pedb, self._edb_object.GetComponent())
        return comp if not comp.is_null else False

    @property
    def position(self):
        """Padstack instance position.

        Returns
        -------
        list
            List of ``[x, y]`` coordinates for the padstack instance position.
        """
        self._position = []
        out = self._edb_padstackinstance.GetPositionAndRotationValue()
        if self._edb_padstackinstance.GetComponent():
            out2 = self._edb_padstackinstance.GetComponent().GetTransform().TransformPoint(out[1])
            self._position = [out2.X.ToDouble(), out2.Y.ToDouble()]
        elif out[0]:
            self._position = [out[1].X.ToDouble(), out[1].Y.ToDouble()]
        return self._position

    @position.setter
    def position(self, value):
        pos = []
        for v in value:
            if isinstance(v, (float, int, str)):
                pos.append(self._pedb.edb_value(v))
            else:
                pos.append(v)
        point_data = self._pedb.edb_api.geometry.point_data(pos[0], pos[1])
        self._edb_padstackinstance.SetPositionAndRotation(point_data, self._pedb.edb_value(self.rotation))

    @property
    def rotation(self):
        """Padstack instance rotation.

        Returns
        -------
        float
            Rotatation value for the padstack instance.
        """
        point_data = self._pedb.edb_api.geometry.point_data(self._pedb.edb_value(0.0), self._pedb.edb_value(0.0))
        out = self._edb_padstackinstance.GetPositionAndRotationValue()

        if out[0]:
            return out[2].ToDouble()

    @property
    def name(self):
        """Padstack Instance Name. If it is a pin, the syntax will be like in AEDT ComponentName-PinName."""
        if self.is_pin:
            return self.aedt_name
        else:
            return self.component_pin

    @name.setter
    def name(self, value):
        self._edb_padstackinstance.SetName(value)
        self._edb_padstackinstance.SetProductProperty(self._pedb.edb_api.ProductId.Designer, 11, value)

    @property
    def metal_volume(self):
        """Metal volume of the via hole instance in cubic units (m3). Metal plating ratio is accounted.

        Returns
        -------
        float
            Metal volume of the via hole instance.

        """
        volume = 0
        if not self.start_layer == self.stop_layer:
            start_layer = self.start_layer
            stop_layer = self.stop_layer
            if self.backdrill_top:  # pragma no cover
                start_layer = self.backdrill_top[0]
            if self.backdrill_bottom:  # pragma no cover
                stop_layer = self.backdrill_bottom[0]
            padstack_def = self._pedb.padstacks.definitions[self.padstack_definition]
            hole_diam = 0
            try:  # pragma no cover
                hole_diam = padstack_def.hole_properties[0]
            except:  # pragma no cover
                pass
            if hole_diam:  # pragma no cover
                hole_finished_size = padstack_def.hole_finished_size
                via_length = (
                    self._pedb.stackup.signal_layers[start_layer].upper_elevation
                    - self._pedb.stackup.signal_layers[stop_layer].lower_elevation
                )
                volume = (math.pi * (hole_diam / 2) ** 2 - math.pi * (hole_finished_size / 2) ** 2) * via_length
        return volume

    @property
    def pin_number(self):
        """Get pin number."""
        warnings.warn("`pin_number` is deprecated. Use `component_pin` method instead.", DeprecationWarning)
        return self.component_pin

    @property
    def component_pin(self):
        """Get component pin."""
        return self._edb_padstackinstance.GetName()

    @property
    def aedt_name(self):
        """Retrieve the pin name that is shown in AEDT.

        .. note::
           To obtain the EDB core pin name, use `pin.GetName()`.

        Returns
        -------
        str
            Name of the pin in AEDT.

        Examples
        --------

        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", "project name", "release version")
        >>> edbapp.padstacks.instances[111].get_aedt_pin_name()

        """

        val = String("")
        _, name = self._edb_padstackinstance.GetProductProperty(self._pedb.edb_api.ProductId.Designer, 11, val)
        name = str(name).strip("'")
        return name

    def parametrize_position(self, prefix=None):
        """Parametrize the instance position.

        Parameters
        ----------
        prefix : str, optional
            Prefix for the variable name. Default is ``None``.
            Example `"MyVariableName"` will create 2 Project variables $MyVariableNamesX and $MyVariableNamesY.

        Returns
        -------
        List
            List of variables created.
        """
        p = self.position
        if not prefix:
            var_name = "${}_pos".format(self.name)
        else:
            var_name = "${}".format(prefix)
        self._pedb.add_project_variable(var_name + "X", p[0])
        self._pedb.add_project_variable(var_name + "Y", p[1])
        self.position = [var_name + "X", var_name + "Y"]
        return [var_name + "X", var_name + "Y"]

    def in_voids(self, net_name=None, layer_name=None):
        """Check if this padstack instance is in any void.

        Parameters
        ----------
        net_name : str
            Net name of the voids to be checked. Default is ``None``.
        layer_name : str
            Layer name of the voids to be checked. Default is ``None``.

        Returns
        -------
        list
            List of the voids that include this padstack instance.
        """
        x_pos = self._pedb.edb_value(self.position[0])
        y_pos = self._pedb.edb_value(self.position[1])
        point_data = self._pedb.modeler._edb.geometry.point_data(x_pos, y_pos)

        voids = []
        for prim in self._pedb.modeler.get_primitives(net_name, layer_name, is_void=True):
            if prim.primitive_object.GetPolygonData().PointInPolygon(point_data):
                voids.append(prim)
        return voids

    @property
    def pingroups(self):
        """Pin groups that the pin belongs to.

        Returns
        -------
        list
            List of pin groups that the pin belongs to.
        """
        return self._edb_padstackinstance.GetPinGroups()

    @property
    def placement_layer(self):
        """Placement layer.

        Returns
        -------
        str
            Name of the placement layer.
        """
        return self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetName()

    @property
    def lower_elevation(self):
        """Lower elevation of the placement layer.

        Returns
        -------
        float
            Lower elavation of the placement layer.
        """
        try:
            return self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetLowerElevation()
        except AttributeError:  # pragma: no cover
            return None

    @property
    def upper_elevation(self):
        """Upper elevation of the placement layer.

        Returns
        -------
        float
           Upper elevation of the placement layer.
        """
        try:
            return self._edb_padstackinstance.GetGroup().GetPlacementLayer().Clone().GetUpperElevation()
        except AttributeError:  # pragma: no cover
            return None

    @property
    def top_bottom_association(self):
        """Top/bottom association of the placement layer.

        Returns
        -------
        int
            Top/bottom association of the placement layer.

            * 0 Top associated.
            * 1 No association.
            * 2 Bottom associated.
            * 4 Number of top/bottom association type.
            * -1 Undefined.
        """
        return int(self._edb_padstackinstance.GetGroup().GetPlacementLayer().GetTopBottomAssociation())

    def create_rectangle_in_pad(self, layer_name, return_points=False, partition_max_order=16):
        """Create a rectangle inscribed inside a padstack instance pad.

        The rectangle is fully inscribed in the pad and has the maximum area.
        It is necessary to specify the layer on which the rectangle will be created.

        Parameters
        ----------
        layer_name : str
            Name of the layer on which to create the polygon.
        return_points : bool, optional
            If `True` does not create the rectangle and just returns a list containing the rectangle vertices.
            Default is `False`.
        partition_max_order : float, optional
            Order of the lattice partition used to find the quasi-lattice polygon that approximates ``polygon``.
            Default is ``16``.

        Returns
        -------
        bool, List,  :class:`pyedb.dotnet.edb_core.edb_data.primitives.EDBPrimitives`
            Polygon when successful, ``False`` when failed, list of list if `return_points=True`.

        Examples
        --------
        >>> from pyedb import Edb
        >>> edbapp = Edb("myaedbfolder", edbversion="2021.2")
        >>> edb_layout = edbapp.modeler
        >>> list_of_padstack_instances = list(edbapp.padstacks.instances.values())
        >>> padstack_inst = list_of_padstack_instances[0]
        >>> padstack_inst.create_rectangle_in_pad("TOP")
        """

        padstack_center = self.position
        rotation = self.rotation  # in radians
        padstack_name = self.padstack_definition
        try:
            padstack = self._pedb.padstacks.definitions[padstack_name]
        except KeyError:  # pragma: no cover
            return False
        try:
            padstack_pad = padstack.pad_by_layer[layer_name]
        except KeyError:  # pragma: no cover
            try:
                padstack_pad = padstack.pad_by_layer[padstack.via_start_layer]
            except KeyError:  # pragma: no cover
                return False

        pad_shape = padstack_pad.geometry_type
        params = padstack_pad.parameters_values
        polygon_data = padstack_pad.polygon_data

        def _rotate(p):
            x = p[0] * math.cos(rotation) - p[1] * math.sin(rotation)
            y = p[0] * math.sin(rotation) + p[1] * math.cos(rotation)
            return [x, y]

        def _translate(p):
            x = p[0] + padstack_center[0]
            y = p[1] + padstack_center[1]
            return [x, y]

        rect = None

        if pad_shape == 1:
            # Circle
            diameter = params[0]
            r = diameter * 0.5
            p1 = [r, 0.0]
            p2 = [0.0, r]
            p3 = [-r, 0.0]
            p4 = [0.0, -r]
            rect = [_translate(p1), _translate(p2), _translate(p3), _translate(p4)]
        elif pad_shape == 2:
            # Square
            square_size = params[0]
            s2 = square_size * 0.5
            p1 = [s2, s2]
            p2 = [-s2, s2]
            p3 = [-s2, -s2]
            p4 = [s2, -s2]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 3:
            # Rectangle
            x_size = float(params[0])
            y_size = float(params[1])
            sx2 = x_size * 0.5
            sy2 = y_size * 0.5
            p1 = [sx2, sy2]
            p2 = [-sx2, sy2]
            p3 = [-sx2, -sy2]
            p4 = [sx2, -sy2]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 4:
            # Oval
            x_size = params[0]
            y_size = params[1]
            corner_radius = float(params[2])
            if corner_radius >= min(x_size, y_size):
                r = min(x_size, y_size)
            else:
                r = corner_radius
            sx = x_size * 0.5 - r
            sy = y_size * 0.5 - r
            k = r / math.sqrt(2)
            p1 = [sx + k, sy + k]
            p2 = [-sx - k, sy + k]
            p3 = [-sx - k, -sy - k]
            p4 = [sx + k, -sy - k]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 5:
            # Bullet
            x_size = params[0]
            y_size = params[1]
            corner_radius = params[2]
            if corner_radius >= min(x_size, y_size):
                r = min(x_size, y_size)
            else:
                r = corner_radius
            sx = x_size * 0.5 - r
            sy = y_size * 0.5 - r
            k = r / math.sqrt(2)
            p1 = [sx + k, sy + k]
            p2 = [-x_size * 0.5, sy + k]
            p3 = [-x_size * 0.5, -sy - k]
            p4 = [sx + k, -sy - k]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 6:
            # N-Sided Polygon
            size = params[0]
            num_sides = params[1]
            ext_radius = size * 0.5
            apothem = ext_radius * math.cos(math.pi / num_sides)
            p1 = [apothem, 0.0]
            p2 = [0.0, apothem]
            p3 = [-apothem, 0.0]
            p4 = [0.0, -apothem]
            rect = [
                _translate(_rotate(p1)),
                _translate(_rotate(p2)),
                _translate(_rotate(p3)),
                _translate(_rotate(p4)),
            ]
        elif pad_shape == 0 and polygon_data is not None:
            # Polygon
            points = []
            i = 0
            while i < polygon_data.edb_api.Count:
                point = polygon_data.edb_api.GetPoint(i)
                i += 1
                if point.IsArc():
                    continue
                else:
                    points.append([point.X.ToDouble(), point.Y.ToDouble()])
            xpoly, ypoly = zip(*points)
            polygon = [list(xpoly), list(ypoly)]
            rectangles = GeometryOperators.find_largest_rectangle_inside_polygon(
                polygon, partition_max_order=partition_max_order
            )
            rect = rectangles[0]
            for i in range(4):
                rect[i] = _translate(_rotate(rect[i]))

        if rect is None or len(rect) != 4:
            return False
        path = self._pedb.modeler.Shape("polygon", points=rect)
        pdata = self._pedb.modeler.shape_to_polygon_data(path)
        new_rect = []
        for point in pdata.Points:
            p_transf = self._edb_padstackinstance.GetComponent().GetTransform().TransformPoint(point)
            new_rect.append([p_transf.X.ToDouble(), p_transf.Y.ToDouble()])
        if return_points:
            return new_rect
        else:
            path = self._pedb.modeler.Shape("polygon", points=new_rect)
            created_polygon = self._pedb.modeler.create_polygon(path, layer_name)
            return created_polygon

    def get_reference_pins(self, reference_net="GND", search_radius=5e-3, max_limit=0, component_only=True):
        """Search for reference pins using given criteria.

        Parameters
        ----------
        reference_net : str, optional
            Reference net. The default is ``"GND"``.
        search_radius : float, optional
            Search radius for finding padstack instances. The default is ``5e-3``.
        max_limit : int, optional
            Maximum limit for the padstack instances found. The default is ``0``, in which
            case no limit is applied. The maximum limit value occurs on the nearest
            reference pins from the positive one that is found.
        component_only : bool, optional
            Whether to limit the search to component padstack instances only. The
            default is ``True``. When ``False``, the search is extended to the entire layout.

        Returns
        -------
        list
            List of :class:`dotnet.edb_core.edb_data.padstacks_data.EDBPadstackInstance`.

        Examples
        --------
        >>> edbapp = Edb("target_path")
        >>> pin = edbapp.components.instances["J5"].pins["19"]
        >>> reference_pins = pin.get_reference_pins(reference_net="GND", search_radius=5e-3, max_limit=0,
        >>> component_only=True)
        """
        return self._pedb.padstacks.get_reference_pins(
            positive_pin=self,
            reference_net=reference_net,
            search_radius=search_radius,
            max_limit=max_limit,
            component_only=component_only,
        )
