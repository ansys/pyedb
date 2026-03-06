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

import copy
import os
import re
import subprocess  # nosec B404
import sys
from typing import Any, Dict, List, Optional, Union

from defusedxml.ElementTree import parse as defused_parse

from pyedb.generic.general_methods import ET, env_path, env_value, is_linux
from pyedb.generic.settings import settings
from pyedb.misc.aedtlib_personalib_install import write_pretty_xml
from pyedb.misc.misc import list_installed_ansysem


def convert_technology_file(tech_file, edbversion=None, control_file=None):
    """Convert a technology file to EDB control file (XML).

    .. warning::
        Do not execute this function with untrusted function argument, environment
        variables or pyedb global settings.
        See the :ref:`security guide<ref_security_consideration>` for details.

    Parameters
    ----------
    tech_file : str
        Full path to technology file.
    edbversion : str, optional
        EDB version to use, defaults to ``None``.
        If ``None``, uses latest available version.
    control_file : str, optional
        Output control file path, defaults to ``None``.
        If ``None``, uses same path and name as ``tech_file``.

    Returns
    -------
    str or bool
        Full path to created control file if successful, ``False`` otherwise.

    Example
    -------
    Converting a technology file to control file.

    >>> converted_file = convert_technology_file(
    ...     tech_file="/path/to/tech.t", edbversion="2025.2", control_file="/path/to/output.xml"
    ... )
    >>> if converted_file:
    >>>     print(f"Converted to: {converted_file}")
    """
    if is_linux:  # pragma: no cover
        if not edbversion:
            edbversion = "20{}.{}".format(list_installed_ansysem()[0][-3:-1], list_installed_ansysem()[0][-1:])
        if env_value(edbversion) in os.environ:
            base_path = env_path(edbversion)
            sys.path.append(base_path)
        else:
            settings.logger.error("No EDB installation found. Check environment variables")
            return False
        os.environ["HELIC_ROOT"] = os.path.join(base_path, "helic")
        if os.getenv("ANSYSLMD_LICENCE_FILE", None) is None:
            lic = os.path.join(base_path, "..", "..", "shared_files", "licensing", "ansyslmd.ini")
            if os.path.exists(lic):
                with open(lic, "r") as fh:
                    lines = fh.read().splitlines()
                    for line in lines:
                        if line.startswith("SERVER="):
                            os.environ["ANSYSLMD_LICENSE_FILE"] = line.split("=")[1]
                            break
            else:
                settings.logger.error("ANSYSLMD_LICENSE_FILE is not defined.")
        vlc_file_name = os.path.splitext(tech_file)[0]
        if not control_file:
            control_file = vlc_file_name + ".xml"
        vlc_file = vlc_file_name + ".vlc.tech"
        commands = []
        command = [
            os.path.join(base_path, "helic", "tools", "bin", "afet", "tech2afet"),
            "-i",
            tech_file,
            "-o",
            vlc_file,
            "--backplane",
            "False",
        ]
        commands.append(command)
        command = [
            os.path.join(base_path, "helic", "tools", "raptorh", "bin", "make-edb"),
            "--dielectric-simplification-method",
            "1",
            "-t",
            vlc_file,
            "-o",
            vlc_file_name,
            "--export-xml",
            control_file,
        ]
        commands.append(command)
        commands.append(["rm", "-r", vlc_file_name + ".aedb"])
        for command in commands:
            try:
                subprocess.run(command, check=True)  # nosec
            except subprocess.CalledProcessError as e:  # nosec
                raise RuntimeError("An error occurred while converting a technology file to edb control file") from e
        if os.path.exists(control_file):
            settings.logger.info("XML file created.")
            return control_file
    settings.logger.error("Technology files are supported only in Linux. Use control file instead.")
    return False


class ControlProperty:
    """Property in the control file.

    This property has a name, value, and type.

    Parameters
    ----------
    property_name : str
        Name of the property.
    value : str, float, or list
        Value of the property.
    """

    def __init__(self, property_name: str, value: str | float | list) -> None:
        self.name: str = property_name
        self.value: str | float | list = value
        self.type: int = self.__get_type(value)

    def __get_type(self, value: Any) -> int:
        """Determine the type of the property value."""
        if isinstance(value, str):
            return 1
        elif isinstance(value, list):
            return 2
        else:
            try:
                float(value)
                return 0
            except (TypeError, ValueError):
                return -1

    def _write_xml(self, root: ET.Element) -> None:
        """Write the property to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        try:
            if self.type == 0:
                content = ET.SubElement(root, self.name)
                double = ET.SubElement(content, "Double")
                double.text = str(self.value)
            else:
                pass
        except Exception as e:
            settings.logger.error(
                f"A(n) {type(e).__name__} error occurred while attempting to create a new sub-element {self.name} "
                f"for element {root}: {str(e)}"
            )


class ControlFileMaterial:
    """Material in the control file.

    Parameters
    ----------
    name : str
        Material name.
    properties : dict
        Material properties dictionary.
    """

    def __init__(self, name: str, properties: dict[str, Any]) -> None:
        self.name: str = name
        self.properties: dict[str, ControlProperty] = {
            name: ControlProperty(name, prop) for name, prop in properties.items()
        }

    def _write_xml(self, root: ET.Element) -> None:
        """Write material to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "Material")
        content.set("Name", self.name)
        for property in self.properties.values():
            property._write_xml(content)


