src.pyedb.workflows.utilities.cutout
====================================

.. py:module:: src.pyedb.workflows.utilities.cutout

.. autoapi-nested-parse::

   EDB cutout utility module for creating clipped PCB designs.



Classes
-------

.. autoapisummary::

   src.pyedb.workflows.utilities.cutout.Cutout
   src.pyedb.workflows.utilities.cutout.GrpcCutout
   src.pyedb.workflows.utilities.cutout.DotNetCutout


Module Contents
---------------

.. py:class:: Cutout

   Factory class for creating cutout instances based on EDB mode.

   This class automatically selects the appropriate cutout implementation
   (gRPC or .NET) based on the EDB object's configuration.


.. py:class:: GrpcCutout(edb)

   Create a clipped (cut-out) EDB cell from an existing layout.
   High-performance EDB cut-out utility.

   Attributes
   ----------
   signals : list[str]
       List of signal net names to keep in the cut-out.
   references : list[str]
       List of reference net names to keep in the cut-out.
   extent_type : str
       Extent algorithm: ``ConvexHull`` (default), ``Conforming``, ``Bounding``.
   expansion_size : float
       Additional margin (metres) around the computed extent.  Default 0.002.
   use_round_corner : bool
       Round the corners of the expanded extent.  Default ``False``.
   custom_extent : list[tuple[float, float]] | None
       Optional closed polygon [(x1,y1), …] overriding any automatic extent.
   custom_extent_units : str
       Length unit for *custom_extent*.  Default ``mm``.
   include_voids_in_extents : bool
       Include voids ≥ 5 % of the extent area when building the clip polygon.
   open_cutout_at_end : bool
       Open the resulting cut-out database in the active Edb object.  Default ``True``.
   use_pyaedt_cutout : bool
       Use the PyAEDT based implementation instead of native EDB API.  Default ``True``.
   smart_cutout : bool
       Automatically enlarge *expansion_size* until all ports have reference.  Default ``False``.
   expansion_factor : float
       If > 0, compute initial *expansion_size* from trace-width/dielectric.  Default 0.
   maximum_iterations : int
       Maximum attempts for *smart_cutout* before giving up.  Default 10.
   number_of_threads : int
       Worker threads for polygon clipping and padstack cleaning.  Default 1.
   remove_single_pin_components : bool
       Delete RLC components with only one pin after cut-out.  Default ``False``.
   preserve_components_with_model : bool
       Keep every pin of components that carry a Spice/S-parameter model.  Default ``False``.
   check_terminals : bool
       Grow extent until all reference terminals are inside the cut-out.  Default ``False``.
   include_pingroups : bool
       Ensure complete pin-groups are included (needs *check_terminals*).  Default ``False``.
   simple_pad_check : bool
       Use fast centre-point padstack check instead of bounding-box.  Default ``True``.
   keep_lines_as_path : bool
       Keep clipped traces as Path objects (3D Layout only).  Default ``False``.
   extent_defeature : float
       Defeature tolerance (metres) for conformal extent.  Default 0.
   include_partial_instances : bool
       Include padstacks that only partially overlap the clip polygon.  Default ``False``.
   keep_voids : bool
       Retain voids that intersect the clip polygon.  Default ``True``.


   The cut-out can be produced with three different extent strategies:

   * ``ConvexHull`` (default)
   * ``Conforming`` (tight follow of geometry)
   * ``Bounding`` (simple bounding box)

   Multi-threaded execution, automatic terminal expansion and smart
   expansion-factor logic are supported.

   Examples
   --------
   >>> cut = Cutout(edb)
   >>> cut.signals = ["DDR4_DQ0", "DDR4_DQ1"]
   >>> cut.references = ["GND"]
   >>> cut.expansion_size = 0.001
   >>> polygon = cut.run()


   .. py:attribute:: signals
      :type:  list[str]
      :value: []



   .. py:attribute:: references
      :type:  list[str]
      :value: []



   .. py:attribute:: extent_type
      :type:  str
      :value: 'ConvexHull'



   .. py:attribute:: expansion_size
      :type:  str | float
      :value: 0.002



   .. py:attribute:: use_round_corner
      :type:  bool
      :value: False



   .. py:attribute:: output_file
      :type:  str
      :value: ''



   .. py:attribute:: open_cutout_at_end
      :type:  bool
      :value: True



   .. py:attribute:: use_pyaedt_cutout
      :type:  bool
      :value: True



   .. py:attribute:: smart_cutout
      :type:  bool
      :value: False



   .. py:attribute:: number_of_threads
      :type:  int
      :value: 2



   .. py:attribute:: use_pyaedt_extent_computing
      :type:  bool
      :value: True



   .. py:attribute:: extent_defeature
      :type:  int | float
      :value: 0



   .. py:attribute:: remove_single_pin_components
      :type:  bool
      :value: False



   .. py:attribute:: custom_extent
      :type:  list
      :value: None



   .. py:attribute:: custom_extent_units
      :type:  str
      :value: 'mm'



   .. py:attribute:: include_partial_instances
      :type:  bool
      :value: False



   .. py:attribute:: keep_voids
      :type:  bool
      :value: True



   .. py:attribute:: check_terminals
      :type:  bool
      :value: False



   .. py:attribute:: include_pingroups
      :type:  bool
      :value: False



   .. py:attribute:: expansion_factor
      :type:  int | float
      :value: 0



   .. py:attribute:: maximum_iterations
      :type:  int
      :value: 10



   .. py:attribute:: preserve_components_with_model
      :type:  bool
      :value: False



   .. py:attribute:: simple_pad_check
      :type:  bool
      :value: True



   .. py:attribute:: keep_lines_as_path
      :type:  bool
      :value: False



   .. py:attribute:: include_voids_in_extents
      :type:  bool
      :value: False



   .. py:property:: logger

      EDB logger instance.

      Returns
      -------
      Logger
          Logger object from the EDB instance.



   .. py:method:: calculate_initial_extent(expansion_factor: float) -> float

      Compute initial extent based on trace width and dielectric thickness.

      Calculate a float representing the larger number between the dielectric thickness
      or trace width multiplied by the nW factor. The trace width search is limited to
      nets with ports attached.

      Parameters
      ----------
      expansion_factor : float
          Value for the width multiplier (nW factor).

      Returns
      -------
      float
          Calculated initial extent in metres.

      Examples
      --------
      >>> from pyedb.workflows.utilities.cutout import Cutout
      >>> cutout = Cutout(edb)
      >>> initial_extent = cutout.calculate_initial_extent(3.0)



   .. py:method:: pins_to_preserve() -> tuple

      Identify pins and nets that must be preserved during cutout.

      Returns
      -------
      tuple
          Tuple containing (pins_to_preserve, nets_to_preserve) where:

          - pins_to_preserve : list
              List of pin IDs to keep.
          - nets_to_preserve : list[str]
              List of net names to keep.



   .. py:method:: run() -> list

      Execute the cutout operation.

      This method performs the complete cutout workflow including:

      - Smart cutout iterations if enabled
      - Extent computation with expansion factor
      - Multi-threaded geometry clipping
      - Component and net cleanup
      - Output file generation

      Returns
      -------
      list[list[float, float]] or bool
          List of [x, y] coordinate pairs defining the extent polygon if successful,
          ``False`` if cutout failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("design.aedb")
      >>> cutout = Cutout(edb)
      >>> cutout.signals = ["DDR4_DQ0", "DDR4_CLK"]
      >>> cutout.references = ["GND"]
      >>> cutout.expansion_size = 0.002
      >>> cutout.output_file = "cutout.aedb"
      >>> polygon = cutout.run()



