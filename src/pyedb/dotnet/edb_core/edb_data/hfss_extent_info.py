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

from pyedb.dotnet.edb_core.edb_data.edbvalue import EdbValue
from pyedb.dotnet.edb_core.edb_data.primitives_data import cast
from pyedb.dotnet.edb_core.general import convert_pytuple_to_nettuple


class HfssExtentInfo:
    """Manages EDB functionalities for HFSS extent information.

    Parameters
    ----------
    pedb : :class:`pyedb.edb.Edb`
        Inherited EDB object.
    """

    def __init__(self, pedb):
        self._pedb = pedb

        self._hfss_extent_info_type = {
            "bounding_box": self._pedb.edb_api.utility.utility.HFSSExtentInfoType.BoundingBox,
            "conforming": self._pedb.edb_api.utility.utility.HFSSExtentInfoType.Conforming,
            "convexHull": self._pedb.edb_api.utility.utility.HFSSExtentInfoType.ConvexHull,
            "polygon": self._pedb.edb_api.utility.utility.HFSSExtentInfoType.Polygon,
        }
        self._open_region_type = {
            "radiation": self._pedb.edb_api.utility.utility.OpenRegionType.Radiation,
            "pml": self._pedb.edb_api.utility.utility.OpenRegionType.PML,
        }

    def _get_edb_value(self, value):
        """Get EDB value."""
        return self._pedb.edb_value(value)

    def _update_hfss_extent_info(self, hfss_extent_info):
        return self._pedb.active_cell.SetHFSSExtentInfo(hfss_extent_info)

    @property
    def _edb_hfss_extent_info(self):
        return self._pedb.active_cell.GetHFSSExtentInfo()

    @property
    def air_box_horizontal_extent_enabled(self):
        """Whether horizontal extent is enabled for the airbox."""
        return self._edb_hfss_extent_info.AirBoxHorizontalExtent.Item2

    @air_box_horizontal_extent_enabled.setter
    def air_box_horizontal_extent_enabled(self, value):
        info = self._edb_hfss_extent_info
        info.AirBoxHorizontalExtent = convert_pytuple_to_nettuple((self.air_box_horizontal_extent, value))
        self._update_hfss_extent_info(info)

    @property
    def air_box_horizontal_extent(self):
        """Size of horizontal extent for the air box.

        Returns:
        dotnet.edb_core.edb_data.edbvalue.EdbValue
        """
        return self._edb_hfss_extent_info.AirBoxHorizontalExtent.Item1

    @air_box_horizontal_extent.setter
    def air_box_horizontal_extent(self, value):
        info = self._edb_hfss_extent_info
        info.AirBoxHorizontalExtent = convert_pytuple_to_nettuple((value, self.air_box_horizontal_extent_enabled))
        self._update_hfss_extent_info(info)

    @property
    def air_box_positive_vertical_extent_enabled(self):
        """Whether positive vertical extent is enabled for the air box."""
        return self._edb_hfss_extent_info.AirBoxPositiveVerticalExtent.Item2

    @air_box_positive_vertical_extent_enabled.setter
    def air_box_positive_vertical_extent_enabled(self, value):
        info = self._edb_hfss_extent_info
        info.AirBoxPositiveVerticalExtent = convert_pytuple_to_nettuple((self.air_box_positive_vertical_extent, value))
        self._update_hfss_extent_info(info)

    @property
    def air_box_positive_vertical_extent(self):
        """Negative vertical extent for the air box."""
        return self._edb_hfss_extent_info.AirBoxPositiveVerticalExtent.Item1

    @air_box_positive_vertical_extent.setter
    def air_box_positive_vertical_extent(self, value):
        value = float(value)
        info = self._edb_hfss_extent_info
        info.AirBoxPositiveVerticalExtent = convert_pytuple_to_nettuple(
            (value, self.air_box_positive_vertical_extent_enabled)
        )
        self._update_hfss_extent_info(info)

    @property
    def air_box_negative_vertical_extent_enabled(self):
        """Whether negative vertical extent is enabled for the air box."""
        return self._edb_hfss_extent_info.AirBoxNegativeVerticalExtent.Item2

    @air_box_negative_vertical_extent_enabled.setter
    def air_box_negative_vertical_extent_enabled(self, value):
        info = self._edb_hfss_extent_info
        info.AirBoxNegativeVerticalExtent = convert_pytuple_to_nettuple((self.air_box_negative_vertical_extent, value))
        self._update_hfss_extent_info(info)

    @property
    def air_box_negative_vertical_extent(self):
        """Negative vertical extent for the airbox."""
        return self._edb_hfss_extent_info.AirBoxNegativeVerticalExtent.Item1

    @air_box_negative_vertical_extent.setter
    def air_box_negative_vertical_extent(self, value):
        value = float(value)
        info = self._edb_hfss_extent_info
        info.AirBoxNegativeVerticalExtent = convert_pytuple_to_nettuple(
            (value, self.air_box_negative_vertical_extent_enabled)
        )
        self._update_hfss_extent_info(info)

    @property
    def base_polygon(self):
        """Base polygon.

        Returns
        -------
        :class:`dotnet.edb_core.edb_data.primitives_data.EDBPrimitive`
        """
        return cast(self._edb_hfss_extent_info.BasePolygon, self._pedb)

    @base_polygon.setter
    def base_polygon(self, value):
        info = self._edb_hfss_extent_info
        info.BasePolygon = value.primitive_object
        self._update_hfss_extent_info(info)

    @property
    def dielectric_base_polygon(self):
        """Dielectric base polygon.

        Returns
        -------
        :class:`dotnet.edb_core.edb_data.primitives_data.EDBPrimitive`
        """
        return cast(self._edb_hfss_extent_info.DielectricBasePolygon, self._pedb)

    @dielectric_base_polygon.setter
    def dielectric_base_polygon(self, value):
        info = self._edb_hfss_extent_info
        info.DielectricBasePolygon = value.primitive_object
        self._update_hfss_extent_info(info)

    @property
    def dielectric_extent_size_enabled(self):
        """Whether dielectric extent size is enabled."""
        return self._edb_hfss_extent_info.DielectricExtentSize.Item2

    @dielectric_extent_size_enabled.setter
    def dielectric_extent_size_enabled(self, value):
        info = self._edb_hfss_extent_info
        info.DielectricExtentSize = convert_pytuple_to_nettuple((self.dielectric_extent_size, value))
        self._update_hfss_extent_info(info)

    @property
    def dielectric_extent_size(self):
        """Dielectric extent size."""
        return self._edb_hfss_extent_info.DielectricExtentSize.Item1

    @dielectric_extent_size.setter
    def dielectric_extent_size(self, value):
        info = self._edb_hfss_extent_info
        info.DielectricExtentSize = convert_pytuple_to_nettuple((value, self.dielectric_extent_size_enabled))
        self._update_hfss_extent_info(info)

    @property
    def dielectric_extent_type(self):
        """Dielectric extent type."""
        return self._edb_hfss_extent_info.DielectricExtentType.ToString().lower()

    @dielectric_extent_type.setter
    def dielectric_extent_type(self, value):
        value = "bounding_box" if value == "BoundingBox" else value
        info = self._edb_hfss_extent_info
        info.DielectricExtentType = self._hfss_extent_info_type[value.lower()]
        self._update_hfss_extent_info(info)

    @property
    def extent_type(self):
        """Extent type."""
        return self._edb_hfss_extent_info.ExtentType.ToString().lower()

    @extent_type.setter
    def extent_type(self, value):
        info = self._edb_hfss_extent_info
        info.ExtentType = self._hfss_extent_info_type[value]
        self._update_hfss_extent_info(info)

    @property
    def honor_user_dielectric(self):
        """Honor user dielectric."""
        return self._edb_hfss_extent_info.HonorUserDielectric

    @honor_user_dielectric.setter
    def honor_user_dielectric(self, value):
        info = self._edb_hfss_extent_info
        info.HonorUserDielectric = value
        self._update_hfss_extent_info(info)

    @property
    def is_pml_visible(self):
        """Whether visibility of the PML is enabled."""
        return self._edb_hfss_extent_info.IsPMLVisible

    @is_pml_visible.setter
    def is_pml_visible(self, value):
        info = self._edb_hfss_extent_info
        info.IsPMLVisible = value
        self._update_hfss_extent_info(info)

    @property
    def open_region_type(self):
        """Open region type."""
        return self._edb_hfss_extent_info.OpenRegionType.ToString().lower()

    @open_region_type.setter
    def open_region_type(self, value):
        info = self._edb_hfss_extent_info
        info.OpenRegionType = self._open_region_type[value.lower()]
        self._update_hfss_extent_info(info)

    @property
    def operating_freq(self):
        """PML Operating frequency.

        Returns
        -------
        pyedb.dotnet.edb_core.edb_data.edbvalue.EdbValue
        """
        return EdbValue(self._edb_hfss_extent_info.OperatingFreq)

    @operating_freq.setter
    def operating_freq(self, value):
        value = value._edb_obj if isinstance(value, EdbValue) else self._get_edb_value(value)
        info = self._edb_hfss_extent_info
        info.OperatingFreq = value
        self._update_hfss_extent_info(info)

    @property
    def radiation_level(self):
        """PML Radiation level to calculate the thickness of boundary."""
        return EdbValue(self._edb_hfss_extent_info.RadiationLevel)

    @radiation_level.setter
    def radiation_level(self, value):
        value = value._edb_obj if isinstance(value, EdbValue) else self._get_edb_value(value)
        info = self._edb_hfss_extent_info
        info.RadiationLevel = value
        self._update_hfss_extent_info(info)

    @property
    def sync_air_box_vertical_extent(self):
        """Vertical extent of the sync air box."""
        return self._edb_hfss_extent_info.SyncAirBoxVerticalExtent

    @sync_air_box_vertical_extent.setter
    def sync_air_box_vertical_extent(self, value):
        info = self._edb_hfss_extent_info
        info.SyncAirBoxVerticalExtent = value
        self._update_hfss_extent_info(info)

    @property
    def truncate_air_box_at_ground(self):
        """Truncate air box at ground."""
        return self._edb_hfss_extent_info.TruncateAirBoxAtGround

    @truncate_air_box_at_ground.setter
    def truncate_air_box_at_ground(self, value):
        info = self._edb_hfss_extent_info
        info.TruncateAirBoxAtGround = value
        self._update_hfss_extent_info(info)

    @property
    def use_open_region(self):
        """Whether using an open region is enabled."""
        return self._edb_hfss_extent_info.UseOpenRegion

    @use_open_region.setter
    def use_open_region(self, value):
        info = self._edb_hfss_extent_info
        info.UseOpenRegion = value
        self._update_hfss_extent_info(info)

    @property
    def use_xy_data_extent_for_vertical_expansion(self):
        """Whether using the xy data extent for vertical expansion is enabled."""
        return self._edb_hfss_extent_info.UseXYDataExtentForVerticalExpansion

    @use_xy_data_extent_for_vertical_expansion.setter
    def use_xy_data_extent_for_vertical_expansion(self, value):
        info = self._edb_hfss_extent_info
        info.UseXYDataExtentForVerticalExpansion = value
        self._update_hfss_extent_info(info)

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
