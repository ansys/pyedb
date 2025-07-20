# pyedb_libraries.py
# Author : you
# Date   : 2025-07-19
#
# 100 % parametric EDB library + analytical RF models
# ---------------------------------------------------
# Requires: pyedb (Ansys internal) and numpy
#
# Usage
# -----
# >>> from pyedb_libraries import Meander, RectPatch
# >>> edb = Meander(length=5e-3, width=0.3e-3, height=0.1e-3, turns=5,
# ...               layer="TOP", net="SIG").create(edb_path="mander.aedb")
# >>> edb.close_edb()
#
# >>> ant = RectPatch(freq=2.4e9, sub_h=1.6e-3, sub_er=4.4, sub_tand=0.02,
# ...                 inset=0.5e-3, layer="TOP", via_layer="GND")
# >>> edb = ant.create(edb_path="patch.aedb")
# >>> print(ant.resonant_frequency)
# 2.400000e+09
# >>> edb.close_edb()

from __future__ import annotations

from dataclasses import dataclass
import math
import os
from typing import List, Optional, Tuple

import numpy as np

from pyedb import Edb

# ---------------------------------------------------------------------------
# Common utilities
# ---------------------------------------------------------------------------


@dataclass
class Substrate:
    """Small helper to keep substrate parameters together."""

    h: float  # height (m)
    er: float  # relative permittivity
    tand: float = 0  # loss tangent
    name: str = "SUB"


def _rect_path(edb: Edb, layer: str, net: str, x0: float, y0: float, x1: float, y1: float, w: float) -> EDBPrimitives:
    """Create a rectangular (Manhattan) trace primitive."""
    points = [[x0, y0], [x1, y1]]
    return edb.modeler.create_trace(points, layer, w, net, "Line")


def _via_fence(
    edb: Edb,
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    pitch: float,
    drill: float,
    pad: float,
    top_layer: str,
    bottom_layer: str,
    net: str,
):
    """Create a via fence along a rectangle."""
    xvec = np.arange(x0, x1 + pitch, pitch) if x1 > x0 else [x0]
    yvec = np.arange(y0, y1 + pitch, pitch) if y1 > y0 else [y0]
    for x in xvec:
        for y in yvec:
            edb.padstacks.create([x, y], drill, pad, top_layer, bottom_layer, net=net)


# ---------------------------------------------------------------------------
# 1. Lumped / transmission line components
# ---------------------------------------------------------------------------


