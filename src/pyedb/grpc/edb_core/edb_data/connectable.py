from src.pyedb.generic.general_methods import pyedb_function_handler


class LayoutObj(object):
    """Manages EDB functionalities for the layout object."""

    def __getattr__(self, key):  # pragma: no cover
        try:
            return super().__getattribute__(key)
        except AttributeError:
            try:
                return getattr(self._edb_object, key)
            except AttributeError:
                raise AttributeError("Attribute not present")

    def __init__(self, pedb, edb_object):
        self._pedb = pedb
        self._edb_object = edb_object

    @property
    def _edb(self):
        """EDB object.

        Returns
        -------
        Ansys.Ansoft.Edb
        """
        return self._pedb

    @property
    def _layout(self):
        """Return Ansys.Ansoft.Edb.Cell.Layout object."""
        return self._pedb.active_layout

    @property
    def _edb_properties(self):
        p = self._edb_object.product_solver_option(self._edb.database.ProductIdType.DESIGNER, "HFSS")
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        self._edb_object.product_solver_option(self._edb.database.ProductIdType.DESIGNER, "HFSS", value)

    @property
    def is_null(self):
        """Determine if this object is null."""
        return self._edb_object.is_null

    @property
    def id(self):
        """Primitive ID.

        Returns
        -------
        int
        """
        return self._edb_object.id

    @pyedb_function_handler()
    def delete(self):
        """Delete this primitive."""
        self._edb_object.delete()
        return True


class Connectable(LayoutObj):
    """Manages EDB functionalities for a connectable object."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)

    @property
    def net(self):
        """Net Object.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.nets_data.EDBNetsData`
        """
        from edb_core.edb_data.nets_data import EDBNetsData

        return EDBNetsData(self._edb_object.net, self._pedb)

    @property
    def component(self):
        """Component connected to this object.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.nets_data.EDBComponent`
        """
        from edb_core.edb_data.components_data import EDBComponent

        edb_comp = self._edb_object.component
        if edb_comp.is_null:
            return None
        else:
            return EDBComponent(self._pedb, edb_comp)
