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

from ansys.edb.core.definition.bondwire_def import (
    ApdBondwireDef as CoreApdBondwireDef,
    Jedec4BondwireDef as CoreJedec4BondwireDef,
    Jedec5BondwireDef as CoreJedec5BondwireDef,
)


class BondwireDef:
    def __init__(self, pedb, core=None):
        self._pedb = pedb
        self.core = core

    @property
    def name(self):
        """Get the name of the bondwire definition."""
        return self.core.name.value

    @name.setter
    def name(self, value):
        """Set the name of the bondwire definition."""
        self.core.name = self._pedb.value(value)

    def delete(self):
        self.core.delete()


class Jedec4BondwireDef(BondwireDef):
    """Class representing a JEDEC 4 bondwire definition."""

    def __init__(self, pedb, core=None):
        super().__init__(pedb, core)

    @property
    def height(self):
        """Get the bondwire top-to-die distance of the JEDEC 4 bondwire definition."""
        return self.get_parameters()

    @height.setter
    def height(self, value):
        """Set the bondwire top-to-die distance of the JEDEC 4 bondwire definition."""
        self.set_parameters(value)

    def get_parameters(self):
        """Get the bondwire top-to-die distance of the JEDEC 4 bondwire definition.

        Returns
        -------
        float
            Bondwire top-to-die distance.
        """
        return self.core.get_parameters().value

    def set_parameters(self, height):
        """Set the bondwire top-to-die distance of the JEDEC 4 bondwire definition.

        Parameters
        ----------
        height : float
            Bondwire top-to-die distance.
        """
        self.core.set_parameters(self._pedb.value(height))

    @classmethod
    def create(cls, edb, name):
        """Create a new JEDEC 4 bondwire definition.

        Parameters
        ----------
        edb : :class:`pyedb.edb`
            Inherited AEDT object.
        name : str
            Name of the JEDEC 4 bondwire definition.

        Returns
        -------
        :class:`pyedb.grpc.database.definition.wirebond_def.Jedec4BondwireDef`
            The created JEDEC 4 bondwire definition.
        """
        grpc_bondwire_def = CoreJedec4BondwireDef.create(edb._db, name)
        return cls(edb, grpc_bondwire_def)

    @staticmethod
    def find_by_name(edb, name):
        """Find a JEDEC 4 bondwire definition by name.

        Parameters
        ----------
        edb : :class:`pyedb.edb`
            Inherited AEDT object.
        name : str
            Name of the JEDEC 4 bondwire definition.

        Returns
        -------
        :class:`pyedb.grpc.database.definition.wirebond_def.Jedec4BondwireDef` or None
            The found JEDEC 4 bondwire definition or None if not found.
        """
        core_bondwire_def = CoreJedec4BondwireDef.find_by_name(edb._db, name)
        if core_bondwire_def and not core_bondwire_def.is_null:
            return Jedec4BondwireDef(edb, core_bondwire_def)
        return None


