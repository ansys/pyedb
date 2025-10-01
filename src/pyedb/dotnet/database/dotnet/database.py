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

"""Database."""

import re

from pyedb.dotnet.database.general import convert_py_list_to_net_list


class HierarchyDotNet:
    """Hierarchy."""

    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self._hierarchy, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, app):
        self._app = app
        self.core = self._app._edb
        self._hierarchy = self.core.Cell.Hierarchy

    @property
    def api_class(self):  # pragma: no cover
        """Return Ansys.Ansoft.Edb class object."""
        return self._hierarchy

    @property
    def component(self):
        """Edb Dotnet Api Database `Edb.Cell.Hierarchy.Component`."""
        return self._hierarchy.Component

    @property
    def cell_instance(self):
        """Edb Dotnet Api Database `Edb.Cell.Hierarchy.CellInstance`."""
        return self._hierarchy.CellInstance

    @property
    def pin_group(self):
        """Edb Dotnet Api Database `Edb.Cell.Hierarchy.PinGroup`."""
        return self._hierarchy.PinGroup


class PolygonDataDotNet:  # pragma: no cover
    """Polygon Data."""

    def __getattr__(self, key):  # pragma: no cover
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self.dotnetobj, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, pedb, api_object=None):
        self._pedb = pedb
        self.dotnetobj = pedb.core.Geometry.PolygonData
        self.core = api_object
        self._edb_object = api_object

    @property
    def api_class(self):  # pragma: no cover
        """:class:`Ansys.Ansoft.Edb` class object."""
        return self.dotnetobj

    @property
    def arcs(self):  # pragma: no cover
        """List of Edb.Geometry.ArcData."""
        return list(self.core.GetArcData())

    def add_point(self, x, y, incremental=False):
        """Add a point at the end of the point list of the polygon.

        Parameters
        ----------
        x: str, int, float
            X coordinate.
        y: str, in, float
            Y coordinate.
        incremental: bool
            Whether to add the point incrementally. The default value is ``False``. When
            ``True``, the coordinates of the added point are incremental to the last point.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.
        """
        if incremental:
            x = self._pedb.edb_value(x)
            y = self._pedb.edb_value(y)
            last_point = self.get_points()[-1]
            x = "({})+({})".format(x, last_point[0].ToString())
            y = "({})+({})".format(y, last_point[1].ToString())
        return self.core.AddPoint(GeometryDotNet(self._pedb).point_data(x, y))

    def get_bbox_of_boxes(self, points):
        """Get the EDB .NET API ``Edb.Geometry.GetBBoxOfBoxes`` database.

        Parameters
        ----------
        points : list or `Edb.Geometry.PointData`
        """
        if isinstance(points, list):
            points = convert_py_list_to_net_list(points)
        return self.dotnetobj.GetBBoxOfBoxes(points)

    def get_bbox_of_polygons(self, polygons):
        """Edb Dotnet Api Database `Edb.Geometry.GetBBoxOfPolygons`.

        Parameters
        ----------
        polygons : list or `Edb.Geometry.PolygonData`"""
        if isinstance(polygons, list):
            polygons = convert_py_list_to_net_list(polygons)
        return self.dotnetobj.GetBBoxOfPolygons(polygons)

    def create_from_bbox(self, points):
        """Edb Dotnet Api Database `Edb.Geometry.CreateFromBBox`.

        Parameters
        ----------
        points : list or `Edb.Geometry.PointData`
        """
        from pyedb.dotnet.clr_module import Tuple

        if isinstance(points, (tuple, list)):
            points = Tuple[self._pedb.core.Geometry.PointData, self._pedb.core.Geometry.PointData](points[0], points[1])
        return self.dotnetobj.CreateFromBBox(points)

    def create_from_arcs(self, arcs, flag):
        """Edb Dotnet Api Database `Edb.Geometry.CreateFromArcs`.

        Parameters
        ----------
        arcs : list or `Edb.Geometry.ArcData`
            List of ArcData.
        flag : bool
        """
        if isinstance(arcs, list):
            arcs = convert_py_list_to_net_list(arcs)
        return self.dotnetobj.CreateFromArcs(arcs, flag)

    def unite(self, pdata):
        """Edb Dotnet Api Database `Edb.Geometry.Unite`.

        Parameters
        ----------
        pdata : list or `Edb.Geometry.PolygonData`
            Polygons to unite.

        """
        if isinstance(pdata, list):
            pdata = convert_py_list_to_net_list(pdata)
        return list(self.dotnetobj.Unite(pdata))

    def get_convex_hull_of_polygons(self, pdata):
        """Edb Dotnet Api Database `Edb.Geometry.GetConvexHullOfPolygons`.

        Parameters
        ----------
        pdata : list or List of `Edb.Geometry.PolygonData`
            Polygons to unite in a Convex Hull.
        """
        if isinstance(pdata, list):
            pdata = convert_py_list_to_net_list(pdata)
        return self.dotnetobj.GetConvexHullOfPolygons(pdata)


