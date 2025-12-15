# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ansys.edb.core.utility.hfss_extent_info import (
    HfssExtentInfo as GrpcHfssExtentInfo,
    HFSSExtentInfoType as GrpcHfssExtentInfoType,
    OpenRegionType as GrpcOpenRegionType,
)
from ansys.edb.core.utility.value import Value as GrpcValue


class HfssExtentInfo:
    """Manages EDB functionalities for HFSS extent information.

    Parameters
    ----------
    pedb : :class:`pyedb.grpc.edb.Edb`
        Inherited EDB object.
    """

    def __init__(self, pedb):
        self._pedb = pedb
        self.core = self._pedb.active_cell.hfss_extent_info
        self.extent_type_mapping = {
            "bounding_box": GrpcHfssExtentInfoType.BOUNDING_BOX,
            "conforming": GrpcHfssExtentInfoType.CONFORMING,
            "convex_hull": GrpcHfssExtentInfoType.CONVEX_HUL,
            "polygon": GrpcHfssExtentInfoType.POLYGON,
        }
        self._open_region_type = {
            "radiation": GrpcOpenRegionType.RADIATION,
            "pml": GrpcOpenRegionType.PML,
        }
        self.hfss_extent_type = self.core.extent_type

    def _update_hfss_extent_info(self, hfss_extent):
        return self._pedb.active_cell.set_hfss_extent_info(hfss_extent)

    def get_air_box_horizontal_extent(self) -> (float, bool):
        """Size of horizontal extent for the air box.

        Returns
        -------
        float
            Air box horizontal extent value.
        """
        value, is_multiple = self.core.airbox_horizontal
        if hasattr(value, "value"):
            return float(value.value)
        return float(value), is_multiple

    def set_air_box_horizontal_extent(self, size: float, is_multiple: bool = True):
        hfss_extent = self.core
        hfss_extent.airbox_horizontal = (GrpcValue(size).value, is_multiple)
        self._update_hfss_extent_info(hfss_extent)

    def get_air_box_positive_vertical_extent(self) -> (float, bool):
        """Negative vertical extent for the air box.

        Returns
        -------
        float
            Air box positive vertical extent value.

        """
        value, is_multiple = self.core.airbox_vertical_positive
        if hasattr(value, "value"):
            return float(value.value)
        return float(value), is_multiple

    def set_air_box_positive_vertical_extent(self, size: float, is_multiple: bool):
        hfss_exent = self.core
        hfss_exent.airbox_vertical_positive = (GrpcValue(size).value, is_multiple)
        self._update_hfss_extent_info(hfss_exent)

    def get_air_box_negative_vertical_extent(self) -> (float, bool):
        """Negative vertical extent for the airbox.

        Returns
        -------
        float
            Air box negative vertical extent value.

        """
        value, is_multiple = self.core.airbox_vertical_negative
        if hasattr(value, "value"):
            return float(value.value)
        return float(value), is_multiple

    def set_air_box_negative_vertical_extent(self, size: float, is_multiple: bool = True):
        hfss_extent = self.core
        hfss_extent.airbox_vertical_negative = (GrpcValue(size).value, is_multiple)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def base_polygon(self) -> any:
        """Base polygon.

        Returns
        -------
        :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
        """
        from pyedb.grpc.database.primitive.polygon import Polygon

        obj = self.core.base_polygon
        return Polygon(self._pedb, obj).aedt_name if obj else None

    @base_polygon.setter
    def base_polygon(self, value):
        obj = self._pedb.layout.find_primitive(name=value)[0]
        hfss_extent = self.core
        hfss_extent.base_polygon = obj.core
        self._update_hfss_extent_info(hfss_extent)

    @property
    def dielectric_base_polygon(self) -> any:
        """Dielectric base polygon.

        Returns
        -------
        :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
        """
        from pyedb.grpc.database.primitive.polygon import Polygon

        obj = self.core.dielectric_base_polygon
        return Polygon(self._pedb, obj).aedt_name if obj else None

    @dielectric_base_polygon.setter
    def dielectric_base_polygon(self, value):
        obj = self._pedb.layout.find_primitive(name=value)[0]
        hfss_extent = self.core
        hfss_extent.dielectric_base_polygon = obj.core
        self._update_hfss_extent_info(hfss_extent)

    def get_dielectric_extent(self) -> (float, bool):
        """Dielectric extent size.

        Returns
        -------
        float
            Dielectric extent size value.
        """
        value, is_multiple = self.core.dielectric
        if hasattr(value, "value"):
            return float(value.value)
        return float(value), is_multiple

    def set_dielectric_extent(self, size: float, is_multiple: bool = True):
        hfss_extent = self.core
        hfss_extent.dielectric = (float(size), is_multiple)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def dielectric_extent_type(self) -> str:
        """Dielectric extent type.

        Returns
        -------
        str
            Dielectric extent type.

        """
        return self.core.dielectric_extent_type.name.lower()

    @dielectric_extent_type.setter
    def dielectric_extent_type(self, value):
        hfss_extent = self.core
        hfss_extent.dielectric_extent_type = self.extent_type_mapping[value]
        self._update_hfss_extent_info(hfss_extent)

    @property
    def extent_type(self) -> str:
        """Extent type.

        Returns
        -------
        str
            Extent type.
        """
        return self.core.extent_type.name.lower()

    @extent_type.setter
    def extent_type(self, value):
        hfss_extent = self.core
        hfss_extent.extent_type = self.extent_type_mapping[value]
        self._update_hfss_extent_info(hfss_extent)

    @property
    def honor_user_dielectric(self) -> bool:
        """Honor user dielectric.

        Returns
        -------
        bool
        """
        return self.core.honor_user_dielectric

    @honor_user_dielectric.setter
    def honor_user_dielectric(self, value):
        hfss_extent = self.core
        hfss_extent.honor_user_dielectric = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def is_pml_visible(self) -> bool:
        """Whether visibility of the PML is enabled.

        Returns
        -------
        bool

        """
        return self.core.is_pml_visible

    @is_pml_visible.setter
    def is_pml_visible(self, value):
        hfss_extent = self.core
        hfss_extent.is_pml_visible = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def open_region_type(self) -> str:
        """Open region type.

        Returns
        -------
        str
            Open region type.
        """
        return self.core.open_region_type.name.lower()

    @open_region_type.setter
    def open_region_type(self, value):
        hfss_extent = self.core
        hfss_extent.open_region_type = self._open_region_type[value]
        self._update_hfss_extent_info(hfss_extent)

    @property
    def operating_freq(self) -> float:
        """PML Operating frequency.

        Returns
        -------
        float
            Operating frequency value.

        """
        freq_value = self.core.operating_frequency
        if hasattr(freq_value, "value"):
            return float(freq_value.value)
        return float(freq_value)

    @operating_freq.setter
    def operating_freq(self, value):
        hfss_extent = self.core
        hfss_extent.operating_frequency = GrpcValue(value)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def radiation_level(self) -> float:
        """PML Radiation level to calculate the thickness of boundary.

        Returns
        -------
        float
            Boundary thickness value.

        """
        rad_level = self.core.radiation_level
        if hasattr(rad_level, "value"):
            return float(rad_level.value)
        return float(rad_level)

    @radiation_level.setter
    def radiation_level(self, value):
        hfss_extent = self.core
        hfss_extent.radiation_level = GrpcValue(value)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def sync_air_box_vertical_extent(self) -> bool:
        """Vertical extent of the sync air box.

        Returns
        -------
        bool
            Synchronise vertical extent.

        """
        return self.core.sync_airbox_vertical_extent

    @sync_air_box_vertical_extent.setter
    def sync_air_box_vertical_extent(self, value):
        hfss_extent = self.core
        hfss_extent.sync_airbox_vertical_extent = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def truncate_air_box_at_ground(self) -> bool:
        """Truncate air box at ground.

        Returns
        -------
        bool
            Truncate air box at ground.

        """
        return self.core.airbox_truncate_at_ground

    @truncate_air_box_at_ground.setter
    def truncate_air_box_at_ground(self, value):
        hfss_extent = self.core
        hfss_extent.airbox_truncate_at_ground = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def use_open_region(self) -> bool:
        """Whether using an open region is enabled.

        Returns
        -------
        bool
            Use open region.

        """
        return self.core.use_open_region

    @use_open_region.setter
    def use_open_region(self, value):
        hfss_extent = self.core
        hfss_extent.use_open_region = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def use_xy_data_extent_for_vertical_expansion(self) -> bool:
        """Whether using the xy data extent for vertical expansion is enabled.

        Returns
        -------
        bool
            USe x y data extent for vertical expansion.

        """
        return self.core.user_xy_data_extent_for_vertical_expansion

    @use_xy_data_extent_for_vertical_expansion.setter
    def use_xy_data_extent_for_vertical_expansion(self, value):
        hfss_extent = self.core
        hfss_extent.user_xy_data_extent_for_vertical_expansion = value
        self._update_hfss_extent_info(hfss_extent)

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

    def export_config(self):
        """Export HFSS extent information.

        Returns
        -------
        dict
            Parameters of the HFSS extent information.
        """
        config = dict()
        # Skip properties that return enum names as strings since they can't be easily round-tripped
        skip_properties = [
            "extent_type_mapping",
            "hfss_extent_type",
            "dielectric_extent_type",
            "open_region_type",
            "base_polygon",
            "dielectric_base_polygon",
        ]
        for i in dir(self):
            if i.startswith("_"):
                continue
            elif i in ["load_config", "export_config"] + skip_properties:
                continue
            else:
                try:
                    config[i] = getattr(self, i)
                except (AttributeError, TypeError, ValueError, RuntimeError):
                    pass  # Skip properties that can't be accessed
        return config