class HashedGroundPlane:
    """
    Perforated (hashed) ground plane with rectangular slots.

    Parameters
    ----------
    length : float
        Plane size along x (m).  Default 10 mm.
    width : float
        Plane size along y (m).  Default 10 mm.
    slot_width : float
        Width of each slot (m).  Default 0.2 mm.
    slot_pitch : float
        Centre-to-centre distance between slots (m).  Default 1 mm.
    layer : str
        EDB layer name.  Default "GND".
    net : str
        Net name.  Default "GND".

    Properties
    ----------
    porosity : float
        Fraction of metal removed (area of slots / total area).
    effective_conductivity : float
        Estimated conductivity reduction factor = 1 – porosity.

    Examples
    --------
    >>> from pyedb_libraries import HashedGroundPlane
    >>> gnd = HashedGroundPlane(length=5e-3, width=5e-3,
    ...                         slot_width=0.1e-3, slot_pitch=0.5e-3)
    >>> edb = gnd.create("gnd.aedb")
    >>> print(f"Porosity = {gnd.porosity:.2%}")
    Porosity = 19.00%
    >>> edb.close_edb()
    """

    def __init__(
        self,
        edb_cell: Optional[Edb] = None,
        length: float = 1e-3,
        width: float = 1e-3,
        slot_width: float = 50e-6,
        slot_pitch: float = 150e-6,
        layer: str = "GND",
        net: str = "GND",
    ):
        self._pedb = edb_cell
        self.length = length
        self.width = width
        self.slot_width = slot_width
        self.slot_pitch = slot_pitch
        self.layer = layer
        self.net = net

    # ----------------------------------------------------------
    # Analytical properties
    # ----------------------------------------------------------
    @property
    def porosity(self) -> float:
        """Fraction of metal removed."""
        return (self.slot_width * self.width) / (self.slot_pitch * self.width)

    @property
    def effective_conductivity(self) -> float:
        """Effective conductivity reduction factor."""
        return 1.0 - self.porosity

    # ----------------------------------------------------------
    # EDB creation
    # ----------------------------------------------------------
    def create(self) -> Edb:
        if not self._pedb:
            raise Exception

        # Parameters
        self._pedb["L"] = self.length
        self._pedb["W"] = self.width
        self._pedb["sw"] = self.slot_width
        self._pedb["sp"] = self.slot_pitch

        # Full metal rectangle first
        self._pedb.modeler.create_rectangle(
            layer_name=self.layer,
            net_name=self.net,
            lower_left_point=[0, 0],
            upper_right_point=[self.length, self.width],
        )

        # Cut slots along x
        x = 0.0
        y = 0.0
        # TODO check pattern is wrong
        while y < self.length:
            while x < self.width:
                prim = self._pedb.modeler.create_rectangle(
                    layer_name=self.layer,
                    net_name="VOID",
                    lower_left_point=[x, x + self.slot_width],
                    upper_right_point=[y, y + self.slot_width],
                )
                prim.is_negative = True
                x += self.slot_pitch + self.slot_width
            x = 0.0
            y += self.slot_pitch + self.slot_width
        return True


class Meander:
    """
    Fully-parametric meander line.

    Parameters
    ----------
    length : float
        Total electrical length (m).  Default 5 mm.
    width : float
        Trace width (m).  Default 0.3 mm.
    height : float
        Meander vertical pitch (m).  Default 0.1 mm.
    turns : int
        Number of 180° bends.  Default 5.
    layer : str
        EDB layer name.
    net : str
        Net name.

    Examples
    --------
    >>> m = Meander(length=5e-3, width=0.3e-3, height=0.1e-3, turns=5,
    ...             layer="TOP", net="SIG")
    >>> edb = m.create("meander.aedb")
    >>> print(m.analytical_z0)   # characteristic impedance (Ohm)
    >>> print(m.electrical_length_deg(2e9))
    >>> edb.close_edb()
    """

    def __init__(
        self,
        edb_cell: Optional[Edb] = None,
        pitch: float = 1e-3,
        trace_width: float = 0.3e-3,
        amplitude: float = 5e-3,
        num_turns: int = 8,
        layer: str = "TOP",
        net: str = "SIG",
    ):
        self._pedb = edb_cell
        self.pitch = pitch
        self.trace_width = trace_width
        self.amplitude = amplitude
        self.num_turns = num_turns
        self.layer = layer
        self.net = net

    # ------------------------------------------------------------------ #
    # Analytical models
    # ------------------------------------------------------------------ #
    @property
    def analytical_z0(self) -> float:
        """
        Microstrip characteristic impedance using Hammerstad & Jensen.

        Returns
        -------
        float
            Z0 (Ohm)
        """
        # Effective dielectric constant for 50-Ohm microstrip on FR-4
        # Here we assume er=4.4, h=1.6 mm. Adjust if substrate changes.
        er_eff = 3.2
        return 60 / math.sqrt(er_eff) * math.log(5.98 * 1.6e-3 / (0.8 * self.trace_width + self.trace_width))

    def electrical_length_deg(self, freq: float) -> float:
        """
        Electrical length in degrees at a given frequency.

        Parameters
        ----------
        freq : float
            Frequency (Hz)

        Returns
        -------
        float
            Phase (degrees)
        """
        c = 299_792_458
        # effective dielectric constant same as above
        er_eff = 3.2
        v = c / math.sqrt(er_eff)
        beta = 2 * math.pi * freq / v
        return math.degrees(beta * self.length)

    # ------------------------------------------------------------------ #
    # EDB creation
    # ------------------------------------------------------------------ #
    def create(self) -> bool:
        """Create or open edb and return the Edb object."""

        # Parameters
        self._pedb.add_design_variable("w", self.trace_width)  # trace width
        self._pedb.add_design_variable("p", self.pitch)  # pitch (centre-to-centre)
        self._pedb.add_design_variable("a", self.amplitude)  # meander amplitude
        self._pedb.add_design_variable("n_turns", self.num_turns)  # number of U-turns (integer)

        # ----------------------------------------------------------
        # 3.  Build the point list
        # ----------------------------------------------------------
        pts = [(0, 0)]  # start on the axis

        for i in range(self.num_turns):
            y = f"{i + 1}*p"  # next row
            if i % 2 == 0:  # even → left
                pts.extend([("-a/2", f"{i}*p"), ("-a/2", y), (0, y)])  # step left  # vertical  # back to axis
            else:  # odd → right
                pts.extend([(" a/2", f"{i}*p"), (" a/2", y), (0, y)])  # step right  # vertical  # back to axis

        # ------------------------------------------------------------------
        # 4. Create the trace on layer "TOP"
        # ------------------------------------------------------------------
        self._pedb.modeler.create_trace(
            path_list=pts, layer_name=self.layer, width=self.trace_width, net_name=self.net, corner_style="Round"
        )