class NetDotNet:
    """Net Objects."""

    def __init__(self, app, net_obj=None):
        self.net = app._edb.Cell.Net

        self.core = app._edb
        self._app = app
        self.net_obj = net_obj

    @property
    def api_class(self):  # pragma: no cover
        """Return Ansys.Ansoft.Edb class object."""
        return self.net

    @property
    def api_object(self):
        """Return Ansys.Ansoft.Edb object."""
        return self.net_obj

    def find_by_name(self, layout, net):  # pragma: no cover
        """Edb Dotnet Api Database `Edb.Net.FindByName`."""
        return NetDotNet(self._app, self.net.FindByName(layout, net))

    def create(self, layout, name):
        """Edb Dotnet Api Database `Edb.Net.Create`."""

        return NetDotNet(self._app, self.net.Create(layout, name))

    def delete(self):
        """Edb Dotnet Api Database `Edb.Net.Delete`."""
        if self.net_obj:
            self.net_obj.Delete()
            self.net_obj = None

    @property
    def name(self):
        """Edb Dotnet Api Database `net.name` and  `Net.SetName()`."""
        if self.net_obj:
            return self.net_obj.GetName()

    @name.setter
    def name(self, value):
        if self.net_obj:
            self.net_obj.SetName(value)

    @property
    def is_null(self):
        """Edb Dotnet Api Database `Net.IsNull()`."""
        if self.net_obj:
            return self.net_obj.IsNull()

    @property
    def is_power_ground(self):
        """Edb Dotnet Api Database `Net.IsPowerGround()` and  `Net.SetIsPowerGround()`."""
        if self.net_obj:
            return self.net_obj.IsPowerGround()

    @property
    def _api_get_extended_net(self):
        """Extended net this net belongs to if it belongs to an extended net.
        If it does not belong to an extendednet, a null extended net is returned.
        """
        return self.net_obj.GetExtendedNet()

    @is_power_ground.setter
    def is_power_ground(self, value):
        if self.net_obj:
            self.net_obj.SetIsPowerGround(value)


class NetClassDotNet:
    """Net Class."""

    def __init__(self, app, api_object=None):
        self.cell_net_class = app._edb.Cell.NetClass
        self.api_object = api_object
        self.core = app._edb
        self._app = app

    @property
    def api_nets(self):
        """Return Edb Nets object dictionary."""
        return {i.GetName(): i for i in list(self.api_object.Nets)}

    def api_create(self, name):
        """Edb Dotnet Api Database `Edb.NetClass.Create`."""
        return NetClassDotNet(self._app, self.cell_net_class.Create(self._app.active_layout, name))

    @property
    def name(self):
        """Edb Dotnet Api Database `NetClass.name` and  `NetClass.SetName()`."""
        if self.api_object:
            return self.api_object.GetName()

    @name.setter
    def name(self, value):
        if self.api_object:
            self.api_object.SetName(value)

    def add_net(self, name):
        """Add a new net.

        Parameters
        ----------
        name : str
            The name of the net to be added.

        Returns
        -------
        object
        """
        if self.api_object:
            edb_api_net = self.core.Cell.Net.FindByName(self._app.active_layout, name)
            return self.api_object.AddNet(edb_api_net)

    def delete(self):  # pragma: no cover
        """Edb Dotnet Api Database `Delete`."""

        if self.api_object:
            self.api_object.Delete()
            self.api_object = None
            return not self.api_object

    @property
    def is_null(self):
        """Edb Dotnet Api Database `NetClass.IsNull()`."""
        if self.api_object:
            return self.api_object.IsNull()


