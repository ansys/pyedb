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
from typing import List, Optional, Tuple, Union

import numpy as np

from pyedb import Edb

# ---------------------------------------------------------------------------
# Common utilities
# ---------------------------------------------------------------------------


@dataclass
class Substrate:
    """Small helper to keep substrate parameters together."""

    h: float = 100e-6  # height (m)
    er: float = 4.4  # relative permittivity
    tan_d: float = 0  # loss tangent
    name: str = "SUB"
    size: Tuple[float, float] = (0.001, 0.001)  # width, length in metres


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
        edb_cell: Optional[Edb] = None,
        area: float = 0.1e-6,
        gap: float = 1e-6,
        er: float = 7,
        layer_top: str = "M1",
        layer_bottom: str = "M2",
        net: str = "RF",
    ):
        self._pedb = edb_cell
        self.area = area
        self.gap = gap
        self.layer_top = layer_top
        self.layer_bottom = layer_bottom
        self.net = net
        self.substrate = Substrate()

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
        return eps0 * self.substrate.er * self.area / self.gap

    def create(self) -> bool:
        self._pedb["area"] = self.area
        self._pedb["gap"] = self.gap
        side = math.sqrt(self.area)
        self._pedb["side"] = side

        self._pedb.modeler.create_rectangle(self.layer_top, self.net, [0, -side / 2, side, side])
        self._pedb.modeler.create_rectangle(self.layer_bottom, self.net, [0, -side / 2, side, side])
        return True


