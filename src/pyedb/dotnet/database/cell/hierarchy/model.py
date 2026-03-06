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

from pyedb.dotnet.database.cell.hierarchy.pin_pair_model import PinPair
from pyedb.dotnet.database.utilities.obj_base import ObjBase


class Model(ObjBase):
    """Manages model class."""

    def __init__(self, pedb, edb_object):
        super().__init__(pedb, edb_object)
        self._model_type_mapping = {"PinPairModel": self._pedb.core.Cell}

    @property
    def model_type(self):
        """Component model type."""
        return self._edb_object.GetModelType().ToString()


class PinPairModel(Model):
    """Manages pin pair model class."""

    def __init__(self, component, edb_object=None):
        super().__init__(component._pedb, edb_object)
        self.component = component

    @property
    def pin_pairs(self):
        """List of pin pair definitions."""
        return [PinPair(self.component, i) for i in self._edb_object.PinPairs]

    def delete_pin_pair_rlc(self, pin_pair):
        """Delete a pin pair definition.

        Parameters
        ----------
        pin_pair: Ansys.Ansoft.Edb.Utility.PinPair

        Returns
        -------
        bool
        """
        return self._edb_object.DeletePinPairRlc(pin_pair)

    def _set_pin_pair_rlc(self, pin_pair, pin_par_rlc):
        """Set resistance, inductance, capacitance to a pin pair definition.

        Parameters
        ----------
        pin_pair: Ansys.Ansoft.Edb.Utility.PinPair
        pin_par_rlc: Ansys.Ansoft.Edb.Utility.Rlc

        Returns
        -------
        bool
        """
        return self._edb_object.SetPinPairRlc(pin_pair, pin_par_rlc)

    def add_pin_pair(
        self,
        r: float | None = None,
        l: float | None = None,
        c: float | None = None,
        r_enabled: bool | None = None,
        l_enabled: bool | None = None,
        c_enabled: bool | None = None,
        fisrt_pin: str | None = None,
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
        fisrt_pin: str
        second_pin: str
        is_parallel: bool

        Returns
        -------

        """
        m = self._pedb._edb.Cell.Hierarchy.PinPairModel()
        p = self._pedb._edb.Utility.PinPair(fisrt_pin, second_pin)
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

        rlc = self._pedb._edb.Utility.Rlc(
            self._pedb.edb_value(r),
            en_res,
            self._pedb.edb_value(l),
            en_ind,
            self._pedb.edb_value(c),
            en_cap,
            is_parallel,
        )
        m.SetPinPairRlc(p, rlc)
        core = self.component.component_property.core.Clone()
        core.SetModel(m)
        self.component.component_property = core
