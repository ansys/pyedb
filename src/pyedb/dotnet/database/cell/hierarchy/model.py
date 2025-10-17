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

    def __init__(self, pedb, edb_object=None):
        super().__init__(pedb, edb_object)

    @property
    def pin_pairs(self):
        """List of pin pair definitions."""
        return list(self._edb_object.PinPairs)

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
