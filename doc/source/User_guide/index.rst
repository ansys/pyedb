.. _ref_user_guide:

==========
User guide
==========
PyEDB is loading ANSYS EDB in memory meaning non graphically.


.. code:: python

    # Load EDB

    from pyedb.legacy.edb_core.edb import EdbLegacy
    edb_file = pyedb.layout_examples.ANSYS_HSD_v1.aedb
    edb = EdbLegacy(edb_file)

.. toctree::
   :hidden:
   :maxdepth: 3

   loading_layout
   edb_queries
   cutout
   layer_stackup
   create_coax_port_on_component
   get_layout_bounding_box
   create_circuit_ports_on_component
   create_current_source
   create_resistor_on_pin
   add_siwave_analysis
   export_edb_to_hfss
   export_edb_to_q3d
   export_edb_to_maxwell
   create_dc_simulation_setup
   create_rlc_component
   create_coax_port_on_component
   define_hfss_simulation_setup
   create_dc_simulation_setup_2
   create_ac_simulation_setup
   build_ac_project
   create_edge_port_on_polygon
   create_rlc_boundary_on_pins
   create_various_ports
   set_all_antipads_value
   use_design_variables
   create_port_between_pin_and_layer
   delete_pin_group
   create_padsatck_instance
   define_hfss_extent
   define_layer_stackup
   import_gds_file
   create_edb_with_dxf
   build_signal_integrity_project