class SpiralInductor:
    """
    Square spiral inductor with underpass.
    """

    def __init__(
        self,
        edb_cell: Optional[Edb] = None,
        turns: Union[int, float] = 4.5,
        trace_width: float = 20e-6,
        spacing: float = 12e-6,
        inner_diameter: float = 60e-6,
        layer: str = "M1",
        bridge_layer: str = "M2",
        via_layer: str = "M3",
        net: str = "IN",
        inductor_center: Tuple[float, float] = (0, 0),  # centre of spiral
        via_size: float = 25e-6,  # via metal pad
        bridge_width: float = 12e-6,  # under-pass trace width
        bridge_clearance: float = 6e-6,  # dielectric gap under bridge
        bridge_length: float = 200e-6,  # how far the bridge extends
        ground_layer: str = "GND",
    ):
        self._pedb = edb_cell
        self.turns = turns  # half-turns → 4.5 = 4 full + 1 half
        self.trace_width = trace_width
        self.spacing = spacing
        self.inner_diameter = inner_diameter  # first inner square side
        self.via_size = via_size  # centre via finished hole
        self.inductor_center = inductor_center  # via centre position
        self.bridge_width = bridge_width  # under-pass trace width
        self.bridge_clearance = bridge_clearance  # dielectric gap under bridge
        self.bridge_length = bridge_length  # how far the bridge extends
        self.layer = layer
        self.bridge_layer = bridge_layer
        self.via_layer = via_layer  # layer for the centre via
        self.substrate = Substrate()  # default substrate
        self.net_name = net
        self.ground_layer = ground_layer

    @property
    def inductance_nh(self) -> float:
        """
        Accurate inductance for the **square** spiral actually drawn by create().
        Uses the improved Wheeler formula with square-layout coefficients.

        Returns
        -------
        float
            Inductance in nH
        """
        # 1. Geometry exactly as it is built in create()

        w = self.trace_width
        s = self.spacing
        N = self.turns
        d_in = self.inner_diameter
        d_out = d_in + 4 * N * (w + s)  # outer side length

        # 2. Parameters for the improved Wheeler formula (square)
        d_avg = (d_out + d_in) / 2.0
        rho = (d_out - d_in) / (d_out + d_in)

        C1, C2, C3, C4 = 1.27, 2.07, 0.18, 0.13  # square coefficients
        mu0 = 4e-7 * math.pi  # H·m⁻¹

        # 3. Wheeler formula in SI
        L_h = (mu0 * N**2 * d_avg * C1 / 2.0) * (math.log(C2 / rho) + C3 * rho**2 + C4 * rho**3)

        return L_h * 1e9  # → nH

    def create(self) -> bool:
        cx = self.inductor_center[0]
        cy = self.inductor_center[1]
        pts = []
        x, y = cx, cy
        side = self.inner_diameter
        direction = 0  # 0=+y, 1=-x, 2=-y, 3=+x (vertical first)

        for i in range(int(math.ceil(2 * self.turns))):
            # choose direction and length
            if direction == 0:
                dx, dy = 0, side / 2
            elif direction == 1:
                dx, dy = -side / 2, 0
            elif direction == 2:
                dx, dy = 0, -side / 2
            else:
                dx, dy = side / 2, 0

            x += dx
            y += dy
            pts.append((x, y))

            direction = (direction + 1) % 4
            if i % 2 == 1:  # every two sides increase pitch
                side += 2 * (self.trace_width + self.spacing)

        via_pos = pts[0]
        bridge_dir = -1  # -1 = down, +1 = up
        bridge_end = (via_pos[0] + bridge_dir * self.bridge_length, via_pos[1])

        self._pedb.modeler.create_trace(
            path_list=pts,
            layer_name=self.layer,
            width=self.trace_width,
            net_name=self.net_name,
            start_cap_style="Flat",
            end_cap_style="Flat",
        )

        # Centre via (spiral inner end → bottom metal)
        self._pedb.modeler.create_rectangle(
            layer_name=self.via_layer,
            center_point=pts[0],
            width=self.via_size,
            height=self.via_size,
            representation_type="CenterWidthHeight",
            net_name=self.net_name,
        )

        # bridge trace on bottom metal
        self._pedb.modeler.create_trace(
            path_list=[via_pos, bridge_end],
            layer_name=self.bridge_layer,
            width=self.bridge_width,
            net_name=self.net_name,
            start_cap_style="Flat",
            end_cap_style="Flat",
        )

        # ground plane
        self._pedb.modeler.create_rectangle(
            layer_name=self.ground_layer,
            center_point=self.inductor_center,
            width=self.substrate.size[0],
            height=self.substrate.size[1],
            representation_type="CenterWidthHeight",
            net_name="ref",
        )
        return True


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
    substrate : Substrate
    """

    def __init__(
        self,
        edb_cell: Optional[Edb] = None,
        length: float = 1e-3,
        width: float = 0.3e-3,
        gap: float = 0.1e-3,
        layer: str = "TOP",
        ground_net: str = "GND",
        ground_width: float = 0.1e-3,
        ground_layer: str = "GND",
        net: str = "SIG",
        substrate: Substrate = Substrate(100e-6, 4.4, 0.02, "SUB", (0.001, 0.001)),
    ):
        self._pedb = edb_cell
        self.length = length
        self.width = width
        self.gap = gap
        self.layer = layer
        self.ground_net = ground_net
        self.ground_width = ground_width  # width of ground plane
        self.ground_layer = ground_layer  # layer for the ground plane
        self.net = net
        self.substrate = substrate

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

    def create(self) -> bool:
        self._pedb["l"] = self.length
        self._pedb["w"] = self.width
        self._pedb["g"] = self.gap

        # signal
        self._pedb.modeler.create_rectangle(
            self.layer,
            net_name=self.net,
            lower_left_point=[-self.width / 2, 0],
            upper_right_point=[self.width / 2, self.length],
        )
        # grounds
        self._pedb.modeler.create_rectangle(
            self.layer,
            net_name=self.ground_net,
            lower_left_point=[-self.width / 2 - self.gap - self.ground_width, 0],
            upper_right_point=[-self.width / 2 - self.gap, self.length],
        )
        self._pedb.modeler.create_rectangle(
            self.layer,
            net_name=self.ground_net,
            lower_left_point=[self.width / 2 + self.gap, 0],
            upper_right_point=[self.width / 2 + self.gap + self.ground_width, self.length],
        )
        self._pedb.modeler.create_rectangle(
            self.ground_layer,
            lower_left_point=[-self.width / 2 - self.gap - self.ground_width, 0],
            upper_right_point=[self.width / 2 + self.gap + self.ground_width, self.length],
        )
        return True


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
        self,
        edb_cell,
        radius: float = 500e-6,
        angle_deg: float = 60,
        width: float = 0.2e-3,
        layer: str = "TOP",
        net: str = "RF",
    ):
        self._pedb = edb_cell
        self.radius = radius
        self.angle_deg = angle_deg
        self.width = width
        self.layer = layer
        self.net = net
        self.substrate: Substrate = Substrate(100e-6, 4.4, 0.02, "SUB", (0.001, 0.001))

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
        v = c / math.sqrt(self.substrate.er)
        beta = 2 * math.pi * freq / v
        return math.degrees(beta * self.radius)

    def create(self) -> bool:
        self._pedb["r"] = self.radius
        self._pedb["ang"] = self.angle_deg
        self._pedb["w"] = self.width

        # Create wedge polygon
        theta = math.radians(self.angle_deg)
        pts = [
            [0, 0],
            [self.radius * math.cos(-theta / 2), self.radius * math.sin(-theta / 2)],
            [self.radius * math.cos(theta / 2), self.radius * math.sin(theta / 2)],
        ]
        self._pedb.modeler.create_polygon(main_shape=pts, layer_name=self.layer, net_name=self.net)
        # feed
        self._pedb.modeler.create_rectangle(
            layer_name=self.layer,
            net_name=self.net,
            lower_left_point=[0, -self.width / 2],
            upper_right_point=[self.width, self.width / 2],
        )
        return True


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


class RatRace:
    """
    180° rat-race coupler realised with discretised arcs.

    Parameters
    ----------
    z0 : float
        Characteristic impedance of the ring (ohm).
    freq : float
        Centre frequency (Hz).
    layer : str
        Metal layer name.
    net : str
        Net name.
    width : float
        Micro-strip width (m).
    nr_segments : int
        Number of straight segments used to approximate 90 ° of arc.
    """

    def __init__(
        self,
        *,
        z0: float = 50,
        freq: float = 2e9,
        layer: str = "TOP",
        net: str = "RR",
        width: float = 0.3e-3,
        nr_segments: int = 32,
    ):
        self.z0 = z0
        self.freq = freq
        self.layer = layer
        self.net = net
        self.width = width
        self.nr_segments = nr_segments
        self.substrate = Substrate()

    # ------------------------------------------------------------------
    # Helper properties
    # ------------------------------------------------------------------
    @property
    def circumference(self) -> float:
        """Electrical length = 1.5 λg."""
        c = 299_792_458
        v = c / math.sqrt(self.substrate.er)
        return 1.5 * v / self.freq

    @property
    def radius(self) -> float:
        """Mean radius of the ring."""
        return self.circumference / (2 * math.pi)

    # ------------------------------------------------------------------
    # Geometry builders
    # ------------------------------------------------------------------
    def _arc_points(
        self,
        centre: Tuple[float, float],
        radius: float,
        start_angle: float,  # rad
        delta_angle: float,  # rad
    ) -> List[Tuple[float, float]]:
        """Return a list of (x,y) for a discretised arc."""
        points = []
        step = delta_angle / self.nr_segments
        for i in range(self.nr_segments + 1):
            ang = start_angle + i * step
            x = centre[0] + radius * math.cos(ang)
            y = centre[1] + radius * math.sin(ang)
            points.append((x, y))
        return points

    def _port_stub(self, start: Tuple[float, float], length: float, angle: float):
        """Return a two-point list for a straight stub."""
        dx = length * math.cos(angle)
        dy = length * math.sin(angle)
        return [start, (start[0] + dx, start[1] + dy)]

    # ------------------------------------------------------------------
    # Main creation routine
    # ------------------------------------------------------------------
    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)

        edb["c"] = self.circumference
        edb["r"] = self.radius
        edb["w"] = self.width

        # ----------------------------------------------------------------------
        # 1. Geometry parameters
        # ----------------------------------------------------------------------
        r = self.radius
        w = self.width
        stub_len = 1e-3  # 1 mm straight sections at the four ports

        # ----------------------------------------------------------------------
        # 2. Build the ring as four connected arcs
        # ----------------------------------------------------------------------
        # We go counter-clockwise starting at the right-hand port (0°, port 1).
        #
        # port 1 (0°) -------- arc A (90°) ------- port 2 (90°)
        #      |                                      |
        #      |                                      |
        #      |             270° arc D               |
        #      |                                      |
        # port 4 (270°) ----- arc C (90°) ------ port 3 (180°)

        # Arc A: 0° -> 90°
        pts_a = self._arc_points((0, 0), r, math.radians(0), math.radians(90))

        # Arc B: 90° -> 180°
        pts_b = self._arc_points((0, 0), r, math.radians(90), math.radians(90))

        # Arc C: 180° -> 270°
        pts_c = self._arc_points((0, 0), r, math.radians(180), math.radians(90))

        # Arc D: 270° -> 360° (=0°)  (the long 270° section)
        pts_d = self._arc_points((0, 0), r, math.radians(270), math.radians(90))

        # Stitch them together into a single closed path
        ring_points = pts_a + pts_b[1:] + pts_c[1:] + pts_d[1:]
        edb.modeler.create_trace(
            path_list=ring_points,
            layer_name=self.layer,
            net_name=self.net,
            width=w,
        )

        # ----------------------------------------------------------------------
        # 3. Add the four 50 Ω port stubs
        # ----------------------------------------------------------------------
        # Angles of the ports on the ring
        port_angles = [0, 90, 180, 270]  # degrees

        for idx, ang_deg in enumerate(port_angles, start=1):
            ang = math.radians(ang_deg)
            x_ring = r * math.cos(ang)
            y_ring = r * math.sin(ang)

            # Direction vector pointing outwards
            stub_pts = self._port_stub((x_ring, y_ring), stub_len, ang)
            edb.modeler.create_trace(
                path_list=stub_pts,
                layer_name=self.layer,
                net_name=f"{self.net}_P{idx}",
                width=w,
            )

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
