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


class SparamModel:  # pragma: no cover
    """Manage :class:`SParameterModel <ansys.edb.core.hierarchy.sparameter_model.SParameterModel>`"""

    def __init__(self, edb_object):
        self.core = edb_object
        self._edb_model = edb_object

    @property
    def is_null(self):
        """Check if the S-parameter model is null.

        Returns
        -------
        bool
            True if the S-parameter model is null, False otherwise.

        """
        return self.core.is_null

    @property
    def name(self):
        """Get the name of the S-parameter model.

        Returns
        -------
        str
            The name of the S-parameter model.

        """
        return self.core.component_model

    @name.setter
    def name(self, value):
        """Set the name of the S-parameter model.

        Parameters
        ----------
        value : str
            The new name for the S-parameter model.

        """
        self.core.component_model = value

    @property
    def component_model_name(self):
        """Get the name of the S-parameter model.

        Returns
        -------
        str
            The name of the S-parameter model.

        """
        return self.core.component_model

    @component_model_name.setter
    def component_model_name(self, value):
        """Set the name of the S-parameter model.

        Parameters
        ----------
        value : str
            The new name for the S-parameter model.

        """
        self.core.component_model = value

    @property
    def reference_net(self):
        """Get the reference net of the S-parameter model.

        Returns
        -------
        str
            The reference net of the S-parameter model.

        """
        return self.core.reference_net

    @reference_net.setter
    def reference_net(self, value):
        """Set the reference net of the S-parameter model.

        Parameters
        ----------
        value : str
            The new reference net for the S-parameter model.

        """
        self.core.reference_net = value

    @property
    def file_path(self):
        """Get the file path of the S-parameter model.

        Returns
        -------
        str
            The file path of the S-parameter model.

        """
        return self.core.file_path

    @file_path.setter
    def file_path(self, value):
        """Set the file path of the S-parameter model.

        Parameters
        ----------
        value : str
            The new file path for the S-parameter model.

        """
        self.core.file_path = value
