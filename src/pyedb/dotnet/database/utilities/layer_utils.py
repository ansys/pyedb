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

from System.Reflection import BindingFlags  # type: ignore


def clear_is_owner(obj):
    """Use reflection to set the protected IsOwner property to False,
    preventing the buggy EDBLayer_Cleanup from being called in the destructor.

    This must be called on every Layer object obtained from the EDB API
    (via Clone(), LayerCollection construction, or any other means) to prevent
    the native EDBLayer_Cleanup destructor from running on Python-owned wrappers
    and causing memory access violations during garbage collection.
    """
    prop = obj.GetType().GetProperty("IsOwner", BindingFlags.NonPublic | BindingFlags.Instance)
    prop.SetValue(obj, False, None)