class ExtendedNetDotNet(NetClassDotNet):
    """Extended net class."""

    def __init__(self, app, api_object=None):
        super().__init__(app, api_object)
        self.cell_extended_net = app._edb.Cell.ExtendedNet

    @property
    def api_class(self):  # pragma: no cover
        """Return Ansys.Ansoft.Edb class object."""
        return self.cell_extended_net

    def find_by_name(self, layout, net):  # pragma: no cover
        """Edb Dotnet Api Database `Edb.ExtendedNet.FindByName`."""
        return ExtendedNetDotNet(self._app, self.cell_extended_net.FindByName(layout, net))

    def api_create(self, name):
        """Edb Dotnet Api Database `Edb.ExtendedNet.Create`."""
        return ExtendedNetDotNet(self._app, self.cell_extended_net.Create(self._app.active_layout, name))


class DifferentialPairDotNet(NetClassDotNet):
    """Differential Pairs."""

    def __init__(self, app, api_object=None):
        super().__init__(app, api_object)
        self.cell_diff_pair = app._edb.Cell.DifferentialPair

    @property
    def api_class(self):  # pragma: no cover
        """Return Ansys.Ansoft.Edb class object."""
        return self.cell_diff_pair

    def find_by_name(self, layout, net):  # pragma: no cover
        """Edb Dotnet Api Database `Edb.DifferentialPair.FindByName`."""
        return DifferentialPairDotNet(self._app, self.cell_diff_pair.FindByName(layout, net))

    def api_create(self, name):
        """Edb Dotnet Api Database `Edb.DifferentialPair.Create`."""
        return DifferentialPairDotNet(self._app, self.cell_diff_pair.Create(self._app.active_layout, name))

    def _api_set_differential_pair(self, net_name_p, net_name_n):
        edb_api_net_p = self.core.Cell.Net.FindByName(self._app.active_layout, net_name_p)
        edb_api_net_n = self.core.Cell.Net.FindByName(self._app.active_layout, net_name_n)
        self.api_object.SetDifferentialPair(edb_api_net_p, edb_api_net_n)

    @property
    def api_positive_net(self):
        """Edb Api Positive net object."""
        if self.api_object:
            return self.api_object.GetPositiveNet()

    @property
    def api_negative_net(self):
        """Edb Api Negative net object."""
        if self.api_object:
            return self.api_object.GetNegativeNet()


class CellClassDotNet:
    """Cell Class."""

    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self._cell, key)
            except AttributeError:
                if self._active_cell and key in dir(self._active_cell):
                    try:
                        return getattr(self._active_cell, key)
                    except AttributeError:  # pragma: no cover
                        raise AttributeError("Attribute not present")
                else:
                    raise AttributeError("Attribute not present")

    def __init__(self, app, active_cell=None):
        self._app = app
        self.core = app._edb
        self._cell = self.core.Cell
        self._active_cell = active_cell

    @property
    def api_class(self):
        """Return Ansys.Ansoft.Edb class object."""
        return self._cell

    @property
    def api_object(self):
        """Return Ansys.Ansoft.Edb object."""
        return self._active_cell

    def create(self, db, cell_type, cell_name):
        return CellClassDotNet(self._app, self.cell.Create(db, cell_type, cell_name))

    @property
    def terminal(self):
        """Edb Dotnet Api Database `Edb.Cell.Terminal`."""
        return self._cell.Terminal

    @property
    def hierarchy(self):
        """Edb Dotnet Api Database `Edb.Cell.Hierarchy`.

        Returns
        -------
        :class:`dotnet.database.dotnet.HierarchyDotNet`
        """
        return HierarchyDotNet(self._app)

    @property
    def cell(self):
        """Edb Dotnet Api Database `Edb.Cell`."""
        return self._cell.Cell

    @property
    def net(self):
        """Edb Dotnet Api Cell.Layer."""
        return NetDotNet(self._app)

    @property
    def layer_type(self):
        """Edb Dotnet Api Cell.LayerType."""
        return self._cell.LayerType

    @property
    def layer_type_set(self):
        """Edb Dotnet Api Cell.LayerTypeSet."""
        return self._cell.LayerTypeSet

    @property
    def layer(self):
        """Edb Dotnet Api Cell.Layer."""
        return self._cell.Layer

    @property
    def layout_object_type(self):
        """Edb Dotnet Api LayoutObjType."""
        return self._cell.LayoutObjType

    @property
    def primitive(self):
        """Edb Dotnet Api Database `Edb.Cell.Primitive`."""
        from pyedb.dotnet.database.dotnet.primitive import PrimitiveDotNet

        return PrimitiveDotNet(self._app)

    @property
    def simulation_setups(self):
        return self._app.setups

    def get_all_variable_names(self):
        """Method added for compatibility with grpc.

        Returns
        -------
        List[Str]
            List of variables name.

        """
        return list(self._app.variable_exists("")[1].GetAllVariableNames())

    def get_variable_value(self, variable_name):
        return self._app.variables[variable_name]