class ControlFileDielectric:
    """Dielectric layer in the control file.

    Parameters
    ----------
    name : str
        Layer name.
    properties : dict
        Layer properties dictionary.
    """

    def __init__(self, name: str, properties: dict[str, Any]) -> None:
        self.name: str = name
        self.properties: dict[str, Any] = {name: prop for name, prop in properties.items()}

    def _write_xml(self, root: ET.Element) -> None:
        """Write dielectric layer to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "Layer")
        for property_name, property in self.properties.items():
            if not property_name == "Index":
                content.set(property_name, str(property))


class ControlFileLayer:
    """General layer in the control file.

    Parameters
    ----------
    name : str
        Layer name.
    properties : dict
        Layer properties dictionary.
    """

    def __init__(self, name: str, properties: dict[str, Any]) -> None:
        self.name = name
        self.properties: dict[str, Any] = {name: prop for name, prop in properties.items()}

    def _write_xml(self, root: ET.Element) -> None:
        """Write layer to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "Layer")
        content.set("Color", self.properties.get("Color", "#5c4300"))
        if self.properties.get("Elevation"):
            content.set("Elevation", self.properties["Elevation"])
        if self.properties.get("GDSDataType"):
            content.set("GDSDataType", self.properties["GDSDataType"])
        if self.properties.get("GDSIIVia") or self.properties.get("GDSDataType"):
            content.set("GDSIIVia", self.properties.get("GDSIIVia", "false"))
        if self.properties.get("Material"):
            content.set("Material", self.properties.get("Material", "air"))
        content.set("Name", self.name)
        if self.properties.get("StartLayer"):
            content.set("StartLayer", self.properties["StartLayer"])
        if self.properties.get("StopLayer"):
            content.set("StopLayer", self.properties["StopLayer"])
        if self.properties.get("TargetLayer"):
            content.set("TargetLayer", self.properties["TargetLayer"])
        if self.properties.get("Thickness"):
            content.set("Thickness", self.properties.get("Thickness", "0.001"))
        if self.properties.get("Type"):
            content.set("Type", self.properties.get("Type", "conductor"))


