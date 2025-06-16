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

import warnings

from pyedb.generic.general_methods import deprecate_argument_name

VALUE = "Dummy value"
NEW_VALUE = "Other dummy value"
WARNING_MSG = "Argument `old_arg` is deprecated for method `dummy_function`; use `new_arg` instead."


@deprecate_argument_name({"old_arg": "new_arg"})
def dummy_function(new_arg=None):
    """Dummy function used for testing."""
    return new_arg


def test_warning_on_deprecated_argument():
    """Test deprecation warning on deprecated argument."""
    with warnings.catch_warnings(record=True) as log:
        warnings.simplefilter("always")
        res = dummy_function(old_arg=VALUE)
        warning = log[-1]

        assert VALUE == res
        assert 1 == len(log)
        assert WARNING_MSG in str(warning.message)


def test_warning_on_new_argument():
    """Test deprecation warning on new argument."""
    with warnings.catch_warnings(record=True) as log:
        warnings.simplefilter("always")
        res = dummy_function(new_arg=VALUE)

        assert VALUE == res
        assert 0 == len(log)


def test_warning_on_both_deprecated_and_new_arguments():
    """Test deprecation warning on both new and old arguments."""
    with warnings.catch_warnings(record=True) as log:
        warnings.simplefilter("always")
        res = dummy_function(new_arg=NEW_VALUE, old_arg=VALUE)
        warning = log[-1]

        assert NEW_VALUE == res
        assert 1 == len(log)
        assert WARNING_MSG in str(warning.message)
