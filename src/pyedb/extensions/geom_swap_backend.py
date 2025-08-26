from ezdxf import readfile
from typing import List

from pyedb import Edb
from pyedb.dotnet.database.cell.primitive.primitive import Primitive


#TO-DO: Fix units issue
def create_polygon_from_dxf(edb: Edb, dxf_path: str, layer_name: str) -> Primitive:
    doc = readfile(dxf_path)
    msp = doc.modelspace()
    shape = msp[0]
    points = list(shape.get_points())
    points_2D = [point[:2] for point in points]
    points_2D = [[x/1000, y/1000] for x,y in points_2D]
    return edb.modeler.create_polygon(points_2D, layer_name=layer_name)

#TO-DO: Check landing place of dxf polygon
def swap_polygon_with_dxf(edb: Edb, dxf_path: str, layer_name: str, point_dxf: List[str], point_aedt: List[str]):
    prim_to_delete = edb.modeler.get_primitive_by_layer_and_point(point=point_aedt, layer=layer_name)
    prim_to_delete = prim_to_delete[0]
    prim_to_delete.delete()

    dxf_polygon = create_polygon_from_dxf(edb, dxf_path, layer_name)

    point_dxf_double = [edb.edb_value(point_dxf[0]).ToDouble(), edb.edb_value(point_dxf[1]).ToDouble()]
    point_aedt_double = [edb.edb_value(point_aedt[0]).ToDouble(), edb.edb_value(point_aedt[1]).ToDouble()]
    move_vector_double = [point_aedt_double[0] - point_dxf_double[0], point_aedt_double[1] - point_dxf_double[1]]
    move_vector = [str(1000 * move_vector_double[0]) + "mm", str(1000 * move_vector_double[1]) + "mm"]

    move_result = dxf_polygon.move(vector=move_vector)

