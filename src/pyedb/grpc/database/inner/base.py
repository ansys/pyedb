from ansys.edb.core.inner.base import ObjBase as GRPCObjBase


class ObjBase:
    def __init__(self, pedb, edb_object):
        self.core = edb_object
        self._pedb = pedb

    @property
    def is_null(self):
        """Check if the terminal is a null terminal.

        Returns
        -------
        bool
            ``True`` if the terminal is a null terminal, ``False`` otherwise.
        """
        return self.core.is_null