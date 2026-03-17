src.pyedb.generic.control_file
==============================

.. py:module:: src.pyedb.generic.control_file


Classes
-------

.. autoapisummary::

   src.pyedb.generic.control_file.ControlProperty
   src.pyedb.generic.control_file.ControlFileMaterial
   src.pyedb.generic.control_file.ControlFileDielectric
   src.pyedb.generic.control_file.ControlFileLayer
   src.pyedb.generic.control_file.ControlFileVia
   src.pyedb.generic.control_file.ControlFileStackup
   src.pyedb.generic.control_file.ControlFileImportOptions
   src.pyedb.generic.control_file.ControlExtent
   src.pyedb.generic.control_file.ControlCircuitPt
   src.pyedb.generic.control_file.ControlFileComponent
   src.pyedb.generic.control_file.ControlFileComponents
   src.pyedb.generic.control_file.ControlFileBoundaries
   src.pyedb.generic.control_file.ControlFileSweep
   src.pyedb.generic.control_file.ControlFileMeshOp
   src.pyedb.generic.control_file.ControlFileSetup
   src.pyedb.generic.control_file.ControlFileSetups
   src.pyedb.generic.control_file.ControlFile


Functions
---------

.. autoapisummary::

   src.pyedb.generic.control_file.convert_technology_file


Module Contents
---------------

.. py:function:: convert_technology_file(tech_file, edbversion=None, control_file=None)

   Convert a technology file to EDB control file (XML).

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


.. py:class:: ControlProperty(property_name: str, value: str | float | list)

   Property in the control file.

   This property has a name, value, and type.

   Parameters
   ----------
   property_name : str
       Name of the property.
   value : str, float, or list
       Value of the property.


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: value
      :type:  str | float | list


   .. py:attribute:: type
      :type:  int
      :value: 1



.. py:class:: ControlFileMaterial(name: str, properties: dict[str, Any])

   Material in the control file.

   Parameters
   ----------
   name : str
       Material name.
   properties : dict
       Material properties dictionary.


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: properties
      :type:  dict[str, ControlProperty]


.. py:class:: ControlFileDielectric(name: str, properties: dict[str, Any])

   Dielectric layer in the control file.

   Parameters
   ----------
   name : str
       Layer name.
   properties : dict
       Layer properties dictionary.


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: properties
      :type:  dict[str, Any]


.. py:class:: ControlFileLayer(name: str, properties: dict[str, Any])

   General layer in the control file.

   Parameters
   ----------
   name : str
       Layer name.
   properties : dict
       Layer properties dictionary.


   .. py:attribute:: name


   .. py:attribute:: properties
      :type:  dict[str, Any]


.. py:class:: ControlFileVia(name: str, properties: Dict[str, Any])

   Bases: :py:obj:`ControlFileLayer`


   Via layer in the control file.

   Parameters
   ----------
   name : str
       Via name.
   properties : dict
       Via properties dictionary.



   .. py:attribute:: create_via_group
      :type:  bool
      :value: False



   .. py:attribute:: check_containment
      :type:  bool
      :value: True



   .. py:attribute:: method
      :type:  str
      :value: 'proximity'



   .. py:attribute:: persistent
      :type:  bool
      :value: False



   .. py:attribute:: tolerance
      :type:  str
      :value: '1um'



   .. py:attribute:: snap_via_groups
      :type:  bool
      :value: False



   .. py:attribute:: snap_method
      :type:  str
      :value: 'areaFactor'



   .. py:attribute:: remove_unconnected
      :type:  bool
      :value: True



   .. py:attribute:: snap_tolerance
      :type:  int
      :value: 3