class ControlFileVia(ControlFileLayer):
    """Via layer in the control file.

    Parameters
    ----------
    name : str
        Via name.
    properties : dict
        Via properties dictionary.

    """

    def __init__(self, name: str, properties: Dict[str, Any]) -> None:
        super().__init__(name, properties)
        self.create_via_group: bool = False
        self.check_containment: bool = True
        self.method: str = "proximity"
        self.persistent: bool = False
        self.tolerance: str = "1um"
        self.snap_via_groups: bool = False
        self.snap_method: str = "areaFactor"
        self.remove_unconnected: bool = True
        self.snap_tolerance: int = 3

    def _write_xml(self, root: ET.Element) -> None:
        """Write via to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "Layer")
        content.set("Color", self.properties.get("Color", "#5c4300"))
        if self.properties.get("Elevation"):
            content.set("Elevation", self.properties["Elevation"])
        if self.properties.get("GDSDataType"):
            content.set("GDSDataType", self.properties["GDSDataType"])
        if self.properties.get("Material"):
            content.set("Material", self.properties.get("Material", "air"))
        content.set("Name", self.name)
        content.set("StartLayer", self.properties.get("StartLayer", ""))
        content.set("StopLayer", self.properties.get("StopLayer", ""))
        if self.properties.get("TargetLayer"):
            content.set("TargetLayer", self.properties["TargetLayer"])
        if self.properties.get("Thickness"):
            content.set("Thickness", self.properties.get("Thickness", "0.001"))
        if self.properties.get("Type"):
            content.set("Type", self.properties.get("Type", "conductor"))
        if self.create_via_group:
            viagroup = ET.SubElement(content, "CreateViaGroups")
            viagroup.set("CheckContainment", "true" if self.check_containment else "false")
            viagroup.set("Method", self.method)
            viagroup.set("Persistent", "true" if self.persistent else "false")
            viagroup.set("Tolerance", self.tolerance)
        if self.snap_via_groups:
            snapgroup = ET.SubElement(content, "SnapViaGroups")
            snapgroup.set("Method", self.snap_method)
            snapgroup.set("RemoveUnconnected", "true" if self.remove_unconnected else "false")
            snapgroup.set("Tolerance", str(self.snap_tolerance))


class ControlFileStackup:
    """Stackup information for the control file.

    Parameters
    ----------
    units : str, optional
        Length units (e.g., "mm", "um"). Default is "mm".
    """

    def __init__(self, units: str = "mm") -> None:
        self._materials: dict[str, ControlFileMaterial] = {}
        self._layers: list[ControlFileLayer] = []
        self._dielectrics: list[Any] = []
        self._vias: list[ControlFileVia] = []
        self.units: str = units
        self.metal_layer_snapping_tolerance: float | None = None
        self.dielectrics_base_elevation: float = 0.0

    @property
    def vias(self) -> list[ControlFileVia]:
        """List of via objects.

        Returns
        -------
        list
            List of ControlFileVia objects.
        """
        return self._vias

    @property
    def materials(self) -> dict[str, ControlFileMaterial]:
        """Dictionary of material objects.

        Returns
        -------
        dict
            Dictionary of material names to ControlFileMaterial objects.
        """
        return self._materials

    @property
    def dielectrics(self) -> list[ControlFileDielectric]:
        """List of dielectric layers.

        Returns
        -------
        list
            List of ControlFileDielectric objects.
        """
        return self._dielectrics

    @property
    def layers(self) -> list[ControlFileLayer]:
        """List of general layers.

        Returns
        -------
        list
            List of ControlFileLayer objects.
        """
        return self._layers

    def add_material(
        self,
        material_name: str,
        permittivity: float = 1.0,
        dielectric_loss_tg: float = 0.0,
        permeability: float = 1.0,
        conductivity: float = 0.0,
        properties: dict[str, Any] | None = None,
    ) -> ControlFileMaterial:
        """Add a new material.

        Parameters
        ----------
        material_name : str
            Material name.
        permittivity : float, optional
            Relative permittivity. Default is ``1.0``.
        dielectric_loss_tg : float, optional
            Dielectric loss tangent. Default is ``0.0``.
        permeability : float, optional
            Relative permeability. Default is ``1.0``.
        conductivity : float, optional
            Conductivity (S/m). Default is ``0.0``.
        properties : dict[str, Any], optional
            Additional material properties. Overrides default parameters.

        Returns
        -------
        ControlFileMaterial
            Created material object.
        """
        if isinstance(properties, dict):
            cfm = ControlFileMaterial(material_name, properties)
        else:
            properties = {
                "Name": material_name,
                "Permittivity": permittivity,
                "Permeability": permeability,
                "Conductivity": conductivity,
                "DielectricLossTangent": dielectric_loss_tg,
            }
            cfm = ControlFileMaterial(material_name, properties)
        self._materials[material_name] = cfm
        return cfm

    def add_layer(
        self,
        layer_name: str,
        elevation: float = 0.0,
        material: str = "",
        gds_type: int = 0,
        target_layer: str = "",
        thickness: float = 0.0,
        layer_type: str = "conductor",
        solve_inside: bool = True,
        properties: dict[str, Any] | None = None,
    ) -> ControlFileLayer:
        """Add a new layer.

        Parameters
        ----------
        layer_name : str
            Layer name.
        elevation : float
            Layer elevation (Z-position). Default is ``0.0``.
        material : str
            Material name. Default is ``""``.
        gds_type : int
            GDS data type for layer. Default is ``0``.
        target_layer : str
            Target layer name in EDB/HFSS. Default is ``""``.
        thickness : float
            Layer thickness. Default is ``0.0``.
        layer_type : str, optional
            Layer type ("conductor", "signal", etc.). Default is "conductor".
        solve_inside : bool, optional
            Whether to solve inside metal. Default is ``True``.
        properties : dict, optional
            Additional layer properties. Overrides default parameters.

        Returns
        -------
        ControlFileLayer
            Created layer object.
        """
        if isinstance(properties, dict):
            cfl = ControlFileLayer(layer_name, properties)
        else:
            properties = {
                "Name": layer_name,
                "GDSDataType": str(gds_type),
                "TargetLayer": target_layer,
                "Type": layer_type,
                "Material": material,
                "Thickness": str(thickness),
                "Elevation": str(elevation),
                "SolveInside": str(solve_inside).lower(),
            }
            cfl = ControlFileDielectric(layer_name, properties)
        self._layers.append(cfl)
        return cfl

    def add_dielectric(
        self,
        layer_name: str,
        layer_index: int | None = None,
        material: str = "",
        thickness: float = 0.0,
        properties: dict[str, Any] | None = None,
        base_layer: str | None = None,
        add_on_top: bool = True,
    ) -> ControlFileDielectric:
        """Add a new dielectric layer.

        Parameters
        ----------
        layer_name : str
            Dielectric layer name.
        layer_index : int, optional
            Stacking order index. Default is ``None`` (auto-assigned).
        material : str
            Material name. Default is ``""``.
        thickness : float
            Layer thickness. Default is ``0.0``.
        properties : dict, optional
            Additional properties to override default parameters.
            Default is ``None``.
        base_layer : str, optional
            Existing layer name for relative placement. Default is ``None``.
        add_on_top : bool, optional
            Whether to add on top of base layer. Default is ``True``.

        Returns
        -------
        ControlFileDielectric
            Created dielectric layer object.
        """
        if isinstance(properties, dict):
            cfd = ControlFileDielectric(layer_name, properties)
        else:
            if not layer_index and self.dielectrics and not base_layer:
                layer_index = max([diel.properties["Index"] for diel in self.dielectrics]) + 1
            elif base_layer and self.dielectrics:
                if base_layer in [diel.properties["Name"] for diel in self.dielectrics]:
                    base_layer_index = next(
                        diel.properties["Index"] for diel in self.dielectrics if diel.properties["Name"] == base_layer
                    )
                    if add_on_top:
                        layer_index = base_layer_index + 1
                        for diel_layer in self.dielectrics:
                            if diel_layer.properties["Index"] > base_layer_index:
                                diel_layer.properties["Index"] += 1
                    else:
                        layer_index = base_layer_index
                        for diel_layer in self.dielectrics:
                            if diel_layer.properties["Index"] >= base_layer_index:
                                diel_layer.properties["Index"] += 1
            elif not layer_index:
                layer_index = 0
            properties = {"Index": layer_index, "Material": material, "Name": layer_name, "Thickness": thickness}
            cfd = ControlFileDielectric(layer_name, properties)
        self._dielectrics.append(cfd)
        return cfd

    def add_via(
        self,
        layer_name: str,
        material: str = "",
        gds_type: int = 0,
        target_layer: str = "",
        start_layer: str = "",
        stop_layer: str = "",
        solve_inside: bool = True,
        via_group_method: str = "proximity",
        via_group_tol: float = 1e-6,
        via_group_persistent: bool = True,
        snap_via_group_method: str = "distance",
        snap_via_group_tol: float = 10e-9,
        properties: dict[str, Any] | None = None,
    ) -> ControlFileVia:
        """Add a new via layer.

        Parameters
        ----------
        layer_name : str
            Via layer name.
        material : str
            Material name. Default is ``""``.
        gds_type : int
            GDS data type for via layer. Default is ``0``.
        target_layer : str
            Target layer name in EDB/HFSS. Default is ``""``.
        start_layer : str
            Starting layer name. Default is ``""``.
        stop_layer : str
            Stopping layer name. Default is ``""``.
        solve_inside : bool
            Whether to solve inside via. Default is ``True``.
        via_group_method : str
            Via grouping method. Default is "proximity".
        via_group_tol : float, optional
            Via grouping tolerance. Default is 1e-6.
        via_group_persistent : bool, optional
            Whether via groups are persistent. Default is ``True``.
        snap_via_group_method : str, optional
            Snap via group method. Default is "distance".
        snap_via_group_tol : float, optional
            Snap via group tolerance. Default is 10e-9.
        properties : dict, optional
            Additional properties. Overrides default parameters.

        Returns
        -------
        ControlFileVia
            Created via object.
        """
        if isinstance(properties, dict):
            cfv = ControlFileVia(layer_name, properties)
        else:
            properties = {
                "Name": layer_name,
                "GDSDataType": str(gds_type),
                "TargetLayer": target_layer,
                "Material": material,
                "StartLayer": start_layer,
                "StopLayer": stop_layer,
                "SolveInside": str(solve_inside).lower(),
                "ViaGroupMethod": via_group_method,
                "Persistent": via_group_persistent,
                "ViaGroupTolerance": via_group_tol,
                "SnapViaGroupMethod": snap_via_group_method,
                "SnapViaGroupTolerance": snap_via_group_tol,
            }
            cfv = ControlFileVia(layer_name, properties)
        self._vias.append(cfv)
        return cfv

    def _write_xml(self, root: ET.Element) -> None:
        """Write stackup to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "Stackup")
        content.set("schemaVersion", "1.0")
        materials = ET.SubElement(content, "Materials")
        for _, material in self.materials.items():
            material._write_xml(materials)
        elayers = ET.SubElement(content, "ELayers")
        elayers.set("LengthUnit", self.units)
        if self.metal_layer_snapping_tolerance:
            elayers.set("MetalLayerSnappingTolerance", str(self.metal_layer_snapping_tolerance))
        dielectrics = ET.SubElement(elayers, "Dielectrics")
        dielectrics.set("BaseElevation", str(self.dielectrics_base_elevation))
        # sorting dielectric layers
        self._dielectrics = list(sorted(list(self._dielectrics), key=lambda x: x.properties["Index"], reverse=False))
        for layer in self.dielectrics:
            layer._write_xml(dielectrics)
        layers = ET.SubElement(elayers, "Layers")

        for layer in self.layers:
            layer._write_xml(layers)
        vias = ET.SubElement(elayers, "Vias")

        for layer in self.vias:
            layer._write_xml(vias)


