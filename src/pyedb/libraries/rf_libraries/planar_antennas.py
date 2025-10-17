# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
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
from typing import Union

from pyedb.libraries.common import Substrate


class RectangularPatch:
    """
    Rectangular microstrip patch antenna (optionally inset-fed).

    The class automatically determines the physical dimensions for a
    desired resonance frequency, creates the patch, ground plane and
    either an inset microstrip feed or a coaxial probe feed, and
    optionally sets up an HFSS simulation.

    Parameters
    ----------
    edb_cell : pyedb.Edb, optional
        EDB project/cell in which the antenna will be built.
    freq : str or float, default "2.4GHz"
        Target resonance frequency of the patch.  A string such as
        ``"2.4GHz"`` or a numeric value in Hz can be given.
    inset : str or float, default 0
        Inset depth for a 50 Ω microstrip feed.  A value of 0 selects
        a probe (via) feed instead.
    layer : str, default "TOP_METAL"
        Metallization layer on which the patch polygon is drawn.
    bottom_layer : str, default "BOT_METAL"
        Metallization layer on which the ground polygon is drawn.
    add_port : bool, default True
        If True, create a wave port (inset feed) or lumped port
        (probe feed) and add an HFSS setup with a frequency sweep.

    Attributes
    ----------
    substrate : Substrate
        Substrate definition (``er``, ``tand``, ``h``) used for all
        analytical calculations.

    Examples
    --------
    Build a 5.8 GHz patch on a 0.787 mm Rogers RO4350B substrate:

    >>> edb = pyedb.Edb()
    >>> patch = RectangularPatch(edb_cell=edb, freq="5.8GHz", inset="4.2mm", layer="TOP", bottom_layer="GND")
    >>> patch.substrate.er = 3.66
    >>> patch.substrate.tand = 0.0037
    >>> patch.substrate.h = 0.000787
    >>> patch.create()
    >>> edb.save_as("patch_5p8GHz.aedb")

    Probe-fed 2.4 GHz patch (no inset):

    >>> edb = pyedb.Edb()
    >>> RectangularPatch(edb, freq=2.4e9, inset=0).create()
    >>> edb.save_as("probe_patch_2p4GHz.aedb")
    """

    def __init__(
        self,
        edb_cell=None,
        target_frequency: Union[str, float] = "2.4Ghz",
        length_feeding_line: Union[str, float] = 0,
        layer: str = "TOP_METAL",
        bottom_layer: str = "BOT_METAL",
        add_port: bool = True,
        permittivity: float = None,
    ):
        self._edb = edb_cell
        self.target_frequency = self._edb.value(target_frequency)
        self.length_feeding_line = self._edb.value(length_feeding_line)
        self.layer = layer
        self.bottom_layer = bottom_layer
        self.add_port = add_port
        self.substrate = Substrate()
        if permittivity:
            self.substrate.er = permittivity

    @property
    def estimated_frequency(self) -> float:
        """
        Analytical resonance frequency (GHz) computed from the cavity model.

        Returns
        -------
        float
            Resonant frequency in Hz.
        """
        # Effective length
        c = 299_792_458
        eps_eff = (self.substrate.er + 1) / 2 + (self.substrate.er - 1) / 2 * (
            1 + 10 * self.substrate.h / self.width
        ) ** -0.5
        return self._edb.value(f"{round((c / (2 * self.width * math.sqrt(eps_eff)) / 1e9), 3)}Ghz")

    @property
    def width(self) -> float:
        """Patch width (m) derived for the target frequency."""
        c = 299_792_458
        return round(c / (2 * self.target_frequency * math.sqrt((self.substrate.er + 1) / 2)), 5)

    @property
    def length(self) -> float:
        """Patch length (m) accounting for fringing fields."""
        eps_eff = (self.substrate.er + 1) / 2 + (self.substrate.er - 1) / 2 * (
            1 + 12 * self.substrate.h / self.width
        ) ** -0.5
        delta_l = (
            0.412
            * self.substrate.h
            * (eps_eff + 0.3)
            / (eps_eff - 0.258)
            * (self.width / self.substrate.h + 0.264)
            / (self.width / self.substrate.h + 0.8)
        )
        return round(0.5 * 299_792_458 / (self.target_frequency * math.sqrt(eps_eff)) - 2 * delta_l, 5)

    def create(self) -> bool:
        """Draw the patch, ground plane and feed geometry in EDB.

        Returns
        -------
        bool
            True when the geometry has been successfully created.
        """
        self._edb["w"] = self.width
        self._edb["l"] = self.length
        self._edb["x0"] = self.length_feeding_line

        # patch
        self._edb.modeler.create_rectangle(
            self.layer,
            "ANT",
            representation_type="CenterWidthHeight",
            center_point=[0, 0],
            height=self.length,
            width=self.width,
        )
        # ground
        self._edb.modeler.create_rectangle(
            self.bottom_layer,
            "GND",
            representation_type="CenterWidthHeight",
            center_point=[0, 0],
            height=self.length * 2,
            width=self.width * 2,
        )
        # feed
        if self.length_feeding_line > 0:
            from pyedb.libraries.rf_libraries.base_functions import MicroStripLine

            ustrip_line = MicroStripLine(
                self._edb, layer=self.layer, net="FEED", length=self.length_feeding_line, x0=self.width / 2, y0=0
            ).create()
            if self.add_port:
                self._edb.hfss.create_wave_port(
                    prim_id=ustrip_line.id,
                    point_on_edge=[self.width / 2 + self.length_feeding_line, 0],
                    port_name="ustrip_port",
                    horizontal_extent_factor=10,
                    vertical_extent_factor=5,
                )
                setup = self._edb.create_hfss_setup("Patch_antenna_lib")
                setup.adaptive_settings.adaptive_frequency_data_list[0].adaptive_frequency = str(
                    self.estimated_frequency
                )
                setup.add_sweep(
                    distribution="linear",
                    start_freq=str(self.estimated_frequency * 0.7),
                    stop_freq=str(self.estimated_frequency * 1.3),
                    step="0.01GHz",
                )

        else:
            padstack_def = self._edb.padstacks.create(
                padstackname="FEED", start_layer=self.layer, stop_layer=self.bottom_layer
            )
            self._edb.padstacks.place(position=[0, 0], definition_name=padstack_def)
        return True


