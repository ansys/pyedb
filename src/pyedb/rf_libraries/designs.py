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


class HatchGround:
    """
    Create a board with a hatched copper ground plane.

    Parameters
    ----------
    pitch : float
        Center-to-center distance of hatch bars [m].
    width : float
        Width of each copper bar [m].
    fill_target : float
        Desired copper area in percent (10 … 90).
    board_size : float
        Edge length of square demo board [m].
    edb_path : str | None
        Optional explicit EDB path.  If None, a unique temp folder is used.
    edb_version : str
        EDB/Siwave version string, e.g. "2024.1".
    """

    def __init__(
        self,
        edb_cell: Optional[Edb] = None,
        pitch: float = 17.07e-3,
        width: float = 5.0e-3,
        fill_target: float = 50.0,
        board_size: float = 100e-3,
        layer_gnd: str = "GND",
    ):
        """Initialize the hatch ground object."""
        self._edb = edb_cell
        self.pitch = float(pitch)
        self.width = float(width)
        self.fill_target = float(fill_target)
        self.board_size = float(board_size)
        self.layer_gnd = layer_gnd
        self._outline = None

    @property
    def copper_fill_ratio(self) -> float:
        """Return actual copper fill ratio in percent."""
        cu_area = self._edb.modeler.get_polygon_area(layer_name=self.layer_gnd)
        return 100.0 * cu_area / (self.board_size**2)

    def _generate_hatch(self) -> None:
        """Draw orthogonal stripes, then punch gaps for the requested fill."""
        # ---------- horizontal bars ----------
        y = 0.0
        while y < self.board_size:
            self._add_stripe(0.0, y, self.board_size, y + self.width)
            y += self.pitch

        # ---------- vertical bars ------------
        x = 0.0
        while x < self.board_size:
            self._add_stripe(x, 0.0, x + self.width, self.board_size)
            x += self.pitch

        # ---------- punch square gaps --------
        gaps: List[List[Tuple[float, float]]] = []
        x = 0.0
        while x < self.board_size:
            y = 0.0
            while y < self.board_size:
                gaps.append(
                    [
                        (x, y),
                        (x + self.width, y),
                        (x + self.width, y + self.width),
                        (x, y + self.width),
                        (x, y),
                    ]
                )
                y += self.pitch
            x += self.pitch
        polygons = self._edb.modeler.polygons
        polygons[0].unite(polygons[1:])

    def _add_stripe(self, x0: float, y0: float, x1: float, y1: float) -> None:
        """Create one rectangular copper bar on the GND layer."""
        points = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        self._edb.modeler.create_polygon(points, layer_name=self.layer_gnd, net_name="GND")

    def create(self) -> bool:
        """Create the stack-up, outline and hatch pattern."""
        self._generate_hatch()
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
        edb_cell: Optional[Edb] = None,
        z0: float = 50,
        freq: float = 10e9,
        layer: str = "TOP",
        bottom_layer: Optional[str] = None,
        net: str = "RR",
        width: float = 0.2e-3,
        nr_segments: int = 32,
    ):
        self._pedb = edb_cell
        self.z0 = z0
        self.freq = freq
        self.layer = layer
        self.bottom_layer = bottom_layer
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
    def create(self) -> bool:
        self._pedb["c"] = self.circumference
        self._pedb["r"] = self.radius
        self._pedb["w"] = self.width

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
        self._pedb.modeler.create_trace(
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
            self._pedb.modeler.create_trace(
                path_list=stub_pts,
                layer_name=self.layer,
                net_name=f"{self.net}_P{idx}",
                width=w,
                start_cap_style="flast",
                end_cap_style="flat",
            )

        self._pedb.modeler.create_rectangle(
            lower_left_point=[-self.circumference / 4, -self.circumference / 4],
            upper_right_point=[self.circumference / 4, self.circumference / 4],
            layer_name=self.bottom_layer,
            net_name=self.net,
        )
        return True


class InterdigitalCapacitor:
    """
    Inter-digital capacitor with **comb-up / comb-down** fingers.
    All dimensions are stored as EDB design variables so they can be
    edited after import.
    """

    # fmt: off
    VAR_PREFIX = "IDC"  # prefix for every EDB variable

    # fmt: on

    def __init__(
        self,
        edb_cell: Optional[Edb] = None,
        fingers: int = 8,
        finger_length: str = "0.9mm",
        finger_width: str = "0.08mm",
        gap: str = "0.04mm",
        comb_gap: str = "0.06mm",
        bus_width: str = "0.25mm",
        layer: str = "TOP",
        net_a: str = "PORT1",
        net_b: str = "PORT2",
    ):
        self._pedb = edb_cell
        self.layer = layer
        self.net_a = net_a
        self.net_b = net_b
        self.substrate = Substrate()

        # ------------------------------------------------------
        # 1.  Register every dimension as an EDB variable
        # ------------------------------------------------------
        pfx = self.VAR_PREFIX
        self._vars = {
            "fingers": int(fingers),  # integer is fine
            "finger_length": finger_length,
            "finger_width": finger_width,
            "gap": gap,
            "comb_gap": comb_gap,
            "bus_width": bus_width,
        }
        for k, v in self._vars.items():
            var_name = f"{pfx}_{k}"
            # Use design variable (no $ prefix) -> stored in cell
            self._pedb[var_name] = v

        # ------------------------------------------------------------------
        #  Live capacitance (pF) – tracks any variable change
        # ------------------------------------------------------------------

    @property
    def capacitance_pf(self) -> float:
        """
        Rough lumped parallel-plate estimate:
        C = ε₀ εᵣ  N  L  W  /  g
        where
            N = total finger pairs  = fingers
            L = finger_length
            W = finger_width
            g = gap
        """
        pfx = self.VAR_PREFIX
        eps0 = 8.854e-12
        er = self.substrate.er
        N = self._pedb[f"{pfx}_fingers"]
        L = self._pedb[f"{pfx}_finger_length"]
        W = self._pedb[f"{pfx}_finger_width"]
        g = self._pedb[f"{pfx}_gap"]
        return (eps0 * er * N * L * W / g) * 1e12

    # ----------------------------------------------------------
    # 2.  Draw the geometry using the EDB variables
    # ----------------------------------------------------------
    def create(self) -> bool:
        if self._pedb is None:
            raise ValueError("No EDB cell provided.")

        pfx = self.VAR_PREFIX
        pitch = f"({pfx}_finger_width + {pfx}_gap)"
        total_width = f"(2*{pfx}_bus_width + (2*{pfx}_fingers-1)*{pitch} + {pfx}_finger_width)"
        total_height = f"(2*{pfx}_bus_width + 2*{pfx}_finger_length + {pfx}_comb_gap)"

        # --- helper lambda to build expressions with units
        expr = lambda s: f"{s}[mm]" if "[" not in s else s

        # 1. Bottom bus bar (NET_A)
        self._pedb.modeler.create_rectangle(
            layer_name=self.layer,
            net_name=self.net_a,
            lower_left_point=["0", "0"],
            upper_right_point=[total_width, f"{pfx}_bus_width"],
        )

        # 2. Top bus bar (NET_B)
        right_bar_y = f"({total_height} - {pfx}_bus_width)"
        self._pedb.modeler.create_rectangle(
            layer_name=self.layer,
            net_name=self.net_b,
            lower_left_point=["0", right_bar_y],
            upper_right_point=[total_width, total_height],
        )

        # 3. Fingers (interleaved)
        y_a = f"{pfx}_bus_width"  # base of up fingers
        y_b = f"({total_height} - {pfx}_bus_width - {pfx}_finger_length)"  # base of down fingers

        for i in range(self._vars["fingers"] * 2):
            x = f"({pfx}_bus_width + {i}*{pitch})"
            if i % 2 == 0:  # NET_A finger (points up)
                self._pedb.modeler.create_rectangle(
                    layer_name=self.layer,
                    net_name=self.net_a,
                    lower_left_point=[x, y_a],
                    upper_right_point=[f"{x} + {pfx}_finger_width", f"{y_a} + {pfx}_finger_length"],
                )
            else:  # NET_B finger (points down)
                self._pedb.modeler.create_rectangle(
                    layer_name=self.layer,
                    net_name=self.net_b,
                    lower_left_point=[x, y_b],
                    upper_right_point=[f"{x} + {pfx}_finger_width", f"{y_b} + {pfx}_finger_length"],
                )

        return True


class DifferentialTLine:
    """
    Fully-parametric edge-coupled differential pair.
    All dimensions are native EDB parameters so they stay editable
    after the EDB is imported into AEDT.
    """

    def __init__(
        self,
        edb: Edb,
        length: float = 10e-3,
        width: float = 0.20e-3,
        spacing: float = 0.20e-3,
        x0: float = 0.0,
        y0: float = 0.0,
        angle: float = 0.0,
        layer: str = "TOP",
        net_p: str = "P",
        net_n: str = "N",
    ):
        self._edb = edb
        self.length = length  # total length
        self.width = width
        self.spacing = spacing
        self.x0 = x0
        self.y0 = y0
        self.layer = layer
        self.net_p = net_p
        self.net_n = net_n

        # ----------------------------------------------------------
        # Declare every numeric value as an EDB variable
        # ----------------------------------------------------------
        self._edb["diff_len"] = self.length  # total length
        self._edb["diff_w"] = self.width  # single trace width
        self._edb["diff_s"] = self.spacing  # edge-to-edge spacing
        self._edb["diff_x0"] = self.x0  # start-x
        self._edb["diff_y0"] = self.y0  # start-y
        self._edb["diff_angle"] = math.degrees(angle)  # rotation in degrees

    # ----------------------------------------------------------
    # Read-only impedance helper (uses live parameter values)
    # ----------------------------------------------------------
    @property
    def diff_impedance(self) -> float:
        w = self._edb["diff_w"]
        s = self._edb["diff_s"]
        z0_single = 60.0
        return 2 * z0_single * (1 - 0.48 * math.exp(-0.96 * s / w))

    # ----------------------------------------------------------
    # Geometry creation – returns the two EDB path objects
    # ----------------------------------------------------------
    def create(self) -> List[float]:
        # Build the two traces using ONLY parameter strings
        # so AEDT keeps them live.
        pos_trace = self._edb.modeler.create_trace(
            path_list=[
                ["diff_x0", "diff_y0"],
                ["diff_x0 + diff_len*cos(diff_angle*1deg)", "diff_y0 + diff_len*sin(diff_angle*1deg)"],
            ],
            layer_name=self.layer,
            width="diff_w",
            net_name=self.net_p,
            start_cap_style="Flat",
            end_cap_style="Flat",
        )

        neg_y_expr = "diff_y0 - diff_w - diff_s"
        neg_trace = self._edb.modeler.create_trace(
            path_list=[
                ["diff_x0", neg_y_expr],
                ["diff_x0 + diff_len*cos(diff_angle*1deg)", f"{neg_y_expr} + diff_len*sin(diff_angle*1deg)"],
            ],
            layer_name=self.layer,
            width="diff_w",
            net_name=self.net_n,
            start_cap_style="Flat",
            end_cap_style="Flat",
        )
        return [pos_trace, neg_trace]