class ControlFileImportOptions:
    """Import options for the control file."""

    def __init__(self) -> None:
        self.auto_close: bool = False
        self.convert_closed_wide_lines_to_polys: bool = False
        self.round_to: int = 0
        self.defeature_tolerance: float = 0.0
        self.flatten: bool = True
        self.enable_default_component_values: bool = True
        self.import_dummy_nets: bool = False
        self.gdsii_convert_polygon_to_circles: bool = False
        self.import_cross_hatch_shapes_as_lines: bool = True
        self.max_antipad_radius: float = 0.0
        self.extracta_use_pin_names: bool = False
        self.min_bondwire_width: float = 0.0
        self.antipad_replace_radius: float = 0.0
        self.gdsii_scaling_factor: float = 0.0
        self.delete_empty_non_laminate_signal_layers: bool = False

    def _write_xml(self, root: ET.Element) -> bool:
        """Write control file to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.

        Returns
        -------
        bool
            True if XML content was written successfully.
        """

        content = ET.SubElement(root, "ImportOptions")
        content.set("AutoClose", str(self.auto_close).lower())
        if self.round_to != 0:
            content.set("RoundTo", str(self.round_to))
        if self.defeature_tolerance != 0.0:
            content.set("DefeatureTolerance", str(self.defeature_tolerance))
        content.set("Flatten", str(self.flatten).lower())
        content.set("EnableDefaultComponentValues", str(self.enable_default_component_values).lower())
        content.set("ImportDummyNet", str(self.import_dummy_nets).lower())
        content.set("GDSIIConvertPolygonToCircles", str(self.convert_closed_wide_lines_to_polys).lower())
        content.set("ImportCrossHatchShapesAsLines", str(self.import_cross_hatch_shapes_as_lines).lower())
        content.set("ExtractaUsePinNames", str(self.extracta_use_pin_names).lower())
        if self.max_antipad_radius != 0.0:
            content.set("MaxAntiPadRadius", str(self.max_antipad_radius))
        if self.antipad_repalce_radius != 0.0:
            content.set("AntiPadReplaceRadius", str(self.antipad_repalce_radius))
        if self.min_bondwire_width != 0.0:
            content.set("MinBondwireWidth", str(self.min_bondwire_width))
        if self.gdsii_scaling_factor != 0.0:
            content.set("GDSIIScalingFactor", str(self.gdsii_scaling_factor))
        content.set("DeleteEmptyNonLaminateSignalLayers", str(self.delte_empty_non_laminate_signal_layers).lower())
        return True


class ControlExtent:
    """Extent options for boundaries for the control file..

    Parameters
    ----------
    type : str, optional
        Extent type. Default is ``"bbox"``.
    dieltype : str, optional
        Dielectric extent type. Default is ``"bbox"``.
    diel_hactor : float, optional
        Dielectric horizontal factor. Default is ``0.25``.
    airbox_hfactor : float, optional
        Airbox horizontal factor. Default is ``0.25``.
    airbox_vr_p : float, optional
        Airbox vertical factor (positive). Default is ``0.25``.
    airbox_vr_n : float, optional
        Airbox vertical factor (negative). Default is ``0.25``.
    useradiation : bool, optional
        Use radiation boundary. Default is ``True``.
    honor_primitives : bool, optional
        Honor primitives. Default is ``True``.
    truncate_at_gnd : bool, optional
        Truncate at ground. Default is ``True``.
    """

    def __init__(
        self,
        type: str = "bbox",
        dieltype: str = "bbox",
        diel_hactor: float = 0.25,
        airbox_hfactor: float = 0.25,
        airbox_vr_p: float = 0.25,
        airbox_vr_n: float = 0.25,
        useradiation: bool = True,
        honor_primitives: bool = True,
        truncate_at_gnd: bool = True,
    ) -> None:
        self.type: str = type
        self.dieltype: str = dieltype
        self.diel_hactor: float = diel_hactor
        self.airbox_hfactor: float = airbox_hfactor
        self.airbox_vr_p: float = airbox_vr_p
        self.airbox_vr_n: float = airbox_vr_n
        self.useradiation: bool = useradiation
        self.honor_primitives: bool = honor_primitives
        self.truncate_at_gnd: bool = truncate_at_gnd

    def _write_xml(self, root: ET.Element) -> None:
        """Write extent options to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "Extents")
        content.set("Type", self.type)
        content.set("DielType", self.dieltype)
        content.set("DielHorizFactor", str(self.diel_hactor))
        content.set("AirboxHorizFactor", str(self.airbox_hfactor))
        content.set("AirboxVertFactorPos", str(self.airbox_vr_p))
        content.set("AirboxVertFactorNeg", str(self.airbox_vr_n))
        content.set("UseRadiationBoundary", str(self.useradiation).lower())
        content.set("DielHonorPrimitives", str(self.honor_primitives).lower())
        content.set("AirboxTruncateAtGround", str(self.truncate_at_gnd).lower())


class ControlCircuitPt:
    """Circuit port for the control file.

    Parameters
    ----------
    name : str
        Port name.
    x1 : float
        X-coordinate of the first point.
    y1 : float
        Y-coordinate of first point.
    lay1 : str
        Layer of the first point.
    x2 : float
        X-coordinate of the second point.
    y2 : float
        Y-coordinate of the second point.
    lay2 : str
        Layer of the second point.
    z0 : float
        Characteristic impedance.
    """

    def __init__(self, name, x1, y1, lay1, x2, y2, lay2, z0):
        self.name: str = name
        self.x1: float = x1
        self.x2: float = x2
        self.lay1: str = lay1
        self.lay2: str = lay2
        self.y1: float = y1
        self.y2: float = y2
        self.z0: float = z0

    def _write_xml(self, root: ET.Element) -> None:
        """Write circuit port to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "CircuitPortPt")
        content.set("Name", self.name)
        content.set("x1", self.x1)
        content.set("y1", self.y1)
        content.set("Layer1", self.lay1)
        content.set("x2", self.x2)
        content.set("y2", self.y2)
        content.set("Layer2", self.lay2)
        content.set("Z0", self.z0)


