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

from typing import List

from ezdxf import readfile

from pyedb import Edb
from pyedb.grpc.database.primitive.primitive import Primitive

# TODO: Fix units issue


def create_polygon_from_dxf(edb: Edb, dxf_path: str, layer_name: str) -> Primitive:
    """
    Create a polygon primitive in the EDB layout from the first entity
    found in a DXF file.

    Parameters
    ----------
    edb : Edb
        An active EDB (Electronics Database) instance that the polygon
        will be added to.
    dxf_path : str
        Absolute or relative path to the DXF file containing the
        geometry to import.
    layer_name : str
        Name of the EDB layer on which the polygon will be created.

    Returns
    -------
    Primitive
        The newly created polygon primitive object.

    Notes
    -----
    * Only the first entity in the DXF modelspace is used; all other
      entities are ignored.
    * Coordinates in the DXF are assumed to be in **microns** and are
      divided by 1000 to convert to **millimetres** before being passed
      to EDB.
    * The resulting polygon is **not** translated or rotated; it is
      placed exactly as defined in the DXF (after scaling).

    Examples
    --------
    >>> edb = Edb(edbpath="my_design.aedb")
    >>> poly = create_polygon_from_dxf(edb, dxf_path="outline.dxf", layer_name="Outline")
    >>> print(poly)
    <pyedb.dotnet.edb_core.edb_data.primitives.EDBPrimitives object ...>
    """
    doc = readfile(dxf_path)
    msp = doc.modelspace()
    shape = msp[0]
    points = list(shape.get_points())
    points_2D = [point[:2] for point in points]
    points_2D = [[x / 1000, y / 1000] for x, y in points_2D]
    return edb.modeler.create_polygon(points_2D, layer_name=layer_name)


def swap_polygon_with_dxf(edb: Edb, dxf_path: str, layer_name: str, point_dxf: List[str], point_aedt: List[str]):
    """
    Replace an existing polygon on a given layer with a new polygon
    imported from a DXF file, aligning the two geometries via reference
    points.

    Parameters
    ----------
    edb : Edb
        An active EDB instance.
    dxf_path : str
        Path to the DXF file that contains the replacement geometry.
    layer_name : str
        Layer on which the old polygon will be deleted and the new one
        created.
    point_dxf : List[str]
        Two-element list of strings specifying the **reference point**
        inside the DXF geometry (units: **mm**).
        Example: ``["-1.5", "4.2"]``.
    point_aedt : List[str]
        Two-element list of strings specifying the **target location**
        in the EDB layout where the DXF reference point should land
        (units: **mm**).
        Example: ["12.0", "7.5"].

    Returns
    -------
    None
        The function operates in-place on the provided EDB instance.

    Workflow
    --------
    1. Identify and delete the existing polygon that encloses
       ``point_aedt`` on the specified layer.
    2. Import the first entity from the DXF file as a new polygon on
       the same layer (see :func:`create_polygon_from_dxf`).
    3. Translate the new polygon so that ``point_dxf`` coincides with
       ``point_aedt``.

    Notes
    -----
    * Only the first entity in the DXF modelspace is used.
    * Both input points are internally converted to **metres** before
      computing the translation vector.
    * The translation vector is then scaled back to **millimetres**
      and expressed as strings with an "mm" suffix, as required by
      the EDB move API.

    Examples
    --------
    >>> edb = Edb(edbpath="design.aedb")
    >>> swap_polygon_with_dxf(
    ...     edb,
    ...     dxf_path="new_outline.dxf",
    ...     layer_name="Outline",
    ...     point_dxf=["0", "0"],  # Origin in DXF
    ...     point_aedt=["10", "5"],  # Where DXF origin should land
    ... )
    >>> edb.save()
    """
    if not float(edb.version) >= 2025.2:
        raise AttributeError("This function is only supported with ANSYS release 2025R2 and higher.")
    prim_to_delete = edb.modeler.get_primitive_by_layer_and_point(point=point_aedt, layer=layer_name)
    prim_to_delete = prim_to_delete[0]
    prim_to_delete.delete()

    dxf_polygon = create_polygon_from_dxf(edb, dxf_path, layer_name)

    point_dxf_double = [
        edb.value(point_dxf[0]),
        edb.value(point_dxf[1]),
    ]
    point_aedt_double = [
        edb.value(point_aedt[0]),
        edb.value(point_aedt[1]),
    ]
    move_vector_double = [
        point_aedt_double[0] - point_dxf_double[0],
        point_aedt_double[1] - point_dxf_double[1],
    ]
    move_vector = [
        f"{1000 * move_vector_double[0]}mm",
        f"{1000 * move_vector_double[1]}mm",
    ]

    dxf_polygon.move(vector=move_vector)
    edb.modeler._reload_all()


