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


class EdbDesignOptions:
    def __init__(self, active_cell):
        self._active_cell = active_cell

    @property
    def suppress_pads(self):
        """Whether to suppress non-functional pads.

        Returns
        -------
        bool
            ``True`` if suppress non-functional pads is on, ``False`` otherwise.

        """
        return self._active_cell.GetSuppressPads()

    @suppress_pads.setter
    def suppress_pads(self, value):
        self._active_cell.SetSuppressPads(value)

    @property
    def antipads_always_on(self):
        """Whether to always turn on antipad.

        Returns
        -------
        bool
            ``True`` if antipad is always on, ``False`` otherwise.

        """
        return self._active_cell.GetAntiPadsAlwaysOn()

    @antipads_always_on.setter
    def antipads_always_on(self, value):
        self._active_cell.SetAntiPadsAlwaysOn(value)
