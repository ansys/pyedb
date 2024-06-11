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

"""
"""

import csv
import os
from os.path import dirname

import numpy as np
import pytest

example_models_path = os.path.join(dirname(dirname(dirname(os.path.realpath(__file__)))), "example_models")

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

    # START
    pts = np.array(points)

    # Enlarge the point base
    n = 2
    m = 2

    min_x = pts[:, 0].min()
    max_x = pts[:, 0].max()
    min_y = pts[:, 1].min()
    max_y = pts[:, 1].max()
    size_x = max_x - min_x
    size_y = max_y - min_y

    size_y_n = size_y * 1.5

    # Function to rotate points
    def rotate_points(points, angle_degrees):
        angle_radians = np.radians(angle_degrees)
        # Create the rotation matrix
        rotation_matrix = np.array(
            [[np.cos(angle_radians), -np.sin(angle_radians)], [np.sin(angle_radians), np.cos(angle_radians)]]
        )
        # Apply the rotation matrix to each point
        rotated_points = points.dot(rotation_matrix.T)
        return rotated_points

    center = np.array([(min_x + max_x) / 2, (min_y + max_y) / 2])
    centered_points = pts - center
    # axis autoscale: squared
    centered_points[:, 0] = centered_points[:, 0] / size_x * size_y
    pts2 = centered_points
    for r in range(n):
        for c in range(m):
            if r == 0 and c == 0:
                continue
            rotated_points = rotate_points(centered_points, 15 * (r + 1) * (c + 1))

            move_vector = np.array([r * size_y_n, c * size_y_n])
            additional_points = rotated_points + move_vector
            # Add the additional points to the initial array
            pts2 = np.vstack((pts2, additional_points))

    return pts2
