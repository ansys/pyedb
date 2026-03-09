# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

from __future__ import annotations

from typing import TYPE_CHECKING

from ansys.edb.core.utility.rlc import Rlc as CoreRlc

from pyedb.grpc.database.utility.value import Value

if TYPE_CHECKING:
    from ansys.edb.core.hierarchy.pin_pair_model import PinPairModel as CorePinPairModel

    from pyedb.grpc.database.hierarchy.component import Component


class PinPair:
    def __init__(self, model, edb_pin_pair):
        self._edb_pin_pair = edb_pin_pair
        self._model = model
        self.core = model.core

    @property
    def first_pin(self) -> str:
        """First pin name.

        This attribute is read-only since pin pair model is defined between two pins,
        and changing pin names will change the pin pair itself.

        Returns
        -------
        str
            First pin name.

        """
        return self._edb_pin_pair[0]

    @property
    def second_pin(self) -> str:
        """Second pin name.

        This attribute is read-only since pin pair model is defined between two pins,
        and changing pin names will change the pin pair itself.

        Returns
        -------
        str
            Second pin name.

        """
        return self._edb_pin_pair[1]

    @property
    def rlc_enable(self) -> tuple[bool, bool, bool]:
        """Enable model.

        Returns
        -------
        tuple[r_enabled(bool), l_enabled(bool), c_enabled(bool)].

        """
        rlc = self.core.rlc(self._edb_pin_pair)
        return rlc.r_enabled, rlc.l_enabled, rlc.c_enabled

    @rlc_enable.setter
    def rlc_enable(self, value):
        rlc = self.core.rlc(self._edb_pin_pair)
        rlc.r_enabled = value
        self._model.set_rlc(self._edb_pin_pair, rlc)

    @property
    def resistance(self) -> float:
        """Resistance.

        Returns
        -------
        float
            Resistance value.

        """
        rlc = self.core.rlc(self._edb_pin_pair)
        return rlc.r

    @resistance.setter
    def resistance(self, value):
        rlc = self.core.rlc(self._edb_pin_pair)
        rlc.r = value
        self._model.set_rlc(self._edb_pin_pair, rlc)

    @property
    def inductance(self) -> float:
        """Inductance.

        Returns
        -------
        float
            Inductance value.

        """
        rlc = self.core.rlc(self._edb_pin_pair)
        return rlc.l

    @inductance.setter
    def inductance(self, value):
        rlc = self.core.rlc(self._edb_pin_pair)
        rlc.l = value
        self._model.set_rlc(self._edb_pin_pair, rlc)

    @property
    def capacitance(self) -> float:
        """Capacitance.

        Returns
        -------
        float
            Capacitance value.

        """
        rlc = self.core.rlc(self._edb_pin_pair)
        return rlc.c

    @capacitance.setter
    def capacitance(self, value):
        rlc = self.core.rlc(self._edb_pin_pair)
        rlc.c = value
        self._model.set_rlc(self._edb_pin_pair, rlc)

    @property
    def rlc_values(self) -> list[float]:
        """Rlc value.

        Returns
        -------
        List[float, float, float]
            [R value, L value, C value].

        """
        rlc = self.core.rlc(self._edb_pin_pair)

        return [Value(rlc.r), Value(rlc.l), Value(rlc.c)]

    @rlc_values.setter
    def rlc_values(self, values):  # pragma: no cover
        rlc = self.core.rlc(self._edb_pin_pair)
        rlc.r = Value(values[0])
        rlc.l = Value(values[1])
        rlc.c = Value(values[2])
        self._model.set_rlc(self._edb_pin_pair, rlc)

    @property
    def is_parallel(self) -> bool:
        """Check if the pin pair model is parallel.

        Returns
        -------
        bool
            True if the pin pair model is parallel, False otherwise.

        """
        rlc = self.core.rlc(self._edb_pin_pair)
        return rlc.is_parallel

    @is_parallel.setter
    def is_parallel(self, value):
        rlc = self.core.rlc(self._edb_pin_pair)
        rlc.is_parallel = value
        self._model.set_rlc(self._edb_pin_pair, rlc)


