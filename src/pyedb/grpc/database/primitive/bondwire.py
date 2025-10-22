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

from ansys.edb.core.primitive.bondwire import (
    Bondwire as GrpcBondWire,
    BondwireCrossSectionType as GrpcBondwireCrossSectionType,
    BondwireType as GrpcBondWireType,
)

from pyedb.grpc.database.utility.value import Value


class Bondwire(GrpcBondWire):
    """Class representing a bond-wire object."""

    def __init__(self, _pedb, edb_object):
        super().__init__(edb_object.msg)
        self._pedb = _pedb
        self._edb_object = edb_object
        # TODO add create and delete methods to keep cache in sync

    @property
    def material(self):
        """Bondwire material

        Returns
        -------
        str
            Material name.

        """
        return self.get_material().value

    @material.setter
    def material(self, value):
        self.set_material(value)

    @property
    def type(self):
        """str: Bondwire-type of a bondwire object. Supported values for setter: `"apd"`, `"jedec4"`, `"jedec5"`,
        `"num_of_type"`"""
        return super().type.name.lower()

    @type.setter
    def type(self, bondwire_type):
        mapping = {
            "apd": GrpcBondWireType.APD,
            "jedec4": GrpcBondWireType.JEDEC4,
            "jedec5": GrpcBondWireType.JEDEC5,
            "num_of_type": GrpcBondWireType.NUM_OF_TYPE,
        }
        super(Bondwire, self.__class__).type.__set__(self, mapping[bondwire_type])

    @property
    def cross_section_type(self):
        """str: Bondwire-cross-section-type of a bondwire object. Supported values for setter: `"round",
        `"rectangle"`

        Returns
        -------
        str
            cross section type.
        """
        return super().cross_section_type.name.lower()

    @cross_section_type.setter
    def cross_section_type(self, cross_section_type):
        mapping = {"round": GrpcBondwireCrossSectionType.ROUND, "rectangle": GrpcBondwireCrossSectionType.RECTANGLE}
        super(Bondwire, self.__class__).cross_section_type.__set__(self, mapping[cross_section_type])

    @property
    def cross_section_height(self):
        """float: Bondwire-cross-section height of a bondwire object.

        Returns
        -------
        float
            Cross section height.
        """
        return Value(super().cross_section_height)

    @cross_section_height.setter
    def cross_section_height(self, cross_section_height):
        super(Bondwire, self.__class__).cross_section_height.__set__(self, Value(cross_section_height))

    @property
    def width(self):
        """:class:`Value <ansys.edb.utility.Value>`: Width of a bondwire object.

        Returns
        -------
        float
            Width value.
        """
        return Value(super().width)

    @width.setter
    def width(self, width):
        super(Bondwire, self.__class__).width.__set__(self, Value(width))
