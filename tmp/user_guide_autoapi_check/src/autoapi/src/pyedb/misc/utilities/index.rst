src.pyedb.misc.utilities
========================

.. py:module:: src.pyedb.misc.utilities

.. autoapi-nested-parse::

   Module gathering utility functions for PyEDB modules.



Functions
---------

.. autoapisummary::

   src.pyedb.misc.utilities.compute_arc_points


Module Contents
---------------

.. py:function:: compute_arc_points(p1: list[float], p2: list[float], h: float, n: int = 6, tol: float = 1e-12) -> tuple[list[float], list[float]]

   Get the points of the arc.

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



