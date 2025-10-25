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
from typing import TYPE_CHECKING, Literal, Union, overload
import warnings

from pyedb.generic.grpc_warnings import GRPC_GENERAL_WARNING
from pyedb.generic.settings import settings
from pyedb.misc.decorators import deprecate_argument_name

if TYPE_CHECKING:
    from pyedb.dotnet.edb import Edb as EdbDotnet
    from pyedb.grpc.edb import Edb as EdbGrpc


@overload
def Edb(*, grpc: Literal[True], **kwargs) -> "EdbGrpc": ...


@overload
def Edb(*, grpc: Literal[False] = False, **kwargs) -> "EdbDotnet": ...


@overload
def Edb(*, grpc: bool, **kwargs) -> Union["EdbGrpc", "EdbDotnet"]: ...


# lazy imports
@deprecate_argument_name({"edbversion": "version"})
def Edb(
    edbpath=None,
    cellname=None,
    isreadonly=False,
    version=None,
    isaedtowned=False,
    oproject=None,
    student_version=False,
    use_ppe=False,
    map_file=None,
    technology_file=None,
    grpc=False,
    control_file=None,
    layer_filter=None,
):
    """Provides the EDB application interface.

        This module inherits all objects that belong to EDB.

        Parameters
        ----------
        edbpath : str, optional
            Full path to the ``aedb`` folder. The variable can also contain
            the path to a layout to import. Allowed formats are BRD,
            XML (IPC2581), GDS, and DXF. The default is ``None``.
            For GDS import, the Ansys control file (also XML) should have the same
            name as the GDS file. Only the file extension differs.
        cellname : str, optional
            Name of the cell to select. The default is ``None``.
        isreadonly : bool, optional
            Whether to open EBD in read-only mode when it is
            owned by HFSS 3D Layout. The default is ``False``.
        version : str, optional
            Version of EDB to use. The default is ``"2021.2"``.
        isaedtowned : bool, optional
            Whether to launch EDB from HFSS 3D Layout. The
            default is ``False``.
        oproject : optional
            Reference to the AEDT project object.
        student_version : bool, optional
            Whether to open the AEDT student version. The default is ``False.``
        use_ppe : bool, optional
            Whether to use PPE license. The default is ``False``.
        technology_file : str, optional
            Full path to technology file to be converted to xml before importing or xml. Supported by GDS format only.
        grpc : bool, optional
            Whether to enable gRPC. Default value is ``False``.
        layer_filter: str,optional
            Layer filter .txt file.
        map_file : str, optional
            Layer map .map file.
        control_file : str, optional
            Path to the XML file. The default is ``None``, in which case an attempt is made to find
            the XML file in the same directory as the board file. To succeed, the XML file and board file
            must have the same name. Only the extension differs.

        Returns
        -------
        :class:`Edb <pyedb.dotnet.edb.Edb>` or :class:`Edb <pyedb.grpc.edb.Edb>`

        Note
        ----
        PyEDB gRPC will be released starting ANSYS release 2025R2. For legacy purpose, the gRPC will not be activated by
        default. However, PyEDB gRPC will be the lon term supported version. The legacy PyEDB .NET will be deprecated
        and at some point all new features will only be implemented in PyEDB gRPC. We highly encourage users moving to
        gRPC starting release 2025R2, we tried keeping gRPC version backward compatible with legace .NET as much as
        possible and only minor adjustments are required to be compatible.

        Examples
        --------
        1. Creating and Opening an EDB Database

    >>> from pyedb import Edb

        # Create a new EDB instance
    >>> edb = Edb()

        # Open an existing AEDB database
    >>> edb = Edb(edbpath="my_project.aedb")

        # Import a board file (BRD, XML, GDS, etc.)
    >>> edb = Edb(edbpath="my_board.brd")

        2. Cutout Operation

        # Simple cutout with signal and reference nets
    >>> edb.cutout(
    >>>    signal_list=["PCIe", "USB"],
    >>>    reference_list=["GND"]
    >>>    )

        # Advanced cutout with custom parameters
    >>> edb.cutout(
    >>>    signal_list=["DDR"],
    >>>    reference_list=["GND"],
    >>>    extent_type="ConvexHull",
    >>>    expansion_size=0.002,
    >>>    use_round_corner=True,
    >>>    output_aedb_path="cutout.aedb",
    >>>    remove_single_pin_components=True
    >>>    )

        3. Exporting Designs

        # Export to IPC2581 format
    >>> edb.export_to_ipc2581("output.xml", units="millimeter")

        # Export to HFSS project
    >>> edb.export_hfss("hfss_output")

        # Export to Q3D project
    >>> edb.export_q3d("q3d_output", net_list=["PowerNet"])

        # Export to Maxwell project
    >>> edb.export_maxwell("maxwell_output")

        4. Simulation Setup

        # Create SIwave SYZ setup
    >>> syz_setup = edb.create_siwave_syz_setup(name="GHz_Setup", start_freq="1GHz", stop_freq="10GHz")

        # Create SIwave DC setup
    >>> dc_setup = edb.create_siwave_dc_setup(name="DC_Analysis", use_dc_point=True)

        # Solve with SIwave
    >>> edb.solve_siwave()

        5. Database Management

        # Save database
    >>> edb.save()

        # Save as new database
    >>> edb.save_as("new_project.aedb")

        # Close database
    >>> edb.close()

        6. Stackup and Material Operations

        # Access stackup layers
    >>> for layer_name, layer in edb.stackup.layers.items():
    >>> print(f"Layer: {layer_name}, Thickness: {layer.thickness}")

        # Add new material
    >>> edb.materials.add_material("MyMaterial", permittivity=4.3, loss_tangent=0.02)

        # Change layer thickness
    >>> edb.stackup["TopLayer"].thickness = "0.035mm"

        7. Port Creation

        # Create wave port between two pins
    >>> wave_port = edb.source_excitation.create_port(positive_terminal=pin1, negative_terminal=pin2, port_type="Wave")

        # Create lumped port
    >>> lumped_port = edb.source_excitation.create_port(positive_terminal=via_terminal, port_type="Lumped")

        8. Component Management

        # Delete components by type
    >>> edb.components.delete_component(["R1", "C2"])

        # Set component properties
    >>> edb.components["U1"].set_property("Value", "10nH")

        9. Parametrization

        # Auto-parametrize design elements
    >>> params = edb.auto_parametrize_design(traces=True, pads=True, antipads=True, use_relative_variables=True)
    >>> print("Created parameters:", params)

        10. Design Statistics

        # Get layout statistics with area calculation
    >>> stats = edb.get_statistics(compute_area=True)
    >>> print(f"Total nets: {stats.net_count}")
    >>> print(f"Total components: {stats.component_count}")

        11. Layout Validation

        # Run DRC check
    >>> drc_errors = edb.layout_validation.run_drc()
    >>> print(f"Found {len(drc_errors)} DRC violations")

        12. Differential Pairs

        # Create differential pair
    >>> edb.differential_pairs.create(positive_net="USB_P", negative_net="USB_N", name="USB_DP")

        13. Workflow Automation

        # Define and run workflow
    >>> workflow = edb.workflow
    >>> workflow.add_task("Import", file_path="input.brd")
    >>> workflow.add_task("Cutout", signal_nets=["PCIe"])
    >>> workflow.add_task("Export", format="IPC2581")
    >>> workflow.run()

    """
    settings.is_student_version = student_version
    if grpc is False and settings.edb_dll_path is not None:
        # Check if the user specified a .dll path
        settings.logger.info(f"Force to use .dll from {settings.edb_dll_path} defined in settings.")
    elif version is None:
        if settings.specified_version is not None:
            settings.logger.info(f"Use {settings.specified_version} defined in settings.")
            # Use the latest version
        elif student_version:
            if settings.LATEST_STUDENT_VERSION is None:
                raise RuntimeWarning("AEDT is not properly installed.")
            else:
                settings.specified_version = settings.LATEST_STUDENT_VERSION
        else:
            if settings.LATEST_VERSION is None:
                raise RuntimeWarning("AEDT is not properly installed.")
            else:
                settings.specified_version = settings.LATEST_VERSION
    else:
        # Version is specified
        version = str(version)
        if student_version:
            if version not in settings.INSTALLED_STUDENT_VERSIONS:
                raise RuntimeWarning(f"AEDT student version {version} is not properly installed.")
            else:
                settings.specified_version = version
        else:
            if version not in settings.INSTALLED_VERSIONS:
                raise RuntimeWarning(f"AEDT version {version} is not properly installed.")
            else:
                settings.specified_version = version

    if grpc:
        if float(settings.specified_version) < 2025.2:
            raise ValueError(
                f"gRPC flag was enabled however your ANSYS AEDT version {settings.specified_version} is not compatible"
            )

        from pyedb.grpc.edb import Edb as app

        return app(
            edbpath=edbpath,
            cellname=cellname,
            isreadonly=isreadonly,
            edbversion=version,
            isaedtowned=isaedtowned,
            oproject=oproject,
            use_ppe=use_ppe,
            technology_file=technology_file,
            control_file=control_file,
        )
    else:
        if float(settings.specified_version) >= 2025.2:
            warnings.warn(GRPC_GENERAL_WARNING, UserWarning)

        from pyedb.dotnet.edb import Edb

        return Edb(
            edbpath=edbpath,
            cellname=cellname,
            isreadonly=isreadonly,
            isaedtowned=isaedtowned,
            oproject=oproject,
            use_ppe=use_ppe,
            control_file=control_file,
            map_file=map_file,
            technology_file=technology_file,
            layer_filter=layer_filter,
        )


def Siwave(
    specified_version=None,
):
    """Siwave Class."""
    from pyedb.siwave import Siwave as app

    return app(
        specified_version=specified_version,
    )


app_map = {"EDB": Edb}