class UtilityDotNet:
    """Utility Edb class."""

    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self.utility, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, app):
        self._app = app
        self.utility = app._edb.Utility
        self.core = app._edb
        self.active_db = app._db
        self.active_cell = app._active_cell

    @property
    def api_class(self):
        """Return Ansys.Ansoft.Edb class object."""
        return self.utility

    def value(self, value, var_server=None):
        """Edb Dotnet Api Utility.Value."""
        if isinstance(value, self.utility.Value):
            return value
        if var_server:
            return self.utility.Value(value, var_server)
        if isinstance(value, (int, float)):
            return self.utility.Value(value)
        m1 = re.findall(r"(?<=[/+-/*//^/(/[])([a-z_A-Z/$]\w*)", str(value).replace(" ", ""))
        m2 = re.findall(r"^([a-z_A-Z/$]\w*)", str(value).replace(" ", ""))
        val_decomposed = list(set(m1).union(m2))
        if not val_decomposed:
            return self.utility.Value(value)
        var_server_db = self.active_db.GetVariableServer()
        var_names = var_server_db.GetAllVariableNames()
        var_server_cell = self.active_cell.GetVariableServer()
        var_names_cell = var_server_cell.GetAllVariableNames()
        if set(val_decomposed).intersection(var_names_cell):
            return self.utility.Value(value, var_server_cell)
        if set(val_decomposed).intersection(var_names):
            return self.utility.Value(value, var_server_db)
        return self.utility.Value(value)


class GeometryDotNet:
    """Geometry Edb Class."""

    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self.geometry, key)
            except AttributeError:  # pragma: no cover
                raise AttributeError("Attribute {} not present".format(key))

    def __init__(self, app):
        self._app = app
        self.geometry = self._app._edb.Geometry
        self.core = self._app._edb

    @property
    def api_class(self):
        """Return Ansys.Ansoft.Edb class object."""
        return self.geometry

    @property
    def utility(self):
        return UtilityDotNet(self._app)

    def point_data(self, p1, p2):
        """Edb Dotnet Api Point."""
        if isinstance(p1, (int, float, str, list)):
            p1 = self.utility.value(p1)
        if isinstance(p2, (int, float, str, list)):
            p2 = self.utility.value(p2)
        return self.geometry.PointData(p1, p2)

    def point3d_data(self, p1, p2, p3):
        """Edb Dotnet Api Point 3D."""
        if isinstance(p1, (int, float, str, list)):
            p1 = self.utility.value(p1)
        if isinstance(p2, (int, float, str, list)):
            p2 = self.utility.value(p2)
        if isinstance(p3, (int, float, str, list)):
            p3 = self.utility.value(p3)
        return self.geometry.Point3DData(p1, p2, p3)

    @property
    def extent_type(self):
        """Edb Dotnet Api Extent Type."""
        return self.geometry.ExtentType

    @property
    def polygon_data(self):
        """Polygon Data.

        Returns
        -------
        :class:`dotnet.database.dotnet.PolygonDataDotNet`
        """
        return PolygonDataDotNet(self._app)

    def arc_data(self, point1, point2, rotation=None, center=None, height=None):
        """Compute EBD arc data.

        Parameters
        ----------
        point1 : list or PointData object
        point2 : list or PointData object
        rotation : int or RotationDir enumerator
        center :  list or PointData object
        height : float

        Returns
        -------
        Edb ArcData object
        """
        if isinstance(point1, (list, tuple)):
            point1 = self.point_data(point1[0], point1[1])
        if isinstance(point2, (list, tuple)):
            point2 = self.point_data(point2[0], point2[1])
        if center and isinstance(center, (list, tuple)):
            center = self.point_data(center[0], center[1])
        if rotation and center:
            return self.geometry.ArcData(point1, point2, rotation, center)
        elif height:
            return self.geometry.ArcData(point1, point2, height)
        else:
            return self.geometry.ArcData(point1, point2)