class PinPairModel:
    """Manage pin-pair model."""

    def __init__(self, component: "Component"):
        self._component = component
        self._pedb = component._pedb
        self.core = self._component.component_property.model

    @classmethod
    def create(
        cls,
        component: Component,
        resistance: float | None = None,
        inductance: float | None = None,
        capacitance: float | None = None,
        pin1_name: str | None = None,
        pin2_name: str | None = None,
        is_parallel: bool = False,
    ) -> "PinPairModel":
        """Create pin pair model. Pin pair model is defined between two pins, and it can be used to define the RLC model
        between two pins. Adding optional RLC values will enable the RLC model for the pin pair.

        Parameters
        ----------
        component : Component
            Edb instance.
        resistance : float, optional
            Resistance value. If not provided, the default value will be used. Default value is 0.
        inductance : float, optional
            Inductance value. If not provided, the default value will be used. Default value is 0.
        capacitance : float, optional
            Capacitance value. If not provided, the default value will be used. Default value is 0.
        pin1_name : str, optional
            First pin name. If not provided, the default name will be used. Default name is `1`.
        pin2_name : str, optional
            Second pin name. If not provided, the default name will be used. Default name is `2`.
        is_parallel : bool, optional
            Whether the RLC model is parallel. If not provided, the default value will be used

        Returns
        -------
        PinPairModel
            The created pin pair model.

        """
        core_pin_pair = CorePinPairModel.create()
        rlc = CoreRlc()
        if resistance is not None:
            rlc.r_enabled = True  # codacy-disable-line
            rlc.r = Value(resistance)  # codacy-disable-line
        if inductance is not None:
            rlc.l_enabled = True  # codacy-disable-line
            rlc.l = Value(inductance)  # codacy-disable-line
        if capacitance is not None:
            rlc.c_enabled = True  # codacy-disable-line
            rlc.c = Value(capacitance)  # codacy-disable-line
        rlc.is_parallel = is_parallel
        if not pin1_name:
            pin1_name = "1"
        if not pin2_name:
            pin2_name = "2"
        core_pin_pair.set_rlc(pin_pair=(pin1_name, pin2_name), rlc=rlc)
        component_property = component.component_property
        component_property.model = core_pin_pair
        component.component_property = component_property
        return cls(component)

    @property
    def pin_pairs(self) -> list[PinPair]:
        """Get all pin pairs.

        Returns
        -------
        List[Tuple[str, str]]
            List of pin pairs.

        """
        return [PinPair(self, i) for i in self.core.pin_pairs()]

    @property
    def is_null(self) -> bool:
        """Check if the pin pair model is null.

        Returns
        -------
        bool
            True if the pin pair model is null, False otherwise.

        """
        return self.core.is_null

    @property
    def rlc(self, pin_pair: tuple[str, str] = None) -> CoreRlc | None:
        """Retrieve RLC model given pin pair.

        If pin pair is not provided, the first pin pair will be used by default.
        If there is no pin pair, ``None`` will be returned.

        Parameters
        ----------
        pin_pair : Tuple[str, str], optional
            Tuple of pin names (first_pin, second_pin). If not provided, the first pin pair will be used by default.
            If not provided and there is no pin pair, the first pin will be taken.

        Returns
        -------
        CoreRlc
            RLC model for the pin pair.
        """
        pp = self.core.pin_pairs()
        if not pp:
            self._pedb.logger.warning("No pin pair found. Returning None.")
            return None
        if pin_pair:
            for p in pp:
                if p[0] == pin_pair[0] and p[1] == pin_pair[1]:
                    pin_pair = self.core.rlc(pp)
                else:
                    self._pedb.logger.warning(
                        f"Pin pair {pin_pair} not found. Returning RLC for the first pin pair {pp[0]}."
                    )
                    pin_pair = pp[0]
        else:
            pin_pair = pp[0]
        return self.core.rlc(pin_pair)

    def set_rlc(self, pin_pair: tuple[str, str], rlc: CoreRlc):
        """Set RLC model for the pin pair.

        Parameters
        ----------
        pin_pair : Tuple[str, str]
            Tuple of pin names (first_pin, second_pin).
        rlc : CoreRlc
            RLC model to set for the pin pair.

        """
        self.core.set_rlc(pin_pair=pin_pair, rlc=rlc)
        component_property = self._component.component_property
        component_property.model = self.core
        self._component.component_property = component_property

    def delete_rlc(self, pin_pair: tuple[str, str]):
        """Delete RLC model for the pin pair.

        Parameters
        ----------
        pin_pair : Tuple[str, str]
            Tuple of pin names (first_pin, second_pin).

        """
        if pin_pair in self.pin_pairs:
            self.core.delete_rlc(pin_pair=pin_pair)

    def add_pin_pair(
        self,
        r: float | None = None,
        l: float | None = None,
        c: float | None = None,
        r_enabled: bool | None = None,
        l_enabled: bool | None = None,
        c_enabled: bool | None = None,
        first_pin: str | None = None,
        second_pin: str | None = None,
        is_parallel: bool = False,
    ):
        """
        Add a pin pair definition.

        Parameters
        ----------
        r: float | None
        l: float | None
        c: float | None
        r_enabled: bool
        l_enabled: bool
        c_enabled: bool
        first_pin: str
        second_pin: str
        is_parallel: bool

        Returns
        -------

        """
        if r is None:
            # If resistance is not defined, set it to 0 and disable it
            r = "0ohm"
            en_res = False
        else:
            # If resistance is defined, use the provided value and enabled status
            en_res = True if r_enabled is True or r_enabled is None else False
        if l is None:
            # If inductance is not defined, set it to 0 and disable it
            l = "0nH"
            en_ind = False
        else:
            # If inductance is defined, use the provided value and enabled status
            en_ind = True if l_enabled is True or l_enabled is None else False
        if c is None:
            # If capacitance is not defined, set it to 0 and disable it
            c = "0pF"
            en_cap = False
        else:
            # If capacitance is defined, use the provided value and enabled status
            en_cap = True if c_enabled is True or c_enabled is None else False

        rlc = CoreRlc(
            r,
            en_res,
            l,
            en_ind,
            c,
            en_cap,
            is_parallel,
        )
        self.set_rlc((first_pin, second_pin), rlc)
