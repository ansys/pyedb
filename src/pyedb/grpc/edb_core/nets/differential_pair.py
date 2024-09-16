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


from ansys.edb.core.net.differential_pair import (
    DifferentialPair as GrpcDifferentialPair,
)

from pyedb.grpc.edb_core.nets.net import Net


class DifferentialPair(GrpcDifferentialPair):
    """Manages EDB functionalities for a primitive.
    It inherits EDB object properties.
    """

    def __init__(self, core_app, edb_object=None):
        super().__init__(edb_object)
        self._app = core_app
        self._core_components = core_app.components
        self._core_primitive = core_app.modeler
        self._core_nets = core_app.nets
        DifferentialPair.__init__(self, self._app, edb_object)

    @property
    def positive_net(self):
        """Positive Net."""
        return Net(self._app, self.positive_net)

    @property
    def negative_net(self):
        """Negative Net."""
        return Net(self._app, self.negative_net)