.. py:class:: ControlFileStackup(units: str = 'mm')

   Stackup information for the control file.

   Parameters
   ----------
   units : str, optional
       Length units (e.g., "mm", "um"). Default is "mm".


   .. py:attribute:: units
      :type:  str
      :value: 'mm'



   .. py:attribute:: metal_layer_snapping_tolerance
      :type:  float | None
      :value: None



   .. py:attribute:: dielectrics_base_elevation
      :type:  float
      :value: 0.0



   .. py:property:: vias
      :type: list[ControlFileVia]


      List of via objects.

      Returns
      -------
      list
          List of ControlFileVia objects.



   .. py:property:: materials
      :type: dict[str, ControlFileMaterial]


      Dictionary of material objects.

      Returns
      -------
      dict
          Dictionary of material names to ControlFileMaterial objects.



   .. py:property:: dielectrics
      :type: list[ControlFileDielectric]


      List of dielectric layers.

      Returns
      -------
      list
          List of ControlFileDielectric objects.



   .. py:property:: layers
      :type: list[ControlFileLayer]


      List of general layers.

      Returns
      -------
      list
          List of ControlFileLayer objects.



   .. py:method:: add_material(material_name: str, permittivity: float = 1.0, dielectric_loss_tg: float = 0.0, permeability: float = 1.0, conductivity: float = 0.0, properties: dict[str, Any] | None = None) -> ControlFileMaterial

      Add a new material.

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



   .. py:method:: add_layer(layer_name: str, elevation: float = 0.0, material: str = '', gds_type: int = 0, target_layer: str = '', thickness: float = 0.0, layer_type: str = 'conductor', solve_inside: bool = True, properties: dict[str, Any] | None = None) -> ControlFileLayer

      Add a new layer.

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



   .. py:method:: add_dielectric(layer_name: str, layer_index: int | None = None, material: str = '', thickness: float = 0.0, properties: dict[str, Any] | None = None, base_layer: str | None = None, add_on_top: bool = True) -> ControlFileDielectric

      Add a new dielectric layer.

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



   .. py:method:: add_via(layer_name: str, material: str = '', gds_type: int = 0, target_layer: str = '', start_layer: str = '', stop_layer: str = '', solve_inside: bool = True, via_group_method: str = 'proximity', via_group_tol: float = 1e-06, via_group_persistent: bool = True, snap_via_group_method: str = 'distance', snap_via_group_tol: float = 1e-08, properties: dict[str, Any] | None = None) -> ControlFileVia

      Add a new via layer.

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



.. py:class:: ControlFileImportOptions

   Import options for the control file.


   .. py:attribute:: auto_close
      :type:  bool
      :value: False



   .. py:attribute:: convert_closed_wide_lines_to_polys
      :type:  bool
      :value: False



   .. py:attribute:: round_to
      :type:  int
      :value: 0



   .. py:attribute:: defeature_tolerance
      :type:  float
      :value: 0.0



   .. py:attribute:: flatten
      :type:  bool
      :value: True



   .. py:attribute:: enable_default_component_values
      :type:  bool
      :value: True



   .. py:attribute:: import_dummy_nets
      :type:  bool
      :value: False



   .. py:attribute:: gdsii_convert_polygon_to_circles
      :type:  bool
      :value: False



   .. py:attribute:: import_cross_hatch_shapes_as_lines
      :type:  bool
      :value: True



   .. py:attribute:: max_antipad_radius
      :type:  float
      :value: 0.0



   .. py:attribute:: extracta_use_pin_names
      :type:  bool
      :value: False



   .. py:attribute:: min_bondwire_width
      :type:  float
      :value: 0.0



   .. py:attribute:: antipad_replace_radius
      :type:  float
      :value: 0.0



   .. py:attribute:: gdsii_scaling_factor
      :type:  float
      :value: 0.0



   .. py:attribute:: delete_empty_non_laminate_signal_layers
      :type:  bool
      :value: False



.. py:class:: ControlExtent(type: str = 'bbox', dieltype: str = 'bbox', diel_hactor: float = 0.25, airbox_hfactor: float = 0.25, airbox_vr_p: float = 0.25, airbox_vr_n: float = 0.25, useradiation: bool = True, honor_primitives: bool = True, truncate_at_gnd: bool = True)

   Extent options for boundaries for the control file..

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


   .. py:attribute:: type
      :type:  str
      :value: 'bbox'



   .. py:attribute:: dieltype
      :type:  str
      :value: 'bbox'



   .. py:attribute:: diel_hactor
      :type:  float
      :value: 0.25



   .. py:attribute:: airbox_hfactor
      :type:  float
      :value: 0.25



   .. py:attribute:: airbox_vr_p
      :type:  float
      :value: 0.25



   .. py:attribute:: airbox_vr_n
      :type:  float
      :value: 0.25



   .. py:attribute:: useradiation
      :type:  bool
      :value: True



   .. py:attribute:: honor_primitives
      :type:  bool
      :value: True



   .. py:attribute:: truncate_at_gnd
      :type:  bool
      :value: True



