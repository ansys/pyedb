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

from System import Tuple

from pyedb.dotnet.edb_core.general import convert_py_list_to_net_list


class MeshOperation(object):
    """Mesh Operation Class."""

    def __init__(self, parent, mesh_operation):
        self._parent = parent
        self.mesh_operation = mesh_operation
        self._mesh_op_mapping = {
            "kMeshSetupBase": mesh_operation.TMeshOpType.kMeshSetupBase,
            "kMeshSetupLength": mesh_operation.TMeshOpType.kMeshSetupLength,
            "kMeshSetupSkinDepth": mesh_operation.TMeshOpType.kMeshSetupSkinDepth,
            "kNumMeshOpTypes": mesh_operation.TMeshOpType.kNumMeshOpTypes,
        }

    @property
    def enabled(self):
        """Whether if mesh operation is enabled.

        Returns
        -------
        bool
            ``True`` if mesh operation is used, ``False`` otherwise.
        """
        return self.mesh_operation.Enabled

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
        int
        """
        return self.mesh_operation.MeshOpType.ToString()

    @property
    def mesh_region(self):
        """Mesh region name.

        Returns
        -------
        str
            Name of the mesh region.
        """
        return self.mesh_operation.MeshRegion

    @property
    def name(self):
        """Mesh operation name.

        Returns
        -------
        str
        """
        return self.mesh_operation.Name

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
        return self.mesh_operation.NetsLayersList

    @nets_layers_list.setter
    def nets_layers_list(self, values):
        temp = []
        for net, layers in values.items():
            for layer in layers:
                temp.append(Tuple[str, str, bool](net, layer, True))
        self.mesh_operation.NetsLayersList = convert_py_list_to_net_list(temp)

    @property
    def refine_inside(self):
        """Whether to turn on refine inside objects.

        Returns
        -------
        bool
            ``True`` if refine inside objects is used, ``False`` otherwise.

        """
        return self.mesh_operation.RefineInside

    @enabled.setter
    def enabled(self, value):
        self.mesh_operation.Enabled = value
        self._parent._update_setup()

    @mesh_region.setter
    def mesh_region(self, value):
        self.mesh_operation.MeshRegion = value
        self._parent._update_setup()

    @name.setter
    def name(self, value):
        self.mesh_operation.Name = value
        self._parent._update_setup()

    @refine_inside.setter
    def refine_inside(self, value):
        self.mesh_operation.RefineInside = value
        self._parent._update_setup()

    @property
    def max_elements(self):
        """Maximum number of elements.

        Returns
        -------
        str
        """
        return self.mesh_operation.MaxElems

    @property
    def restrict_max_elements(self):
        """Whether to restrict maximum number  of elements.

        Returns
        -------
        bool
        """
        return self.mesh_operation.RestrictMaxElem

    @max_elements.setter
    def max_elements(self, value):
        self.mesh_operation.MaxElems = str(value)
        self._parent._update_setup()

    @restrict_max_elements.setter
    def restrict_max_elements(self, value):
        """Whether to restrict maximum number  of elements.

        Returns
        -------
        bool
        """
        self.mesh_operation.RestrictMaxElem = value
        self._parent._update_setup()


class MeshOperationLength(MeshOperation, object):
    """Mesh operation Length class.
    This class is accessible from Hfss Setup in EDB and add_length_mesh_operation method.

    Examples
    --------
    >>> mop = edbapp.setups["setup1a"].add_length_mesh_operation({"GND": ["TOP", "BOTTOM"]})
    >>> mop.max_elements = 3000
    """

    def __init__(self, parent, mesh_operation):
        MeshOperation.__init__(self, parent, mesh_operation)

    @property
    def max_length(self):
        """Maximum length of elements.

        Returns
        -------
        str
        """
        return self.mesh_operation.MaxLength

    @property
    def restrict_length(self):
        """Whether to restrict length of elements.

        Returns
        -------
        bool
        """
        return self.mesh_operation.RestrictLength

    @max_length.setter
    def max_length(self, value):
        self.mesh_operation.MaxLength = value
        self._parent._update_setup()

    @restrict_length.setter
    def restrict_length(self, value):
        """Whether to restrict length of elements.

        Returns
        -------
        bool
        """
        self.mesh_operation.RestrictLength = value
        self._parent._update_setup()


class MeshOperationSkinDepth(MeshOperation, object):
    """Mesh operation Skin Depth class.
    This class is accessible from Hfss Setup in EDB and assign_skin_depth_mesh_operation method.

    Examples
    --------
    >>> mop = edbapp.setups["setup1a"].add_skin_depth_mesh_operation({"GND": ["TOP", "BOTTOM"]})
    >>> mop.max_elements = 3000
    """

    def __init__(self, parent, mesh_operation):
        MeshOperation.__init__(self, parent, mesh_operation)

    @property
    def skin_depth(self):
        """Skin depth value.

        Returns
        -------
        str
        """
        return self.mesh_operation.SkinDepth

    @skin_depth.setter
    def skin_depth(self, value):
        self.mesh_operation.SkinDepth = value
        self._parent._update_setup()

    @property
    def surface_triangle_length(self):
        """Surface triangle length value.

        Returns
        -------
        str
        """
        return self.mesh_operation.SurfTriLength

    @surface_triangle_length.setter
    def surface_triangle_length(self, value):
        self.mesh_operation.SurfTriLength = value
        self._parent._update_setup()

    @property
    def number_of_layer_elements(self):
        """Number of layer elements.

        Returns
        -------
        str
        """
        return self.mesh_operation.NumLayers

    @number_of_layer_elements.setter
    def number_of_layer_elements(self, value):
        self.mesh_operation.NumLayers = str(value)
        self._parent._update_setup()