class ControlFileComponent:
    """Component in the control file."""

    def __init__(self) -> None:
        self.refdes: str = "U1"
        self.partname: str = "BGA"
        self.parttype: str = "IC"
        self.die_type: str = "None"
        self.die_orientation: str = "Chip down"
        self.solderball_shape: str = "None"
        self.solder_diameter: str = "65um"
        self.solder_height: str = "65um"
        self.solder_material: str = "solder"
        self.pins: list[dict[str, str | float]] = []
        self.ports: list[dict[str, str | float | None]] = []

    def add_pin(self, name: str, x: float, y: float, layer: str) -> None:
        """Add a pin to the component.

        Parameters
        ----------
        name : str
            Pin name.
        x : float
            X-coordinate.
        y : float
            Y-coordinate.
        layer : str
            Layer name.
        """
        self.pins.append({"Name": name, "x": x, "y": y, "Layer": layer})

    def add_port(
        self,
        name: str,
        z0: float,
        pospin: str,
        refpin: Optional[str] = None,
        pos_type: str = "pin",
        ref_type: str = "pin",
    ) -> None:
        """Add a port to the component.

        Parameters
        ----------
        name : str
            Port name.
        z0 : float
            Characteristic impedance.
        pospin : str
            Positive pin/group name.
        refpin : str, optional
            Reference pin/group name.
        pos_type : str, optional
            Positive element type ("pin" or "pingroup"). Default is ``"pin"``.
        ref_type : str, optional
            Reference element type ("pin", "pingroup", or "net"). Default is ``"pin"``.
        """
        args = {"Name": name, "Z0": z0}
        if pos_type == "pin":
            args["PosPin"] = pospin
        elif pos_type == "pingroup":
            args["PosPinGroup"] = pospin
        if refpin:
            if ref_type == "pin":
                args["RefPin"] = refpin
            elif ref_type == "pingroup":
                args["RefPinGroup"] = refpin
            elif ref_type == "net":
                args["RefNet"] = refpin
        self.ports.append(args)

    def _write_xml(self, root: ET.Element) -> None:
        """Write component to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "GDS_COMPONENT")
        for p in self.pins:
            prop = ET.SubElement(content, "GDS_PIN")
            for pname, value in p.items():
                prop.set(pname, value)

        prop = ET.SubElement(content, "Component")
        prop.set("RefDes", self.refdes)
        prop.set("PartName", self.partname)
        prop.set("PartType", self.parttype)
        prop2 = ET.SubElement(prop, "DieProperties")
        prop2.set("Type", self.die_type)
        prop2.set("Orientation", self.die_orientation)
        prop2 = ET.SubElement(prop, "SolderballProperties")
        prop2.set("Shape", self.solderball_shape)
        prop2.set("Diameter", self.solder_diameter)
        prop2.set("Height", self.solder_height)
        prop2.set("Material", self.solder_material)
        for p in self.ports:
            prop = ET.SubElement(prop, "ComponentPort")
            for pname, value in p.items():
                prop.set(pname, value)


class ControlFileComponents:
    """Manage components for the control file."""

    def __init__(self):
        self.units: str = "um"
        self.components: list[ControlFileComponent] = []

    def add_component(
        self, ref_des: str, partname: str, component_type: str, die_type: str = "None", solderball_shape: str = "None"
    ) -> ControlFileComponent:
        """Add a new component.

        Parameters
        ----------
        ref_des : str
            Reference designator.
        partname : str
            Part name.
        component_type : str
            Component type ("IC", "IO", or "Other").
        die_type : str, optional
            Die type ("None", "Flip chip", or "Wire bond"). Default is ``"None"``.
        solderball_shape : str, optional
            Solderball shape ("None", "Cylinder", or "Spheroid"). Default is ``"None"``.

        Returns
        -------
        ControlFileComponent
            Created component object.
        """
        comp = ControlFileComponent()
        comp.refdes = ref_des
        comp.partname = partname
        comp.parttype = component_type
        comp.die_type = die_type
        comp.solderball_shape = solderball_shape
        self.components.append(comp)
        return comp


class ControlFileBoundaries:
    """Boundaries for the control file.

    Parameters
    ----------
    units : str, optional
        Length units. Default is ``"um"``.
    """

    # FIXME: Commented circui_models and circuit_elements since they are never defined.
    def __init__(self, units: str = "um") -> None:
        self.ports: dict[str, ControlCircuitPt] = {}
        self.extents: list[ControlExtent] = []
        # self.circuit_models: dict[str, Any] = {}
        # self.circuit_elements: dict[str, Any] = {}
        self.units: str = units

    def add_port(
        self, name: str, x1: float, y1: float, layer1: str, x2: float, y2: float, layer2: str, z0: float = 50
    ) -> ControlCircuitPt:
        """Add a port.

        Parameters
        ----------
        name : str
            Port name.
        x1 : float
            X-coordinate of the first point.
        y1 : float
            Y-coordinate of the first point.
        layer1 : str
            Layer of the first point.
        x2 : float
            X-coordinate of the second point.
        y2 : float
            Y-coordinate of the second point.
        layer2 : str
            Layer of the second point.
        z0 : float, optional
            Characteristic impedance. Default is ``50``.

        Returns
        -------
        ControlCircuitPt
            Created port object.
        """
        ccp = ControlCircuitPt(name, str(x1), str(y1), layer1, str(x2), str(y2), layer2, str(z0))
        self.ports[name] = ccp
        return ccp

    def add_extent(
        self,
        type: str = "bbox",
        dieltype: str = "bbox",
        diel_hactor: float = 0.25,
        airbox_hfactor: float = 0.25,
        airbox_vr_p: float = 0.25,
        airbox_vr_n: float = 0.25,
        useradiation: bool = True,
        honor_primitives: bool = True,
        truncate_at_gnd: bool = True,
    ) -> ControlExtent:
        """Add an extent.

        Parameters
        ----------
        type : str, optional
            Extent type. Default is ``"bbox"``.
        dieltype : str, optional
            Dielectric extent type. Default is ``"bbox"``.
        diel_hactor : float, optional
            Dielectric horizontal factor. Default is ``0.25``.
        airbox_hfactor : float, optional
            Airbox horizontal factor. Default is ``0.25``.
        airbox_vr_p : float, optional
            Airbox vertical factor (positive). Default is ``0.25``.
        airbox_vr_n : float, optional
            Airbox vertical factor (negative). Default is ``0.25``.
        useradiation : bool, optional
            Use radiation boundary. Default is ``True``.
        honor_primitives : bool, optional
            Honor primitives. Default is ``True``.
        truncate_at_gnd : bool, optional
            Truncate at ground. Default is ``True``.

        Returns
        -------
        ControlExtent
            Created extent object.
        """
        ce = ControlExtent(
            type=type,
            dieltype=dieltype,
            diel_hactor=diel_hactor,
            airbox_hfactor=airbox_hfactor,
            airbox_vr_p=airbox_vr_p,
            airbox_vr_n=airbox_vr_n,
            useradiation=useradiation,
            honor_primitives=honor_primitives,
            truncate_at_gnd=truncate_at_gnd,
        )
        self.extents.append(ce)
        return ce

    # FIXME: Commented circui_models and circuit_elements since they are never defined.
    def _write_xml(self, root: ET.Element) -> None:
        """Write boundaries to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "Boundaries")
        content.set("LengthUnit", self.units)
        # for p in self.circuit_models.values():
        #     p._write_xml(content)
        # for p in self.circuit_elements.values():
        #     p._write_xml(content)
        for p in self.ports.values():
            p._write_xml(content)
        for p in self.extents:
            p._write_xml(content)