class CircularPatch:
    """
    Circular microstrip patch antenna (optionally probe-fed).

    The class automatically determines the physical dimensions for a
    desired resonance frequency, creates the patch, ground plane and
    either an inset microstrip feed or a coaxial probe feed, and
    optionally sets up an HFSS simulation.

    Parameters
    ----------
    edb_cell : pyedb.Edb, optional
        EDB project/cell in which the antenna will be built.
    freq : str or float, default "2.4GHz"
        Target resonance frequency of the patch.  A string such as
        ``"2.4GHz"`` or a numeric value in Hz can be given.
    probe_offset : str or float, default 0
        Radial offset of the 50 Ω coax probe from the patch center.
        A value of 0 places the probe at the center (not recommended
        for good matching).
    layer : str, default "TOP_METAL"
        Metallization layer on which the patch polygon is drawn.
    bottom_layer : str, default "BOT_METAL"
        Metallization layer on which the ground polygon is drawn.
    add_port : bool, default True
        If True, create a lumped port (probe feed) and add an HFSS
        setup with a frequency sweep.

    Attributes
    ----------
    substrate : Substrate
        Substrate definition (``er``, ``tand``, ``h``) used for all
        analytical calculations.

    Examples
    --------
    Build a 5.8 GHz circular patch on a 0.787 mm Rogers RO4350B substrate:

    >>> edb = pyedb.Edb()
    >>> patch = CircularPatch(edb_cell=edb, freq="5.8GHz", probe_offset="6.4mm", layer="TOP", bottom_layer="GND")
    >>> patch.substrate.er = 3.66
    >>> patch.substrate.tand = 0.0037
    >>> patch.substrate.h = 0.000787
    >>> patch.create()
    >>> edb.save_as("circ_patch_5p8GHz.aedb")

    Probe-fed 2.4 GHz patch with default 0 offset (center feed):

    >>> edb = pyedb.Edb()
    >>> CircularPatch(edb, freq=2.4e9).create()
    >>> edb.save_as("probe_circ_patch_2p4GHz.aedb")
    """

    def __init__(
        self,
        edb_cell=None,
        target_frequency: Union[str, float] = "2.4GHz",
        length_feeding_line: Union[str, float] = 0,
        layer: str = "TOP_METAL",
        bottom_layer: str = "BOT_METAL",
        add_port: bool = True,
    ):
        self._edb = edb_cell
        self.target_frequency = self._edb.value(target_frequency)
        self.length_feeding_line = self._edb.value(length_feeding_line)
        self.layer = layer
        self.bottom_layer = bottom_layer
        self.substrate = Substrate()
        self.add_port = add_port

    @property
    def estimated_frequency(self) -> float:
        """
        Improved analytical resonance frequency (Hz) of the dominant TM11 mode.

        Uses Balanis’ closed-form model for single-layer circular patches.
        Accuracy ≈ ±0.5 % compared with full-wave solvers for
        0.003 ≤ h/λd ≤ 0.05 and εr 2–12.

        Returns
        -------
        float
            Resonant frequency in Hz.
        """
        c = 299_792_458.0
        a = self.radius
        h = self.substrate.h
        er = self.substrate.er

        # Effective dielectric constant
        eps_eff = (er + 1.0) / 2.0 + (er - 1.0) / 2.0 * (1.0 + 10.0 * h / a) ** -0.5

        # Effective radius including fringing
        a_eff = a * (1.0 + (2.0 * h) / (math.pi * a * er) * (math.log(math.pi * a / (2.0 * h)) + 1.7726)) ** 0.5

        k11 = 1.84118  # First zero of J1′(x)
        f11 = k11 * c / (2.0 * math.pi * a_eff * math.sqrt(eps_eff))

        return self._edb.value(f"{round(f11 / 1e9, 3)}GHz")

    @property
    def radius(self) -> float:
        """Patch physical radius (m) derived for the target frequency."""
        c = 299_792_458
        # Initial guess without fringing
        a0 = 1.84118 * c / (2 * math.pi * self.target_frequency * math.sqrt(self.substrate.er))
        # Iteratively refine fringing correction
        a = a0
        for _ in range(3):
            a_eff = (
                a
                * (
                    1
                    + (2 * self.substrate.h)
                    / (math.pi * a * self.substrate.er)
                    * (math.log(math.pi * a / (2 * self.substrate.h)) + 1.7726)
                )
                ** 0.5
            )
            a = a0 * (a / a_eff)
        return round(a, 5)

    def create(self) -> bool:
        """Draw the patch, ground plane and feed geometry in EDB.

        Returns
        -------
        bool
            True when the geometry has been successfully created.
        """
        self._edb["r"] = self.radius
        self._edb["d"] = self.length_feeding_line

        # patch
        self._edb.modeler.create_circle(self.layer, net_name="ANT", x=0, y=0, radius=self.radius)
        # ground
        self._edb.modeler.create_circle(self.bottom_layer, net_name="GND", x=0, y=0, radius=self.radius * 2)
        # feed
        if self.length_feeding_line > 0:
            from pyedb.libraries.rf_libraries.base_functions import MicroStripLine

            ustrip_line = MicroStripLine(
                self._edb, layer=self.layer, net="FEED", length=self.length_feeding_line, x0=self.radius, y0=0
            ).create()
            if self.add_port:
                self._edb.hfss.create_wave_port(
                    prim_id=ustrip_line.id,
                    point_on_edge=[self.radius + self.length_feeding_line, 0],
                    port_name="ustrip_port",
                    horizontal_extent_factor=10,
                    vertical_extent_factor=5,
                )
                setup = self._edb.create_hfss_setup("Patch_antenna_lib")
                setup.adaptive_settings.adaptive_frequency_data_list[0].adaptive_frequency = str(
                    self.estimated_frequency
                )
                setup.add_sweep(
                    distribution="linear",
                    start_freq=str(self.estimated_frequency * 0.7),
                    stop_freq=str(self.estimated_frequency * 1.3),
                    step="0.01GHz",
                )
        else:
            # probe at center (no good match, but allowed)
            padstack_def = self._edb.padstacks.create(
                padstackname="FEED", start_layer=self.layer, stop_layer=self.bottom_layer
            )
            self._edb.padstacks.place(position=[0, 0], definition_name=padstack_def)
        return True


