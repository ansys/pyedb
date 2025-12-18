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

# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import absolute_import, annotations

from ansys.edb.core.layer.layer import Layer as GrpcLayer, LayerType as GrpcLayerType

layer_type_mapping = {
    "conducting": GrpcLayerType.CONDUCTING_LAYER,
    "air_lines": GrpcLayerType.AIRLINES_LAYER,
    "errors": GrpcLayerType.ERRORS_LAYER,
    "symbol": GrpcLayerType.SYMBOL_LAYER,
    "measure": GrpcLayerType.MEASURE_LAYER,
    "assembly": GrpcLayerType.ASSEMBLY_LAYER,
    "silkscreen": GrpcLayerType.SILKSCREEN_LAYER,
    "solder_mask": GrpcLayerType.SOLDER_MASK_LAYER,
    "solder_paste": GrpcLayerType.SOLDER_PASTE_LAYER,
    "glue": GrpcLayerType.GLUE_LAYER,
    "wirebond": GrpcLayerType.WIREBOND_LAYER,
    "user": GrpcLayerType.USER_LAYER,
    "siwave_hfss_solver_regions": GrpcLayerType.SIWAVE_HFSS_SOLVER_REGIONS,
    "postprocessing": GrpcLayerType.POST_PROCESSING_LAYER,
    "outline": GrpcLayerType.OUTLINE_LAYER,
    "layer_types_count": GrpcLayerType.LAYER_TYPES_COUNT,
    "undefined_layer_type": GrpcLayerType.UNDEFINED_LAYER_TYPE,
}


class Layer:
    """Manages Layer."""

    def __init__(self, edb_object=None, name="", layer_type="undefined", **kwargs):
        self.core = edb_object
        self._name = name
        self._color = ()
        self._type = ""
        if edb_object:
            self._cloned_layer = self.core.clone()
        else:
            if layer_type in layer_type_mapping:
                self.core.create(name=name, lyr_type=layer_type_mapping[layer_type])
                self.update(**kwargs)

    @classmethod
    def create(cls, name, layer_type: str = "solder_mask") -> Layer:
        """
        Parameters
        ----------
        name : str
            Layer name
        layer_type : str
            Layer type

        Returns
        -------
        :class: `Layer <pyedb.`
        """
        layer = GrpcLayer.create(name=name, lyr_type=layer_type_mapping[layer_type])
        return cls(edb_object=layer)

    @property
    def id(self):
        """Get the layer ID."""
        return self.core.id

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if k in dir(self):
                self.__setattr__(k, v)
            else:
                raise Exception(f"{k} is not a valid layer attribute")

    @property
    def name(self) -> str:
        """Get the layer name."""
        return self.core.name

    @name.setter
    def name(self, value: str):
        self.core.name = value

    @property
    def properties(self) -> dict[str, str]:
        from ansys.edb.core.layer.stackup_layer import StackupLayer as GrpcStackupLayer

        from pyedb.grpc.database.stackup import StackupLayer

        if isinstance(self.core.cast(), GrpcStackupLayer):
            return StackupLayer(self.core.cast()).properties
        else:
            data = {"name": self.name, "type": self.type, "color": self.core.color}
            return data

    @properties.setter
    def properties(self, params):
        name = params.get("name", "")
        if name:
            self.name = name
        type = params.get("type", "")
        if type:
            self.core.type = type
        color = params.get("color", "")
        if color:
            self.core.color = color

    @property
    def type(self) -> str:
        return self.core.type.name.lower().split("_")[0]

    @property
    def _layer_name_mapping_reversed(self):
        return {j: i for i, j in self._layer_name_mapping.items()}

    @property
    def is_stackup_layer(self):
        """Check if the layer is a stackup layer."""
        return self.core.is_stackup_layer
