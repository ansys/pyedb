Import GDS file
===============
This section describes how to import GDS file using control file.
Files and location must be adapted by the user.

.. autosummary::
   :toctree: _autosummary

.. code:: python


    # these example shows how to work with GDS file,.

    from pyedb.legacy.edb_core.edb import EdbLegacy
    from pyedb.legacy.edb_core.edb_data.control_file import ControlFile
    c_file_in = os.path.join(
            local_path, "example_models", "cad", "GDS", "sky130_fictitious_dtc_example_control_no_map.xml"
        )
    target_location = r"C:\Temp"
    c_map = os.path.join(local_path, "example_models", "cad", "GDS", "dummy_layermap.map")
    gds_in = os.path.join(local_path, "example_models", "cad", "GDS", "sky130_fictitious_dtc_example.gds")
    gds_out = os.path.join(target_location, "sky130_fictitious_dtc_example.gds")
    pyedb.legacy.misc.copyfile(gds_in, gds_out)

    c = ControlFile(c_file_in, layer_map=c_map)
    setup = c.setups.add_setup("Setup1", "1GHz")
    setup.add_sweep("Sweep1", "0.01GHz", "5GHz", "0.1GHz")
    c.boundaries.units = "um"
    c.stackup.units = "um"
    c.boundaries.add_port("P1", x1=223.7, y1=222.6, layer1="Metal6", x2=223.7, y2=100, layer2="Metal6")
    c.boundaries.add_extent()
    comp = c.components.add_component("B1", "BGA", "IC", "Flip chip", "Cylinder")
    comp.solder_diameter = "65um"
    comp.add_pin("1", "81.28", "84.6", "met2")
    comp.add_pin("2", "211.28", "84.6", "met2")
    comp.add_pin("3", "211.28", "214.6", "met2")
    comp.add_pin("4", "81.28", "214.6", "met2")
    for via in c.stackup.vias:
        via.create_via_group = True
        via.snap_via_group = True
    c.write_xml(os.path.join(self.local_scratch.path, "test_138.xml"))
    c.import_options.import_dummy_nets = True
    edb = EdbLegacy(
        gds_out, edbversion=desktop_version, technology_file=os.path.join(self.local_scratch.path, "test_138.xml")
    )

    edb.close()