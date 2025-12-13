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

from __future__ import absolute_import

from ansys.edb.core.utility.layer_map import (
    LayerMap as GrpcLayerMap,
    LayerMapUniqueDirection as GrpcLayerMapUniqueDirection,
)


class LayerMap:
    def __init__(self, edb_object):
        self.core = edb_object

    @classmethod
    def create(cls, direction: str = "two_way") -> "LayerMap":
        """Create a layer map.

        Parameters
        ----------
        direction : str, optional
            Direction of the layer map. Options are "two_way", "forward", and "backward". Default is "two_way".

        Returns
        -------
        LayerMap
            Layer map object.
        """
        mapping = {
            "two_way": GrpcLayerMapUniqueDirection.TWOWAY_UNIQUE,
            "forward": GrpcLayerMapUniqueDirection.FORWARD_UNIQUE,
            "backward": GrpcLayerMapUniqueDirection.BACKWARD_UNIQUE,
        }
        core_layer_map = GrpcLayerMap.create(mapping[direction])
        return cls(core_layer_map)

    @property
    def id(self):
        """Get the layer map ID.

        Returns
        -------
        int
            Layer map ID.
        """
        return self.core.id

    @property
    def is_null(self) -> bool:
        """Check if the layer map is null.

        Returns
        -------
        bool
            True if the layer map is null, False otherwise.
        """
        return self.core.is_null

    def clear(self):
        """Clear the layer map."""
        self.core.clear()

    def get_mapping_backward(self, layer_id: int) -> int:
        """Get the backward mapping for a given layer ID.

        Parameters
        ----------
        layer_id : int
            Layer ID to get the backward mapping for.

        Returns
        -------
        int
            Mapped layer ID.
        """
        return self.core.get_mapping_backward(layer_id)

    def get_mapping_forward(self, layer_id: int) -> int:
        """Get the forward mapping for a given layer ID.

        Parameters
        ----------
        layer_id : int
            Layer ID to get the forward mapping for.

        Returns
        -------
        int
            Mapped layer ID.
        """
        return self.core.get_mapping_forward(layer_id)

    def set_mapping(self, layer_id_from: int, layer_id_to: int):
        """Set the mapping from one layer ID to another.

        Parameters
        ----------
        layer_id_from : int
            Layer ID to map from.
        layer_id_to : int
            Layer ID to map to.
        """
        self.core.set_mapping(layer_id_from, layer_id_to)
