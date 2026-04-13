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

from dataclasses import dataclass
import re

from ansys.edb.core.database import ProductIdType as CoreProductIdType

from pyedb.grpc.database.inner.base import ObjBase


@dataclass
class HFSSProductProperty:
    """Represents the HFSS product properties.

    This class encapsulates configuration settings for HFSS simulations, including
    port type, orientation, layer alignment, and extent factors for various dimensions.

    Attributes:
        hfss_type (str): The type of HFSS port (e.g., "Gap", "Wave(coax)"). Default is "Gap".
        orientation (str): The orientation of the port (e.g., "Horizontal", "Vertical"). Default is "".
        layer_alignment (str): The layer alignment setting (e.g., "Upper", "Lower"). Default is "".
        horizontal_extent_factor (float | int): Horizontal extent factor for the port. Default is 0.0.
        vertical_extent_factor (float | int): Vertical extent factor for the port. Default is 0.0.
        radial_extent_factor (float | int): Radial extent factor for the port. Default is 0.0.
        pec_launch_width (str): PEC (Perfect Electric Conductor) launch width. Default is "10um".
        reference_name (str): Reference name for the port. Default is "".
    """
    hfss_type: str = "Gap"
    orientation: str = ""
    layer_alignment: str = ""
    horizontal_extent_factor: float | int = 0.0
    vertical_extent_factor: float | int = 0.0
    radial_extent_factor: float | int = 0.0
    pec_launch_width: str = "10um"
    reference_name: str = ""

    def to_hfss_string(self) -> str:
        """Convert HFSSProductProperty instance into an HFSS configuration string.

        Returns:
            str: A formatted HFSS configuration string with all properties encoded.
        """
        def _fmt_num(val: float) -> str:
            try:
                v = float(val)
            except Exception:
                return str(val)
            # Render as integer when the float is integral
            if v.is_integer():
                return str(int(v))
            return str(v)

        h_val = _fmt_num(self.horizontal_extent_factor)
        v_val = _fmt_num(self.vertical_extent_factor)
        r_val = _fmt_num(self.radial_extent_factor)

        return (
            "HFSS("
            f"'HFSS Type'='{self.hfss_type}', "
            f"Orientation='{self.orientation}', "
            f"'Layer Alignment'='{self.layer_alignment}', "
            f"'Horizontal Extent Factor'='{h_val}', "
            f"'Vertical Extent Factor'='{v_val}', "
            f"'Radial Extent Factor'='{r_val}', "
            f"'PEC Launch Width'='{self.pec_launch_width}', "
            f"ReferenceName='{self.reference_name}'"
            ")"
        )


def parse_hfss_string(s: str | None) -> HFSSProductProperty:
    """Parse an HFSS property string into an HFSSProductProperty object.

    This function extracts configuration settings from a formatted string representation of
    HFSS properties and reconstructs them into a structured object.

    Parameters
    ----------
    s (str | None): A formatted string containing HFSS configuration settings.
        If None, returns an HFSSProductProperty with default values.
        Expected format includes key-value pairs like "'HFSS Type'='value'", etc.,
        and may contain parameters like Orientation, Layer Alignment, extent factors, etc.

    Returns
    -------
    HFSSProductProperty: An object containing the parsed HFSS properties
        with all settings extracted from the input string. If the string is None or any specific
        property is not found, default values are used.
    """
    if s is None:
        return HFSSProductProperty()

    def get(key: str) -> str | None:
        match = re.search(rf"'{re.escape(key)}'='([^']*)'", s)
        return match.group(1) if match else None

    def get_unquoted(key: str) -> str | None:
        match = re.search(rf"{re.escape(key)}='([^']*)'", s)
        return match.group(1) if match else None

    def get_float(key: str, default: float | int) -> float | int:
        val = get(key) or get_unquoted(key)
        try:
            return float(val) if val else default
        except (ValueError, TypeError):
            return default

    defaults = HFSSProductProperty()

    return HFSSProductProperty(
        hfss_type=get("HFSS Type") or defaults.hfss_type,
        orientation=get_unquoted("Orientation") or defaults.orientation,
        layer_alignment=get("Layer Alignment") or defaults.layer_alignment,
        horizontal_extent_factor=get_float("Horizontal Extent Factor", defaults.horizontal_extent_factor),
        vertical_extent_factor=get_float("Vertical Extent Factor", defaults.vertical_extent_factor),
        radial_extent_factor=get_float("Radial Extent Factor", defaults.radial_extent_factor),
        pec_launch_width=get("PEC Launch Width") or defaults.pec_launch_width,
        reference_name=get_unquoted("ReferenceName") or defaults.reference_name,
    )