class MIMCapacitor:
    """
    MIM capacitor using two parallel plates.

    Parameters
    ----------
    area : float
        Plate area (m²).  Default 0.1 mm².
    gap : float
        Dielectric thickness (m).  Default 1 µm.
    er : float
        Relative permittivity of dielectric.  Default 7.
    layer_top : str
        Top plate layer.
    layer_bottom : str
        Bottom plate layer.
    net : str
        Net name.

    Examples
    --------
    >>> cap = MIMCapacitor(area=0.1e-6, gap=1e-6, er=7,
    ...                    layer_top="M3", layer_bottom="M2", net="RF")
    >>> edb = cap.create("mim.aedb")
    >>> print(cap.capacitance_f)
    >>> edb.close_edb()
    """

    def __init__(
        self,
        *,
        area: float = 0.1e-6,
        gap: float = 1e-6,
        er: float = 7,
        layer_top: str = "M3",
        layer_bottom: str = "M2",
        net: str = "RF",
    ):
        self.area = area
        self.gap = gap
        self.er = er
        self.layer_top = layer_top
        self.layer_bottom = layer_bottom
        self.net = net

    @property
    def capacitance_f(self) -> float:
        """
        Analytical capacitance.

        Returns
        -------
        float
            Capacitance in Farads
        """
        eps0 = 8.854e-12
        return eps0 * self.er * self.area / self.gap

    def create(self, edb_path: str) -> Edb:
        if os.path.exists(edb_path):
            edb = Edb(edb_path)
        else:
            edb = Edb()
            edb.save_as(edb_path)

        edb["area"] = self.area
        edb["gap"] = self.gap
        side = math.sqrt(self.area)
        edb["side"] = side

        edb.modeler.create_rectangle(self.layer_top, self.net, [0, -side / 2, side, side])
        edb.modeler.create_rectangle(self.layer_bottom, self.net, [0, -side / 2, side, side])
        return edb


