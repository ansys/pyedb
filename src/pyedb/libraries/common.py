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

from dataclasses import dataclass
from typing import Tuple, Union


@dataclass
class Substrate:
    """
    Small helper that groups the four basic substrate parameters used
    throughout the library.

    Parameters
    ----------
    h : float, default 100 µm
        Substrate height in metres.
    er : float, default 4.4
        Relative permittivity.
    tan_d : float, default 0
        Loss tangent.
    name : str, default "SUB"
        Logical name used for layer creation.
    size : tuple[float, float], default (1 mm, 1 mm)
        (width, length) of the surrounding ground plane in metres.

    Examples
    --------
    >>> sub = Substrate(h=1.6e-3, er=4.4, tan_d=0.02, name="FR4", size=(10e-3, 15e-3))
    >>> sub.h
    0.0016
    """

    h: float = 100e-6  # height (m)
    er: float = 4.4  # relative permittivity
    tan_d: float = 0  # loss tangent
    name: str = "SUB"
    size: Tuple[float, float] = (0.001, 0.001)  # width, length in metres


from typing import Union


# ------------------------------------------------------------------
# Material
# ------------------------------------------------------------------
class Material:
    """
    Generic material definition.

    When the material name is set, the object automatically registers
    itself in the provided PyEDB material database if the name is not
    already present.

    Parameters
    ----------
    pedb : ansys.edb.core.database.Database
        Active EDB session.
    name : str
        Material name (e.g. ``"Copper"``).

    Examples
    --------
    >>> m = Material(edb, "MyMaterial")
    >>> m.name
    'MyMaterial'
    >>> edb.materials["MyMaterial"]  # now exists in the database
    <Material object at ...>
    """

    def __init__(self, pedb, name):
        self._pedb = pedb
        self.name = name

    @property
    def name(self) -> str:
        """Material name."""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        if value not in self._pedb.materials:
            self._pedb.materials.add_material(value)


# ------------------------------------------------------------------
# Conductor
# ------------------------------------------------------------------
class Conductor(Material):
    """
    Metallic conductor material with electrical conductivity.

    Parameters
    ----------
    pedb : ansys.edb.core.database.Database
        Active EDB session.
    name : str
        Material name.
    conductivity : float, optional
        Electrical conductivity in S/m.  Default is 5.8e7 (Copper).

    Examples
    --------
    >>> cu = Conductor(edb, "Copper", conductivity=5.8e7)
    >>> cu.conductivity
    58000000.0
    >>> cu.conductivity = 3.5e7  # update on-the-fly
    >>> edb.materials["Copper"].conductivity
    35000000.0
    """

    def __init__(self, pedb, name: str, conductivity: float = 5.8e7):
        super().__init__(pedb, name)
        self.conductivity = conductivity

    @property
    def conductivity(self) -> float:
        """Electrical conductivity (S/m)."""
        return self._conductivity

    @conductivity.setter
    def conductivity(self, value: float):
        self._conductivity = value
        self._pedb.materials[self.name].conductivity = value


# ------------------------------------------------------------------
# Dielectric
# ------------------------------------------------------------------
class Dielectric(Material):
    """
    Dielectric material with relative permittivity and loss tangent.

    Parameters
    ----------
    pedb : ansys.edb.core.database.Database
        Active EDB session.
    name : str
        Material name.
    permittivity : float, optional
        Relative permittivity (εᵣ).  Default is 11.9 (Silicon).
    loss_tg : float, optional
        Loss tangent (tan δ).  Default is 0.02.

    Examples
    --------
    >>> sub = Dielectric(edb, "Silicon", permittivity=11.9, loss_tg=0.01)
    >>> sub.permittivity
    11.9
    >>> sub.loss_tg = 0.005
    >>> edb.materials["Silicon"].loss_tangent
    0.005
    """

    def __init__(self, pedb, name: str, permittivity: float = 11.9, loss_tg: float = 0.02):
        super().__init__(pedb, name)
        self.permittivity = permittivity
        self.loss_tg = loss_tg

    @property
    def permittivity(self) -> float:
        """Relative permittivity (εᵣ)."""
        return self._permittivity

    @permittivity.setter
    def permittivity(self, value: float):
        self._permittivity = value
        self._pedb.materials[self.name].permittivity = value

    @property
    def loss_tg(self) -> float:
        """Loss tangent (tan δ)."""
        return self._loss_tg

    @loss_tg.setter
    def loss_tg(self, value: float):
        self._loss_tg = value
        self._pedb.materials[self.name].loss_tangent = value