def swap_polygon_with_dxf_center_point(edb: Edb, dxf_path: str, layer_name: str, point_aedt: List[str]):
    """
    Replace an existing polygon on a given layer with a new polygon
    imported from a DXF file, aligning the two geometries via reference
    points. Uses the center point of the DXF polygon as reference (not an input point).

    Parameters
    ----------
    edb : Edb
        An active EDB instance.
    dxf_path : str
        Path to the DXF file that contains the replacement geometry.
    layer_name : str
        Layer on which the old polygon will be deleted and the new one
        created.
    point_aedt : List[str]
        Two-element list of strings specifying the **target location**
        in the EDB layout where the DXF reference point should land
        (units: **mm**).
        Example: ["12.0", "7.5"].

    Returns
    -------
    None
        The function operates in-place on the provided EDB instance.

    Workflow
    --------
    1. Identify and delete the existing polygon that encloses
       ``point_aedt`` on the specified layer.
    2. Import the first entity from the DXF file as a new polygon on
       the same layer (see :func:`create_polygon_from_dxf`).
    3. Translate the new polygon so that ``point_dxf`` coincides with
       ``point_aedt``.

    Notes
    -----
    * Only the first entity in the DXF modelspace is used.
    * Both input points are internally converted to **metres** before
      computing the translation vector.
    * The translation vector is then scaled back to **millimetres**
      and expressed as strings with an "mm" suffix, as required by
      the EDB move API.

    Examples
    --------
    >>> edb = Edb(edbpath="design.aedb")
    >>> swap_polygon_with_dxf(
    ...     edb,
    ...     dxf_path="new_outline.dxf",
    ...     layer_name="Outline",
    ...     point_aedt=["10", "5"],  # Where DXF origin should land
    ... )
    >>> edb.save()
    """
    if not float(edb.version) >= 2025.2:
        raise AttributeError("This function is only supported with ANSYS release 2025R2 and higher.")
    prim_to_delete = edb.modeler.get_primitive_by_layer_and_point(point=point_aedt, layer=layer_name)
    prim_to_delete = prim_to_delete[0]
    prim_to_delete.delete()

    dxf_polygon = create_polygon_from_dxf(edb, dxf_path, layer_name)
    point_dxf = dxf_polygon.center
    point_dxf = [f"{x.value * 1000}mm" for x in point_dxf]

    point_dxf_double = [
        edb.value(point_dxf[0]),
        edb.value(point_dxf[1]),
    ]
    point_aedt_double = [
        edb.value(point_aedt[0]),
        edb.value(point_aedt[1]),
    ]
    move_vector_double = [
        point_aedt_double[0] - point_dxf_double[0],
        point_aedt_double[1] - point_dxf_double[1],
    ]
    move_vector = [
        f"{1000 * move_vector_double[0].value}mm",
        f"{1000 * move_vector_double[1].value}mm",
    ]

    dxf_polygon.move(vector=move_vector)
    edb.modeler._reload_all()  # Force reload to update primitive positions in EDB GUI
