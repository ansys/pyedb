from pyedb.dotnet.edb_core.geometry.point_data import PointData
from pyedb.dotnet.edb_core.obj_base import BBox
from pyedb.generic.general_methods import pyedb_function_handler


class PolygonData:
    """Polygon Data."""

    def __init__(
        self,
        pedb,
        edb_object=None,
        create_from_points=None,
        create_from_circle=None,
        create_from_rectangle=None,
        create_from_bounding_box=None,
        **args,
    ):
        self._pedb = pedb

        if create_from_points:
            self._edb_object = self.create_from_points(**args)
        elif create_from_circle:
            x_center, y_center, radius = args
        elif create_from_rectangle:
            x_lower_left, y_lower_left, x_upper_right, y_upper_right = args
        elif create_from_bounding_box:
            self._edb_object = self.create_from_bounding_box(**args)
        else:  # pragma: no cover
            self._edb_object = edb_object

    @property
    def points(self):
        """Get all points in polygon.

        Returns
        -------
        list[list[float]]
        """
        return [
            [self._pedb.edb_value(i.X).ToDouble(), self._pedb.edb_value(i.Y).ToDouble()]
            for i in list(self._edb_object.Points)
        ]

    @pyedb_function_handler
    def create_from_points(self, points, closed=True):
        list_of_point_data = []
        for pt in points:
            list_of_point_data.append(PointData(self._pedb, x=pt[0], y=pt[1]))
        return self._pedb.edb_api.geometry.api_class.PolygonData(list_of_point_data, closed)

    @pyedb_function_handler
    def create_from_bounding_box(self, points):
        bbox = BBox(self._pedb, point_1=points[0], point_2=points[1])
        return self._pedb.edb_api.geometry.api_class.PolygonData.CreateFromBBox(bbox._edb_object)