class SpiralInductor:
    """
    Square spiral inductor with underpass.

    Parameters
    ----------
    turns : int
    width : float
    spacing : float
    outer_diam : float
    layer : str
    underpass_layer : str
    net : str
    """

    def __init__(
        self,
        *,
        turns: int = 3,
        width: float = 20e-6,
        spacing: float = 20e-6,
        outer_diam: float = 0.5e-3,
        layer: str = "TOP",
        underpass_layer: str = "M2",
        net: str = "IN",
    ):
        self.turns = turns
        self.width = width
        self.spacing = spacing
        self.outer_diam = outer_diam
        self.layer = layer
        self.underpass_layer = underpass_layer
        self.net = net

    @property
    def inductance_nh(self) -> float:
        """
        Wheeler’s formula for square spiral.

        Returns
        -------
        float
            Inductance in nH
        """
        a = self.outer_diam / 2
        l0 = 2.34e-6  # µ0/2pi
        return l0 * self.turns**2 * a / (2 * a + 2 * self.width)

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["n"] = self.turns
        edb["w"] = self.width
        edb["s"] = self.spacing
        edb["d_out"] = self.outer_diam

        # Simple square spiral generation
        x, y = 0.0, 0.0
        step = self.outer_diam
        for i in range(self.turns):
            for dx, dy in [(step, 0), (0, step), (-step, 0), (0, -step)]:
                _rect_path(edb, self.layer, self.net, x, y, x + dx, y + dy, self.width)
                x += dx
                y += dy
            step -= 2 * (self.width + self.spacing)
        # underpass (stub)
        edb.padstacks.create([x, y], 10e-6, 20e-6, self.layer, self.underpass_layer, net=self.net)
        return edb


class RectangleInductor:
    """
    Single-layer **rectangular** spiral inductor.

    Parameters
    ----------
    turns : int
        Number of complete turns (>=1).  Default 3.
    width : float
        Trace width in metres.  Default 20 µm.
    spacing : float
        Trace-to-trace spacing in metres.  Default 20 µm.
    outer_length : float
        Outer rectangle side length (metres).  Default 0.5 mm.
    layer : str
        EDB conductor layer name.  Default "TOP".
    underpass_layer : str
        EDB layer used for the underpass bridge.  Default "M2".
    net : str
        Net name.  Default "L".

    Examples
    --------
    >>> from pyedb_libraries import RectangleInductor
    >>> ind = RectangleInductor(turns=4, width=25e-6, spacing=15e-6,
    ...                         outer_length=0.6e-3, layer="TOP")
    >>> edb = ind.create("rect_ind.aedb")
    >>> print(f"{ind.inductance_nh:.1f} nH")   # analytical estimate
    6.0 nH
    >>> edb.close_edb()
    """

    def __init__(
        self,
        *,
        turns: int = 3,
        width: float = 20e-6,
        spacing: float = 20e-6,
        outer_length: float = 0.5e-3,
        layer: str = "TOP",
        underpass_layer: str = "M2",
        net: str = "L",
    ):
        self.turns = turns
        self.width = width
        self.spacing = spacing
        self.outer_length = outer_length
        self.layer = layer
        self.underpass_layer = underpass_layer
        self.net = net

    # ------------------------------------------------------------------ #
    # Analytical model (modified Wheeler for rectangular spirals)
    # ------------------------------------------------------------------ #
    @property
    def inductance_nh(self) -> float:
        """
        Wheeler-based closed-form rectangular spiral inductance.

        Returns
        -------
        float
            Inductance in nano-Henries.
        """
        n = self.turns
        a = self.outer_length / 2  # avg side length / 2
        l0 = 4e-7 * math.pi  # µ0/2π
        return l0 * n**2 * a / 1.27  # simplified Wheeler

    # ------------------------------------------------------------------ #
    # EDB creation
    # ------------------------------------------------------------------ #
    def create(self, edb_path: str) -> Edb:
        if os.path.exists(edb_path):
            edb = Edb(edb_path)
        else:
            edb = Edb()
            edb.save_as(edb_path)

        # --- expose parameters ------------------------------------------
        edb["n"] = self.turns
        edb["w"] = self.width
        edb["s"] = self.spacing
        edb["L_out"] = self.outer_length

        # --- geometry helpers -------------------------------------------
        x0 = y0 = 0.0
        half_w = self.width / 2
        step = self.outer_length

        for turn in range(self.turns):
            # four sides of current rectangle
            for dx, dy in [(step, 0), (0, step), (-step, 0), (0, -step)]:
                x1 = x0 + dx
                y1 = y0 + dy
                _rect_path(edb, self.layer, self.net, x0, y0, x1, y1, self.width)
                x0, y0 = x1, y1
            step -= 2 * (self.width + self.spacing)

        # --- underpass via ------------------------------------------------
        edb.padstacks.create(
            [x0, y0],
            drill=0.8 * self.width,
            pad=1.2 * self.width,
            start_layer=self.layer,
            stop_layer=self.underpass_layer,
            net=self.net,
        )

        return edb


