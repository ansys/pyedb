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
    >>> sub = Substrate(h=1.6e-3, er=4.4, tan_d=0.02,
    ...                 name="FR4", size=(10e-3, 15e-3))
    >>> sub.h
    0.0016
    """

    h: float = 100e-6  # height (m)
    er: float = 4.4  # relative permittivity
    tan_d: float = 0  # loss tangent
    name: str = "SUB"
    size: Tuple[float, float] = (0.001, 0.001)  # width, length in metres


class Material:
    def __init__(self, pedb, name):
        self._pedb = pedb
        self.name = name

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        if not value in self._pedb.materials:
            self._pedb.materials.add_material(value)


class Conductor(Material):
    def __init__(self, pedb, name: str, conductivity: float = 5.8e7):
        super().__init__(pedb, name)
        self._pedb = pedb
        self.conductivity = conductivity

    @property
    def conductivity(self) -> float:
        return self._conductivity

    @conductivity.setter
    def conductivity(self, value: float):
        self._conductivity = value
        self._pedb.materials[self.name].conductivity = value


class Dielectric(Material):
    def __init__(self, pedb, name: str, permittivity: float = 4.4, loss_tg: float = 0.02):
        super().__init__(pedb, name)
        self._pedb = pedb
        self.permittivity = permittivity
        self.loss_tg = loss_tg

    @property
    def permittivity(self) -> float:
        return self._permittivity

    @permittivity.setter
    def permittivity(self, value: float):
        self._permittivity = value
        self._pedb.materials[self.name].permittivity = value

    @property
    def loss_tg(self) -> float:
        return self._loss_tg

    @loss_tg.setter
    def loss_tg(self, value: float):
        self._loss_tg = value
        self._pedb.materials[self.name].loss_tangent = value


class Layer:
    def __init__(self, pedb, name: str, material: Union[Conductor, Dielectric] = None, thickness: float = 1e-6):
        self._pedb = pedb
        self.name: str = name
        self.thickness: float = thickness
        self._material = material

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value
        if not value in self._pedb.stackup.layers:
            self._pedb.stackup.add_layer(value)
        else:
            self._pedb.stackup.layers[self.name].name = self.name

    @property
    def thickness(self) -> float:
        return self._thickness

    @thickness.setter
    def thickness(self, value: float):
        self._thickness = value
        self._pedb.stackup.layers[self.name].thickness = value

    @property
    def material(self) -> any:
        return self._material

    @material.setter
    def material(self, material: Union[Conductor, Dielectric]):
        self._material = material
        self._pedb.stackup.layers[self.name].material = material.name


class MetalLayer(Layer):
    def __init__(self, pedb, name, thickness=1e-6, material: str = "Copper"):
        super().__init__(pedb, name, thickness=thickness)
        self.material = Conductor(pedb, name=material)


class DielectricLayer(Layer):
    def __init__(self, pedb, name, thickness=1e-6, material: str = "FR4"):
        super().__init__(pedb, name, thickness=thickness)
        self._pedb.stackup[self.name].type = "dielectric"
        self.material = Dielectric(pedb, name=material)


class MicroStripTechnologyStackup:
    def __init__(self, pedb):
        self._pedb = pedb
        self.bottom_metal = MetalLayer(pedb, name="BOT_METAL", thickness=4e-6, material="Gold")
        self.substrate = DielectricLayer(pedb, name="Substrate", thickness=100e-6, material="Silicon")
        self.top_metal = MetalLayer(pedb, name="TOP_METAL", thickness=4e-6, material="Gold")
