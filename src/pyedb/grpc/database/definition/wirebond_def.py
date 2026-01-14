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
    ApdBondwireDef as GrpcApdBondwireDef,
    Jedec4BondwireDef as GrpcJedec4BondwireDef,
    Jedec5BondwireDef as GrpcJedec5BondwireDef,
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

    @property
    def height(self):
        """Get the bondwire top-to-die distance of the bondwire definition."""
        return self.get_parameters()

    @height.setter
    def height(self, value):
        """Set the bondwire top-to-die distance of the bondwire definition."""
        self.set_parameters(value)

    def delete(self):
        self.core.delete()

    def get_parameters(self):
        """Get the bondwire top-to-die distance of the JEDEC 4 bondwire definition.

        Returns
        -------
        float
            Bondwire top-to-die distance.
        """
        return self.core.get_parameters().value

    def set_parameters(self, parameters):
        """Set the bondwire top-to-die distance of the JEDEC 4 bondwire definition.

        Parameters
        ----------
        parameters : float
            Bondwire top-to-die distance.
        """

        self.core.set_parameters(self._pedb.value(parameters))


class Jedec4BondwireDef(BondwireDef):
    """Class representing a JEDEC 4 bondwire definition."""

    def __init__(self, pedb, core=None):
        super().__init__(pedb, core)
        self._pedb = pedb
        self.core = core

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
        grpc_bondwire_def = GrpcJedec4BondwireDef.create(edb._db, name)
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
        grpc_bondwire_def = GrpcJedec4BondwireDef.find_by_name(edb._db, name)
        if grpc_bondwire_def:
            return Jedec4BondwireDef(edb, grpc_bondwire_def)
        return None


class Jedec5BondwireDef(BondwireDef):
    """Class representing a JEDEC 5 bondwire definition."""

    def __init__(self, pedb, core=None):
        super().__init__(pedb, core)
        self._pedb = pedb
        self.core = core

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
        grpc_bondwire_def = GrpcJedec5BondwireDef.create(edb._db, name)
        return cls(edb, grpc_bondwire_def)

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
        grpc_bondwire_def = GrpcJedec5BondwireDef.find_by_name(edb._db, name)
        if grpc_bondwire_def:
            return Jedec5BondwireDef(edb, grpc_bondwire_def)
        return None


class ApdBondwireDef(BondwireDef):
    """Class representing an Apd bondwire definition."""

    def __init__(self, pedb, core=None):
        super().__init__(pedb, core)
        self._pedb = pedb
        self.core = core

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
        grpc_bondwire_def = GrpcApdBondwireDef.create(edb._db, name)
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
        grpc_bondwire_def = GrpcApdBondwireDef.find_by_name(edb._db, name)
        if grpc_bondwire_def:
            return ApdBondwireDef(edb, grpc_bondwire_def)
        return None