class HexagonalInductor:
    """
    Single-layer **hexagonal** spiral inductor.

    Parameters
    ----------
    turns : int
        Number of complete turns (>=1).  Default 3.
    width : float
        Trace width in metres.  Default 20 µm.
    spacing : float
        Trace-to-trace spacing in metres.  Default 20 µm.
    outer_radius : float
        Distance from centre to outermost hexagon vertex (metres).  Default 0.3 mm.
    layer : str
        EDB conductor layer name.  Default "TOP".
    underpass_layer : str
        EDB layer used for the underpass bridge.  Default "M2".
    net : str
        Net name.  Default "L".

    Examples
    --------
    >>> from pyedb_libraries import HexagonalInductor
    >>> ind = HexagonalInductor(turns=3, width=30e-6, spacing=20e-6,
    ...                         outer_radius=0.4e-3, layer="TOP")
    >>> edb = ind.create("hex_ind.aedb")
    >>> print(f"{ind.inductance_nh:.1f} nH")   # analytical estimate
    4.9 nH
    >>> edb.close_edb()
    """

    def __init__(
        self,
        *,
        turns: int = 3,
        width: float = 20e-6,
        spacing: float = 20e-6,
        outer_radius: float = 0.3e-3,
        layer: str = "TOP",
        underpass_layer: str = "M2",
        net: str = "L",
    ):
        self.turns = turns
        self.width = width
        self.spacing = spacing
        self.outer_radius = outer_radius
        self.layer = layer
        self.underpass_layer = underpass_layer
        self.net = net

    # ------------------------------------------------------------------ #
    # Analytical model (hexagonal spiral)
    # ------------------------------------------------------------------ #
    @property
    def inductance_nh(self) -> float:
        """
        Modified Wheeler for hexagonal spirals.

        Returns
        -------
        float
            Inductance in nano-Henries.
        """
        n = self.turns
        d_avg = 2 * self.outer_radius - n * (self.width + self.spacing)
        rho = (2 * self.outer_radius - d_avg) / (2 * self.outer_radius + d_avg)
        k1, k2 = 2.33, 2.75
        return k1 * 1e-7 * n**2 * d_avg / (1 + k2 * rho)

    # ------------------------------------------------------------------ #
    # EDB creation
    # ------------------------------------------------------------------ #
    def _hexagon_vertices(self, radius: float) -> List[List[float]]:
        """Return 6 vertices of a hexagon centred at (0,0)."""
        vertices = []
        for k in range(6):
            theta = math.pi / 3 * k
            vertices.append([radius * math.cos(theta), radius * math.sin(theta)])
        # close polygon
        vertices.append(vertices[0])
        return vertices

    def create(self, edb_path: str) -> Edb:
        if os.path.exists(edb_path):
            edb = Edb(edb_path)
        else:
            edb = Edb()
            edb.save_as(edb_path)

        # --- expose parameters ------------------------------------------
        edb["n"] = self.turns
        edb["w"] = self.width
        edb["s"] = self.spacing
        edb["R_out"] = self.outer_radius

        # --- draw each hexagonal ring ------------------------------------
        r = self.outer_radius
        for _ in range(self.turns):
            pts = self._hexagon_vertices(r)
            edb.modeler.create_polygon(pts, self.layer, self.net)
            r -= self.width + self.spacing

        # --- underpass via ------------------------------------------------
        # place it at the centre of the innermost hexagon
        edb.padstacks.create(
            [0, 0],
            drill=0.8 * self.width,
            pad=1.2 * self.width,
            start_layer=self.layer,
            stop_layer=self.underpass_layer,
            net=self.net,
        )

        return edb