class ControlFileSweep:
    """Frequency sweep in the control file.

    Parameters
    ----------
    name : str
        Sweep name.
    start : str
        Start frequency.
    stop : str
        Stop frequency.
    step : str
        Frequency step/count.
    sweep_type : str
        Sweep type ("Discrete" or "Interpolating").
    step_type : str
        Step type ("LinearStep", "DecadeCount", or "LinearCount").
    use_q3d : bool
        Whether to use Q3D for DC point.
    """

    def __init__(
        self, name: str, start: str, stop: str, step: str, sweep_type: str, step_type: str, use_q3d: bool
    ) -> None:
        self.name: str = name
        self.start: str = start
        self.stop: str = stop
        self.step: str = step
        self.sweep_type: str = sweep_type
        self.step_type: str = step_type
        self.use_q3d: bool = use_q3d

    def _write_xml(self, root: ET.Element) -> None:
        """Write sweep to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        sweep = ET.SubElement(root, "FreqSweep")
        prop = ET.SubElement(sweep, "Name")
        prop.text = self.name
        prop = ET.SubElement(sweep, "UseQ3DForDC")
        prop.text = str(self.use_q3d).lower()
        prop = ET.SubElement(sweep, self.sweep_type)
        prop2 = ET.SubElement(prop, self.step_type)
        prop3 = ET.SubElement(prop2, "Start")
        prop3.text = self.start
        prop3 = ET.SubElement(prop2, "Stop")
        prop3.text = self.stop
        if self.step_type == "LinearStep":
            prop3 = ET.SubElement(prop2, "Step")
            prop3.text = str(self.step)
        else:
            prop3 = ET.SubElement(prop2, "Count")
            prop3.text = str(self.step)


class ControlFileMeshOp:
    """Mesh operation in the control file.

    Parameters
    ----------
    name : str
        Operation name.
    region : str
        Region name.
    type : str
        Operation type ("MeshOperationLength" or "MeshOperationSkinDepth").
    nets_layers : dict
        Dictionary of nets and layers.
    """

    def __init__(self, name: str, region: str, type: str, nets_layers: dict[str, str]) -> None:
        self.name: str = name
        self.region: str = region
        self.type: str = type
        self.nets_layers: Dict[str, str] = nets_layers
        self.num_max_elem: int = 1000
        self.restrict_elem: bool = False
        self.restrict_length: bool = True
        self.max_length: str = "20um"
        self.skin_depth: str = "1um"
        self.surf_tri_length: str = "1mm"
        self.num_layers: int = 2
        self.region_solve_inside: bool = False

    def _write_xml(self, root: ET.Element) -> None:
        """Write mesh operation to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        mop = ET.SubElement(root, "MeshOperation")
        prop = ET.SubElement(mop, "Name")
        prop.text = self.name
        prop = ET.SubElement(mop, "Enabled")
        prop.text = "true"
        prop = ET.SubElement(mop, "Region")
        prop.text = self.region
        prop = ET.SubElement(mop, "Type")
        prop.text = self.type
        prop = ET.SubElement(mop, "NetsLayers")
        for net, layer in self.nets_layers.items():
            prop2 = ET.SubElement(prop, "NetsLayer")
            prop3 = ET.SubElement(prop2, "Net")
            prop3.text = net
            prop3 = ET.SubElement(prop2, "Layer")
            prop3.text = layer
        prop = ET.SubElement(mop, "RestrictElem")
        prop.text = self.restrict_elem
        prop = ET.SubElement(mop, "NumMaxElem")
        prop.text = self.num_max_elem
        if self.type == "MeshOperationLength":
            prop = ET.SubElement(mop, "RestrictLength")
            prop.text = self.restrict_length
            prop = ET.SubElement(mop, "MaxLength")
            prop.text = self.max_length
        else:
            prop = ET.SubElement(mop, "SkinDepth")
            prop.text = self.skin_depth
            prop = ET.SubElement(mop, "SurfTriLength")
            prop.text = self.surf_tri_length
            prop = ET.SubElement(mop, "NumLayers")
            prop.text = self.num_layers
        prop = ET.SubElement(mop, "RegionSolveInside")
        prop.text = self.region_solve_inside


