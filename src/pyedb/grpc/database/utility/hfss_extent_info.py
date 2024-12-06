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

from ansys.edb.core.utility.hfss_extent_info import HfssExtentInfo as GrpcHfssExtentInfo
from ansys.edb.core.utility.value import Value as GrpcValue


class HfssExtentInfo(GrpcHfssExtentInfo):
    """Manages EDB functionalities for HFSS extent information.

    Parameters
    ----------
    pedb : :class:`pyedb.edb.Edb`
        Inherited EDB object.
    """

    def __init__(self, pedb):
        self._pedb = pedb
        super().__init__()
        self.extent_type_mapping = {
            "bounding_box": GrpcHfssExtentInfo.HFSSExtentInfoType.BOUNDING_BOX,
            "conforming": GrpcHfssExtentInfo.HFSSExtentInfoType.CONFORMING,
            "convex_hull": GrpcHfssExtentInfo.HFSSExtentInfoType.CONVEX_HUL,
            "polygon": GrpcHfssExtentInfo.HFSSExtentInfoType.POLYGON,
        }
        self._open_region_type = {
            "radiation": GrpcHfssExtentInfo.OpenRegionType.RADIATION,
            "pml": GrpcHfssExtentInfo.OpenRegionType.PML,
        }
        self.hfss_extent_type = self.HFSSExtentInfoType.value

    def _update_hfss_extent_info(self):
        return self._pedb.active_cell.set_hfss_extent_info(self._hfss_extent_info)

    @property
    def _hfss_extent_info(self):
        return self._pedb.active_cell.hfss_extent_info

    @property
    def air_box_horizontal_extent_enabled(self):
        """Whether horizontal extent is enabled for the airbox."""
        return self._hfss_extent_info.air_box_horizontal_extent[1]

    @air_box_horizontal_extent_enabled.setter
    def air_box_horizontal_extent_enabled(self, value):
        self._hfss_extent_info.air_box_horizontal_extent = (self.air_box_horizontal_extent, value)
        self._update_hfss_extent_info()

    @property
    def air_box_horizontal_extent(self):
        """Size of horizontal extent for the air box.

        Returns:
        dotnet.database.edb_data.edbvalue.EdbValue
        """
        return self._hfss_extent_info.air_box_horizontal_extent[0]

    @air_box_horizontal_extent.setter
    def air_box_horizontal_extent(self, value):
        self._hfss_extent_info.air_box_horizontal_extent = (float(value), self.air_box_horizontal_extent_enabled)
        self._update_hfss_extent_info()

    @property
    def air_box_positive_vertical_extent_enabled(self):
        """Whether positive vertical extent is enabled for the air box."""
        return self._hfss_extent_info.air_box_positive_vertical_extent[1]

    @air_box_positive_vertical_extent_enabled.setter
    def air_box_positive_vertical_extent_enabled(self, value):
        self._hfss_extent_info.air_box_positive_vertical_extent = (self.air_box_positive_vertical_extent, value)
        self._update_hfss_extent_info()

    @property
    def air_box_positive_vertical_extent(self):
        """Negative vertical extent for the air box."""
        return self._hfss_extent_info.air_box_positive_vertical_extent[0]

    @air_box_positive_vertical_extent.setter
    def air_box_positive_vertical_extent(self, value):
        self._hfss_extent_info.air_box_positive_vertical_extent = (
            float(value),
            self.air_box_positive_vertical_extent_enabled,
        )
        self._update_hfss_extent_info()

    @property
    def air_box_negative_vertical_extent_enabled(self):
        """Whether negative vertical extent is enabled for the air box."""
        return self._hfss_extent_info.air_box_negative_vertical_extent[1]

    @air_box_negative_vertical_extent_enabled.setter
    def air_box_negative_vertical_extent_enabled(self, value):
        self._hfss_extent_info.air_box_negative_vertical_extent = (self.air_box_negative_vertical_extent, value)
        self._update_hfss_extent_info()

    @property
    def air_box_negative_vertical_extent(self):
        """Negative vertical extent for the airbox."""
        return self._hfss_extent_info.air_box_negative_vertical_extent[0]

    @air_box_negative_vertical_extent.setter
    def air_box_negative_vertical_extent(self, value):
        self._hfss_extent_info.air_box_negative_vertical_extent = (
            float(value),
            self.air_box_negative_vertical_extent_enabled,
        )
        self._update_hfss_extent_info()

    @property
    def base_polygon(self):
        """Base polygon.

        Returns
        -------
        :class:`dotnet.database.edb_data.primitives_data.EDBPrimitive`
        """
        return self._hfss_extent_info.base_polygon

    @base_polygon.setter
    def base_polygon(self, value):
        self._hfss_extent_info.base_polygon = value
        self._update_hfss_extent_info()

    @property
    def dielectric_base_polygon(self):
        """Dielectric base polygon.

        Returns
        -------
        :class:`dotnet.database.edb_data.primitives_data.EDBPrimitive`
        """
        return self._hfss_extent_info.dielectric_base_polygon

    @dielectric_base_polygon.setter
    def dielectric_base_polygon(self, value):
        self._hfss_extent_info.dielectric_base_polygon = value
        self._update_hfss_extent_info()

    @property
    def dielectric_extent_size_enabled(self):
        """Whether dielectric extent size is enabled."""
        return self._hfss_extent_info.dielectric_extent_size[1]

    @dielectric_extent_size_enabled.setter
    def dielectric_extent_size_enabled(self, value):
        self._hfss_extent_info.dielectric_extent_size = (self.dielectric_extent_size, value)
        self._update_hfss_extent_info()

    @property
    def dielectric_extent_size(self):
        """Dielectric extent size."""
        return self._hfss_extent_info.dielectric_extent_size[0]

    @dielectric_extent_size.setter
    def dielectric_extent_size(self, value):
        self._hfss_extent_info.dielectric_extent_size = (value, self.dielectric_extent_size_enabled)
        self._update_hfss_extent_info()

    @property
    def dielectric_extent_type(self):
        """Dielectric extent type."""
        return self._hfss_extent_info.dielectric_extent_type.name.lower()

    @dielectric_extent_type.setter
    def dielectric_extent_type(self, value):
        self._hfss_extent_info.dielectric_extent_type = self.extent_type_mapping[value.lower()]
        self._update_hfss_extent_info()

    @property
    def extent_type(self):
        """Extent type."""
        return self._hfss_extent_info.extent_type.name.lower()

    @extent_type.setter
    def extent_type(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.extent_type = value
        self._pedb.active_cell.set_hfss_extent_info(hfss_extent)

    @property
    def honor_user_dielectric(self):
        """Honor user dielectric."""
        return self._hfss_extent_info.honor_user_dielectric

    @honor_user_dielectric.setter
    def honor_user_dielectric(self, value):
        hfss_extent = self._hfss_extent_info
        hfss_extent.honor_user_dielectric = value
        self._pedb.active_cell.set_hfss_extent_info(hfss_extent)

    @property
    def is_pml_visible(self):
        """Whether visibility of the PML is enabled."""
        return self._hfss_extent_info.is_pml_visible

    @is_pml_visible.setter
    def is_pml_visible(self, value):
        self._hfss_extent_info.is_pml_visible = value
        self._update_hfss_extent_info()

    @property
    def open_region_type(self):
        """Open region type."""
        return self._hfss_extent_info.open_region_type.name.lower()

    @open_region_type.setter
    def open_region_type(self, value):
        self._hfss_extent_info.open_region_type = self._open_region_type[value.lower()]
        self._update_hfss_extent_info()

    @property
    def operating_freq(self):
        """PML Operating frequency.

        Returns
        -------
        pyedb.dotnet.database.edb_data.edbvalue.EdbValue
        """
        return GrpcValue(self._hfss_extent_info.operating_frequency).value

    @operating_freq.setter
    def operating_freq(self, value):
        self._hfss_extent_info.operating_frequency = GrpcValue(value)
        self._update_hfss_extent_info()

    @property
    def radiation_level(self):
        """PML Radiation level to calculate the thickness of boundary."""
        return GrpcValue(self._hfss_extent_info.radiation_level).value

    @radiation_level.setter
    def radiation_level(self, value):
        self._hfss_extent_info.RadiationLevel = GrpcValue(value)
        self._update_hfss_extent_info()

    @property
    def sync_air_box_vertical_extent(self):
        """Vertical extent of the sync air box."""
        return self._hfss_extent_info.sync_air_box_vertical_extent

    @sync_air_box_vertical_extent.setter
    def sync_air_box_vertical_extent(self, value):
        self._hfss_extent_info.sync_air_box_vertical_extent = value
        self._update_hfss_extent_info()

    @property
    def truncate_air_box_at_ground(self):
        """Truncate air box at ground."""
        return self._hfss_extent_info.truncate_air_box_at_ground

    @truncate_air_box_at_ground.setter
    def truncate_air_box_at_ground(self, value):
        self._hfss_extent_info.truncate_air_box_at_ground = value
        self._update_hfss_extent_info()

    @property
    def use_open_region(self):
        """Whether using an open region is enabled."""
        return self._hfss_extent_info.use_open_region

    @use_open_region.setter
    def use_open_region(self, value):
        self._hfss_extent_info.use_open_region = value
        self._update_hfss_extent_info()

    @property
    def use_xy_data_extent_for_vertical_expansion(self):
        """Whether using the xy data extent for vertical expansion is enabled."""
        return self._hfss_extent_info.use_xy_data_extent_for_vertical_expansion

    @use_xy_data_extent_for_vertical_expansion.setter
    def use_xy_data_extent_for_vertical_expansion(self, value):
        self._hfss_extent_info.use_xy_data_extent_for_vertical_expansion = value
        self._update_hfss_extent_info()

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
