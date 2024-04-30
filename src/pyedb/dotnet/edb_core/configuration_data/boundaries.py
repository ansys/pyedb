class Boundaries:
    def __init__(self, pedb, boundaries_dict):
        self._pedb = pedb
        self._boundaries = boundaries_dict
        self.open_region = self._boundaries.get("open_region", None)
        self.open_region_type = self._boundaries.get("open_region_type", None)
        self.pml_visible = self._boundaries.get("pml_visible", None)
        self.pml_operation_frequency = self._boundaries.get("pml_operation_frequency", None)
        self.pml_radiation_factor = self._boundaries.get("pml_radiation_factor", None)
        self.dielectric_extents_type = self._boundaries.get("dielectric_extents_type", None)
        self.dielectric_base_polygon = self._boundaries.get("dielectric_base_polygon", None)
        self.horizontal_padding = self._boundaries.get("horizontal_padding", None)
        self.honor_primitives_on_dielectric_layers = self._boundaries.get("honor_primitives_on_dielectric_layers", None)
        self.air_box_extents_type = self._boundaries.get("air_box_extents_type", None)
        self.air_box_truncate_model_ground_layers = self._boundaries.get("air_box_truncate_model_ground_layers", None)
        self.air_box_horizontal_padding = self._boundaries.get("air_box_horizontal_padding", None)
        self.air_box_positive_vertical_padding = self._boundaries.get("air_box_positive_vertical_padding", None)
        self.air_box_negative_vertical_padding = self._boundaries.get("air_box_negative_vertical_padding", None)

    def apply(self):
        self._pedb.hfss.hfss_extent_info.use_open_region = self.open_region
        self._pedb.hfss.hfss_extent_info.open_region_type = self.open_region_type
        self._pedb.hfss.hfss_extent_info.is_pml_visible = self.pml_visible
        self._pedb.hfss.hfss_extent_info.operating_freq = self.pml_operation_frequency
        self._pedb.hfss.hfss_extent_info.radiation_level = self.pml_radiation_factor
        self._pedb.hfss.hfss_extent_info.extent_type = self.dielectric_extents_type
        self._pedb.hfss.hfss_extent_info.dielectric_base_polygon = self.dielectric_base_polygon
        self._pedb.hfss.hfss_extent_info.dielectric_extent_size = self.horizontal_padding
        self._pedb.hfss.hfss_extent_info.honor_user_dielectric = self.honor_primitives_on_dielectric_layers
        self._pedb.hfss.hfss_extent_info.extent_type = self.air_box_extents_type
        self._pedb.hfss.hfss_extent_info.truncate_air_box_at_ground = self.air_box_truncate_model_ground_layers
        self._pedb.hfss.hfss_extent_info.air_box_horizontal_extent = self.air_box_horizontal_padding
        self._pedb.hfss.hfss_extent_info.air_box_positive_vertical_extent = self.air_box_positive_vertical_padding
        self._pedb.hfss.hfss_extent_info.air_box_negative_vertical_extent = self.air_box_negative_vertical_padding
