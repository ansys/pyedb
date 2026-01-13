from ansys.edb.core.database import ProductIdType as GrpcProductIdType
from pyedb.grpc.database.inner.base import ObjBase

class LayoutObj(ObjBase):
    """Represents a layout object."""
    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def _edb_properties(self):
        p = self.core.get_product_property(GrpcProductIdType.DESIGNER, 18)
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        self.core.set_product_property(GrpcProductIdType.DESIGNER, 18, value)