class CellDotNet:
    """Cell Dot net."""

    def __getattr__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self.core, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, app):
        self._app = app
        self.core = app._edb

    @property
    def definition(self):
        """Edb Dotnet Api Definition."""

        return self.core.Definition

    @property
    def database(self):
        """Edb Dotnet Api Database."""
        return self.core.Database

    @property
    def cell(self):
        """Edb Dotnet Api Database `Edb.Cell`.

        Returns
        -------
        :class:`pyedb.dotnet.database.dotnet.database.CellClassDotNet`"""
        return CellClassDotNet(self._app)

    @property
    def utility(self):
        """Utility class.

        Returns
        -------
        :class:`pyedb.dotnet.database.dotnet.database.UtilityDotNet`"""

        return UtilityDotNet(self._app)

    @property
    def geometry(self):
        """Geometry class.

        Returns
        -------
        :class:`pyedb.dotnet.database.dotnet.database.GeometryDotNet`"""
        return GeometryDotNet(self._app)


class Database:
    """Class representing a database object."""

    @property
    def database(self):
        """Edb Dotnet Api Database."""
        return self.core.database

    @property
    def definition(self):
        """Edb Dotnet Api Database `Edb.Definition`."""
        return self.core.Definition

    def delete(self, db_path):
        """Delete a database at the specified file location.

        Parameters
        ----------
        db_path : str
            Path to top-level database folder.
        """
        return self.core.database.Delete(db_path)

    def save(self):
        """Save any changes into a file."""
        return self._db.Save()

    def close(self):
        """Close the database.

        .. note::
            Unsaved changes will be lost.
        """
        return self._db.Close()

    @property
    def top_circuit_cells(self):
        """Get top circuit cells.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return [CellClassDotNet(self, i) for i in list(self._db.TopCircuitCells)]

    @property
    def circuit_cells(self):
        """Get all circuit cells in the Database.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return [CellClassDotNet(self, i) for i in list(self._db.CircuitCells)]

    @property
    def footprint_cells(self):
        """Get all footprint cells in the Database.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
        """
        return [CellClassDotNet(self, i) for i in list(self._db.FootprintCells)]

    @property
    def edb_uid(self):
        """Get ID of the database.

        Returns
        -------
        int
            The unique EDB id of the Database.
        """
        return self._db.GetId()

    @property
    def is_read_only(self):
        """Determine if the database is open in a read-only mode.

        Returns
        -------
        bool
            True if Database is open with read only access, otherwise False.
        """
        return self._db.IsReadOnly()

    def find_by_id(self, db_id):
        """Find a database by ID.

        Parameters
        ----------
        db_id : int
            The Database's unique EDB id.

        Returns
        -------
        Database
            The Database or Null on failure.
        """
        self.core.database.FindById(db_id)

    def save_as(self, path, version=""):
        """Save this Database to a new location and older EDB version.

        Parameters
        ----------
        path : str
            New Database file location.
        version : str
            EDB version to save to. Empty string means current version.
        """
        self._db.SaveAs(path, version)

    @property
    def directory(self):
        """Get the directory of the Database.

        Returns
        -------
        str
            Directory of the Database.
        """
        return self._db.GetDirectory()

    def get_product_property(self, prod_id, attr_it):
        """Get the product-specific property value.

        Parameters
        ----------
        prod_id : ProductIdType
            Product ID.
        attr_it : int
            Attribute ID.

        Returns
        -------
        str
            Property value returned.
        """
        return self._db.GetProductProperty(prod_id, attr_it)

    def set_product_property(self, prod_id, attr_it, prop_value):
        """Set the product property associated with the given product and attribute ids.

        Parameters
        ----------
        prod_id : ProductIdType
            Product ID.
        attr_it : int
            Attribute ID.
        prop_value : str
            Product property's new value
        """
        self._db.SetProductProperty(prod_id, attr_it, prop_value)

    def get_product_property_ids(self, prod_id):
        """Get a list of attribute ids corresponding to a product property id.

        Parameters
        ----------
        prod_id : ProductIdType
            Product ID.

        Returns
        -------
        list[int]
            The attribute ids associated with this product property.
        """
        return self._db.GetProductPropertyIds(prod_id)

    def import_material_from_control_file(self, control_file, schema_dir=None, append=True):
        """Import materials from the provided control file.

        Parameters
        ----------
        control_file : str
            Control file name with full path.
        schema_dir : str
            Schema file path.
        append : bool
            True if the existing materials in Database are kept. False to remove existing materials in database.
        """
        self._db.ImportMaterialFromControlFile(
            control_file,
            schema_dir,
            append,
        )

    @property
    def version(self):
        """Get version of the Database.

        Returns
        -------
        tuple(int, int)
            A tuple of the version numbers [major, minor]
        """
        major, minor = self._db.GetVersion()
        return major, minor

    def scale(self, scale_factor):
        """Uniformly scale all geometry and their locations by a positive factor.

        Parameters
        ----------
        scale_factor : float
            Amount that coordinates are multiplied by.
        """
        return self._db.Scale(scale_factor)

    @property
    def source(self):
        """Get source name for this Database.

        This attribute is also used to set the source name.

        Returns
        -------
        str
            name of the source
        """
        return self._db.GetSource()

    @source.setter
    def source(self, source):
        """Set source name of the database."""
        self._db.SetSource(source)

    @property
    def source_version(self):
        """Get the source version for this Database.

        This attribute is also used to set the version.

        Returns
        -------
        str
            version string

        """
        return self._db.GetSourceVersion()

    @source_version.setter
    def source_version(self, source_version):
        """Set source version of the database."""
        self._db.SetSourceVersion(source_version)

    def copy_cells(self, cells_to_copy):
        """Copy Cells from other Databases or this Database into this Database.

        Parameters
        ----------
        cells_to_copy : list[:class:`Cell <ansys.edb.layout.Cell>`]
            Cells to copy.

        Returns
        -------
        list[:class:`Cell <ansys.edb.layout.Cell>`]
            New Cells created in this Database.
        """
        if not isinstance(cells_to_copy, list):
            cells_to_copy = [cells_to_copy]
        _dbCells = convert_py_list_to_net_list(cells_to_copy)
        return self._db.CopyCells(_dbCells)

    @property
    def apd_bondwire_defs(self):
        """Get all APD bondwire definitions in this Database.

        Returns
        -------
        list[:class:`ApdBondwireDef <ansys.edb.definition.ApdBondwireDef>`]
        """
        return list(self._db.APDBondwireDefs)

    @property
    def jedec4_bondwire_defs(self):
        """Get all JEDEC4 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec4BondwireDef <ansys.edb.definition.Jedec4BondwireDef>`]
        """
        return list(self._db.Jedec4BondwireDefs)

    @property
    def jedec5_bondwire_defs(self):
        """Get all JEDEC5 bondwire definitions in this Database.

        Returns
        -------
        list[:class:`Jedec5BondwireDef <ansys.edb.definition.Jedec5BondwireDef>`]
        """
        return list(self._db.Jedec5BondwireDefs)

    @property
    def padstack_defs(self):
        """Get all Padstack definitions in this Database.

        Returns
        -------
        list[:class:`PadstackDef <ansys.edb.definition.PadstackDef>`]
        """
        return list(self._db.PadstackDefs)

    @property
    def package_defs(self):
        """Get all Package definitions in this Database.

        Returns
        -------
        list[:class:`PackageDef <ansys.edb.definition.PackageDef>`]
        """
        return list(self._db.PackageDefs)

    @property
    def component_defs(self):
        """Get all component definitions in the database.

        Returns
        -------
        list[:class:`ComponentDef <ansys.edb.definition.ComponentDef>`]
        """
        return list(self._db.ComponentDefs)

    @property
    def material_defs(self):
        """Get all material definitions in the database.

        Returns
        -------
        list[:class:`MaterialDef <ansys.edb.definition.MaterialDef>`]
        """
        return list(self._db.MaterialDefs)

    @property
    def dataset_defs(self):
        """Get all dataset definitions in the database.

        Returns
        -------
        list[:class:`DatasetDef <ansys.edb.definition.DatasetDef>`]
        """
        return list(self._db.DatasetDefs)

    def attach(self, hdb):  # pragma no cover
        """Attach the database to existing AEDT instance.

        Parameters
        ----------
        hdb

        Returns
        -------

        """
        from pyedb.dotnet.clr_module import Convert

        hdl = Convert.ToUInt64(hdb)
        self._db = self.core.database.Attach(hdl)
        return self._db