.. py:class:: ControlCircuitPt(name, x1, y1, lay1, x2, y2, lay2, z0)

   Circuit port for the control file.

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


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: x1
      :type:  float


   .. py:attribute:: x2
      :type:  float


   .. py:attribute:: lay1
      :type:  str


   .. py:attribute:: lay2
      :type:  str


   .. py:attribute:: y1
      :type:  float


   .. py:attribute:: y2
      :type:  float


   .. py:attribute:: z0
      :type:  float


.. py:class:: ControlFileComponent

   Component in the control file.


   .. py:attribute:: refdes
      :type:  str
      :value: 'U1'



   .. py:attribute:: partname
      :type:  str
      :value: 'BGA'



   .. py:attribute:: parttype
      :type:  str
      :value: 'IC'



   .. py:attribute:: die_type
      :type:  str
      :value: 'None'



   .. py:attribute:: die_orientation
      :type:  str
      :value: 'Chip down'



   .. py:attribute:: solderball_shape
      :type:  str
      :value: 'None'



   .. py:attribute:: solder_diameter
      :type:  str
      :value: '65um'



   .. py:attribute:: solder_height
      :type:  str
      :value: '65um'



   .. py:attribute:: solder_material
      :type:  str
      :value: 'solder'



   .. py:attribute:: pins
      :type:  list[dict[str, str | float]]
      :value: []



   .. py:attribute:: ports
      :type:  list[dict[str, str | float | None]]
      :value: []



   .. py:method:: add_pin(name: str, x: float, y: float, layer: str) -> None

      Add a pin to the component.

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



   .. py:method:: add_port(name: str, z0: float, pospin: str, refpin: Optional[str] = None, pos_type: str = 'pin', ref_type: str = 'pin') -> None

      Add a port to the component.

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



.. py:class:: ControlFileComponents

   Manage components for the control file.


   .. py:attribute:: units
      :type:  str
      :value: 'um'



   .. py:attribute:: components
      :type:  list[ControlFileComponent]
      :value: []



   .. py:method:: add_component(ref_des: str, partname: str, component_type: str, die_type: str = 'None', solderball_shape: str = 'None') -> ControlFileComponent

      Add a new component.

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



.. py:class:: ControlFileBoundaries(units: str = 'um')

   Boundaries for the control file.

   Parameters
   ----------
   units : str, optional
       Length units. Default is ``"um"``.


   .. py:attribute:: ports
      :type:  dict[str, ControlCircuitPt]


   .. py:attribute:: extents
      :type:  list[ControlExtent]
      :value: []



   .. py:attribute:: units
      :type:  str
      :value: 'um'



   .. py:method:: add_port(name: str, x1: float, y1: float, layer1: str, x2: float, y2: float, layer2: str, z0: float = 50) -> ControlCircuitPt

      Add a port.

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



   .. py:method:: add_extent(type: str = 'bbox', dieltype: str = 'bbox', diel_hactor: float = 0.25, airbox_hfactor: float = 0.25, airbox_vr_p: float = 0.25, airbox_vr_n: float = 0.25, useradiation: bool = True, honor_primitives: bool = True, truncate_at_gnd: bool = True) -> ControlExtent

      Add an extent.

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



.. py:class:: ControlFileSweep(name: str, start: str, stop: str, step: str, sweep_type: str, step_type: str, use_q3d: bool)

   Frequency sweep in the control file.

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


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: start
      :type:  str


   .. py:attribute:: stop
      :type:  str


   .. py:attribute:: step
      :type:  str


   .. py:attribute:: sweep_type
      :type:  str


   .. py:attribute:: step_type
      :type:  str


   .. py:attribute:: use_q3d
      :type:  bool


