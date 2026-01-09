from pyedb.grpc.database.inner.layout_obj import LayoutObj

class ConnObj(LayoutObj):
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)