.. py:class:: DotNetCutout(edb)

   Create a clipped (cut-out) EDB cell from an existing layout.
   High-performance EDB cut-out utility.

   Attributes
   ----------
   signals : list[str]
       List of signal net names to keep in the cut-out.
   references : list[str]
       List of reference net names to keep in the cut-out.
   extent_type : str
       Extent algorithm: ``ConvexHull`` (default), ``Conforming``, ``Bounding``.
   expansion_size : float
       Additional margin (metres) around the computed extent.  Default 0.002.
   use_round_corner : bool
       Round the corners of the expanded extent.  Default ``False``.
   custom_extent : list[tuple[float, float]] | None
       Optional closed polygon [(x1,y1), …] overriding any automatic extent.
   custom_extent_units : str
       Length unit for *custom_extent*.  Default ``mm``.
   include_voids_in_extents : bool
       Include voids ≥ 5 % of the extent area when building the clip polygon.
   open_cutout_at_end : bool
       Open the resulting cut-out database in the active Edb object.  Default ``True``.
   use_pyaedt_cutout : bool
       Use the PyAEDT based implementation instead of native EDB API.  Default ``True``.
   smart_cutout : bool
       Automatically enlarge *expansion_size* until all ports have reference.  Default ``False``.
   expansion_factor : float
       If > 0, compute initial *expansion_size* from trace-width/dielectric.  Default 0.
   maximum_iterations : int
       Maximum attempts for *smart_cutout* before giving up.  Default 10.
   number_of_threads : int
       Worker threads for polygon clipping and padstack cleaning.  Default 1.
   remove_single_pin_components : bool
       Delete RLC components with only one pin after cut-out.  Default ``False``.
   preserve_components_with_model : bool
       Keep every pin of components that carry a Spice/S-parameter model.  Default ``False``.
   check_terminals : bool
       Grow extent until all reference terminals are inside the cut-out.  Default ``False``.
   include_pingroups : bool
       Ensure complete pin-groups are included (needs *check_terminals*).  Default ``False``.
   simple_pad_check : bool
       Use fast centre-point padstack check instead of bounding-box.  Default ``True``.
   keep_lines_as_path : bool
       Keep clipped traces as Path objects (3D Layout only).  Default ``False``.
   extent_defeature : float
       Defeature tolerance (metres) for conformal extent.  Default 0.
   include_partial_instances : bool
       Include padstacks that only partially overlap the clip polygon.  Default ``False``.
   keep_voids : bool
       Retain voids that intersect the clip polygon.  Default ``True``.


   The cut-out can be produced with three different extent strategies:

   * ``ConvexHull`` (default)
   * ``Conforming`` (tight follow of geometry)
   * ``Bounding`` (simple bounding box)

   Multi-threaded execution, automatic terminal expansion and smart
   expansion-factor logic are supported.

   Examples
   --------
   >>> cut = Cutout(edb)
   >>> cut.signals = ["DDR4_DQ0", "DDR4_DQ1"]
   >>> cut.references = ["GND"]
   >>> cut.expansion_size = 0.001
   >>> polygon = cut.run()


   .. py:attribute:: signals
      :type:  list[str]
      :value: []



   .. py:attribute:: references
      :type:  list[str]
      :value: []



   .. py:attribute:: extent_type
      :type:  str
      :value: 'ConvexHull'



   .. py:attribute:: expansion_size
      :type:  str | float
      :value: 0.002



   .. py:attribute:: use_round_corner
      :type:  bool
      :value: False



   .. py:attribute:: output_file
      :type:  str
      :value: ''



   .. py:attribute:: open_cutout_at_end
      :type:  bool
      :value: True



   .. py:attribute:: use_pyaedt_cutout
      :type:  bool
      :value: True



   .. py:attribute:: smart_cutout
      :type:  bool
      :value: False



   .. py:attribute:: number_of_threads
      :type:  int
      :value: 2



   .. py:attribute:: use_pyaedt_extent_computing
      :type:  bool
      :value: True



   .. py:attribute:: extent_defeature
      :type:  int | float
      :value: 0



   .. py:attribute:: remove_single_pin_components
      :type:  bool
      :value: False



   .. py:attribute:: custom_extent
      :type:  list
      :value: None



   .. py:attribute:: custom_extent_units
      :type:  str
      :value: 'mm'



   .. py:attribute:: include_partial_instances
      :type:  bool
      :value: False



   .. py:attribute:: keep_voids
      :type:  bool
      :value: True



   .. py:attribute:: check_terminals
      :type:  bool
      :value: False



   .. py:attribute:: include_pingroups
      :type:  bool
      :value: False



   .. py:attribute:: expansion_factor
      :type:  int | float
      :value: 0



   .. py:attribute:: maximum_iterations
      :type:  int
      :value: 10



   .. py:attribute:: preserve_components_with_model
      :type:  bool
      :value: False



   .. py:attribute:: simple_pad_check
      :type:  bool
      :value: True



   .. py:attribute:: keep_lines_as_path
      :type:  bool
      :value: False



   .. py:attribute:: include_voids_in_extents
      :type:  bool
      :value: False



   .. py:property:: logger

      EDB logger instance.

      Returns
      -------
      Logger
          Logger object from the EDB instance.



   .. py:method:: calculate_initial_extent(expansion_factor: float) -> float

      Compute initial extent based on trace width and dielectric thickness.

      Calculate a float representing the larger number between the dielectric thickness
      or trace width multiplied by the nW factor. The trace width search is limited to
      nets with ports attached.

      Parameters
      ----------
      expansion_factor : float
          Value for the width multiplier (nW factor).

      Returns
      -------
      float
          Calculated initial extent in metres.

      Examples
      --------
      >>> cutout = Cutout(edb)
      >>> initial_extent = cutout.calculate_initial_extent(3.0)



   .. py:method:: pins_to_preserve() -> tuple

      Identify pins and nets that must be preserved during cutout.

      Returns
      -------
      tuple
          Tuple containing (pins_to_preserve, nets_to_preserve) where:

          - pins_to_preserve : list
              List of pin IDs to keep.
          - nets_to_preserve : list[str]
              List of net names to keep.



   .. py:method:: run() -> list | bool

      Execute the cutout operation.

      This method performs the complete cutout workflow including:

      - Smart cutout iterations if enabled
      - Extent computation with expansion factor
      - Multi-threaded geometry clipping
      - Component and net cleanup
      - Output file generation

      Returns
      -------
      list[list[float, float]] or bool
          List of [x, y] coordinate pairs defining the extent polygon if successful,
          ``False`` if cutout failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb("design.aedb")
      >>> cutout = Cutout(edb)
      >>> cutout.signals = ["DDR4_DQ0", "DDR4_CLK"]
      >>> cutout.references = ["GND"]
      >>> cutout.expansion_size = 0.002
      >>> cutout.output_file = "cutout.aedb"
      >>> polygon = cutout.run()



