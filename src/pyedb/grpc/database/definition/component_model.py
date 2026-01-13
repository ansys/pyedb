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

from ansys.edb.core.definition.component_model import (
    ComponentModel as GrpcComponentModel,
)


class ComponentModel:
    """Class managing :class:`ComponentModel <ansys.edb.core.definition.component_model.ComponentModel>`."""

    def __init__(self, edb_object):
        self.core = GrpcComponentModel(edb_object.msg)

    @property
    def is_null(self):
        """Check if the component model is null.

        Returns
        -------
        bool
            True if the component model is null, False otherwise.

        """
        return self.core.is_null

    @property
    def name(self):
        """Get the name of the component model.

        Returns
        -------
        str
            The name of the component model.

        """
        return self.core.name

    @property
    def reference_file(self):
        """Get the reference file of the component model.

        Returns
        -------
        str
            The reference file of the component model.

        """
        return self.core.reference_file


class NPortComponentModel:
    """Class managing :class:`NPortComponentModel <ansys.edb.core.definition.component_model.ComponentModel>`"""

    def __init__(self, edb_object):
        self.core = GrpcComponentModel(edb_object.msg)