@dataclass
class HorizontalWavePortProperty:
    """Represents the properties of a horizontal wave port.
    
    This class encapsulates configuration settings for horizontal wave ports used in
    electromagnetic simulations. It stores port characteristics such as type, geometry
    (arms), and associated port names (padstack instances).

    Attributes:
        port_type (str): The type of port. Default is "Pad Port".
        arms (int): The number of arms for the port structure. Default is 2.
        hfss_last_type (int): The last HFSS type identifier. Default is 8.
        port_names (tuple[str, ...]): Tuple of port/via names (padstack instance names) associated
            with this property. Can contain multiple via names (e.g., positive and negative vias).
            Default is an empty tuple.
        horizontal_wave_primary (bool): Whether this is a primary horizontal wave port.
            Default is False.
        is_gap_source (bool): Whether the port is a gap source. Default is True.

    Examples:
        Create with two vias:
        >>> prop = HorizontalWavePortProperty(
        ...     port_type="Pad Port",
        ...     arms=2,
        ...     hfss_last_type=8,
        ...     port_names=("pos_via", "neg_via"),
        ...     horizontal_wave_primary=True,
        ...     is_gap_source=True
        ... )
        >>> print(prop.to_property_string())
        $begin ''
        \tType='Pad Port'
        \tArms=2
        \tHFSSLastType=8
        \tHorizWavePort('pos_via', 'neg_via')
        \tHorizWavePrimary=true
        \tIsGapSource=true
        $end ''
    """

    port_type: str = "Pad Port"
    arms: int = 2
    hfss_last_type: int = 8
    port_names: tuple[str, ...] = ()
    horizontal_wave_primary: bool = False
    is_gap_source: bool = True

    def to_property_string(self) -> str:
        """Convert HorizontalWavePortProperty instance into an interpretable property string.

        Generates a formatted string representation of the horizontal wave port properties,
        including all port names (padstack instances) as a comma-separated list within the
        HorizWavePort(...) section.

        Returns:
            str: A formatted property string with all attributes encoded, suitable for
                storage or transmission.
        """
        lines = [
            "$begin ''",
            f"\tType='{self.port_type}'",
            f"\tArms={self.arms}",
            f"\tHFSSLastType={self.hfss_last_type}",
        ]
        if self.port_names:
            # Ensure port_names is a tuple/list of strings
            if isinstance(self.port_names, str):
                quoted_names = f"'{self.port_names}'"
            else:
                quoted_names = ", ".join(f"'{name}'" for name in self.port_names)
            lines.append(f"\tHorizWavePort({quoted_names})")
        if self.horizontal_wave_primary:
            lines.append("\tHorizWavePrimary=true")
        if self.is_gap_source:
            lines.append("\tIsGapSource=true")
        lines.append("$end ''")
        return "\n".join(lines) + "\n"


def parse_horizontal_wave_port_string(s: str | None) -> HorizontalWavePortProperty:
    """Parse a horizontal wave port property string into a HorizontalWavePortProperty object.

    This function extracts configuration settings from a formatted string representation of
    horizontal wave port properties and reconstructs them into a structured object. It supports
    parsing multiple padstack instance names (vias) from the HorizWavePort section.

    Parameters
    ----------
    s (str | None): A formatted string containing horizontal wave port configuration settings.
        If None, returns a HorizontalWavePortProperty with default values.
        Expected format includes key-value pairs like "Type='value'", "Arms=2", etc.,
        and may contain a "HorizWavePort(...)" section with one or more port/via names.
        Multiple vias are parsed from comma-separated quoted strings, e.g.,
        HorizWavePort('pos_via_name', 'neg_via_name').

    Returns
    -------
    HorizontalWavePortProperty: An object containing the parsed horizontal wave port properties
        with all settings extracted from the input string. The port_names attribute will be
        a tuple containing all parsed via names. If the string is None or any specific
        property is not found, default values are used.

    Examples:
        >>> s = "$begin ''\\n\\tType='Pad Port'\\n\\tArms=2\\n\\tHFSSLastType=8\\n\\tHorizWavePort('via1', 'via2')\\n$end ''\\n"
        >>> prop = parse_horizontal_wave_port_string(s)
        >>> prop.port_names
        ('via1', 'via2')
    """
    if s is None:
        return HorizontalWavePortProperty()

    def get(key: str) -> str | None:
        match = re.search(rf"\b{re.escape(key)}='([^']*)'", s)
        return match.group(1) if match else None

    def get_int(key: str, default: int) -> int:
        match = re.search(rf"\b{re.escape(key)}=(\d+)", s)
        return int(match.group(1)) if match else default

    def get_bool(key: str, default: bool) -> bool:
        match = re.search(rf"\b{re.escape(key)}=(true|false)", s, re.IGNORECASE)
        return match.group(1).lower() == "true" if match else default

    defaults = HorizontalWavePortProperty()
    port_names: tuple[str, ...] = ()
    match = re.search(r"HorizWavePort\((.*?)\)", s)
    if match:
        names = re.findall(r"'([^']*)'", match.group(1))
        port_names = tuple(names)

    return HorizontalWavePortProperty(
        port_type=get("Type") or defaults.port_type,
        arms=get_int("Arms", defaults.arms),
        hfss_last_type=get_int("HFSSLastType", defaults.hfss_last_type),
        port_names=port_names,
        horizontal_wave_primary=get_bool("HorizWavePrimary", defaults.horizontal_wave_primary),
        is_gap_source=get_bool("IsGapSource", defaults.is_gap_source),
    )


