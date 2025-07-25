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

from __future__ import annotations

import math

from pyedb.libraries.common import Substrate


class RectPatch:
    """
    Rectangular microstrip patch (incl. inset fed).

    Parameters
    ----------
    freq : float
        Target resonance (Hz)
    sub_h : float
        Substrate height (m)
    sub_er : float
    sub_tand : float
    inset : float
        Inset depth for 50-Ω feed (m).  0 = probe feed.
    layer : str
    via_layer : str
    """

    def __init__(
        self, edb_cell=None, freq: float = 2.4e9, inset: float = 0, layer: str = "TOP", bottom_layer: str = "GND"
    ):
        self._edb = edb_cell
        self.freq = freq
        self.inset = inset
        self.layer = layer
        self.bottom_layer = bottom_layer
        self.substrate = Substrate()

    @property
    def resonant_frequency(self) -> float:
        """
        Analytical cavity model.

        Returns
        -------
        float
        """
        # Effective length
        c = 299_792_458
        eps_eff = (self.substrate.er + 1) / 2 + (self.substrate.er - 1) / 2 * (
            1 + 10 * self.substrate.h / self.width_patch
        ) ** -0.5
        return c / (2 * self.width_patch * math.sqrt(eps_eff))

    @property
    def width_patch(self) -> float:
        """Patch width."""
        c = 299_792_458
        return c / (2 * self.freq * math.sqrt((self.substrate.er + 1) / 2))

    @property
    def length_patch(self) -> float:
        """Patch length accounting for fringing."""
        eps_eff = (self.substrate.er + 1) / 2 + (self.substrate.er - 1) / 2 * (
            1 + 12 * self.substrate.h / self.width_patch
        ) ** -0.5
        delta_l = (
            0.412
            * self.substrate.h
            * (eps_eff + 0.3)
            / (eps_eff - 0.258)
            * (self.width_patch / self.substrate.h + 0.264)
            / (self.width_patch / self.substrate.h + 0.8)
        )
        return 0.5 * 299_792_458 / (self.freq * math.sqrt(eps_eff)) - 2 * delta_l

    def create(self) -> bool:
        self._edb["w"] = self.width_patch
        self._edb["l"] = self.length_patch
        self._edb["x0"] = self.inset

        # patch
        self._edb.modeler.create_rectangle(
            self.layer,
            "ANT",
            representation_type="CenterWidthHeight",
            center_point=[0, 0],
            height=self.length_patch,
            width=self.width_patch,
        )
        # feed
        if self.inset > 0:
            y = self.width_patch / 2 - self.inset
            self._edb.modeler.create_trace(
                layer_name=self.layer,
                net_name="FEED",
                path_list=[-2e-3, y, 0, y, 0.2e-3],
                start_cap_style="Flat",
                end_cap_style="Flat",
            )
        else:
            padstack_def = self._edb.padstacks.create(
                padstackname="FEED", start_layer=self.layer, stop_layer=self.bottom_layer
            )
            padstack_def.place([0, self.width_patch / 2])
        return True


class CircularPatch:
    """
    Circular microstrip patch.

    Parameters
    ----------
    freq : float
    sub_h : float
    sub_er : float
    layer : str
    via_layer : str
    """

    def __init__(
        self,
        *,
        freq: float = 2.4e9,
        sub_h: float = 1.6e-3,
        sub_er: float = 4.4,
        layer: str = "TOP",
        via_layer: str = "GND",
    ):
        self.freq = freq
        self.sub_h = sub_h
        self.sub_er = sub_er
        self.layer = layer
        self.via_layer = via_layer

    @property
    def radius(self) -> float:
        """
        Approximate patch radius.

        Returns
        -------
        float
        """
        c = 299_792_458
        k = 1.84118  # TM11
        return k * c / (2 * math.pi * self.freq * math.sqrt(self.sub_er))

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["r"] = self.radius
        edb.modeler.create_circle(self.layer, "ANT", [0, 0], self.radius)
        edb.padstacks.create([0, 0], 0.3e-3, 0.5e-3, self.layer, self.via_layer, net="FEED")
        return edb


class AnnularRingPatch:
    """
    Annular-ring patch.

    Parameters
    ----------
    freq : float
    sub_h : float
    sub_er : float
    ratio : float
        r_outer / r_inner.  Default 2.
    layer : str
    via_layer : str
    """

    def __init__(
        self,
        *,
        freq: float = 2.4e9,
        sub_h: float = 1.6e-3,
        sub_er: float = 4.4,
        ratio: float = 2,
        layer: str = "TOP",
        via_layer: str = "GND",
    ):
        self.freq = freq
        self.sub_h = sub_h
        self.sub_er = sub_er
        self.ratio = ratio
        self.layer = layer
        self.via_layer = via_layer

    @property
    def r_outer(self) -> float:
        c = 299_792_458
        k = 2.057  # TM12
        return k * c / (2 * math.pi * self.freq * math.sqrt(self.sub_er))

    @property
    def r_inner(self) -> float:
        return self.r_outer / self.ratio

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["ro"] = self.r_outer
        edb["ri"] = self.r_inner
        edb.modeler.create_circle(self.layer, "ANT", [0, 0], self.r_outer)
        edb.modeler.create_circle(self.layer, "VOID", [0, 0], self.r_inner)
        return edb


