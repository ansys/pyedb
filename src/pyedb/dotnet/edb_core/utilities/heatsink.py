class HeatSink:

    """Heatsink model description.

    Parameters
    ----------
    pedb : :class:`pyedb.dotnet.edb.Edb`
        Inherited object.
    edb_object : :class:`Ansys.Ansoft.Edb.Utility.HeatSink`,
    """

    def __init__(self, pedb, edb_object=None):
        self._pedb = pedb
        self._fin_orientation_type = {
            "x_oriented": self._pedb.edb_api.utility.utility.HeatSinkFinOrientation.XOriented,
            "y_oriented": self._pedb.edb_api.utility.utility.HeatSinkFinOrientation.YOriented,
            "other_oriented": self._pedb.edb_api.utility.utility.HeatSinkFinOrientation.OtherOriented,
        }

        if edb_object:
            self._edb_object = edb_object
        else:
            self._edb_object = self._pedb.edb_api.utility.utility.HeatSink()

    @property
    def fin_base_height(self):
        """The base elevation of the fins."""
        return self._edb_object.FinBaseHeight.ToDouble()

    @fin_base_height.setter
    def fin_base_height(self, value):
        self._edb_object.FinBaseHeight = self._pedb.edb_value(value)

    @property
    def fin_height(self):
        """The fin height."""
        return self._edb_object.FinHeight.ToDouble()

    @fin_height.setter
    def fin_height(self, value):
        self._edb_object.FinHeight = self._pedb.edb_value(value)

    @property
    def fin_orientation(self):
        """The fin orientation."""
        temp = self._edb_object.FinOrientation
        return list(self._fin_orientation_type.keys())[list(self._fin_orientation_type.values()).index(temp)]

    @fin_orientation.setter
    def fin_orientation(self, value):
        self._edb_object.FinOrientation = self._fin_orientation_type[value]

    @property
    def fin_spacing(self):
        """The fin spacing."""
        return self._edb_object.FinSpacing.ToDouble()

    @fin_spacing.setter
    def fin_spacing(self, value):
        self._edb_object.FinSpacing = self._pedb.edb_value(value)

    @property
    def fin_thickness(self):
        """The fin thickness."""
        return self._edb_object.FinThickness.ToDouble()

    @fin_thickness.setter
    def fin_thickness(self, value):
        self._edb_object.FinThickness = self._pedb.edb_value(value)