class Jedec5BondwireDef(BondwireDef):
    """Class representing a JEDEC 5 bondwire definition."""

    def __init__(self, pedb, core=None):
        super().__init__(pedb, core)

    @property
    def height(self):
        """Get the bondwire top-to-die distance of the JEDEC 5 bondwire definition."""
        return self.get_parameters()[0]

    @height.setter
    def height(self, value):
        """Set the bondwire top-to-die distance, keeping existing angles."""
        _, die_pad_angle, lead_pad_angle = self.get_parameters()
        self.set_parameters(value, die_pad_angle, lead_pad_angle)

    def get_parameters(self):
        """Get the parameters of the JEDEC 5 bondwire definition.

        Returns
        -------
        tuple[float, float, float]
            Tuple of (top_to_die_distance, die_pad_angle, lead_pad_angle).
        """
        result = self.core.get_parameters()
        return result[0].value, result[1].value, result[2].value

    def set_parameters(self, top_to_die_distance, die_pad_angle, lead_pad_angle):
        """Set the parameters of the JEDEC 5 bondwire definition.

        Parameters
        ----------
        top_to_die_distance : float
            Bondwire top-to-die distance.
        die_pad_angle : float
            Die pad angle in degrees.
        lead_pad_angle : float
            Lead pad angle in degrees.
        """
        self.core.set_parameters(
            self._pedb.value(top_to_die_distance),
            self._pedb.value(die_pad_angle),
            self._pedb.value(lead_pad_angle),
        )

    @classmethod
    def create(cls, edb, name):
        """Create a new JEDEC 5 bondwire definition.

        Parameters
        ----------
        edb : :class:`pyedb.edb`
            Inherited AEDT object.
        name : str
            Name of the JEDEC 5 bondwire definition.

        Returns
        -------
        :class:`pyedb.grpc.database.definition.wirebond_def.Jedec5BondwireDef`
            The created JEDEC 5 bondwire definition.
        """
        core_bondwire_def = CoreJedec5BondwireDef.create(edb._db, name)
        return cls(edb, core_bondwire_def)

    @staticmethod
    def find_by_name(edb, name):
        """Find a JEDEC 5 bondwire definition by name.

        Parameters
        ----------
        edb : :class:`pyedb.edb`
            Inherited AEDT object.
        name : str
            Name of the JEDEC 5 bondwire definition.

        Returns
        -------
        :class:`pyedb.grpc.database.definition.wirebond_def.Jedec5BondwireDef` or None
            The found JEDEC 5 bondwire definition or None if not found.
        """
        grpc_bondwire_def = CoreJedec5BondwireDef.find_by_name(edb._db, name)
        if grpc_bondwire_def and not grpc_bondwire_def.is_null:
            return Jedec5BondwireDef(edb, grpc_bondwire_def)
        return None


class ApdBondwireDef(BondwireDef):
    """Class representing an Apd bondwire definition."""

    def __init__(self, pedb, core=None):
        super().__init__(pedb, core)

    @property
    def height(self):
        """Not applicable for APD bondwire definitions. Raises AttributeError."""
        raise AttributeError("APD bondwire definitions do not have a height parameter. Use 'parameter_block' instead.")

    @height.setter
    def height(self, value):
        raise AttributeError("APD bondwire definitions do not have a height parameter. Use 'set_parameters()' instead.")

    @property
    def parameter_block(self):
        """Get the APD bondwire parameter block string.

        Returns
        -------
        str
            APD bondwire parameter block (bwd descriptor string).
        """
        return self.get_parameters()

    @parameter_block.setter
    def parameter_block(self, value):
        """Set the APD bondwire parameter block string."""
        self.set_parameters(value)

    def get_parameters(self):
        """Get the APD bondwire parameter block string.

        Returns
        -------
        str
            APD bondwire parameter block (bwd descriptor string).
        """
        result = self.core.get_parameters()
        return result.value if hasattr(result, "value") else result

    def set_parameters(self, parameter_block):
        """Set the APD bondwire parameter block string.

        Parameters
        ----------
        parameter_block : str
            APD bondwire parameter block (bwd descriptor string).
        """
        self.core.set_parameters(parameter_block)

    @classmethod
    def create(cls, edb, name):
        """Create a new Apd bondwire definition.

        Parameters
        ----------
        edb : :class:`pyedb.edb`
            Inherited AEDT object.
        name : str
            Name of the Apd bondwire definition.

        Returns
        -------
        :class:`pyedb.grpc.database.definition.wirebond_def.ApdBondwireDef`
            The created Apd bondwire definition.
        """
        grpc_bondwire_def = CoreApdBondwireDef.create(edb._db, name)
        return cls(edb, grpc_bondwire_def)

    @staticmethod
    def find_by_name(edb, name):
        """Find an Apd bondwire definition by name.

        Parameters
        ----------
        edb : :class:`pyedb.edb`
            Inherited AEDT object.
        name : str
            Name of the Apd bondwire definition.

        Returns
        -------
        :class:`pyedb.grpc.database.definition.wirebond_def.ApdBondwireDef` or None
            The found Apd bondwire definition or None if not found.
        """
        grpc_bondwire_def = CoreApdBondwireDef.find_by_name(edb._db, name)
        if grpc_bondwire_def and not grpc_bondwire_def.is_null:
            return ApdBondwireDef(edb, grpc_bondwire_def)
        return None
