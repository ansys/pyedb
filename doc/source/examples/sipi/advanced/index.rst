Advanced standalone SI/PI examples
====================================

These six workflows use direct PyEDB APIs and require no helper module,
configuration file, Configuration Builder, or automatic-configuration class.
Every example is a complete Python file with command-line inputs.

.. grid:: 2

   .. grid-item-card:: Reduce PCIe Gen5 via-stub impact
      :link: pcie_gen5_backdrill_optimization
      :link-type: doc

      Uses direct padstack queries and dielectric-filled backdrill creation on a protected working copy.

   .. grid-item-card:: Audit DDR5 return-path transitions
      :link: ddr5_return_path_audit
      :link-type: doc

      Finds the nearest reference via for every selected DDR5 signal via and exports a CSV review list.

   .. grid-item-card:: Audit differential-pair physical symmetry
      :link: differential_pair_symmetry_audit
      :link-type: doc

      Compares routed length, layer usage, trace width, via count, padstack definitions, and endpoint components.

   .. grid-item-card:: Prepare a VDD_CORE target-impedance model
      :link: vdd_core_target_impedance_model
      :link-type: doc

      Creates direct circuit ports at the VRM and loads and adds a SIwave setup to a working EDB.

   .. grid-item-card:: Review local decoupling placement
      :link: decoupling_placement_review
      :link-type: doc

      Finds capacitors connected between the selected rail and reference net and measures their proximity to load power pins.

   .. grid-item-card:: Compare HFSS cutout scope strategies
      :link: hfss_cutout_scope_study
      :link-type: doc

      Creates independent Bounding, ConvexHull, and Conforming cutouts and reports retained-object and file-size metrics.

.. toctree::
   :hidden:
   :maxdepth: 1

   pcie_gen5_backdrill_optimization
   ddr5_return_path_audit
   differential_pair_symmetry_audit
   vdd_core_target_impedance_model
   decoupling_placement_review
   hfss_cutout_scope_study