@dataclass
class PadstackInstanceMeshingProperty:
    """Represents the padstack instance meshing properties.

    This class encapsulates configuration settings for padstack instance meshing,
    including stack identifier, material type, and meshing settings.

    Attributes:
        sid (int): Stack identifier. Default is 0.
        material (str): Material name for the padstack instance. Default is "".
        meshing_setting (str): Meshing setting or technique (e.g., "Mesh", "Auto"). Default is "".
    """
    sid: int = 0
    material: str = ""
    meshing_setting: str = ""

    def to_property_string(self) -> str:
        """Convert PadstackInstanceMeshingProperty instance into a property string.

        Returns:
            str: A formatted property string with all properties encoded.
        """
        lines = [
            "$begin ''",
            f"\tsid={self.sid}",
            f"\tmat='{self.material}'",
            f"\tvs='{self.meshing_setting}'",
            "$end ''",
        ]
        return "\n".join(lines) + "\n"


def parse_padstack_instance_meshing_string(s: str | None) -> PadstackInstanceMeshingProperty:
    """Parse a padstack instance meshing property string into a PadstackInstanceMeshingProperty object.

    This function extracts configuration settings from a formatted string representation of
    padstack instance meshing properties and reconstructs them into a structured object.

    Parameters
    ----------
    s (str | None): A formatted string containing padstack instance meshing configuration settings.
        If None, returns a PadstackInstanceMeshingProperty with default values.
        Expected format includes key-value pairs like "sid=3", "mat='copper'", "vs='Mesh'", etc.

    Returns
    -------
    PadstackInstanceMeshingProperty: An object containing the parsed padstack instance meshing properties
        with all settings extracted from the input string. If the string is None or any specific
        property is not found, default values are used.
    """
    if s is None:
        return PadstackInstanceMeshingProperty()

    def get(key: str) -> str | None:
        match = re.search(rf"{re.escape(key)}='([^']*)'", s)
        return match.group(1) if match else None

    def get_int(key: str, default: int) -> int:
        match = re.search(rf"{re.escape(key)}=(\d+)", s)
        return int(match.group(1)) if match else default

    defaults = PadstackInstanceMeshingProperty()

    return PadstackInstanceMeshingProperty(
        sid=get_int("sid", defaults.sid),
        material=get("mat") or defaults.material,
        meshing_setting=get("vs") or defaults.meshing_setting,
    )


@dataclass
class PlanarEMProperty:
    """Represents the PlanarEM solver properties.

    This class encapsulates configuration settings for PlanarEM simulations, including
    port type, solver options, and reference handling.

    Attributes:
        port_type (str): The type of port (e.g., "Pad Port Gap Source", "Gap Source"). Default is "Pad Port Gap Source".
        port_solver (bool): Whether to use port solver. Default is True.
        ignore_reference (bool): Whether to ignore reference. Default is False.
    """
    port_type: str = "Pad Port Gap Source"
    port_solver: bool = True
    ignore_reference: bool = False

    def to_property_string(self) -> str:
        """Convert PlanarEMProperty instance into a PlanarEM configuration string.

        Returns:
            str: A formatted PlanarEM configuration string with all properties encoded.
        """
        port_solver_str = "true" if self.port_solver else "false"
        ignore_ref_str = "true" if self.ignore_reference else "false"

        return (
            "PlanarEM("
            f"Type='{self.port_type}', "
            f"PortSolver={port_solver_str}, "
            f"'Ignore Reference'={ignore_ref_str}"
            ")"
        )


def parse_planar_em_string(s: str | None) -> PlanarEMProperty:
    """Parse a PlanarEM property string into a PlanarEMProperty object.

    This function extracts configuration settings from a formatted string representation of
    PlanarEM properties and reconstructs them into a structured object.

    Parameters
    ----------
    s (str | None): A formatted string containing PlanarEM configuration settings.
        If None, returns a PlanarEMProperty with default values.
        Expected format includes key-value pairs like "Type='value'", "PortSolver=true", etc.

    Returns
    -------
    PlanarEMProperty: An object containing the parsed PlanarEM properties
        with all settings extracted from the input string. If the string is None or any specific
        property is not found, default values are used.
    """
    if s is None:
        return PlanarEMProperty()

    def get(key: str) -> str | None:
        match = re.search(rf"{re.escape(key)}='([^']*)'", s)
        return match.group(1) if match else None

    def get_bool(key: str, default: bool) -> bool:
        match = re.search(rf"{re.escape(key)}=(true|false)", s, re.IGNORECASE)
        return match.group(1).lower() == "true" if match else default

    defaults = PlanarEMProperty()

    return PlanarEMProperty(
        port_type=get("Type") or defaults.port_type,
        port_solver=get_bool("PortSolver", defaults.port_solver),
        ignore_reference=get_bool("Ignore Reference", defaults.ignore_reference),
    )