class TriangularPatch:
    """
    Equilateral triangular patch.

    Parameters
    ----------
    freq : float
    sub_h : float
    sub_er : float
    layer : str
    via_layer : str
    """

    def __init__(
        self,
        *,
        freq: float = 2.4e9,
        sub_h: float = 1.6e-3,
        sub_er: float = 4.4,
        layer: str = "TOP",
        via_layer: str = "GND",
    ):
        self.freq = freq
        self.sub_h = sub_h
        self.sub_er = sub_er
        self.layer = layer
        self.via_layer = via_layer

    @property
    def side(self) -> float:
        c = 299_792_458
        k = 2 / 3 * math.pi
        return k * c / (math.pi * self.freq * math.sqrt(self.sub_er))

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["s"] = self.side
        h = self.side * math.sqrt(3) / 2
        pts = [[0, 0], [self.side, 0], [self.side / 2, h]]
        edb.modeler.create_polygon(pts, self.layer, "ANT")
        return edb


class SlotRing:
    """
    Circular slot-ring antenna.

    Parameters
    ----------
    freq : float
    sub_h : float
    sub_er : float
    slot_width : float
    layer : str
    """

    def __init__(
        self,
        *,
        freq: float = 2.4e9,
        sub_h: float = 1.6e-3,
        sub_er: float = 4.4,
        slot_width: float = 0.5e-3,
        layer: str = "TOP",
    ):
        self.freq = freq
        self.sub_h = sub_h
        self.sub_er = sub_er
        self.slot_width = slot_width
        self.layer = layer

    @property
    def mean_radius(self) -> float:
        c = 299_792_458
        return c / (2 * math.pi * self.freq * math.sqrt((self.sub_er + 1) / 2))

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["r"] = self.mean_radius
        edb["w"] = self.slot_width
        edb.modeler.create_circle(self.layer, "ANT", [0, 0], self.mean_radius + self.slot_width / 2)
        edb.modeler.create_circle(self.layer, "VOID", [0, 0], self.mean_radius - self.slot_width / 2)
        return edb


class BowTie:
    """
    Bow-tie dipole.

    Parameters
    ----------
    freq : float
    angle_deg : float
    layer : str
    """

    def __init__(self, *, freq: float = 2.4e-9, angle_deg: float = 45, layer: str = "TOP"):
        self.freq = freq
        self.angle_deg = angle_deg
        self.layer = layer

    @property
    def length(self) -> float:
        c = 299_792_458
        return 0.5 * c / self.freq

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["l"] = self.length
        ang = math.radians(self.angle_deg)
        # Create two triangles
        x = self.length / 2
        y = x * math.tan(ang)
        pts1 = [[0, 0], [x, y], [x, -y]]
        pts2 = [[0, 0], [-x, y], [-x, -y]]
        edb.modeler.create_polygon(self.layer, "ANT", pts1)
        edb.modeler.create_polygon(self.layer, "ANT", pts2)
        return edb


class IFA:
    """
    Inverted-F antenna.

    Parameters
    ----------
    freq : float
    sub_h : float
    sub_er : float
    layer : str
    via_layer : str
    """

    def __init__(
        self,
        *,
        freq: float = 2.4e9,
        sub_h: float = 1.6e-3,
        sub_er: float = 4.4,
        layer: str = "TOP",
        via_layer: str = "GND",
    ):
        self.freq = freq
        self.sub_h = sub_h
        self.sub_er = sub_er
        self.layer = layer
        self.via_layer = via_layer

    @property
    def length(self) -> float:
        c = 299_792_458
        return 0.25 * c / (self.freq * math.sqrt((self.sub_er + 1) / 2))

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["l"] = self.length
        # L-shape
        _rect_path(edb, self.layer, "ANT", 0, 0, 0, self.length, 1e-3)
        _rect_path(edb, self.layer, "ANT", 0, self.length, self.length / 4, self.length, 1e-3)
        # ground via
        edb.padstacks.create([0, 0], 0.5e-3, 0.7e-3, self.layer, self.via_layer, net="GND")
        return edb


