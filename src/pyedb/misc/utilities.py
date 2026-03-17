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
        Arc height (sagitta). Positive values arc upward from p1 to p2,
        negative values arc downward.
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

    Notes
    -----
    Correctly handles arcs that subtend more than 180° (h > r case).

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

    if h > 0:
        x1, y1, x2, y2 = p1[0], p1[1], p2[0], p2[1]
        reverse = False
    else:
        x1, y1, x2, y2 = p2[0], p2[1], p1[0], p1[1]
        h = -h
        reverse = True

    xa = (x2 - x1) / 2
    ya = (y2 - y1) / 2
    a = math.sqrt(xa**2 + ya**2)
    if a < tol:
        return [], []

    r = (a**2) / (2 * h) + h / 2
    b = math.sqrt(max(r**2 - a**2, 0.0))

    # h > r means arc > semicircle: center is on the same side as the bulge
    sign = -1.0 if h > r else 1.0
    xc = x1 + xa + sign * b * ya / a
    yc = y1 + ya - sign * b * xa / a

    alpha = math.atan2(y1 - yc, x1 - xc)
    beta = math.atan2(y2 - yc, x2 - xc)

    dangle = alpha - beta
    if dangle <= 0:
        dangle += 2 * math.pi
    if h > r and dangle < math.pi:
        dangle = 2 * math.pi - dangle

    xr, yr = [], []
    for i in range(1, n + 1):
        t = i / (n + 1)
        angle = alpha - t * dangle
        xr.append(xc + r * math.cos(angle))
        yr.append(yc + r * math.sin(angle))

    if reverse:
        xr.reverse()
        yr.reverse()

    return xr, yr
