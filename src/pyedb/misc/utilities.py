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

"""Module gathering utility functions for PyEDB modules."""

import math


def compute_arc_points(
    p1: list[float], p2: list[float], h: float, n: int = 6, tol: float = 1e-12
) -> tuple[list[float], list[float]]:
    """Get the points of the arc.

    Parameters
    ----------
    p1 : list[float]
        Arc starting point.
    p2 : list[float]
        Arc ending point.
    h : float
        Arc height.
    n : int, optional
        Number of points to generate along the arc.
        The default is ``6``.
    tol : float, optional
        Geometric tolerance.
        The default is ``1e-12``.

    Returns
    -------
    tuple[list[float], list[float]]
        Points generated along the arc as (x_coordinates, y_coordinates).

    Examples
    --------
    >>> from pyedb.misc.utilities import compute_arc_points
    >>> p1 = [0.0, 0.0]
    >>> p2 = [1.0, 0.0]
    >>> h = 0.2
    >>> xr, yr = compute_arc_points(p1, p2, h, n=6)
    >>> len(xr) == len(yr) == 6
    True

    """
    if abs(h) < tol:
        return [], []
    elif h > 0:
        reverse = False
        x1 = p1[0]
        y1 = p1[1]
        x2 = p2[0]
        y2 = p2[1]
    else:
        reverse = True
        x1 = p2[0]
        y1 = p2[1]
        x2 = p1[0]
        y2 = p1[1]
        h *= -1

    xa = (x2 - x1) / 2
    ya = (y2 - y1) / 2
    xo = x1 + xa
    yo = y1 + ya
    a = math.sqrt(xa**2 + ya**2)
    if a < tol:
        return [], []
    r = (a**2) / (2 * h) + h / 2
    if abs(r - a) < tol:
        b = 0
        th = 2 * math.asin(1)  # chord angle
    else:
        b = math.sqrt(r**2 - a**2)
        th = 2 * math.asin(a / r)  # chord angle

    # Center of the circle
    xc = xo + b * ya / a
    yc = yo - b * xa / a

    alpha = math.atan2((y1 - yc), (x1 - xc))
    xr = []
    yr = []
    for i in range(n):
        i += 1
        dth = (float(i) / (n + 1)) * th
        xi = xc + r * math.cos(alpha - dth)
        yi = yc + r * math.sin(alpha - dth)
        xr.append(xi)
        yr.append(yi)

    if reverse:
        xr.reverse()
        yr.reverse()

    return xr, yr
