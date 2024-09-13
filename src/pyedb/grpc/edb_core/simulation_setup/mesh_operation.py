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

from enum import Enum

from System import Tuple

from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list


class MeshOpType(Enum):
    kMeshSetupBase = "base"
    kMeshSetupLength = "length"
    kMeshSetupSkinDepth = "skin_depth"
    kNumMeshOpTypes = "num_mesh_op_types"


class MeshOperation(object):
    """Mesh Operation Class."""

    def __init__(self, parent, edb_object):
        self._parent = parent
        self._edb_object = edb_object
        self._mesh_op_mapping = {
            "kMeshSetupBase": self._edb_object.TMeshOpType.kMeshSetupBase,
            "kMeshSetupLength": self._edb_object.TMeshOpType.kMeshSetupLength,
            "kMeshSetupSkinDepth": self._edb_object.TMeshOpType.kMeshSetupSkinDepth,
            "kNumMeshOpTypes": self._edb_object.TMeshOpType.kNumMeshOpTypes,
        }

    @property
    def enabled(self):
        """Whether if mesh operation is enabled.

        Returns
        -------
        bool
            ``True`` if mesh operation is used, ``False`` otherwise.
        """
        return self._edb_object.Enabled

    @property
    def mesh_operation_type(self):
        """Mesh operation type.
        Options:
        0- ``kMeshSetupBase``
        1- ``kMeshSetupLength``
        2- ``kMeshSetupSkinDepth``
        3- ``kNumMeshOpTypes``.

        Returns
        -------
        str
        """
        return self._edb_object.MeshOpType.ToString()

    @property
    def type(self):
        mop_type = self.mesh_operation_type
        return MeshOpType[mop_type].value

    @property
    def mesh_region(self):
        """Mesh region name.

        Returns
        -------
        str
            Name of the mesh region.
        """
        return self._edb_object.MeshRegion

    @property
    def name(self):
        """Mesh operation name.

        Returns
        -------
        str
        """
        return self._edb_object.Name

    @property
    def nets_layers_list(self):
        """List of nets and layers.

        Returns
        -------
        list
           List of lists with three elements. Each list must contain:
           1- net name
           2- layer name
           3- bool.
           Third element is represents whether if the mesh operation is enabled or disabled.

        """
        nets_layers = {}
        for i in list(self._edb_object.NetsLayersList):
            net = i.Item1
            layer = i.Item2
            flag = i.Item3
            if not flag:
                continue
            if net not in nets_layers:
                nets_layers[net] = [layer]
            else:
                nets_layers[net].append(layer)
        return nets_layers

    @nets_layers_list.setter
    def nets_layers_list(self, values):
        temp = []
        for net, layers in values.items():
            for layer in layers:
                temp.append(Tuple[str, str, bool](net, layer, True))
        self._edb_object.NetsLayersList = convert_py_list_to_net_list(temp)

    @property
    def refine_inside(self):
        """Whether to turn on refine inside objects.

        Returns
        -------
        bool
            ``True`` if refine inside objects is used, ``False`` otherwise.

        """
        return self._edb_object.RefineInside

    @enabled.setter
    def enabled(self, value):
        self._edb_object.Enabled = value

    @mesh_region.setter
    def mesh_region(self, value):
        self._edb_object.MeshRegion = value

    @name.setter
    def name(self, value):
        self._edb_object.Name = value

    @refine_inside.setter
    def refine_inside(self, value):
        self._edb_object.RefineInside = value

    @property
    def max_elements(self):
        """Maximum number of elements.

        Returns
        -------
        str
        """
        return int(self._edb_object.MaxElems)

    @property
    def restrict_max_elements(self):
        """Whether to restrict maximum number  of elements.

        Returns
        -------
        bool
        """
        return self._edb_object.RestrictMaxElem

    @max_elements.setter
    def max_elements(self, value):
        self._edb_object.MaxElems = str(value)

    @restrict_max_elements.setter
    def restrict_max_elements(self, value):
        """Whether to restrict maximum number  of elements.

        Returns
        -------
        bool
        """
        self._edb_object.RestrictMaxElem = value


class LengthMeshOperation(MeshOperation, object):
    """Mesh operation Length class.
    This class is accessible from Hfss Setup in EDB and add_length_mesh_operation method.

    Examples
    --------
    >>> mop = edbapp.setups["setup1a"].add_length_mesh_operation({"GND": ["TOP", "BOTTOM"]})
    >>> mop.max_elements = 3000
    """

    def __init__(self, parent, edb_object):
        MeshOperation.__init__(self, parent, edb_object)

    @property
    def max_length(self):
        """Maximum length of elements.

        Returns
        -------
        str
        """
        return self._edb_object.MaxLength

    @property
    def restrict_length(self):
        """Whether to restrict length of elements.

        Returns
        -------
        bool
        """
        return self._edb_object.RestrictLength

    @max_length.setter
    def max_length(self, value):
        self._edb_object.MaxLength = value

    @restrict_length.setter
    def restrict_length(self, value):
        """Whether to restrict length of elements.

        Returns
        -------
        bool
        """
        self._edb_object.RestrictLength = value


class SkinDepthMeshOperation(MeshOperation, object):
    """Mesh operation Skin Depth class.
    This class is accessible from Hfss Setup in EDB and assign_skin_depth_mesh_operation method.

    Examples
    --------
    >>> mop = edbapp.setups["setup1a"].add_skin_depth_mesh_operation({"GND": ["TOP", "BOTTOM"]})
    >>> mop.max_elements = 3000
    """

    def __init__(self, parent, edb_object):
        MeshOperation.__init__(self, parent, edb_object)

    @property
    def skin_depth(self):
        """Skin depth value.

        Returns
        -------
        str
        """
        return self._edb_object.SkinDepth

    @skin_depth.setter
    def skin_depth(self, value):
        self._edb_object.SkinDepth = value

    @property
    def surface_triangle_length(self):
        """Surface triangle length value.

        Returns
        -------
        str
        """
        return self._edb_object.SurfTriLength

    @surface_triangle_length.setter
    def surface_triangle_length(self, value):
        self._edb_object.SurfTriLength = value

    @property
    def number_of_layer_elements(self):
        """Number of layer elements.

        Returns
        -------
        str
        """
        return self._edb_object.NumLayers

    @number_of_layer_elements.setter
    def number_of_layer_elements(self, value):
        self._edb_object.NumLayers = str(value)
