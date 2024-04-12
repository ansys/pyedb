class PointData:
    """Point Data."""

    def __init__(self, pedb, edb_object=None, x=None, y=None):
        self._pedb = pedb
        if edb_object:
            self._edb_object = edb_object
        else:
            self._edb_object = self._pedb.edb_api.geometry.point_data(
                self._pedb.edb_value(x),
                self._pedb.edb_value(y),
            )
