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


class CfgBase:
    protected_attributes = []

    def get_attributes(self, exclude=None):
        attrs = {i: j for i, j in self.__dict__.items() if i not in self.protected_attributes}
        if exclude is not None:
            exclude = exclude if isinstance(exclude, list) else [exclude]
            attrs = {i: j for i, j in attrs.items() if i not in exclude}
        attrs = {i: j for i, j in attrs.items() if not i.startswith("_")}
        attrs = {i: j for i, j in attrs.items() if j is not None}
        return attrs

    def set_attributes(self, pedb_object):
        attrs = self.get_attributes()
        for attr, value in attrs.items():
            if attr not in dir(pedb_object):
                raise AttributeError(f"Invalid attribute '{attr}' in '{pedb_object}'")
            setattr(pedb_object, attr, value)