class PIFA:
    """
    Planar inverted-F antenna (short-circuited patch).

    Parameters
    ----------
    freq : float
    sub_h : float
    sub_er : float
    layer : str
    via_layer : str
    """

    def __init__(
        self,
        *,
        freq: float = 2.4e9,
        sub_h: float = 1.6e-3,
        sub_er: float = 4.4,
        layer: str = "TOP",
        via_layer: str = "GND",
    ):
        self.freq = freq
        self.sub_h = sub_h
        self.sub_er = sub_er
        self.layer = layer
        self.via_layer = via_layer

    @property
    def length(self) -> float:
        c = 299_792_458
        return 0.25 * c / (self.freq * math.sqrt(self.sub_er))

    def create(self, edb_path: str) -> Edb:
        edb = Edb()
        edb.save_as(edb_path)
        edb["l"] = self.length
        edb.modeler.create_rectangle(self.layer, "ANT", [0, 0, self.length, self.length / 2])
        # shorting wall
        _via_fence(edb, 0, 0, 0, self.length / 2, 1e-3, 0.3e-3, 0.5e-3, self.layer, self.via_layer, "GND")
        # feed
        edb.padstacks.create([self.length / 4, self.length / 4], 0.3e-3, 0.5e-3, self.layer, self.via_layer, net="FEED")
        return edb


class FractalAntenna:
    """
    Sierpiński-gasket microstrip fractal antenna with selectable order.

    Parameters
    ----------
    freq : float
        Target fundamental resonance (**order = 1**) in Hz.
    sub_h : float
        Substrate height (m).  Default 1.6 mm.
    sub_er : float
        Substrate εr.  Default 4.4.
    order : int
        Fractal iteration (1, 2, 3 …).  Default 1.
    layer : str
        EDB layer.  Default "TOP".
    via_layer : str
        Via layer for probe feed.  Default "GND".

    Properties
    ----------
    triangle_size : float
        Side length of the **largest** (order-1) triangle.
    resonant_frequency : float
        Estimated resonance of the **selected order** based on size scaling.

    Examples
    --------
    >>> fa = FractalAntenna(freq=2.4e9, order=3)
    >>> edb = fa.create("frac3.aedb")
    >>> print(f"Order 3 resonance ≈ {fa.resonant_frequency/1e9:.2f} GHz")
    7.20 GHz
    >>> edb.close_edb()
    """

    def __init__(
        self,
        *,
        freq: float = 2.4e9,
        sub_h: float = 1.6e-3,
        sub_er: float = 4.4,
        order: int = 1,
        layer: str = "TOP",
        via_layer: str = "GND",
    ):
        self.freq = freq
        self.sub_h = sub_h
        self.sub_er = sub_er
        self.order = max(1, int(order))
        self.layer = layer
        self.via_layer = via_layer

    # ----------------------------------------------------------
    # Analytical properties
    # ----------------------------------------------------------
    @property
    def triangle_size(self) -> float:
        """Side length of the largest (order-1) equilateral triangle."""
        c = 299_792_458
        return 0.5 * c / (self.freq * math.sqrt((self.sub_er + 1) / 2))

    @property
    def resonant_frequency(self) -> float:
        """
        Approximate resonance for the chosen fractal order.

        Each higher order shrinks the effective radiator by 1/2,
        so frequency doubles per order.
        """
        return self.freq * (2 ** (self.order - 1))

    # ----------------------------------------------------------
    # EDB creation
    # ----------------------------------------------------------
    def _sierpinski_vertices(self, side: float, center=(0.0, 0.0)) -> list[list[float]]:
        """Return 3 vertices of an equilateral triangle."""
        cx, cy = center
        h = side * math.sqrt(3) / 2
        return [
            [cx - side / 2, cy - h / 3],
            [cx + side / 2, cy - h / 3],
            [cx, cy + 2 * h / 3],
            [cx - side / 2, cy - h / 3],  # close polygon
        ]

    def _subtract_triangle(self, edb: "Edb", side: float, center=(0.0, 0.0)) -> None:
        """Create a VOID polygon for the given triangle."""
        pts = self._sierpinski_vertices(side, center)
        edb.modeler.create_polygon(self.layer, "VOID", pts)

    def _generate_order(self, edb: "Edb", side: float, center=(0.0, 0.0), current=1):
        """Recursively add metallisation and voids up to the target order."""
        if current > self.order:
            return
        # Draw the metal triangle for current order
        pts = self._sierpinski_vertices(side, center)
        edb.modeler.create_polygon(self.layer, "ANT", pts)

        if current < self.order:
            half = side / 2
            midpoints = [
                (center[0], center[1] + side * math.sqrt(3) / 6),
                (center[0] - half / 2, center[1] - side * math.sqrt(3) / 12),
                (center[0] + half / 2, center[1] - side * math.sqrt(3) / 12),
            ]
            for mp in midpoints:
                self._generate_order(edb, side / 2, mp, current + 1)
                self._subtract_triangle(edb, side / 2, mp)

    def create(self, edb_path: str) -> "Edb":
        import os

        if os.path.exists(edb_path):
            from pyedb import Edb

            edb = Edb(edb_path)
        else:
            from pyedb import Edb

            edb = Edb()
            edb.save_edb_as(edb_path)

        # Expose parameters
        edb["size"] = self.triangle_size
        edb["order"] = self.order

        # Build geometry
        self._generate_order(edb, self.triangle_size)

        # Coax feed at the centroid
        edb.padstacks.create(
            [0, 0], drill=0.3e-3, pad=0.5e-3, start_layer=self.layer, stop_layer=self.via_layer, net="FEED"
        )

        return edb