.. py:class:: ControlFileMeshOp(name: str, region: str, type: str, nets_layers: dict[str, str])

   Mesh operation in the control file.

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


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: region
      :type:  str


   .. py:attribute:: type
      :type:  str


   .. py:attribute:: nets_layers
      :type:  Dict[str, str]


   .. py:attribute:: num_max_elem
      :type:  int
      :value: 1000



   .. py:attribute:: restrict_elem
      :type:  bool
      :value: False



   .. py:attribute:: restrict_length
      :type:  bool
      :value: True



   .. py:attribute:: max_length
      :type:  str
      :value: '20um'



   .. py:attribute:: skin_depth
      :type:  str
      :value: '1um'



   .. py:attribute:: surf_tri_length
      :type:  str
      :value: '1mm'



   .. py:attribute:: num_layers
      :type:  int
      :value: 2



   .. py:attribute:: region_solve_inside
      :type:  bool
      :value: False



.. py:class:: ControlFileSetup(name: str)

   Simulation setup for the control file.

   Parameters
   ----------
   name : str
       Setup name.


   .. py:attribute:: name
      :type:  str


   .. py:attribute:: enabled
      :type:  bool
      :value: True



   .. py:attribute:: save_fields
      :type:  bool
      :value: False



   .. py:attribute:: save_rad_fields
      :type:  bool
      :value: False



   .. py:attribute:: frequency
      :type:  str
      :value: '1GHz'



   .. py:attribute:: maxpasses
      :type:  int
      :value: 10



   .. py:attribute:: max_delta
      :type:  float
      :value: 0.02



   .. py:attribute:: union_polygons
      :type:  bool
      :value: True



   .. py:attribute:: small_voids_area
      :type:  int
      :value: 0



   .. py:attribute:: mode_type
      :type:  str
      :value: 'IC'



   .. py:attribute:: ic_model_resolution
      :type:  str
      :value: 'Auto'



   .. py:attribute:: order_basis
      :type:  str
      :value: 'FirstOrder'



   .. py:attribute:: solver_type
      :type:  str
      :value: 'Auto'



   .. py:attribute:: low_freq_accuracy
      :type:  bool
      :value: False



   .. py:attribute:: mesh_operations
      :type:  list[ControlFileMeshOp]
      :value: []



   .. py:attribute:: sweeps
      :type:  list[ControlFileSweep]
      :value: []



   .. py:method:: add_sweep(name: str, start: str, stop: str, step: str, sweep_type: str = 'Interpolating', step_type: str = 'LinearStep', use_q3d: bool = True) -> ControlFileSweep

      Add a frequency sweep.

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



   .. py:method:: add_mesh_operation(name: str, region: str, type: str, nets_layers: dict[str, str]) -> ControlFileMeshOp

      Add a mesh operation.

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



.. py:class:: ControlFileSetups

   Manage simulation setups.


   .. py:attribute:: setups
      :type:  list[ControlFileSetup]
      :value: []



   .. py:method:: add_setup(name: str, frequency: str) -> ControlFileSetup

      Add a simulation setup.

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



.. py:class:: ControlFile(xml_input: str | None = None, technology: str | None = None, layer_map: str | None = None)

   Main class for EDB control file creation and management.

   Parameters
   ----------
   xml_input : str, optional
       Path to existing XML file to parse.
   tecnhology : str, optional
       Path to technology file to convert.
   layer_map : str, optional
       Path to layer map file.


   .. py:attribute:: stackup


   .. py:attribute:: boundaries


   .. py:attribute:: remove_holes
      :value: False



   .. py:attribute:: remove_holes_area_minimum
      :value: 30



   .. py:attribute:: remove_holes_units
      :value: 'um'



   .. py:attribute:: setups


   .. py:attribute:: components


   .. py:attribute:: import_options


   .. py:method:: parse_technology(tecnhology: str, edbversion: str | None = None) -> None

      Parse a technology file and convert to an XML control file.

      Parameters
      ----------
      tecnhology : str
          Path to technology file.
      edbversion : str, optional
          EDB version to use for conversion.



   .. py:method:: parse_layer_map(layer_map: str) -> None

      Parse a layer map file and update stackup.

      Parameters
      ----------
      layer_map : str
          Path to layer map file.



   .. py:method:: parse_xml(xml_input: str) -> None

      Parse an XML control file and populate the object.

      Parameters
      ----------
      xml_input : str
          Path to XML control file.



   .. py:method:: write_xml(xml_output)

      Write control file to XML.

      Parameters
      ----------
      xml_output : str
          Output XML file path.

      Returns
      -------
      bool
          ``True`` if file created successfully, ``False`` otherwise.



