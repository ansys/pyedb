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

""" """

import csv
import os
from os.path import dirname

import pytest

example_models_path = os.path.join(dirname(dirname(os.path.realpath(__file__))), "example_models")

test_subfolder = "misc"


@pytest.fixture(scope="function", autouse=False)
def points_for_line_detection():
    csv_file = os.path.join(example_models_path, test_subfolder, "points_for_line_detection.csv")

    points = []
    with open(csv_file, mode="r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            x, y = map(float, row)
            points.append((x, y))

    return points


@pytest.fixture(scope="function", autouse=False)
def points_for_line_detection_135():
    csv_file = os.path.join(example_models_path, test_subfolder, "points_for_line_detection_135.csv")

    points = []
    with open(csv_file, mode="r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            x, y = map(float, row)
            points.append((x, y))

    return points