@dataclass
class SiwaveProperty:
    """Represents the SIwave solver properties.

    This class encapsulates configuration settings for SIwave simulations, including
    reference net specification.

    Attributes:
        reference_net (str): The reference net name. Default is an empty string.
    """
    reference_net: str = ""

    def to_property_string(self) -> str:
        """Convert SiwaveProperty instance into a SIwave configuration string.

        Returns:
            str: A formatted SIwave configuration string with all properties encoded.
        """
        return f"SIwave('Reference Net'='{self.reference_net}')"


def parse_siwave_string(s: str | None) -> SiwaveProperty:
    """Parse a SIwave property string into a SiwaveProperty object.

    This function extracts configuration settings from a formatted string representation of
    SIwave properties and reconstructs them into a structured object.

    Parameters
    ----------
    s (str | None): A formatted string containing SIwave configuration settings.
        If None, returns a SiwaveProperty with default values.
        Expected format includes key-value pairs like "'Reference Net'='value'", etc.

    Returns
    -------
    SiwaveProperty: An object containing the parsed SIwave properties
        with all settings extracted from the input string. If the string is None or any specific
        property is not found, default values are used.
    """
    if s is None:
        return SiwaveProperty()

    def get(key: str) -> str | None:
        match = re.search(rf"'{re.escape(key)}'='([^']*)'", s)
        return match.group(1) if match else None

    defaults = SiwaveProperty()

    return SiwaveProperty(
        reference_net=get("Reference Net") or defaults.reference_net,
    )


class LayoutObj(ObjBase):
    """Represents a layout object."""

    def __init__(self, pedb, core):
        super().__init__(pedb, core)

    @property
    def _edb_properties(self):
        p = self.core.get_product_property(CoreProductIdType.DESIGNER, 18)
        return p

    @_edb_properties.setter
    def _edb_properties(self, value):
        self.core.set_product_property(CoreProductIdType.DESIGNER, 18, value)

    @property
    def _hfss_properties(self) -> HFSSProductProperty:
        return parse_hfss_string(self.core.product_solver_option(CoreProductIdType.DESIGNER, "HFSS"))

    @_hfss_properties.setter
    def _hfss_properties(self, value):
        if isinstance(value, HFSSProductProperty):
            self.core.set_product_solver_option(CoreProductIdType.DESIGNER, "HFSS", value.to_hfss_string())

    @property
    def _horizontal_wave_port_properties(self) -> HorizontalWavePortProperty:
        return parse_horizontal_wave_port_string(self.core.get_product_property(CoreProductIdType.DESIGNER, 25))

    @_horizontal_wave_port_properties.setter
    def _horizontal_wave_port_properties(self, value):
        if isinstance(value, HorizontalWavePortProperty):
            self.core.set_product_property(CoreProductIdType.DESIGNER, 25, value.to_property_string())

    @property
    def _padstack_instance_meshing_properties(self) -> PadstackInstanceMeshingProperty:
        return parse_padstack_instance_meshing_string(self.core.get_product_property(CoreProductIdType.DESIGNER, 26))

    @_padstack_instance_meshing_properties.setter
    def _padstack_instance_meshing_properties(self, value):
        if isinstance(value, PadstackInstanceMeshingProperty):
            self.core.set_product_property(CoreProductIdType.DESIGNER, 26, value.to_property_string())

    @property
    def _planar_em_properties(self) -> PlanarEMProperty:
        return parse_planar_em_string(self.core.product_solver_option(CoreProductIdType.DESIGNER, "PlanarEM"))

    @_planar_em_properties.setter
    def _planar_em_properties(self, value):
        if isinstance(value, PlanarEMProperty):
            self.core.set_product_solver_option(CoreProductIdType.DESIGNER, "PlanarEM", value.to_property_string())

    @property
    def _siwave_properties(self) -> SiwaveProperty:
        return parse_siwave_string(self.core.product_solver_option(CoreProductIdType.DESIGNER, "SIwave"))

    @_siwave_properties.setter
    def _siwave_properties(self, value):
        if isinstance(value, SiwaveProperty):
            self.core.set_product_solver_option(CoreProductIdType.DESIGNER, "SIwave", value.to_property_string())