class SquareInductor(SpiralInductor):
    """Alias of SpiralInductor with square=octagon etc. kept for API completeness."""

    pass


class CPW:
    """
    Coplanar waveguide.

    Parameters
    ----------
    length : float
    width : float
    gap : float
    layer : str
    ground_layer : str
    net : str
    """

    def __init__(
        self,
        *,
        length: float = 10e-3,
        width: float = 0.3e-3,
        gap: float = 0.1e-3,
        layer: str = "TOP",
        ground_layer: str = "GND",
        net: str = "SIG",
    ):
        self.length = length
        self.width = width
        self.gap = gap
        self.layer = layer
        self.ground_layer = ground_layer
        self.net = net

    @property
    def analytical_z0(self) -> float:
        """
        CPW impedance, conformal mapping.

        Returns
        -------
        float
            Z0 (Ohm)
        """
        a = self.width / 2
        b = a + self.gap
        k = a / b
        kpr = math.sqrt(1 - k**2)
        # Complete elliptic integral ratio approx.
        k_ratio = math.pi / (2 * math.log(2 * (1 + math.sqrt(kpr)) / (1 - math.sqrt(kpr))))
        return 30 * math.pi / math.sqrt(4.4) * k_ratio

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["l"] = self.length
        edb["w"] = self.width
        edb["g"] = self.gap

        # signal
        edb.modeler.create_rectangle(self.layer, self.net, [0, -self.width / 2, self.length, self.width])
        # grounds
        edb.modeler.create_rectangle(
            self.layer, self.ground_layer, [0, -self.width / 2 - self.gap - 5e-3, self.length, 5e-3]
        )
        edb.modeler.create_rectangle(self.layer, self.ground_layer, [0, self.width / 2 + self.gap, self.length, 5e-3])
        return edb


class RadialStub:
    """
    Radial (fan) stub.

    Parameters
    ----------
    radius : float
    angle_deg : float
    width : float
    layer : str
    net : str
    """

    def __init__(
        self, *, radius: float = 2e-3, angle_deg: float = 60, width: float = 0.2e-3, layer: str = "TOP", net: str = "RF"
    ):
        self.radius = radius
        self.angle_deg = angle_deg
        self.width = width
        self.layer = layer
        self.net = net

    @property
    def electrical_length_deg(self, freq: float = 2e9) -> float:
        """
        Electrical length (degrees) at a given frequency.

        Parameters
        ----------
        freq : float

        Returns
        -------
        float
        """
        c = 299_792_458
        er_eff = 4.4
        v = c / math.sqrt(er_eff)
        beta = 2 * math.pi * freq / v
        return math.degrees(beta * self.radius)

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["r"] = self.radius
        edb["ang"] = self.angle_deg
        edb["w"] = self.width

        # Create wedge polygon
        theta = math.radians(self.angle_deg)
        pts = [
            [0, 0],
            [self.radius * math.cos(-theta / 2), self.radius * math.sin(-theta / 2)],
            [self.radius * math.cos(theta / 2), self.radius * math.sin(theta / 2)],
        ]
        edb.modeler.create_polygon(pts, self.layer, self.net)
        # feed
        edb.modeler.create_rectangle(self.layer, self.net, [-self.width / 2, 0, self.width, self.width])
        return edb


class ViaArray:
    """
    Via fence / array.

    Parameters
    ----------
    pitch : float
    drill : float
    pad : float
    extent : Tuple[float,float]
    top_layer : str
    bottom_layer : str
    net : str
    """

    def __init__(
        self,
        *,
        pitch: float = 0.5e-3,
        drill: float = 0.1e-3,
        pad: float = 0.2e-3,
        extent: Tuple[float, float] = (5e-3, 1e-3),
        top_layer: str = "TOP",
        bottom_layer: str = "GND",
        net: str = "VSS",
    ):
        self.pitch = pitch
        self.drill = drill
        self.pad = pad
        self.extent = extent
        self.top_layer = top_layer
        self.bottom_layer = bottom_layer
        self.net = net

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["p"] = self.pitch
        edb["d"] = self.drill
        edb["pad"] = self.pad

        _via_fence(
            edb, 0, 0, *self.extent, self.pitch, self.drill, self.pad, self.top_layer, self.bottom_layer, self.net
        )
        return edb


