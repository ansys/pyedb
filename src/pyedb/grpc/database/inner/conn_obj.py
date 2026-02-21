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

from ansys.edb.core.database import ProductIdType as CoreProductIdType

from pyedb.generic.product_property import EMProperties
from pyedb.grpc.database.inner.layout_obj import LayoutObj


class ConnObj(LayoutObj):
    def __init__(self, pedb, core):
        super().__init__(pedb, core)

    def get_em_properties(self) -> EMProperties:
        """Get EM properties."""
        em_string = self.core.get_product_property(CoreProductIdType.DESIGNER, 18)
        if em_string:
            return EMProperties.from_em_string(em_string)
        else:
            return EMProperties()

    def set_em_properties(self, em_properties: EMProperties):
        em_string = em_properties.to_em_string()
        self.core.set_product_property(CoreProductIdType.DESIGNER, 18, em_string)

    @property
    def dcir_equipotential_region(self) -> bool:
        """Get DCIR equipotential region property of a primitive or a padstack instance."""
        emp = self.get_em_properties()
        return emp.properties.dcir_equipotential_region

    @dcir_equipotential_region.setter
    def dcir_equipotential_region(self, value: bool):
        emp = self.get_em_properties()
        emp.properties.dcir_equipotential_region = value
        self.set_em_properties(emp)
