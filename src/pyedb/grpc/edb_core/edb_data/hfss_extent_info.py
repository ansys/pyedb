from ansys.edb.core.utility import Value

from pyedb.generic.general_methods import pyedb_function_handler


class HfssExtentInfo:
    """Manages EDB functionalities for HFSS extent information.

    Parameters
    ----------
    pedb : :class:`pyaedt.edb.Edb`
        Inherited AEDT object.
    """

    def __init__(self, pedb):
        self._pedb = pedb

        self._hfss_extent_info_type = {
            "BoundingBox": self._pedb.edb_api.utility.utility.HFSSExtentInfoType.BOUNDING_BOX,
            "Conforming": self._pedb.edb_api.utility.utility.HFSSExtentInfoType.CONFORMING,
            "ConvexHull": self._pedb.edb_api.utility.utility.HFSSExtentInfoType.CONVEX_HULL,
            "Polygon": self._pedb.edb_api.utility.utility.HFSSExtentInfoType.POLYGON,
        }
        self._open_region_type = {
            "Radiation": self._pedb.edb_api.utility.utility.OpenRegionType.RADIATION,
            "PML": self._pedb.edb_api.utility.utility.OpenRegionType.PML,
        }

    @pyedb_function_handler
    def _update_hfss_extent_info(self, hfss_extent_info):
        return self._pedb.active_cell.set_hfss_extent_info(hfss_extent_info)

    @property
    def _edb_hfss_extent_info(self):
        return self._pedb.active_cell.hfss_extent_info

    @property
    def air_box_horizontal_extent(self):
        """Size of horizontal extent for the air box.

        Returns:
        (float, bool)
            First parameter is the value and second parameter indicates if the value is a multiple
        """
        return self._edb_hfss_extent_info.airbox_horizontal

    @air_box_horizontal_extent.setter
    def air_box_horizontal_extent(self, value, multiple=True):
        info = self._edb_hfss_extent_info
        info.AirBoxHorizontalExtent = (value, multiple)
        self._update_hfss_extent_info(info)

    @property
    def air_box_positive_vertical_extent(self):
        """Negative vertical extent for the air box.

        Returns:
        (float, bool)
            First parameter is the value and second parameter indicates if the value is a multiple
        """
        return self._edb_hfss_extent_info.airbox_vertical_positive

    @air_box_positive_vertical_extent.setter
    def air_box_positive_vertical_extent(self, value, multiple=True):
        info = self._edb_hfss_extent_info
        info.AirBoxPositiveVerticalExtent = (value, multiple)
        self._update_hfss_extent_info(info)

    @property
    def air_box_negative_vertical_extent(self):
        """Negative vertical extent for the air box.

        Returns:
        (float, bool)
            First parameter is the value and second parameter indicates if the value is a multiple
        """
        return self._edb_hfss_extent_info.airbox_vertical_negative

    @air_box_negative_vertical_extent.setter
    def air_box_negative_vertical_extent(self, value, multiple=True):
        info = self._edb_hfss_extent_info
        info.AirBoxNegativeVerticalExtent = (value, multiple)
        self._update_hfss_extent_info(info)

    @property
    def base_polygon(self):
        """Base polygon.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitive`
        """
        return self._edb_hfss_extent_info.base_polygon

    @base_polygon.setter
    def base_polygon(self, value):
        info = self._edb_hfss_extent_info
        info.base_polygon = value.primitive_object
        self._update_hfss_extent_info(info)

    @property
    def dielectric_base_polygon(self):
        """Dielectric base polygon.

        Returns
        -------
        :class:`pyaedt.edb_core.edb_data.primitives_data.EDBPrimitive`
        """
        return self._edb_hfss_extent_info.dielectric_base_polygon

    @dielectric_base_polygon.setter
    def dielectric_base_polygon(self, value):
        info = self._edb_hfss_extent_info
        info.dielectric_base_polygon = value.primitive_object
        self._update_hfss_extent_info(info)

    @property
    def dielectric_extent_size(self):
        """Dielectric extent size.

        Returns:
        (float, bool)
            First parameter is the value and second parameter indicates if the value is a multiple
        """
        return self._edb_hfss_extent_info.dielectric

    @dielectric_extent_size.setter
    def dielectric_extent_size(self, value, multiple=True):
        info = self._edb_hfss_extent_info
        info.DielectricExtentSize = (value, multiple)
        self._update_hfss_extent_info(info)

    @property
    def dielectric_extent_type(self):
        """Dielectric extent type.

        Return:
            HFSSExtentInfoType
        """
        return self._edb_hfss_extent_info.dielectric_extent_type

    @dielectric_extent_type.setter
    def dielectric_extent_type(self, value):
        if isinstance(value, int):
            info = self._edb_hfss_extent_info
            info.dielectric_extent_type.value = value
            self._update_hfss_extent_info(info)

    @property
    def extent_type(self):
        """Extent type.

        Returns:
            HFSSExtentInfoType (for example HFSSExtentInfoType.CONVEX_HUL)
        """
        return self._edb_hfss_extent_info.extent_type

    @extent_type.setter
    def extent_type(self, value):
        if isinstance(value, int):
            info = self._edb_hfss_extent_info
            info.extent_type.value = value
            self._update_hfss_extent_info(info)

    @property
    def honor_user_dielectric(self):
        """Honor user dielectric.

        Returns:
            bool.
        """
        return self._edb_hfss_extent_info.honor_user_dielectric

    @honor_user_dielectric.setter
    def honor_user_dielectric(self, value):
        info = self._edb_hfss_extent_info
        info.honor_user_dielectric = value
        self._update_hfss_extent_info(info)

    @property
    def is_pml_visible(self):
        """Whether visibility of the PML is enabled.

        Returns:
            bool.
        """
        return self._edb_hfss_extent_info.is_pml_visible

    @is_pml_visible.setter
    def is_pml_visible(self, value):
        info = self._edb_hfss_extent_info
        info.is_pml_visible = value
        self._update_hfss_extent_info(info)

    @property
    def open_region_type(self):
        """Open region type.

        Returns:
            OpenRegionType (example OpenRegionType.RADIATION).
        """
        return self._edb_hfss_extent_info.open_region_type

    @open_region_type.setter
    def open_region_type(self, value):
        if isinstance(value, int):
            info = self._edb_hfss_extent_info
            info.open_region_type.value = value
            self._update_hfss_extent_info(info)

    @property
    def operating_freq(self):
        """Operating frequency.

        Returns
        -------
        pyaedt.edb_core.edb_data.edbvalue.EdbValue
        """
        return self._edb_hfss_extent_info.operating_frequency

    @operating_freq.setter
    def operating_freq(self, value):
        value = value if isinstance(value, Value) else Value(value)
        info = self._edb_hfss_extent_info
        info.operating_frequency = value
        self._update_hfss_extent_info(info)

    @property
    def radiation_level(self):
        """Radiation level."""
        return self._edb_hfss_extent_info.radiation_level

    @radiation_level.setter
    def radiation_level(self, value):
        value = value if isinstance(value, Value) else Value(value)
        info = self._edb_hfss_extent_info
        info.radiation_level = value
        self._update_hfss_extent_info(info)

    @property
    def sync_air_box_vertical_extent(self):
        """Vertical extent of the sync air box."""
        return self._edb_hfss_extent_info.sync_airbox_vertical_extent

    @sync_air_box_vertical_extent.setter
    def sync_air_box_vertical_extent(self, value):
        if isinstance(value, bool):
            info = self._edb_hfss_extent_info
            info.sync_airbox_vertical_extent = value
            self._update_hfss_extent_info(info)

    @property
    def truncate_air_box_at_ground(self):
        """Truncate air box at ground."""
        return self._edb_hfss_extent_info.airbox_truncate_at_ground

    @truncate_air_box_at_ground.setter
    def truncate_air_box_at_ground(self, value):
        if isinstance(value, bool):
            info = self._edb_hfss_extent_info
            info.airbox_truncate_at_ground = value
            self._update_hfss_extent_info(info)

    @property
    def use_open_region(self):
        """Whether using an open region is enabled."""
        return self._edb_hfss_extent_info.use_open_region

    @use_open_region.setter
    def use_open_region(self, value):
        if isinstance(value, bool):
            info = self._edb_hfss_extent_info
            info.use_open_region = value
            self._update_hfss_extent_info(info)

    @property
    def use_xy_data_extent_for_vertical_expansion(self):
        """Whether using the xy data extent for vertical expansion is enabled."""
        return self._edb_hfss_extent_info.user_xy_data_extent_for_vertical_expansion

    @use_xy_data_extent_for_vertical_expansion.setter
    def use_xy_data_extent_for_vertical_expansion(self, value):
        if isinstance(value, bool):
            info = self._edb_hfss_extent_info
            info.user_xy_data_extent_for_vertical_expansion = value
            self._update_hfss_extent_info(info)

    @pyedb_function_handler
    def load_config(self, config):
        """Load HFSS extent configuration.

        Parameters
        ----------
        config: dict
            Parameters of the HFSS extent information.
        """
        for i, j in config.items():
            if hasattr(self, i):
                setattr(self, i, j)

    @pyedb_function_handler
    def export_config(self):
        """Export HFSS extent information.

        Returns:
        dict
            Parameters of the HFSS extent information.
        """
        config = dict()
        for i in dir(self):
            if i.startswith("_"):
                continue
            elif i in ["load_config", "export_config"]:
                continue
            else:
                config[i] = getattr(self, i)
        return config
