# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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
    HFSSExtentInfoType as GrpcHfssExtentInfoType,
)
from ansys.edb.core.utility.hfss_extent_info import HfssExtentInfo as GrpcHfssExtentInfo
from ansys.edb.core.utility.hfss_extent_info import OpenRegionType as GrpcOpenRegionType
from ansys.edb.core.utility.value import Value as GrpcValue


class HfssExtentInfo(GrpcHfssExtentInfo):
    """Manages EDB functionalities for HFSS extent information.

    Parameters
    ----------
    pedb : :class:`pyedb.grpc.edb.Edb`
        Inherited EDB object.
    """

    def __init__(self, pedb):
        self._pedb = pedb
        super().__init__()
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
        self.hfss_extent_type = self._hfss_extent_info.extent_type

    def _update_hfss_extent_info(self, hfss_extent):
        return self._pedb.active_cell.set_hfss_extent_info(hfss_extent)

    @property
    def _hfss_extent_info(self):
        return self._pedb.active_cell.hfss_extent_info

    @property
    def air_box_horizontal_extent_enabled(self):
        """Whether horizontal extent is enabled for the airbox.

        Returns
        -------
        bool.

        """
        return self._hfss_extent_info.air_box_horizontal_extent[1]

    @air_box_horizontal_extent_enabled.setter
    def air_box_horizontal_extent_enabled(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.air_box_horizontal_extent = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def air_box_horizontal_extent(self):
        """Size of horizontal extent for the air box.

        Returns
        -------
        float
            Air box horizontal extent value.
        """
        return self._hfss_extent_info.airbox_horizontal[0]

    @air_box_horizontal_extent.setter
    def air_box_horizontal_extent(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.airbox_horizontal = (float(value), True)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def air_box_positive_vertical_extent_enabled(self):
        """Whether positive vertical extent is enabled for the air box.

        Returns
        -------
        bool.

        """
        return self._hfss_extent_info.airbox_vertical_positive[1]

    @air_box_positive_vertical_extent_enabled.setter
    def air_box_positive_vertical_extent_enabled(self, value):
        hfss_exent = self._hfss_extent_info
        hfss_exent.airbox_vertical_positive = (0.15, value)
        self._update_hfss_extent_info(hfss_exent)

    @property
    def air_box_positive_vertical_extent(self):
        """Negative vertical extent for the air box.

        Returns
        -------
        float
            Air box positive vertical extent value.

        """
        return self._hfss_extent_info.airbox_vertical_positive[0]

    @air_box_positive_vertical_extent.setter
    def air_box_positive_vertical_extent(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.airbox_vertical_positive = (float(value), True)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def air_box_negative_vertical_extent_enabled(self):
        """Whether negative vertical extent is enabled for the air box.

        Returns
        -------
        bool.

        """
        return self._hfss_extent_info.airbox_vertical_negative[1]

    @air_box_negative_vertical_extent_enabled.setter
    def air_box_negative_vertical_extent_enabled(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.airbox_vertical_negative = (0.15, value)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def air_box_negative_vertical_extent(self):
        """Negative vertical extent for the airbox.

        Returns
        -------
        float
            Air box negative vertical extent value.

        """
        return self._hfss_extent_info.airbox_vertical_negative[0]

    @air_box_negative_vertical_extent.setter
    def air_box_negative_vertical_extent(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.airbox_vertical_negative = (float(value), True)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def base_polygon(self):
        """Base polygon.

        Returns
        -------
        :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
        """
        return self._hfss_extent_info.base_polygon

    @base_polygon.setter
    def base_polygon(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.base_polygon = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def dielectric_base_polygon(self):
        """Dielectric base polygon.

        Returns
        -------
        :class:`Polygon <pyedb.grpc.database.primitive.polygon.Polygon>`
        """
        return super().dielectric_base_polygon

    @dielectric_base_polygon.setter
    def dielectric_base_polygon(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.dielectric_base_polygon = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def dielectric_extent_size_enabled(self):
        """Whether dielectric extent size is enabled.

        Returns
        -------
        bool.
        """
        return self._hfss_extent_info.dielectric_extent_size[1]

    @dielectric_extent_size_enabled.setter
    def dielectric_extent_size_enabled(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.dielectric_extent_size = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def dielectric_extent_size(self):
        """Dielectric extent size.

        Returns
        -------
        float
            Dielectric extent size value.
        """
        return self._hfss_extent_info.dielectric[0]

    @dielectric_extent_size.setter
    def dielectric_extent_size(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.dielectric = (value, True)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def dielectric_extent_type(self):
        """Dielectric extent type.

        Returns
        -------
        str
            Dielectric extent type.

        """
        return self._hfss_extent_info.dielectric_extent_type.name.lower()

    @dielectric_extent_type.setter
    def dielectric_extent_type(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.dielectric_extent_type = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def extent_type(self):
        """Extent type.

        Returns
        -------
        str
            Extent type.
        """
        return self._hfss_extent_info.extent_type.name.lower()

    @extent_type.setter
    def extent_type(self, value):
        hfss_extent = self._hfss_extent_info
        if isinstance(value, str):
            if value.lower() == "bounding_box":
                value = GrpcHfssExtentInfoType.BOUNDING_BOX
            elif value.lower() == "conforming":
                value = GrpcHfssExtentInfoType.CONFORMING
            elif value.lower() == "convex_hul":
                value = GrpcHfssExtentInfoType.CONVEX_HUL
            elif value.lower() == "polygon":
                value = GrpcHfssExtentInfoType.POLYGON
            else:
                raise f"Invalid extent type : {value}"
        hfss_extent.extent_type = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def honor_user_dielectric(self):
        """Honor user dielectric.

        Returns
        -------
        bool
        """
        return self._hfss_extent_info.honor_user_dielectric

    @honor_user_dielectric.setter
    def honor_user_dielectric(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.honor_user_dielectric = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def is_pml_visible(self):
        """Whether visibility of the PML is enabled.

        Returns
        -------
        bool

        """
        return self._hfss_extent_info.is_pml_visible

    @is_pml_visible.setter
    def is_pml_visible(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.is_pml_visible = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def open_region_type(self):
        """Open region type.

        Returns
        -------
        str
            Open region type.
        """
        return self._hfss_extent_info.open_region_type.name.lower()

    @open_region_type.setter
    def open_region_type(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.open_region_type = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def operating_freq(self):
        """PML Operating frequency.

        Returns
        -------
        float
            Operating frequency value.

        """
        return GrpcValue(self._hfss_extent_info.operating_frequency).value

    @operating_freq.setter
    def operating_freq(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.operating_frequency = GrpcValue(value)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def pml_radiation_factor(self):
        """PML Radiation level to calculate the thickness of boundary.

        Returns
        -------
        float
            Boundary thickness value.

        """
        return self._hfss_extent_info.radiation_level.value

    @pml_radiation_factor.setter
    def pml_radiation_factor(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.radiation_level = GrpcValue(value)
        self._update_hfss_extent_info(hfss_extent)

    @property
    def sync_air_box_vertical_extent(self):
        """Vertical extent of the sync air box.

        Returns
        -------
        bool
            Synchronise vertical extent.

        """
        return self._hfss_extent_info.sync_air_box_vertical_extent

    @sync_air_box_vertical_extent.setter
    def sync_air_box_vertical_extent(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.sync_air_box_vertical_extent = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def truncate_air_box_at_ground(self):
        """Truncate air box at ground.

        Returns
        -------
        bool
            Truncate air box at ground.

        """
        return self._hfss_extent_info.airbox_truncate_at_ground

    @truncate_air_box_at_ground.setter
    def truncate_air_box_at_ground(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.airbox_truncate_at_ground = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def use_open_region(self):
        """Whether using an open region is enabled.

        Returns
        -------
        bool
            Use open region.

        """
        return self._hfss_extent_info.use_open_region

    @use_open_region.setter
    def use_open_region(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.use_open_region = value
        self._update_hfss_extent_info(hfss_extent)

    @property
    def use_xy_data_extent_for_vertical_expansion(self):
        """Whether using the xy data extent for vertical expansion is enabled.

        Returns
        -------
        bool
            USe x y data extent for vertical expansion.

        """
        return self._hfss_extent_info.use_xy_data_extent_for_vertical_expansion

    @use_xy_data_extent_for_vertical_expansion.setter
    def use_xy_data_extent_for_vertical_expansion(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.use_xy_data_extent_for_vertical_expansion = value
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
        for i in dir(self):
            if i.startswith("_"):
                continue
            elif i in ["load_config", "export_config"]:
                continue
            else:
                config[i] = getattr(self, i)
        return config