class ControlFileSetup:
    """Simulation setup for the control file.

    Parameters
    ----------
    name : str
        Setup name.
    """

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.enabled: bool = True
        self.save_fields: bool = False
        self.save_rad_fields: bool = False
        self.frequency: str = "1GHz"
        self.maxpasses: int = 10
        self.max_delta: float = 0.02
        self.union_polygons: bool = True
        self.small_voids_area: int = 0
        self.mode_type: str = "IC"
        self.ic_model_resolution: str = "Auto"
        self.order_basis: str = "FirstOrder"
        self.solver_type: str = "Auto"
        self.low_freq_accuracy: bool = False
        self.mesh_operations: list[ControlFileMeshOp] = []
        self.sweeps: list[ControlFileSweep] = []

    def add_sweep(
        self,
        name: str,
        start: str,
        stop: str,
        step: str,
        sweep_type: str = "Interpolating",
        step_type: str = "LinearStep",
        use_q3d: bool = True,
    ) -> ControlFileSweep:
        """Add a frequency sweep.

        Parameters
        ----------
        name : str
            Sweep name.
        start : str
            Start frequency.
        stop : str
            Stop frequency.
        step : str
            Frequency step/count.
        sweep_type : str, optional
            Sweep type ("Discrete" or "Interpolating"). Default is ``"Interpolating"``.
        step_type : str, optional
            Step type ("LinearStep", "DecadeCount", or "LinearCount"). Default is ``"LinearStep"``.
        use_q3d : bool, optional
            Whether to use Q3D for DC point. Default is ``True``.

        Returns
        -------
        ControlFileSweep
            Created sweep object.
        """
        sweep = ControlFileSweep(name, start, stop, step, sweep_type, step_type, use_q3d)
        self.sweeps.append(sweep)
        return sweep

    def add_mesh_operation(self, name: str, region: str, type: str, nets_layers: dict[str, str]) -> ControlFileMeshOp:
        """Add a mesh operation.

        Parameters
        ----------
        name : str
            Operation name.
        region : str
            Region name.
        type : str
            Operation type ("MeshOperationLength" or "MeshOperationSkinDepth").
        nets_layers : dict
            Dictionary of nets and layers.

        Returns
        -------
        ControlFileMeshOp
            Created mesh operation object.
        """
        mop = ControlFileMeshOp(name, region, type, nets_layers)
        self.mesh_operations.append(mop)
        return mop

    def _write_xml(self, root: ET.Element) -> None:
        """Write setup to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        setups = ET.SubElement(root, "HFSSSetup")
        setups.set("schemaVersion", "1.0")
        setups.set("Name", self.name)
        setup = ET.SubElement(setups, "HFSSSimulationSettings")
        prop = ET.SubElement(setup, "Enabled")
        prop.text = str(self.enabled).lower()
        prop = ET.SubElement(setup, "SaveFields")
        prop.text = str(self.save_fields).lower()
        prop = ET.SubElement(setup, "SaveRadFieldsOnly")
        prop.text = str(self.save_rad_fields).lower()
        prop = ET.SubElement(setup, "HFSSAdaptiveSettings")
        prop = ET.SubElement(prop, "AdaptiveSettings")
        prop = ET.SubElement(prop, "SingleFrequencyDataList")
        prop = ET.SubElement(prop, "AdaptiveFrequencyData")
        prop2 = ET.SubElement(prop, "AdaptiveFrequency")
        prop2.text = self.frequency
        prop2 = ET.SubElement(prop, "MaxPasses")
        prop2.text = str(self.maxpasses)
        prop2 = ET.SubElement(prop, "MaxDelta")
        prop2.text = str(self.max_delta)
        prop = ET.SubElement(setup, "HFSSDefeatureSettings")
        prop2 = ET.SubElement(prop, "UnionPolygons")
        prop2.text = str(self.union_polygons).lower()

        prop2 = ET.SubElement(prop, "SmallVoidArea")
        prop2.text = str(self.small_voids_area)
        prop2 = ET.SubElement(prop, "ModelType")
        prop2.text = str(self.mode_type)
        prop2 = ET.SubElement(prop, "ICModelResolutionType")
        prop2.text = str(self.ic_model_resolution)

        prop = ET.SubElement(setup, "HFSSSolverSettings")
        prop2 = ET.SubElement(prop, "OrderBasis")
        prop2.text = str(self.order_basis)
        prop2 = ET.SubElement(prop, "SolverType")
        prop2.text = str(self.solver_type)
        prop = ET.SubElement(setup, "HFSSMeshOperations")
        for mesh in self.mesh_operations:
            mesh._write_xml(prop)
        prop = ET.SubElement(setups, "HFSSSweepDataList")
        for sweep in self.sweeps:
            sweep._write_xml(prop)


class ControlFileSetups:
    """Manage simulation setups."""

    def __init__(self):
        self.setups: list[ControlFileSetup] = []

    def add_setup(self, name: str, frequency: str) -> ControlFileSetup:
        """Add a simulation setup.

        Parameters
        ----------
        name : str
            Setup name.
        frequency : str
            Adaptive frequency.

        Returns
        -------
        ControlFileSetup
            Created setup object.
        """
        setup = ControlFileSetup(name)
        setup.frequency = frequency
        self.setups.append(setup)
        return setup

    def _write_xml(self, root: ET.Element) -> None:
        """Write setups to XML element.

        Parameters
        ----------
        root : xml.etree.ElementTree.Element
            Parent XML element to append to.
        """
        content = ET.SubElement(root, "SimulationSetups")
        for setup in self.setups:
            setup._write_xml(content)


class ControlFile:
    """Main class for EDB control file creation and management.

    Parameters
    ----------
    xml_input : str, optional
        Path to existing XML file to parse.
    tecnhology : str, optional
        Path to technology file to convert.
    layer_map : str, optional
        Path to layer map file.
    """

    def __init__(
        self, xml_input: str | None = None, technology: str | None = None, layer_map: str | None = None
    ) -> None:
        self.stackup = ControlFileStackup()
        if xml_input:
            self.parse_xml(xml_input)
        if technology:
            self.parse_technology(technology)
        if layer_map:
            self.parse_layer_map(layer_map)
        self.boundaries = ControlFileBoundaries()
        self.remove_holes = False
        self.remove_holes_area_minimum = 30
        self.remove_holes_units = "um"
        self.setups = ControlFileSetups()
        self.components = ControlFileComponents()
        self.import_options = ControlFileImportOptions()

    def parse_technology(self, tecnhology: str, edbversion: str | None = None) -> None:
        """Parse a technology file and convert to an XML control file.

        Parameters
        ----------
        tecnhology : str
            Path to technology file.
        edbversion : str, optional
            EDB version to use for conversion.
        """
        xml_temp = os.path.splitext(tecnhology)[0] + "_temp.xml"
        xml_temp = convert_technology_file(tech_file=tecnhology, edbversion=edbversion, control_file=xml_temp)
        if xml_temp:
            return self.parse_xml(xml_temp)

    def parse_layer_map(self, layer_map: str) -> None:
        """Parse a layer map file and update stackup.

        Parameters
        ----------
        layer_map : str
            Path to layer map file.
        """
        with open(layer_map, "r") as f:
            lines = f.readlines()
            for line in lines:
                if not line.startswith("#") and re.search(r"\w+", line.strip()):
                    out = re.split(r"\s+", line.strip())
                    layer_name = out[0]
                    layer_id = out[2]
                    layer_type = out[3]
                    for layer in self.stackup.layers[:]:
                        if layer.name == layer_name:
                            layer.properties["GDSDataType"] = layer_type
                            layer.name = layer_id
                            layer.properties["TargetLayer"] = layer_name
                            break
                        elif layer.properties.get("TargetLayer", None) == layer_name:
                            new_layer = ControlFileLayer(layer_id, copy.deepcopy(layer.properties))
                            new_layer.properties["GDSDataType"] = layer_type
                            new_layer.name = layer_id
                            new_layer.properties["TargetLayer"] = layer_name
                            self.stackup.layers.append(new_layer)
                            break
                    for layer in self.stackup.vias[:]:
                        if layer.name == layer_name:
                            layer.properties["GDSDataType"] = layer_type
                            layer.name = layer_id
                            layer.properties["TargetLayer"] = layer_name
                            break
                        elif layer.properties.get("TargetLayer", None) == layer_name:
                            new_layer = ControlFileVia(layer_id, copy.deepcopy(layer.properties))
                            new_layer.properties["GDSDataType"] = layer_type
                            new_layer.name = layer_id
                            new_layer.properties["TargetLayer"] = layer_name
                            self.stackup.vias.append(new_layer)
                            self.stackup.vias.append(new_layer)
                            break

    def parse_xml(self, xml_input: str) -> None:
        """Parse an XML control file and populate the object.

        Parameters
        ----------
        xml_input : str
            Path to XML control file.
        """
        tree = defused_parse(xml_input)
        root = tree.getroot()
        for el in root:
            if el.tag == "Stackup":
                for st_el in el:
                    if st_el.tag == "Materials":
                        for mat in st_el:
                            mat_name = mat.attrib["Name"]
                            properties = {}
                            for prop in mat:
                                if prop[0].tag == "Double":
                                    properties[prop.tag] = prop[0].text
                            self.stackup.add_material(mat_name, properties)
                    elif st_el.tag == "ELayers":
                        if st_el.attrib == "LengthUnits":
                            self.stackup.units = st_el.attrib
                        for layers_el in st_el:
                            if "BaseElevation" in layers_el.attrib:
                                self.stackup.dielectrics_base_elevation = layers_el.attrib["BaseElevation"]
                            for layer_el in layers_el:
                                properties = {}
                                layer_name = layer_el.attrib["Name"]
                                for propname, prop_val in layer_el.attrib.items():
                                    properties[propname] = prop_val
                                if layers_el.tag == "Dielectrics":
                                    self.stackup.add_dielectric(
                                        layer_name=layer_name,
                                        material=properties["Material"],
                                        thickness=properties["Thickness"],
                                    )
                                elif layers_el.tag == "Layers":
                                    self.stackup.add_layer(layer_name=layer_name, properties=properties)
                                elif layers_el.tag == "Vias":
                                    via = self.stackup.add_via(layer_name, properties=properties)
                                    for i in layer_el:
                                        if i.tag == "CreateViaGroups":
                                            via.create_via_group = True
                                            if "CheckContainment" in i.attrib:
                                                via.check_containment = (
                                                    True if i.attrib["CheckContainment"] == "true" else False
                                                )
                                            if "Tolerance" in i.attrib:
                                                via.tolerance = i.attrib["Tolerance"]
                                            if "Method" in i.attrib:
                                                via.method = i.attrib["Method"]
                                            if "Persistent" in i.attrib:
                                                via.persistent = True if i.attrib["Persistent"] == "true" else False
                                        elif i.tag == "SnapViaGroups":
                                            if "Method" in i.attrib:
                                                via.snap_method = i.attrib["Method"]
                                            if "Tolerance" in i.attrib:
                                                via.snap_tolerance = i.attrib["Tolerance"]
                                            if "RemoveUnconnected" in i.attrib:
                                                via.remove_unconnected = (
                                                    True if i.attrib["RemoveUnconnected"] == "true" else False
                                                )

    def write_xml(self, xml_output):
        """Write control file to XML.

        Parameters
        ----------
        xml_output : str
            Output XML file path.

        Returns
        -------
        bool
            ``True`` if file created successfully, ``False`` otherwise.
        """
        control = ET.Element("{http://www.ansys.com/control}Control", attrib={"schemaVersion": "1.0"})
        self.stackup._write_xml(control)
        if self.boundaries.ports or self.boundaries.extents:
            self.boundaries._write_xml(control)
        if self.remove_holes:
            hole = ET.SubElement(control, "RemoveHoles")
            hole.set("HoleAreaMinimum", str(self.remove_holes_area_minimum))
            hole.set("LengthUnit", self.remove_holes_units)
        if self.setups.setups:
            setups = ET.SubElement(control, "SimulationSetups")
            for setup in self.setups.setups:
                setup._write_xml(setups)
        self.import_options._write_xml(control)
        if self.components.components:
            comps = ET.SubElement(control, "GDS_COMPONENTS")
            comps.set("LengthUnit", self.components.units)
            for comp in self.components.components:
                comp._write_xml(comps)
        write_pretty_xml(control, xml_output)
        return True if os.path.exists(xml_output) else False