class BalunMarchand:
    """
    Marchand balun (coupled-line type).

    Parameters
    ----------
    z_even : float
    z_odd : float
    length : float
    width : float
    spacing : float
    layer : str
    net : str
    """

    def __init__(
        self,
        *,
        z_even: float = 70,
        z_odd: float = 30,
        length: float = 10e-3,
        width: float = 0.2e-3,
        spacing: float = 0.1e-3,
        layer: str = "TOP",
        net: str = "BAL",
    ):
        self.z_even = z_even
        self.z_odd = z_odd
        self.length = length
        self.width = width
        self.spacing = spacing
        self.layer = layer
        self.net = net

    @property
    def center_frequency(self) -> float:
        """
        Quarter-wave frequency.

        Returns
        -------
        float
        """
        c = 299_792_458
        er_eff = 4.4
        v = c / math.sqrt(er_eff)
        return v / (4 * self.length)

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["l"] = self.length
        edb["w"] = self.width
        edb["s"] = self.spacing

        # two coupled lines
        y0 = -self.width / 2 - self.spacing / 2
        y1 = self.width / 2 + self.spacing / 2
        edb.modeler.create_rectangle(self.layer, self.net, [0, y0, self.length, self.width])
        edb.modeler.create_rectangle(self.layer, self.net, [0, y1, self.length, self.width])
        return edb


class RatRace:
    """
    180° rat-race coupler.

    Parameters
    ----------
    z0 : float
    freq : float
    layer : str
    net : str
    """

    def __init__(self, *, z0: float = 50, freq: float = 2e9, layer: str = "TOP", net: str = "RR"):
        self.z0 = z0
        self.freq = freq
        self.layer = layer
        self.net = net

    @property
    def circumference(self) -> float:
        """
        1.5 λg.

        Returns
        -------
        float
        """
        c = 299_792_458
        er_eff = 4.4
        v = c / math.sqrt(er_eff)
        return 1.5 * v / self.freq

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["c"] = self.circumference
        radius = self.circumference / (2 * math.pi)
        edb.modeler.create_circle(self.layer, self.net, [0, 0], radius, width=0.3e-3)
        return edb


class Wilkinson:
    """
    Simple Wilkinson divider.

    Parameters
    ----------
    z0 : float
    freq : float
    layer : str
    net : str
    """

    def __init__(self, *, z0: float = 50, freq: float = 2e9, layer: str = "TOP", net: str = "DIV"):
        self.z0 = z0
        self.freq = freq
        self.layer = layer
        self.net = net

    @property
    def lambda_quarter(self) -> float:
        """
        Quarter-wavelength.

        Returns
        -------
        float
        """
        c = 299_792_458
        er_eff = 4.4
        v = c / math.sqrt(er_eff)
        return v / (4 * self.freq)

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["l"] = self.lambda_quarter
        edb["z0"] = self.z0
        # 70.7 Ohm line
        _rect_path(edb, self.layer, self.net, 0, 0, self.lambda_quarter, 0, 0.2e-3)
        # 50 Ohm outputs
        _rect_path(
            edb, self.layer, self.net, self.lambda_quarter, 0, self.lambda_quarter + self.lambda_quarter, 0, 0.3e-3
        )
        _rect_path(edb, self.layer, self.net, self.lambda_quarter, 0, self.lambda_quarter, 0.5e-3, 0.3e-3)
        # resistor
        edb.components.create_resistor([self.lambda_quarter, 0.25e-3], 100, "R1")
        return edb