# ------------------------------------------------------------------
# Layer
# ------------------------------------------------------------------
class Layer:
    """
    Physical layer inside a stackup.

    Parameters
    ----------
    pedb : ansys.edb.core.database.Database
        Active EDB session.
    name : str
        Layer name.
    material : Conductor or Dielectric, optional
        Material instance assigned to the layer.
    thickness : float, optional
        Layer thickness in meters.  Default is 1 µm.

    Examples
    --------
    >>> diel = Dielectric(edb, "FR4")
    >>> lyr = Layer(edb, "Core", material=diel, thickness=100e-6)
    >>> lyr.thickness = 50e-6
    >>> edb.stackup.layers["Core"].thickness
    5e-05
    """

    def __init__(self, pedb, name: str, material: Union[Conductor, Dielectric] = None, thickness: float = 1e-6):
        self._pedb = pedb
        self.name: str = name
        self.thickness: float = thickness
        self._material = material

    @property
    def name(self) -> str:
        """Layer name."""
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        if value not in self._pedb.stackup.layers:
            self._pedb.stackup.add_layer(value)
        else:
            self._pedb.stackup.layers[self.name].name = self.name

    @property
    def thickness(self) -> float:
        """Layer thickness (m)."""
        return self._thickness

    @thickness.setter
    def thickness(self, value: float):
        self._thickness = value
        self._pedb.stackup.layers[self.name].thickness = value

    @property
    def material(self) -> Union[Conductor, Dielectric]:
        """Material assigned to this layer."""
        return self._material

    @material.setter
    def material(self, material: Union[Conductor, Dielectric]):
        self._material = material
        self._pedb.stackup.layers[self.name].material = material.name


# ------------------------------------------------------------------
# MetalLayer
# ------------------------------------------------------------------
class MetalLayer(Layer):
    """
    Convenience wrapper for metallic layers.

    Automatically creates a ``Conductor`` material.

    Parameters
    ----------
    pedb : ansys.edb.core.database.Database
        Active EDB session.
    name : str
        Layer name.
    thickness : float, optional
        Thickness in meters.  Default is 1 µm.
    material : str, optional
        Name of the conductor material.  Default is ``"Copper"``.

    Examples
    --------
    >>> top = MetalLayer(edb, "TOP", thickness=18e-6, material="Gold")
    >>> top.material.conductivity
    58000000.0
    """

    def __init__(self, pedb, name, thickness=1e-6, material: str = "Copper"):
        super().__init__(pedb, name, thickness=thickness)
        self.material = Conductor(pedb, name=material)


# ------------------------------------------------------------------
# DielectricLayer
# ------------------------------------------------------------------
class DielectricLayer(Layer):
    """
    Convenience wrapper for dielectric layers.

    Automatically creates a ``Dielectric`` material.

    Parameters
    ----------
    pedb : ansys.edb.core.database.Database
        Active EDB session.
    name : str
        Layer name.
    thickness : float, optional
        Thickness in meters.  Default is 1 µm.
    material : str, optional
        Name of the dielectric material.  Default is ``"FR4"``.

    Examples
    --------
    >>> core = DielectricLayer(edb, "Core", thickness=100e-6, material="FR4")
    >>> core.material.permittivity
    4.4
    """

    def __init__(self, pedb, name, thickness=1e-6, material: str = "FR4"):
        super().__init__(pedb, name, thickness=thickness)
        self._pedb.stackup[name].type = "dielectric"
        self.material = Dielectric(pedb, name=material)


# ------------------------------------------------------------------
# MicroStripTechnologyStackup
# ------------------------------------------------------------------
class MicroStripTechnologyStackup:
    """
    Pre-defined micro-strip stackup with bottom metal, substrate and top metal.

    Parameters
    ----------
    pedb : ansys.edb.core.database.Database
        Active EDB session.

    Attributes
    ----------
    bottom_metal : MetalLayer
        Bottom metal layer.
    substrate : DielectricLayer
        Substrate dielectric layer.
    top_metal : MetalLayer
        Top metal layer.

    Examples
    --------
    >>> stack = MicroStripTechnologyStackup(edb)
    >>> stack.top_metal.thickness = 5e-6
    >>> stack.substrate.material.permittivity = 9.8
    """

    def __init__(
        self, pedb, botton_layer_name="BOT_METAL", substrate_layer_name="Substrate", top_layer_name="TOP_METAL"
    ):
        self._pedb = pedb
        self.bottom_metal = MetalLayer(pedb, name=botton_layer_name, thickness=4e-6, material="Gold")
        self.substrate = DielectricLayer(pedb, name=substrate_layer_name, thickness=100e-6, material="Silicon")
        self.top_metal = MetalLayer(pedb, name=top_layer_name, thickness=4e-6, material="Gold")