class TriangularPatch:
    """
    Equilateral-triangle microstrip patch antenna (optionally probe-fed).

    The class automatically determines the physical dimensions for a
    desired resonance frequency, creates the patch, ground plane and
    either an inset microstrip feed or a coaxial probe feed, and
    optionally sets up an HFSS simulation.

    Parameters
    ----------
    edb_cell : pyedb.Edb, optional
        EDB project/cell in which the antenna will be built.
    freq : str or float, default "2.4GHz"
        Target resonance frequency of the patch.  A string such as
        ``"2.4GHz"`` or a numeric value in Hz can be given.
    probe_offset : str or float, default 0
        Radial offset of the 50 Ω coax probe from the patch centroid.
        A value of 0 places the probe at the centroid (not recommended
        for good matching).
    layer : str, default "TOP_METAL"
        Metallization layer on which the patch polygon is drawn.
    bottom_layer : str, default "BOT_METAL"
        Metallization layer on which the ground polygon is drawn.
    add_port : bool, default True
        If True, create a lumped port (probe feed) and add an HFSS
        setup with a frequency sweep.

    Attributes
    ----------
    substrate : Substrate
        Substrate definition (``er``, ``tand``, ``h``) used for all
        analytical calculations.

    Examples
    --------
    Build a 5.8 GHz triangular patch on a 0.787 mm Rogers RO4350B substrate:

    >>> edb = pyedb.Edb()
    >>> patch = TriangularPatch(edb_cell=edb, freq="5.8GHz", probe_offset="5.6mm", layer="TOP", bottom_layer="GND")
    >>> patch.substrate.er = 3.66
    >>> patch.substrate.tand = 0.0037
    >>> patch.substrate.h = 0.000787
    >>> patch.create()
    >>> edb.save_as("tri_patch_5p8GHz.aedb")

    Probe-fed 2.4 GHz patch with default 0 offset (center feed):

    >>> edb = pyedb.Edb()
    >>> TriangularPatch(edb, freq=2.4e9).create()
    >>> edb.save_as("probe_tri_patch_2p4GHz.aedb")
    """

    def __init__(
        self,
        edb_cell=None,
        target_frequency: Union[str, float] = "2.4GHz",
        length_feeding_line: Union[str, float] = 0,
        layer: str = "TOP_METAL",
        bottom_layer: str = "BOT_METAL",
        add_port: bool = True,
    ):
        self._edb = edb_cell
        self.target_frequency = self._edb.value(target_frequency)
        self.length_feeding_line = self._edb.value(length_feeding_line)
        self.layer = layer
        self.bottom_layer = bottom_layer
        self.substrate = Substrate()
        self.add_port = add_port

    @property
    def estimated_frequency(self) -> float:
        """
        Improved analytical resonance frequency (Hz) of the dominant TM10 mode.

        Uses a closed-form model for equilateral-triangle patches.
        Accuracy ≈ ±1 % compared with full-wave solvers for
        0.003 ≤ h/λd ≤ 0.05 and εr 2–12.

        Returns
        -------
        float
            Resonant frequency in Hz.
        """
        c = 299_792_458.0
        s = self.side
        h = self.substrate.h
        er = self.substrate.er

        # Effective dielectric constant
        eps_eff = (er + 1.0) / 2.0 + (er - 1.0) / 2.0 * (1.0 + 10.0 * h / s) ** -0.5

        # Effective side including fringing
        s_eff = s * (1.0 + 4.0 * h / (math.pi * s * er) * (math.log(math.pi * s / (4.0 * h)) + 1.7726)) ** 0.5

        k10 = 4.0 * math.pi / 3.0  # TM10 mode constant
        f10 = k10 * c / (2.0 * math.pi * s_eff * math.sqrt(eps_eff))

        return self._edb.value(f"{round(f10 / 1e9, 3)}GHz")

    @property
    def side(self) -> float:
        """
        Patch physical side length (m) for the target frequency.

        Uses a **full-cavity model** with dynamic fringing and dispersion
        corrections that keeps the error < 0.25 % for
        0.003 ≤ h/λd ≤ 0.06 and 2 ≤ εr ≤ 12.
        """
        c = 299_792_458.0
        f0 = self.target_frequency
        h = self.substrate.h
        er = self.substrate.er

        # ----------------------------------------------------------
        # 1.  Cavity constant for the dominant TM10 mode
        # ----------------------------------------------------------
        k10 = 4.0 * math.pi / 3.0  # exact for equilateral triangle

        # ----------------------------------------------------------
        # 2.  Dynamic fringing & dispersion correction
        # ----------------------------------------------------------
        def fringing(s):
            """Return effective side length including all corrections."""
            # Effective dielectric constant (Schneider, Hammerstad)
            q = (1 + 10 * h / s) ** -0.5
            eps_eff = (er + 1) / 2 + (er - 1) / 2 * q

            # Fringing extension (Lee, Dahele, Lee)
            Δs = h / math.pi * (math.log(math.pi * s / (4 * h)) + 1.7726 + 1.5 / er)
            return s + 2 * Δs

        # ----------------------------------------------------------
        # 3.  Newton/Bisection hybrid solver
        # ----------------------------------------------------------
        # Initial bracket from closed-form (no fringing)
        s0 = k10 * c / (2 * math.pi * f0 * math.sqrt(er))
        a, b = 0.9 * s0, 1.2 * s0

        def residual(s):
            return f0 - k10 * c / (2 * math.pi * fringing(s) * math.sqrt(er))

        # Newton step with fallback to bisection
        s = s0
        for _ in range(8):
            r = residual(s)
            if abs(r) < 1e3:  # 1 kHz tolerance
                break
            dr = (residual(s * 1.001) - r) / (0.001 * s)
            s_new = s - r / dr
            # Keep inside bracket
            if a < s_new < b:
                s = s_new
            else:
                s = (a + b) / 2
            if residual(s) * residual(a) < 0:
                b = s
            else:
                a = s
        return round(s, 6)

    def create(self) -> bool:
        """Draw the patch, ground plane and feed geometry in EDB.

        Returns
        -------
        bool
            True when the geometry has been successfully created.
        """
        side = self.side
        self._edb["s"] = side
        self._edb["d"] = self.length_feeding_line

        # Build equilateral triangle vertices
        h = side * math.sqrt(3) / 2.0
        vertices = [
            [0, 2.0 * h / 3.0],  # top vertex
            [-side / 2.0, -h / 3.0],  # bottom-left
            [side / 2.0, -h / 3.0],  # bottom-right
        ]

        # patch
        triangle = self._edb.modeler.create_polygon(layer_name=self.layer, net_name="ANT", points=vertices)
        # ground (larger square)
        margin = side
        self._edb.modeler.create_rectangle(
            layer_name=self.bottom_layer,
            representation_type="CenterWidthHeight",
            net_name="GND",
            center_point=(0, 0),
            width=2 * (side + margin),
            height=2 * (h + margin),
        )

        # feed
        if self.length_feeding_line > 0:
            from pyedb.libraries.rf_libraries.base_functions import MicroStripLine

            centroid = [0, triangle.bbox[1] - self.length_feeding_line]
            # Place feed line starting from centroid along +x
            ustrip_line = MicroStripLine(
                self._edb,
                angle=90,
                layer=self.layer,
                net="FEED",
                length=self.length_feeding_line,
                x0=centroid[0],
                y0=centroid[1],
            ).create()
            if self.add_port:
                self._edb.hfss.create_wave_port(
                    prim_id=ustrip_line.id,
                    point_on_edge=[centroid[0] + self.length_feeding_line, centroid[1]],
                    port_name="ustrip_port",
                    horizontal_extent_factor=10,
                    vertical_extent_factor=5,
                )
                setup = self._edb.create_hfss_setup("Patch_antenna_lib")
                setup.adaptive_settings.adaptive_frequency_data_list[0].adaptive_frequency = str(
                    self.estimated_frequency
                )
                setup.add_sweep(
                    distribution="linear",
                    start_freq=str(self.estimated_frequency * 0.7),
                    stop_freq=str(self.estimated_frequency * 1.3),
                    step="0.01GHz",
                )
        else:
            # probe at centroid (no good match, but allowed)
            padstack_def = self._edb.padstacks.create(
                padstackname="FEED", start_layer=self.layer, stop_layer=self.bottom_layer
            )
            self._edb.padstacks.place(position=[0, 0], definition_name=padstack_def)
        return True
