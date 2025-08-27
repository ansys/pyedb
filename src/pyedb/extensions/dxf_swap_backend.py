from ezdxf import readfile
from typing import List

from pyedb import Edb
from pyedb.dotnet.database.cell.primitive.primitive import Primitive


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
    >>> poly = create_polygon_from_dxf(edb,
    ...          dxf_path="outline.dxf",
    ...          layer_name="Outline")
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


def swap_polygon_with_dxf(edb: Edb,
                          dxf_path: str,
                          layer_name: str,
                          point_dxf: List[str],
                          point_aedt: List[str]):
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
    ...     point_dxf=["0", "0"],        # Origin in DXF
    ...     point_aedt=["10", "5"]       # Where DXF origin should land
    ... )
    >>> edb.save()
    """
    prim_to_delete = edb.modeler.get_primitive_by_layer_and_point(
        point=point_aedt, layer=layer_name
    )
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
