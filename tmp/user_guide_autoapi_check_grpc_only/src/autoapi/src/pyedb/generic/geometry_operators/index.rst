src.pyedb.generic.geometry_operators
====================================

.. py:module:: src.pyedb.generic.geometry_operators


Classes
-------

.. autoapisummary::

   src.pyedb.generic.geometry_operators.GeometryOperators


Module Contents
---------------

.. py:class:: GeometryOperators

   Bases: :py:obj:`object`


   Manages geometry operators.


   .. py:method:: List2list(input_list) -> list
      :staticmethod:


      Convert a C# list object to a Python list.

      This function performs a deep conversion.

      Parameters
      ----------
      input_list : list
          C# list to convert to a Python list.

      Returns
      -------
      list
          Converted Python list.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> csharp_list = [1, 2, [3, 4]]
      >>> go.List2list(csharp_list)
      [1, 2, [3, 4]]




   .. py:method:: parse_dim_arg(string: str | float, scale_to_unit: str | None = None, variable_manager: VariableManager = None) -> float | str | None
      :staticmethod:


      Convert a number and unit to a float.

      Angles are converted in radians.

      Parameters
      ----------
      string : str or float
          String to convert. For example, ``"2mm"``.
      scale_to_unit : str or None, optional
          Units for the value to convert.
      variable_manager : VariableManager, optional
          Try to parse formula and returns numeric value.

      Returns
      -------
      float, str, or None
          Value for the converted value and units.

      Examples
      --------
      Parse ``"2mm"``.

      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> go.parse_dim_arg("2mm")
      0.002

      Use the optional argument ``scale_to_unit`` to specify the destination unit.

      >>> go.parse_dim_arg("2mm", scale_to_unit="mm")
      2.0




   .. py:method:: draft_type_str(val: int) -> str
      :staticmethod:


      Retrieve the draft type.

      Parameters
      ----------
      val : int
          ``SWEEPDRAFT`` enum value.

      Returns
      -------
      str
          Type of the draft.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> from pyedb.generic.constants import SWEEPDRAFT
      >>> go.draft_type_str(SWEEPDRAFT.Extended)
      'Extended'




   .. py:method:: get_mid_point(v1: list[float], v2: list[float]) -> list[float]
      :staticmethod:


      Evaluate the midpoint between two points.

      Parameters
      ----------
      v1 : list[float]
          List of ``[x, y, z]`` coordinates for the first point.
      v2 : list[float]
          List of ``[x, y, z]`` coordinates for the second point.

      Returns
      -------
      list[float]
          List of ``[x, y, z]`` coordinates for the midpoint.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> p1 = [0.0, 0.0, 0.0]
      >>> p2 = [2.0, 4.0, 6.0]
      >>> go.get_mid_point(p1, p2)
      [1.0, 2.0, 3.0]




   .. py:method:: get_triangle_area(v1: list[float], v2: list[float], v3: list[float]) -> float
      :staticmethod:


      Evaluate the area of a triangle defined by its three vertices.

      Parameters
      ----------
      v1 : list[float]
          List of ``[x, y, z]`` coordinates for the first vertex.
      v2 : list[float]
          List of ``[x, y, z]`` coordinates for the second vertex.
      v3 : list[float]
          List of ``[x, y, z]`` coordinates for the third vertex.

      Returns
      -------
      float
          Area of the triangle.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> v1 = [0.0, 0.0, 0.0]
      >>> v2 = [1.0, 0.0, 0.0]
      >>> v3 = [0.0, 1.0, 0.0]
      >>> go.get_triangle_area(v1, v2, v3)
      0.5




   .. py:method:: v_cross(a: list[float], b: list[float]) -> list[float]
      :staticmethod:


      Evaluate the cross product of two geometry vectors.

      Parameters
      ----------
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first vector.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second vector.

      Returns
      -------
      list[float]
          List of ``[x, y, z]`` coordinates for the result vector.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> a = [1.0, 0.0, 0.0]
      >>> b = [0.0, 1.0, 0.0]
      >>> go.v_cross(a, b)
      [0.0, 0.0, 1.0]




   .. py:method:: v_dot(a: list[float], b: list[float]) -> float | bool
      :staticmethod:


      Evaluate the dot product between two geometry vectors.

      Parameters
      ----------
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first vector.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second vector.

      Returns
      -------
      float, or bool
          Result of the dot product.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> a = [1.0, 2.0, 3.0]
      >>> b = [4.0, 5.0, 6.0]
      >>> go.v_dot(a, b)
      32.0




   .. py:method:: v_prod(s: float, v: list[float]) -> list[float]
      :staticmethod:


      Evaluate the product between a scalar value and a vector.

      Parameters
      ----------
      s : float
          Scalar value.
      v : list[float]
          List of values for the vector in the format ``[v1, v2,..., vn]``.
          The vector can be any length.

      Returns
      -------
      list[float]
          List of values for the result vector. This list is the
          same length as the list for the input vector.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> v = [1.0, 2.0, 3.0]
      >>> go.v_prod(2.0, v)
      [2.0, 4.0, 6.0]




   .. py:method:: v_rotate_about_axis(vector: list[float], angle: float, radians: bool = False, axis: str = 'z') -> tuple[float, float, float]
      :staticmethod:


      Evaluate rotation of a vector around an axis.

      Parameters
      ----------
      vector : list[float]
          List of the three component of the vector.
      angle : float
          Angle by which the vector is to be rotated (radians or degree).
      radians : bool, optional
          Whether the angle is expressed in radians. The default is ``False``.
      axis : str, optional
          Axis about which to rotate the vector. The default is ``"z"``.

      Returns
      -------
      tuple[float, float, float]
          List of values for the result vector.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> import math
      >>> v = [1.0, 0.0, 0.0]
      >>> go.v_rotate_about_axis(v, 90.0, axis="z")
      (6.123233995736766e-17, 1.0, 0.0)



   .. py:method:: v_sub(a: list[float], b: list[float]) -> list[float]
      :staticmethod:


      Evaluate two geometry vectors by subtracting them (a-b).

      Parameters
      ----------
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first vector.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second vector.

      Returns
      -------
      list[float]
          List of ``[x, y, z]`` coordinates for the result vector.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> a = [5.0, 7.0, 9.0]
      >>> b = [1.0, 2.0, 3.0]
      >>> go.v_sub(a, b)
      [4.0, 5.0, 6.0]




   .. py:method:: v_sum(a: list[float], b: list[float]) -> list[float]
      :staticmethod:


      Evaluate two geometry vectors by adding them (a+b).

      Parameters
      ----------
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first vector.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second vector.

      Returns
      -------
      list[float]
          List of ``[x, y, z]`` coordinates for the result vector.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> a = [1.0, 2.0, 3.0]
      >>> b = [4.0, 5.0, 6.0]
      >>> go.v_sum(a, b)
      [5.0, 7.0, 9.0]




   .. py:method:: v_norm(a: list[float]) -> float
      :staticmethod:


      Evaluate the Euclidean norm of a geometry vector.

      Parameters
      ----------
      a : list[float]
          List of ``[x, y, z]`` coordinates for the vector.

      Returns
      -------
      float
          Evaluated norm in the same unit as the coordinates for the input vector.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> a = [3.0, 4.0, 0.0]
      >>> go.v_norm(a)
      5.0




   .. py:method:: normalize_vector(v: list[float]) -> list[float]
      :staticmethod:


      Normalize a geometry vector.

      Parameters
      ----------
      v : list[float]
          List of ``[x, y, z]`` coordinates for vector.

      Returns
      -------
      list[float]
          List of ``[x, y, z]`` coordinates for the normalized vector.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> v = [3.0, 4.0, 0.0]
      >>> go.normalize_vector(v)
      [0.6, 0.8, 0.0]




   .. py:method:: v_points(p1: list[float], p2: list[float]) -> list[float]
      :staticmethod:


      Vector from one point to another point.

      Parameters
      ----------
      p1 : list[float]
          Coordinates ``[x1,y1,z1]`` for the first point.
      p2 : list[float]
          Coordinates ``[x2,y2,z2]`` for second point.

      Returns
      -------
      list[float]
          Coordinates ``[vx, vy, vz]`` for the vector from the first point to the second point.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> p1 = [1.0, 2.0, 3.0]
      >>> p2 = [4.0, 6.0, 8.0]
      >>> go.v_points(p1, p2)
      [3.0, 4.0, 5.0]




   .. py:method:: points_distance(p1: list[float], p2: list[float]) -> float | bool
      :staticmethod:


      Evaluate the distance between two points expressed as their Cartesian coordinates.

      Parameters
      ----------
      p1 : list[float]
          List of ``[x1,y1,z1]`` coordinates for the first point.
      p2 : list[float]
          List of ``[x2,y2,z2]`` coordinates for the second point.

      Returns
      -------
      float, or bool
          Distance between the two points in the same unit as the coordinates for the points.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> p1 = [0.0, 0.0, 0.0]
      >>> p2 = [3.0, 4.0, 0.0]
      >>> go.points_distance(p1, p2)
      5.0




   .. py:method:: find_point_on_plane(pointlists: list[list[float]], direction: int = 0) -> float
      :staticmethod:


      Find a point on a plane.

      Parameters
      ----------
      pointlists : list[list[float]]
          List of points.
      direction : int, optional
          Direction parameter. The default is ``0``.

      Returns
      -------
      float
          Point on plane.




   .. py:method:: distance_vector(p: list[float], a: list[float], b: list[float]) -> list[float]
      :staticmethod:


      Evaluate the vector distance between point ``p`` and a line defined by two points, ``a`` and ``b``.

      The formula is  ``d = (a-p)-((a-p)dot p)n``, where ``a`` is a point of the line (either ``a`` or ``b``)
      and ``n`` is the unit vector in the direction of the line.

      Parameters
      ----------
      p : list[float]
          List of ``[x, y, z]`` coordinates for the reference point.
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the segment.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the segment.

      Returns
      -------
      list[float]
          List of ``[x, y, z]`` coordinates for the distance vector.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> p = [0.0, 1.0, 0.0]
      >>> a = [0.0, 0.0, 0.0]
      >>> b = [1.0, 0.0, 0.0]
      >>> go.distance_vector(p, a, b)
      [0.0, 1.0, 0.0]




   .. py:method:: is_between_points(p: list[float], a: list[float], b: list[float], tol: float = 1e-06) -> bool
      :staticmethod:


      Check if a point lies on the segment defined by two points.

      Parameters
      ----------
      p : list[float]
          List of ``[x, y, z]`` coordinates for the reference point ``p``.
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the segment.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the segment.
      tol : float, optional
          Linear tolerance.  The default is ``1e-6``.

      Returns
      -------
      bool
          ``True`` when the point lies on the segment defined by the two points, ``False`` otherwise.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> p = [0.5, 0.5, 0.0]
      >>> a = [0.0, 0.0, 0.0]
      >>> b = [1.0, 1.0, 0.0]
      >>> go.is_between_points(p, a, b)
      True




   .. py:method:: is_parallel(a1: list[float], a2: list[float], b1: list[float], b2: list[float], tol: float = 1e-06) -> bool
      :staticmethod:


      Check if a segment defined by two points is parallel to a segment defined by two other points.

      Parameters
      ----------
      a1 : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the first segment.
      a2 : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the first segment.
      b1 : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the second segment.
      b2 : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the second segment.
      tol : float, optional
          Linear tolerance. The default is ``1e-6``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> a1 = [0.0, 0.0, 0.0]
      >>> a2 = [1.0, 0.0, 0.0]
      >>> b1 = [0.0, 1.0, 0.0]
      >>> b2 = [1.0, 1.0, 0.0]
      >>> go.is_parallel(a1, a2, b1, b2)
      True




   .. py:method:: parallel_coeff(a1: list[float], a2: list[float], b1: list[float], b2: list[float]) -> float
      :staticmethod:


      Evaluate the parallelism coefficient between two segments.

      Parameters
      ----------
      a1 : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the first segment.
      a2 : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the first segment.
      b1 : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the second segment.
      b2 : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the second segment.

      Returns
      -------
      float
          Dot product of 4 vertices of 2 segments.




   .. py:method:: is_collinear(a: list[float], b: list[float], tol: float = 1e-06) -> bool
      :staticmethod:


      Check if two vectors are collinear (parallel or anti-parallel).

      Parameters
      ----------
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first vector.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second vector.
      tol : float, optional
          Linear tolerance. The default is ``1e-6``.

      Returns
      -------
      bool
          ``True`` if vectors are collinear, ``False`` otherwise.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> a = [1.0, 0.0, 0.0]
      >>> b = [2.0, 0.0, 0.0]
      >>> go.is_collinear(a, b)
      True




   .. py:method:: is_projection_inside(a1: list[float], a2: list[float], b1: list[float], b2: list[float]) -> bool
      :staticmethod:


      Project a segment onto another segment and check if the projected segment is inside it.

      Parameters
      ----------
      a1 : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the projected segment.
      a2 : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the projected segment.
      b1 : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the other segment.
      b2 : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the other segment.

      Returns
      -------
      bool
          ``True`` when the projected segment is inside the other segment, ``False`` otherwise.




   .. py:method:: arrays_positions_sum(vertlist1: list[list[float]], vertlist2: list[list[float]]) -> float
      :staticmethod:


      Return the sum of two vertices lists.

      Parameters
      ----------
      vertlist1 : list[list[float]]
          First list of vertices.
      vertlist2 : list[list[float]]
          Second list of vertices.

      Returns
      -------
      float
          Average distance between all vertex pairs.




   .. py:method:: v_angle(a: list[float], b: list[float]) -> float
      :staticmethod:


      Evaluate the angle between two geometry vectors.

      Parameters
      ----------
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first vector.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second vector.

      Returns
      -------
      float
          Angle in radians.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> import math
      >>> a = [1.0, 0.0, 0.0]
      >>> b = [0.0, 1.0, 0.0]
      >>> angle = go.v_angle(a, b)
      >>> math.degrees(angle)
      90.0




   .. py:method:: pointing_to_axis(x_pointing: list[float], y_pointing: list[float]) -> tuple[list[float], list[float], list[float]]
      :staticmethod:


      Retrieve the axes from the HFSS X axis and Y pointing axis.

      This is as per the definition of the AEDT interface coordinate system.

      Parameters
      ----------
      x_pointing : list[float]
          List of ``[x, y, z]`` coordinates for the X axis.
      y_pointing : list[float]
          List of ``[x, y, z]`` coordinates for the Y pointing axis.

      Returns
      -------
      tuple[list[float], list[float], list[float]]
          ``[Xx, Xy, Xz], [Yx, Yy, Yz], [Zx, Zy, Zz]`` of the three axes (normalized).




   .. py:method:: axis_to_euler_zxz(x: list[float], y: list[float], z: list[float]) -> tuple[float, float, float]
      :staticmethod:


      Retrieve Euler angles of a frame following the rotation sequence ZXZ.

      Provides assumption for the gimbal lock problem.

      Parameters
      ----------
      x : list[float]
          List of ``[Xx, Xy, Xz]`` coordinates for the X axis.
      y : list[float]
          List of ``[Yx, Yy, Yz]`` coordinates for the Y axis.
      z : list[float]
          List of ``[Zx, Zy, Zz]`` coordinates for the Z axis.

      Returns
      -------
      tuple[float, float, float]
          (phi, theta, psi) containing the Euler angles in radians.




   .. py:method:: axis_to_euler_zyz(x: list[float], y: list[float], z: list[float]) -> tuple[float, float, float]
      :staticmethod:


      Retrieve Euler angles of a frame following the rotation sequence ZYZ.

      Provides assumption for the gimbal lock problem.

      Parameters
      ----------
      x : list[float]
          List of ``[Xx, Xy, Xz]`` coordinates for the X axis.
      y : list[float]
          List of ``[Yx, Yy, Yz]`` coordinates for the Y axis.
      z : list[float]
          List of ``[Zx, Zy, Zz]`` coordinates for the Z axis.

      Returns
      -------
      tuple[float, float, float]
          (phi, theta, psi) containing the Euler angles in radians.




   .. py:method:: quaternion_to_axis(q: list[float]) -> tuple[list[float], list[float], list[float]]
      :staticmethod:


      Convert a quaternion to a rotated frame defined by X, Y, and Z axes.

      Parameters
      ----------
      q : list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

      Returns
      -------
      tuple[list[float], list[float], list[float]]
          [Xx, Xy, Xz], [Yx, Yy, Yz], [Zx, Zy, Zz] of the three axes (normalized).




   .. py:method:: quaternion_to_axis_angle(q: list[float]) -> tuple[list[float], float]
      :staticmethod:


      Convert a quaternion to the axis angle rotation formulation.

      Parameters
      ----------
      q : list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

      Returns
      -------
      tuple[list[float], float]
          ([ux, uy, uz], theta) containing the rotation axes expressed as X, Y, Z components of
          the unit vector ``u`` and the rotation angle theta expressed in radians.




   .. py:method:: axis_angle_to_quaternion(u: list[float], theta: float) -> list[float]
      :staticmethod:


      Convert the axis angle rotation formulation to a quaternion.

      Parameters
      ----------
      u : list[float]
          List of ``[ux, uy, uz]`` coordinates for the rotation axis.
      theta : float
          Angle of rotation in radians.

      Returns
      -------
      list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.




   .. py:method:: quaternion_to_euler_zxz(q: list[float]) -> tuple[float, float, float]
      :staticmethod:


      Convert a quaternion to Euler angles following rotation sequence ZXZ.

      Parameters
      ----------
      q : list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

      Returns
      -------
      tuple[float, float, float]
          (phi, theta, psi) containing the Euler angles in radians.




   .. py:method:: euler_zxz_to_quaternion(phi: float, theta: float, psi: float) -> list[float]
      :staticmethod:


      Convert the Euler angles following rotation sequence ZXZ to a quaternion.

      Parameters
      ----------
      phi : float
          Euler angle phi in radians.
      theta : float
          Euler angle theta in radians.
      psi : float
          Euler angle psi in radians.

      Returns
      -------
      list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.




   .. py:method:: quaternion_to_euler_zyz(q: list[float]) -> tuple[float, float, float]
      :staticmethod:


      Convert a quaternion to Euler angles following rotation sequence ZYZ.

      Parameters
      ----------
      q : list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

      Returns
      -------
      tuple[float, float, float]
          (phi, theta, psi) containing the Euler angles in radians.




   .. py:method:: euler_zyz_to_quaternion(phi: float, theta: float, psi: float) -> list[float]
      :staticmethod:


      Convert the Euler angles following rotation sequence ZYZ to a quaternion.

      Parameters
      ----------
      phi : float
          Euler angle phi in radians.
      theta : float
          Euler angle theta in radians.
      psi : float
          Euler angle psi in radians.

      Returns
      -------
      list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.




   .. py:method:: deg2rad(angle: float) -> float
      :staticmethod:


      Convert the angle from degrees to radians.

      Parameters
      ----------
      angle : float
          Angle in degrees.

      Returns
      -------
      float
          Angle in radians.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> go.deg2rad(180.0)
      3.141592653589793




   .. py:method:: rad2deg(angle: float) -> float
      :staticmethod:


      Convert the angle from radians to degrees.

      Parameters
      ----------
      angle : float
          Angle in radians.

      Returns
      -------
      float
          Angle in degrees.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> import math
      >>> go.rad2deg(math.pi)
      180.0




   .. py:method:: atan2(y: float, x: float) -> float
      :staticmethod:


      Implementation of atan2 that does not suffer from sign issues.

      This implementation always returns 0.0 for very small values.

      Parameters
      ----------
      y : float
          Y-axis value for atan2.
      x : float
          X-axis value for atan2.

      Returns
      -------
      float
          Arctangent of y/x in radians.




   .. py:method:: q_prod(p: list[float], q: list[float]) -> list[float]
      :staticmethod:


      Evaluate the product of two quaternions.

      The product is defined as:
      p = p0 + p' = p0 + ip1 + jp2 + kp3.
      q = q0 + q' = q0 + iq1 + jq2 + kq3.
      r = pq = p0q0 - p' • q' + p0q' + q0p' + p' x q'.

      Parameters
      ----------
      p : list[float]
          List of ``[p1, p2, p3, p4]`` coordinates for quaternion ``p``.
      q : list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for quaternion ``q``.

      Returns
      -------
      list[float]
          List of [r1, r2, r3, r4] coordinates for the result quaternion.




   .. py:method:: q_rotation(v: list[float], q: list[float]) -> list[float]
      :staticmethod:


      Evaluate the rotation of a vector, defined by a quaternion.

      Evaluated as:
      ``q = q0 + q' = q0 + iq1 + jq2 + kq3``,
      ``w = qvq* = (q0^2 - |q'|^2)v + 2(q' • v)q' + 2q0(q' x v)``.

      Parameters
      ----------
      v : list[float]
          List of ``[v1, v2, v3]`` coordinates for the vector.
      q : list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

      Returns
      -------
      list[float]
          List of ``[w1, w2, w3]`` coordinates for the result vector ``w``.




   .. py:method:: q_rotation_inv(v: list[float], q: list[float]) -> list[float]
      :staticmethod:


      Evaluate the inverse rotation of a vector that is defined by a quaternion.

      It can also be the rotation of the coordinate frame with respect to the vector.

      q = q0 + q' = q0 + iq1 + jq2 + kq3
      q* = q0 - q' = q0 - iq1 - jq2 - kq3
      w = q*vq

      Parameters
      ----------
      v : list[float]
          List of ``[v1, v2, v3]`` coordinates for the vector.
      q : list[float]
          List of ``[q1, q2, q3, q4]`` coordinates for the quaternion.

      Returns
      -------
      list[float]
          List of ``[w1, w2, w3]`` coordinates for the vector.




   .. py:method:: get_polygon_centroid(pts: list[list[float]]) -> list[float]
      :staticmethod:


      Evaluate the centroid of a polygon defined by its points.

      Parameters
      ----------
      pts : list[list[float]]
          List of points, with each point defined by its ``[x,y,z]`` coordinates.

      Returns
      -------
      list[float]
          List of [x,y,z] coordinates for the centroid of the polygon.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> pts = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
      >>> go.get_polygon_centroid(pts)
      [0.5, 0.5, 0.0]




   .. py:method:: cs_xy_pointing_expression(yaw: str, pitch: str, roll: str) -> list[list[str]]
      :staticmethod:


      Return x_pointing and y_pointing vectors as expressions.

      Parameters
      ----------
      yaw : str
          String expression for the yaw angle (rotation about Z-axis).
      pitch : str
          String expression for the pitch angle (rotation about Y-axis).
      roll : str
          String expression for the roll angle (rotation about X-axis).

      Returns
      -------
      list[list[str]]
          [x_pointing, y_pointing] vector expressions.




   .. py:method:: get_numeric(s: str | float | None) -> float
      :staticmethod:


      Convert a string to a numeric value. Discard the suffix.

      Parameters
      ----------
      s : str, float, or None
          String or numeric value to convert.

      Returns
      -------
      float
          Numeric value.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> go.get_numeric("123.45mm")
      123.45




   .. py:method:: is_small(s: str | float) -> bool
      :staticmethod:


      Return ``True`` if the number represented by s is zero (i.e very small).

      Parameters
      ----------
      s : str, or float
          Variable value.

      Returns
      -------
      bool
          ``True`` if the value is very small, ``False`` otherwise.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> go.is_small(0.0)
      True
      >>> go.is_small(1e-20)
      True
      >>> go.is_small(1.0)
      False




   .. py:method:: numeric_cs(cs_in: list[str] | str) -> list[float] | None
      :staticmethod:


      Return a list of [x,y,z] numeric values given a coordinate system as input.

      Parameters
      ----------
      cs_in : list[str], or str
          ``["x", "y", "z"]`` or "Global".

      Returns
      -------
      list[float], or None
          Numeric coordinate values or None.




   .. py:method:: orient_polygon(x: list[float], y: list[float], clockwise: bool = True) -> tuple[list[float], list[float]]
      :staticmethod:


      Orient a polygon clockwise or counterclockwise.

      The vertices should be already ordered either way.
      Use this function to change the orientation.
      The polygon is represented by its vertices coordinates.

      Parameters
      ----------
      x : list[float]
          List of x coordinates of the vertices. Length must be >= 1.
          Degenerate polygon with only 2 points is also accepted, in this case the points are returned unchanged.
      y : list[float]
          List of y coordinates of the vertices. Must be of the same length as x.
      clockwise : bool, optional
          If ``True`` the polygon is oriented clockwise, if ``False`` it is oriented counterclockwise.
          The default is ``True``.

      Returns
      -------
      tuple[list[float], list[float]]
          Lists of oriented vertices.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> x = [0.0, 1.0, 1.0, 0.0]
      >>> y = [0.0, 0.0, 1.0, 1.0]
      >>> x_new, y_new = go.orient_polygon(x, y, clockwise=True)




   .. py:method:: v_angle_sign(va: list[float], vb: list[float], vn: list[float], right_handed: bool = True) -> float
      :staticmethod:


      Evaluate the signed angle between two geometry vectors.

      The sign is evaluated respect to the normal to the plane containing the two vectors as per the following rule.
      In case of opposite vectors, it returns an angle equal to 180deg (always positive).
      Assuming that the plane normal is normalized (vb == 1), the signed angle is simplified.
      For the right-handed rotation from Va to Vb:
      - atan2((va x Vb) . vn, va . vb).
      For the left-handed rotation from Va to Vb:
      - atan2((Vb x va) . vn, va . vb).

      Parameters
      ----------
      va : list[float]
          List of ``[x, y, z]`` coordinates for the first vector.
      vb : list[float]
          List of ``[x, y, z]`` coordinates for the second vector.
      vn : list[float]
          List of ``[x, y, z]`` coordinates for the plane normal.
      right_handed : bool, optional
          Whether to consider the right-handed rotation from va to vb.
          When ``False``, left-hand rotation from va to vb is considered.
          The default is ``True``.

      Returns
      -------
      float
          Angle in radians.




   .. py:method:: v_angle_sign_2D(va: list[float], vb: list[float], right_handed: bool = True) -> float
      :staticmethod:


      Evaluate the signed angle between two 2D geometry vectors.

      It is the 2D version of the ``GeometryOperators.v_angle_sign`` considering vn = [0,0,1].
      In case of opposite vectors, it returns an angle equal to 180deg (always positive).

      Parameters
      ----------
      va : list[float]
          List of ``[x, y]`` coordinates for the first vector.
      vb : list[float]
          List of ``[x, y]`` coordinates for the second vector.
      right_handed : bool, optional
          Whether to consider the right-handed rotation from Va to Vb.
          When ``False``, left-hand rotation from Va to Vb is considered.
          The default is ``True``.

      Returns
      -------
      float
          Angle in radians.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> import math
      >>> va = [1.0, 0.0]
      >>> vb = [0.0, 1.0]
      >>> angle = go.v_angle_sign_2D(va, vb)
      >>> math.degrees(angle)
      90.0




   .. py:method:: point_in_polygon(point: list[float], polygon: list[list[float]], tolerance: float = 1e-08) -> int
      :staticmethod:


      Determine if a point is inside, outside the polygon or at exactly at the border.

      The method implements the radial algorithm (https://es.wikipedia.org/wiki/Algoritmo_radial)

      Parameters
      ----------
      point : list[float]
          List of ``[x, y]`` coordinates.
      polygon : list[list[float]]
          [[x1, x2, ..., xn],[y1, y2, ..., yn]]
      tolerance : float, optional
          Tolerance used for the algorithm. The default is ``1e-8``.

      Returns
      -------
      int
          - ``-1`` When the point is outside the polygon.
          - ``0`` When the point is exactly on one of the sides of the polygon.
          - ``1`` When the point is inside the polygon.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> point = [0.5, 0.5]
      >>> polygon = [[0.0, 1.0, 1.0, 0.0], [0.0, 0.0, 1.0, 1.0]]
      >>> go.point_in_polygon(point, polygon)
      1




   .. py:method:: is_point_in_polygon(point: list[float], polygon: list[list[float]]) -> bool
      :staticmethod:


      Determine if a point is inside or outside a polygon, both located on the same plane.

      The method implements the radial algorithm (https://es.wikipedia.org/wiki/Algoritmo_radial)

      Parameters
      ----------
      point : list[float]
          List of ``[x, y]`` coordinates.
      polygon : list[list[float]]
          [[x1, x2, ..., xn],[y1, y2, ..., yn]]

      Returns
      -------
      bool
          ``True`` if the point is inside the polygon or exactly on one of its sides.
          ``False`` otherwise.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> point = [0.5, 0.5]
      >>> polygon = [[0.0, 1.0, 1.0, 0.0], [0.0, 0.0, 1.0, 1.0]]
      >>> go.is_point_in_polygon(point, polygon)
      True




   .. py:method:: are_segments_intersecting(a1: list[float], a2: list[float], b1: list[float], b2: list[float], include_collinear: bool = True) -> bool
      :staticmethod:


      Determine if the two segments a and b are intersecting.

      Parameters
      ----------
      a1 : list[float]
          First point of segment a. List of ``[x, y]`` coordinates.
      a2 : list[float]
          Second point of segment a. List of ``[x, y]`` coordinates.
      b1 : list[float]
          First point of segment b. List of ``[x, y]`` coordinates.
      b2 : list[float]
          Second point of segment b. List of ``[x, y]`` coordinates.
      include_collinear : bool, optional
          If ``True`` two segments are considered intersecting also if just one end lies on the other segment.
          The default is ``True``.

      Returns
      -------
      bool
          ``True`` if the segments are intersecting.
          ``False`` otherwise.




   .. py:method:: is_segment_intersecting_polygon(a: list[float], b: list[float], polygon: list[list[float]]) -> bool
      :staticmethod:


      Determine if a segment defined by two points ``a`` and ``b`` intersects a polygon.

      Points on the vertices and on the polygon boundaries are not considered intersecting.

      Parameters
      ----------
      a : list[float]
          First point of the segment. List of ``[x, y]`` coordinates.
      b : list[float]
          Second point of the segment. List of ``[x, y]`` coordinates.
      polygon : list[list[float]]
          [[x1, x2, ..., xn],[y1, y2, ..., yn]]

      Returns
      -------
      bool
          ``True`` if the segment intersect the polygon. ``False`` otherwise.




   .. py:method:: is_perpendicular(a: list[float], b: list[float], tol: float = 1e-06) -> bool
      :staticmethod:


      Check if two vectors are perpendicular.

      Parameters
      ----------
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first vector.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second vector.
      tol : float, optional
          Linear tolerance. The default is ``1e-6``.

      Returns
      -------
      bool
          ``True`` if vectors are perpendicular, ``False`` otherwise.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> a = [1.0, 0.0, 0.0]
      >>> b = [0.0, 1.0, 0.0]
      >>> go.is_perpendicular(a, b)
      True




   .. py:method:: is_point_projection_in_segment(p: list[float], a: list[float], b: list[float]) -> bool
      :staticmethod:


      Check if a point projection lies on the segment defined by two points.

      Parameters
      ----------
      p : list[float]
          List of ``[x, y, z]`` coordinates for the reference point ``p``.
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the segment.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the segment.

      Returns
      -------
      bool
          ``True`` when the projection point lies on the segment defined by the two points, ``False`` otherwise.




   .. py:method:: point_segment_distance(p: list[float], a: list[float], b: list[float]) -> float
      :staticmethod:


      Calculate the distance between a point ``p`` and a segment defined by two points ``a`` and ``b``.

      Parameters
      ----------
      p : list[float]
          List of ``[x, y, z]`` coordinates for the reference point ``p``.
      a : list[float]
          List of ``[x, y, z]`` coordinates for the first point of the segment.
      b : list[float]
          List of ``[x, y, z]`` coordinates for the second point of the segment.

      Returns
      -------
      float
          Distance between the point and the segment.




   .. py:method:: find_largest_rectangle_inside_polygon(polygon: list[list[float]], partition_max_order: int = 16) -> list[list[list[float]]]
      :staticmethod:


      Find the largest area rectangles of arbitrary orientation in a polygon.

      Implements the algorithm described by Rubén Molano, et al.
      *"Finding the largest area rectangle of arbitrary orientation in a closed contour"*, published in
      *Applied Mathematics and Computation*.
      https://doi.org/10.1016/j.amc.2012.03.063.
      (https://www.sciencedirect.com/science/article/pii/S0096300312003207)

      Parameters
      ----------
      polygon : list[list[float]]
          [[x1, x2, ..., xn],[y1, y2, ..., yn]]
      partition_max_order : int, optional
          Order of the lattice partition used to find the quasi-lattice polygon that approximates ``polygon``.
          The default is ``16``.

      Returns
      -------
      list[list[list[float]]]
          List containing the rectangles points. Return all rectangles found.
          List is in the form: [[[x1, y1],[x2, y2],...],[[x1, y1],[x2, y2],...],...].




   .. py:method:: degrees_over_rounded(angle: float, digits: int) -> float
      :staticmethod:


      Ceil of angle.

      Parameters
      ----------
      angle : float
          Angle in radians which will be converted to degrees and will be over-rounded to the next "digits" decimal.
      digits : int
          Integer number which is the number of decimals.

      Returns
      -------
      float
          Angle in degrees rounded up.




   .. py:method:: radians_over_rounded(angle: float, digits: int) -> float
      :staticmethod:


      Radian angle ceiling.

      Parameters
      ----------
      angle : float
          Angle in degrees which will be converted to radians and will be over-rounded to the  next "digits" decimal.
      digits : int
          Integer number which is the number of decimals.

      Returns
      -------
      float
          Angle in radians rounded up.




   .. py:method:: degrees_default_rounded(angle: float, digits: int) -> float
      :staticmethod:


      Convert angle to degree with given digits rounding.

      Parameters
      ----------
      angle : float
          Angle in radians which will be converted to degrees and will be under-rounded to the next "digits" decimal.
      digits : int
          Integer number which is the number of decimals.

      Returns
      -------
      float
          Angle in degrees rounded down.




   .. py:method:: radians_default_rounded(angle: float, digits: int) -> float
      :staticmethod:


      Convert to radians with given round.

      Parameters
      ----------
      angle : float
          Angle in degrees which will be converted to radians and will be under-rounded to the next "digits" decimal.
      digits : int
          Integer number which is the number of decimals.

      Returns
      -------
      float
          Angle in radians rounded down.




   .. py:method:: find_closest_points(points_list: list[list[float]], reference_point: list[float], tol: float = 1e-06) -> list[list[float]] | bool
      :staticmethod:


      Given a list of points, finds the closest points to a reference point.

      It returns a list of points because more than one can be found.
      It works with 2D or 3D points. The tolerance used to evaluate the distance
      to the reference point can be specified.

      Parameters
      ----------
      points_list : list[list[float]]
          List of points. The points can be defined in 2D or 3D space.
      reference_point : list[float]
          The reference point. The point can be defined in 2D or 3D space (same as points_list).
      tol : float, optional
          The tolerance used to evaluate the distance. The default is ``1e-6``.

      Returns
      -------
      list[list[float]], or bool
          List of closest points or False if none found.




   .. py:method:: mirror_point(start: list[float], reference: list[float], vector: list[float]) -> list[float]
      :staticmethod:


      Mirror point about a plane defining by a point on the plane and a normal point.

      Parameters
      ----------
      start : list[float]
          Point to be mirrored.
      reference : list[float]
          The reference point. Point on the plane around which you want to mirror the object.
      vector : list[float]
          Normalized vector used for the mirroring.

      Returns
      -------
      list[float]
          List of the reflected point.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> start = [1.0, 0.0, 0.0]
      >>> reference = [0.0, 0.0, 0.0]
      >>> vector = [1.0, 0.0, 0.0]
      >>> go.mirror_point(start, reference, vector)
      [-1.0, 0.0, 0.0]




   .. py:method:: find_points_along_lines(points: list[list[float]] | numpy.ndarray, minimum_number_of_points: int = 3, distance_threshold: float | None = None, selected_angles: list[float] | None = None, return_additional_info: bool = False) -> tuple
      :staticmethod:


      Detect all points that are placed along lines.

      The method takes as input a list of 2D points and detects all lines that contain at least 3 points.
      Optionally, the minimum number of points contained in a line can be specified by setting the
      argument ``minimum_number_of_points``.
      As default, all points along the lines are returned, regardless of their relative distance.
      Optionally, a `distance_threshold` can be set. If two points in a line are separated by a distance larger than
      ``distance_threshold``, the line is divided in two parts. If one of those parts does not satisfy the
      ``minimum_number_of_points`` requirement, it is discarded.
      If `distance_threshold` is set (not ``None``), the computational time increases.

      Parameters
      ----------
      points : list[list[float]] or np.ndarray
          The points to process. Can be a list of lists where each sublist
          represents a 2D point ``[x, y]`` coordinates, or a numpy array of shape (n, 2).
      minimum_number_of_points : int, optional
          The minimum number of points that a line must contain.
          The default is ``3``.
      distance_threshold : float or None, optional
          If two points in a line are separated by a distance larger than `distance_threshold`,
          the line is divided in two parts.
          The default is ``None``.
      selected_angles : list[float] or None, optional
          Specify a list of angles in degrees. If specified, the method returns only the lines which
          have one of the specified angles.
          The angle is defined as the positive angle of the infinite line with respect to the x-axis
          It is positive, and between 0 and 180 degrees.
          For example, ``[90]`` indicated vertical lines parallel to the y-axis,
          ``[0]`` or ``[180]`` identifies horizontal lines parallel to the x-axis,
          ``45`` identifies lines parallel to the first quadrant bisector.
          The default is ``None``.
      return_additional_info : bool, optional
          Whether to return additional information about the number of elements processed.
          The default is ``False``.

      Returns
      -------
      tuple
          The tuple contains:
          - lines: a list of lists where each sublist represents a 2D point ``[x, y]`` coordinates in each line.
          - lines indexes: a list of lists where each sublist represents the index of the point in each line.
                          The index is referring to the point position in the input point list.
          - number of processed points: optional, returned if ``return_additional_info`` is ``True``
          - number of processed lines: optional, returned if ``return_additional_info`` is ``True``
          - number of detected lines after ``minimum_number_of_points`` is applied: optional,
              returned if ``return_additional_info`` is ``True``
          - number of detected lines after ``distance_threshold`` is applied: optional,
              returned if ``return_additional_info`` is ``True``




   .. py:method:: smallest_distance_between_polygons(polygon1: list[tuple[float, float]], polygon2: list[tuple[float, float]]) -> float
      :staticmethod:


      Find the smallest distance between two polygons using KDTree for efficient nearest neighbor search.

      Parameters
      ----------
      polygon1 : list[tuple[float, float]]
          List of (x, y) coordinates representing the points of the first polygon.
      polygon2 : list[tuple[float, float]]
          List of (x, y) coordinates representing the points of the second polygon.

      Returns
      -------
      float
          The smallest distance between any two points from the two polygons.

      Examples
      --------
      >>> from pyedb.generic.geometry_operators import GeometryOperators as go
      >>> polygon1 = [(1, 1), (4, 1), (4, 4), (1, 4)]
      >>> polygon2 = [(5, 5), (8, 5), (8, 8), (5, 8)]
      >>> go.smallest_distance_between_polygons(polygon1, polygon2)
      1.4142135623730951