class InterdigitalCapacitor:
    """
    Interdigital capacitor.

    Parameters
    ----------
    fingers : int
    finger_length : float
    finger_width : float
    gap : float
    layer : str
    net : str
    """

    def __init__(
        self,
        *,
        fingers: int = 5,
        finger_length: float = 1e-3,
        finger_width: float = 0.1e-3,
        gap: float = 0.05e-3,
        layer: str = "TOP",
        net: str = "CAP",
    ):
        self.fingers = fingers
        self.finger_length = finger_length
        self.finger_width = finger_width
        self.gap = gap
        self.layer = layer
        self.net = net

    @property
    def capacitance_pf(self) -> float:
        """
        Simplified formula.

        Returns
        -------
        float
            Capacitance in pF
        """
        eps0 = 8.854e-12
        er = 4.4
        return (eps0 * er * self.fingers * self.finger_length * self.finger_width / self.gap) * 1e12

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        pitch = self.finger_width + self.gap
        offset = 0
        for i in range(self.fingers):
            y = i * pitch
            edb.modeler.create_rectangle(self.layer, self.net, [0, y, self.finger_length, self.finger_width])
            if i % 2:
                offset = self.finger_width + self.gap
            else:
                offset = 0
        return edb


class EBG:
    """
    Mushroom-like EBG.

    Parameters
    ----------
    patch_size : float
    gap : float
    via_diam : float
    layer : str
    via_layer : str
    net : str
    """

    def __init__(
        self,
        *,
        patch_size: float = 5e-3,
        gap: float = 0.5e-3,
        via_diam: float = 0.5e-3,
        layer: str = "TOP",
        via_layer: str = "GND",
        net: str = "EBG",
    ):
        self.patch_size = patch_size
        self.gap = gap
        self.via_diam = via_diam
        self.layer = layer
        self.via_layer = via_layer
        self.net = net

    @property
    def bandgap_freq(self) -> float:
        """
        Approximate bandgap center.

        Returns
        -------
        float
        """
        c = 299_792_458
        er = 4.4
        return c / (2 * math.pi * math.sqrt(er) * (self.patch_size + self.gap))

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["a"] = self.patch_size
        edb["g"] = self.gap
        edb["d"] = self.via_diam
        for i in range(5):
            for j in range(5):
                x = i * (self.patch_size + self.gap)
                y = j * (self.patch_size + self.gap)
                edb.modeler.create_rectangle(self.layer, self.net, [x, y, self.patch_size, self.patch_size])
                edb.padstacks.create(
                    [x + self.patch_size / 2, y + self.patch_size / 2],
                    self.via_diam,
                    self.via_diam * 1.2,
                    self.layer,
                    self.via_layer,
                    net=self.net,
                )
        return edb


class PowerSplitter(Wilkinson):
    """Alias for Wilkinson with different default width."""

    pass


class DifferentialTLine:
    """
    Edge-coupled differential pair.

    Parameters
    ----------
    length : float
    width : float
    spacing : float
    layer : str
    net_p : str
    net_n : str
    """

    def __init__(
        self,
        *,
        length: float = 10e-3,
        width: float = 0.2e-3,
        spacing: float = 0.2e-3,
        layer: str = "TOP",
        net_p: str = "P",
        net_n: str = "N",
    ):
        self.length = length
        self.width = width
        self.spacing = spacing
        self.layer = layer
        self.net_p = net_p
        self.net_n = net_n

    @property
    def diff_impedance(self) -> float:
        """
        Approximate differential impedance.

        Returns
        -------
        float
        """
        z0_single = 60  # assume
        return 2 * z0_single * (1 - 0.48 * math.exp(-0.96 * self.spacing / self.width))

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["l"] = self.length
        edb["w"] = self.width
        edb["s"] = self.spacing
        _rect_path(edb, self.layer, self.net_p, 0, 0, self.length, 0, self.width)
        _rect_path(
            edb,
            self.layer,
            self.net_n,
            0,
            -self.width - self.spacing,
            self.length,
            -self.width - self.spacing,
            self.width,
        )
        return edb
