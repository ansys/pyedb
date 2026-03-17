src.pyedb.grpc.edb
==================

.. py:module:: src.pyedb.grpc.edb

.. autoapi-nested-parse::

   Provides the main interface for interacting with Ansys Electronics Desktop Database (EDB).

   This module contains the ``Edb`` class which serves as the primary interface for:
   - Creating and managing EDB projects
   - Importing/exporting layout files
   - Configuring stackups, materials, and components
   - Setting up simulations (HFSS, SIwave, RaptorX)
   - Performing cutout operations
   - Generating ports and excitations
   - Parametrizing designs
   - Exporting to various formats (IPC2581, HFSS, Q3D)

   Key Functionality:
   - Database initialization and management
   - Layout manipulation and cutout generation
   - Material and stackup configuration
   - Net and component management
   - Simulation setup and execution
   - Design parametrization and optimization


   Examples
   --------

   .. code-block:: python

       # Basic EDB initialization
       from pyedb.grpc.edb import Edb

       edb = Edb(edbpath="myproject.aedb")

       # Importing a board file
       edb.import_layout_file("my_board.brd")

       # Creating a cutout
       edb.cutout(signal_list=["Net1", "Net2"], reference_list=["GND"])

       # Exporting to HFSS
       edb.export_hfss("output_dir")



Classes
-------

.. autoapisummary::

   src.pyedb.grpc.edb.Edb


Module Contents
---------------

.. py:class:: Edb(edbpath: Union[str, pyedb.grpc.database.primitive.path.Path] = None, cellname: str = None, isreadonly: bool = False, version: str = None, isaedtowned: bool = False, oproject=None, use_ppe: bool = False, control_file: str = None, map_file: str = None, technology_file: str = None, layer_filter: str = None, restart_rpc_server=False)

   Bases: :py:obj:`pyedb.grpc.edb_init.EdbInit`


   Main class for interacting with Ansys Electronics Desktop Database (EDB).

   Provides comprehensive control over EDB projects including:
   - Project creation/management
   - Layout import/export
   - Material/stackup configuration
   - Component/net management
   - Simulation setup
   - Cutout operations
   - Parameterization

   Parameters
   ----------
   edbpath : str or Path, optional
       Full path to AEDB folder or layout file to import. Supported formats:
       BRD, MCM, XML (IPC2581), GDS, ODB++ (TGZ/ZIP), DXF.
       Default creates new AEDB in documents folder.
   cellname : str, optional
       Specific cell to open. Default opens first cell.
   isreadonly : bool, optional
       Open in read-only mode. Default False.
   edbversion : str, int, float, optional
       EDB version (e.g., "2023.2", 232, 23.2). Default uses latest.
   isaedtowned : bool, optional
       Launch from HFSS 3D Layout. Default False.
   oproject : object, optional
       Reference to AEDT project object.
   use_ppe : bool, optional
       Use PPE license. Default False.
   control_file : str, optional
       XML control file path for import.
   map_file : str, optional
       Layer map file for import.
   technology_file : str, optional
       Technology file for import (GDS only).
   layer_filter : str, optional
       Layer filter file for import.
   restart_rpc_server : bool, optional
       Restart gRPC server. Use with caution. Default False.

   Examples
   --------
   >>> # Create new EDB:
   >>> edb = Edb()

   >>> # Open existing AEDB:
   >>> edb = Edb("myproject.aedb")

   >>> # Import board file:
   >>> edb = Edb("my_board.brd")


   .. py:property:: design_mode
      :type: str


      Get mode of the edb design.

      Returns
      -------
      str
          Value is either "general" or "ic" (lowercase).



   .. py:attribute:: standalone
      :value: True



   .. py:attribute:: oproject
      :value: None



   .. py:attribute:: version
      :value: None



   .. py:attribute:: isaedtowned
      :value: False



   .. py:attribute:: isreadonly
      :value: False



   .. py:attribute:: edbpath
      :value: None



   .. py:attribute:: log_name
      :value: None



   .. py:property:: core
      :type: ansys.edb.core


      Ansys Edb Core module.



   .. py:property:: ansys_em_path
      :type: str


      Ansys installation path.



   .. py:method:: number_with_units(value, units=None) -> str
      :staticmethod:


      Convert a number to a string with units. If value is a string, it's returned as is.

      Parameters
      ----------
      value : float, int, str
          Input number or string.
      units : optional
          Units for formatting. The default is ``None``, which uses ``"meter"``.

      Returns
      -------
      str
         String concatenating the value and unit.




   .. py:method:: value(val) -> pyedb.grpc.database.utility.value.Value | float | str

      Convert a value into a pyedb value.



   .. py:property:: cell_names
      :type: List[str]


      List of all cell names in the database.

      Returns
      -------
      list[str]
          Names of all circuit cells.



   .. py:property:: design_variables
      :type: Dict[str, pyedb.grpc.database.variables.Variable]


      All design variables in active cell.

      Returns
      -------
      dict[str, Variable]
          Variable names and values.



   .. py:property:: project_variables
      :type: Dict[str, pyedb.grpc.database.variables.Variable]


      All project variables in database.

      Returns
      -------
      dict[str, Variable]
          Variable names and values.



   .. py:property:: layout_validation
      :type: pyedb.grpc.database.layout_validation.LayoutValidation


      Layout validation utilities.

      Returns
      -------
      :class:`LayoutValidation <pyedb.grpc.database.layout_validation.LayoutValidation>`
          Tools for design rule checking and layout validation.



   .. py:property:: variables
      :type: Dict[str, pyedb.grpc.database.variables.Variable]


      All variables (project + design) in database.

      Returns
      -------
      dict[str, Variable]
          Combined dictionary of all variables.



   .. py:property:: terminals
      :type: Dict[str, pyedb.grpc.database.terminal.terminal.Terminal]


      Terminals in active layout.

      Returns
      -------
      dict[str, :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
          Terminal names and objects.



   .. py:property:: excitations
      :type: Dict[str, Union[pyedb.grpc.database.ports.ports.BundleWavePort, pyedb.grpc.database.ports.ports.GapPort, pyedb.grpc.database.ports.ports.CircuitPort, pyedb.grpc.database.ports.ports.CoaxPort, pyedb.grpc.database.ports.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.grpc.database.ports.ports.ports.GapPort`,
                 :class:`pyedb.grpc.database.ports.ports.ports.WavePort`,
                 :class:`pyedb.grpc.database.ports.ports.CircuitPort`,
                 :class:`pyedb.grpc.database.ports.ports.CoaxPort`,
                 :class:`pyedb.grpc.database.ports.ports.BundleWavePort`]]




   .. py:property:: ports
      :type: Dict[str, Union[pyedb.grpc.database.ports.ports.BundleWavePort, pyedb.grpc.database.ports.ports.GapPort, pyedb.grpc.database.ports.ports.CircuitPort, pyedb.grpc.database.ports.ports.CoaxPort, pyedb.grpc.database.ports.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.grpc.database.ports.ports.ports.GapPort`,
                 :class:`pyedb.grpc.database.ports.ports.ports.WavePort`,
                 :class:`pyedb.grpc.database.ports.ports.CircuitPort`,
                 :class:`pyedb.grpc.database.ports.ports.CoaxPort`,
                 :class:`pyedb.grpc.database.ports.ports.BundleWavePort`]]




   .. py:property:: excitations_nets
      :type: List[str]


      Nets with excitations defined.

      Returns
      -------
      list[str]
          Net names with excitations.



   .. py:property:: sources
      :type: Dict[str, pyedb.grpc.database.terminal.terminal.Terminal]


      All layout sources.

      Returns
      -------
      dict[str, :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
          Source names and objects.



   .. py:property:: voltage_regulator_modules
      :type: Dict[str, pyedb.grpc.database.layout.voltage_regulator.VoltageRegulator]


      Voltage regulator modules in design.

      Returns
      -------
      dict[str, :class:`VoltageRegulator <pyedb.grpc.database.layout.voltage_regulator.VoltageRegulator>`]
          VRM names and objects.



   .. py:property:: probes
      :type: Dict[str, pyedb.grpc.database.terminal.terminal.Terminal]


      All layout probes.

      Returns
      -------
      dict[str, :class:`Terminal <pyedb.grpc.database.terminal.terminal.Terminal>`]
          Probe names and objects.



   .. py:method:: open(restart_rpc_server=False) -> bool

      Open EDB database.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      >>> # Open an existing EDB database:
      >>> edb = Edb("myproject.aedb")



   .. py:method:: create(restart_rpc_server=False) -> Edb | None

      Create new EDB database.

      Returns
      -------
      bool
          True if successful, False otherwise.



   .. py:method:: import_layout_pcb(input_file, working_dir='', anstranslator_full_path='', use_ppe=False, control_file=None, map_file=None, tech_file=None, layer_filter=None) -> bool

      Import layout file and generate AEDB.

      Supported formats: BRD, MCM, XML (IPC2581), GDS, ODB++ (TGZ/ZIP), DXF

      Parameters
      ----------
      input_file : str
          Full path to input file.
      working_dir : str, optional
          Output directory for AEDB.
      anstranslator_full_path : str, optional
          Path to Ansys translator executable.
      use_ppe : bool, optional
          Use PPE license. Default False.
      control_file : str, optional
          XML control file path.
      tech_file : str, optional
          Technology file path.
      map_file : str, optional
          Layer map file path.
      layer_filter : str, optional
          Layer filter file path.

      Returns
      -------
      bool
          True if translation is successful, False otherwise.



   .. py:method:: import_layout_file(input_file, working_dir='', anstranslator_full_path='', use_ppe=False, control_file=None, map_file=None, tech_file=None, layer_filter=None) -> bool

      Import a board file and generate an ``edb.def`` file in the working directory.

      This function supports all AEDT formats, including DXF, GDS, SML (IPC2581), BRD, MCM, SIP, ZIP and TGZ.

      .. warning::
          Do not execute this function with untrusted function argument, environment
          variables or pyedb global settings.
          See the :ref:`security guide<ref_security_consideration>` for details.

      Parameters
      ----------
      input_file : str
          Full path to the board file.
      working_dir : str, optional
          Directory in which to create the ``aedb`` folder. The name given to the AEDB file
          is the same as the name of the board file.
      anstranslator_full_path : str, optional
          Full path to the Ansys translator. The default is ``""``.
      use_ppe : bool
          Whether to use the PPE License. The default is ``False``.
      control_file : str, optional
          Path to the XML file. The default is ``None``, in which case an attempt is made to find
          the XML file in the same directory as the board file. To succeed, the XML file and board file
          must have the same name. Only the extension differs.
      tech_file : str, optional
          Technology file. The file can be *.ircx, *.vlc.tech, or *.itf
      map_file : str, optional
          Layer map .map file.
      layer_filter:str,optional
          Layer filter .txt file.

      Returns
      -------
      bool
          True if translation is successful, False otherwise.

      Examples
      --------
      >>> # Create an Edb instance and import a BRD file:
      >>> edb = Edb()
      >>> edb.import_layout_file("my_board.brd", r"C:/project")
      >>> # Import a GDS file with control file:
      >>> edb.import_layout_file("layout.gds", control_file="control.xml")



   .. py:method:: import_vlctech_stackup(vlctech_file, working_dir='', export_xml=None) -> bool | str

      Import a vlc.tech file and generate an ``edb.def`` file in the working directory containing only the stackup.

      Parameters
      ----------
      vlctech_file : str
          Full path to the technology stackup file. It must be vlc.tech.
      working_dir : str, optional
          Directory in which to create the ``aedb`` folder. The name given to the AEDB file
          is the same as the name of the board file.
      export_xml : str, optional
          Export technology file in XML control file format.

      Returns
      -------
      bool or str
          `False` if translation failed, file path otherwise.



   .. py:method:: export_to_ipc2581(edbpath='', anstranslator_full_path='', ipc_path=None) -> str

      Export design to IPC2581 format.

      Parameters
      ----------
      edbpath: str
          Full path to aedb folder of the design to convert.
      anstranslator_full_path : str, optional
          Path to Ansys translator executable.
      ipc_path : str, optional
          Output XML file path. Default: <edb_path>.xml.

      Returns
      -------
      str
          Path to output IPC2581 file, and corresponding log file.

      Examples
      --------
      >>> # Create an Edb instance and export to IPC2581 format:
      >>> edb = Edb()
      >>> edb.export_to_ipc2581("output.xml")



   .. py:property:: layout_bounding_box
      :type: list[float]


      Get the bounding box of the active layout.

      Returns
      -------
      list[float]
          Bounding box coordinates as [xmin, ymin, xmax, ymax].



   .. py:property:: configuration
      :type: pyedb.configuration.configuration.Configuration


      Project configuration manager.

      Returns
      -------
      :class:`Configuration <pyedb.configuration.configuration.Configuration>`
          Configuration file interface.



   .. py:method:: edb_exception(ex_value: Exception, tb_data: Any)

      Log Python exceptions to EDB logger.

      Parameters
      ----------
      ex_value : Exception
          Exception value.
      tb_data : traceback
          Traceback object.



   .. py:property:: active_db

      Active database object.

      Returns
      -------
      :class:`ansys.edb.core.database.Database`
          Current database instance.



   .. py:property:: active_cell

      Active cell in the database.

      Returns
      -------
      :class:`ansys.edb.core.layout.cell.Cell`
          Currently active cell.



   .. py:property:: components
      :type: pyedb.grpc.database.components.Components


      Component management interface.

      Returns
      -------
      :class:`Components <pyedb.grpc.database.components.Components>`
          Component manipulation tools.



   .. py:property:: design_options
      :type: pyedb.grpc.database.design_options.EdbDesignOptions



   .. py:property:: stackup
      :type: pyedb.grpc.database.stackup.Stackup


      Stackup management interface.

      Returns
      -------
      :class:`Stackup <pyedb.grpc.database.stackup.Stackup>`
          Layer stack configuration tools.



   .. py:property:: source_excitation
      :type: Optional[pyedb.grpc.database.source_excitations.SourceExcitation]


      Source excitation management.
      .. deprecated:: 0.70
         Use: func:`excitation_manager` property instead.
      Returns
      -------
      :class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`
          Source and port creation tools.



   .. py:property:: excitation_manager
      :type: pyedb.grpc.database.source_excitations.SourceExcitation | None


      Source excitation manager.

      Returns
      -------
      :class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`
          Source and port creation tools.



   .. py:property:: materials
      :type: pyedb.grpc.database.definition.materials.Materials


      Material database interface.

      Returns
      -------
      :class:`Materials <pyedb.grpc.database.definition.materials.Materials>`
          Material definition and management.



   .. py:property:: padstacks
      :type: pyedb.grpc.database.padstacks.Padstacks


      Padstack management interface.

      Returns
      -------
      :class:`Padstacks <pyedb.grpc.database.padstack.Padstacks>`
          Padstack definition and editing.



   .. py:property:: siwave
      :type: pyedb.grpc.database.siwave.Siwave


      SIwave simulation interface.

      Returns
      -------
      :class:`Siwave <pyedb.grpc.database.siwave.Siwave>`
          SIwave analysis setup tools.



   .. py:property:: hfss
      :type: pyedb.grpc.database.hfss.Hfss


      HFSS simulation interface.

      Returns
      -------
      :class:`Hfss <pyedb.grpc.database.hfss.Hfss>`
          HFSS analysis setup tools.



   .. py:property:: nets
      :type: pyedb.grpc.database.nets.Nets


      Net management interface.

      Returns
      -------
      :class:`Nets <pyedb.grpc.database.nets.Nets>`
          Net manipulation tools.



   .. py:property:: net_classes
      :type: Optional[pyedb.grpc.database.nets.NetClasses]


      Net class management.

      Returns
      -------
      :class:`NetClass <pyedb.grpc.database.nets.NetClasses>`
          Net classes objects.



   .. py:property:: extended_nets
      :type: pyedb.grpc.database.net.extended_net.ExtendedNets


      Extended net management.

      Returns
      -------
      :class:`ExtendedNets <pyedb.grpc.database.net.extended_net.ExtendedNets>`
          Extended net tools.



   .. py:property:: differential_pairs
      :type: pyedb.grpc.database.net.differential_pair.DifferentialPairs


      Differential pair management.

      Returns
      -------
      :class:`DifferentialPairs <pyedb.grpc.database.net.differential_par.DifferentialPairs>`
          Differential pair tools.



   .. py:property:: modeler
      :type: pyedb.grpc.database.modeler.Modeler


      Geometry modeling interface.

      Returns
      -------
      :class:`Modeler <pyedb.grpc.database.modeler.Modeler>`
          Geometry creation and editing.



   .. py:property:: layout
      :type: pyedb.grpc.database.layout.layout.Layout


      Layout access interface.

      Returns
      -------
      :class:`Layout <pyedb.grpc.database.layout.layout.Layout>`
          Layout manipulation tools.



   .. py:property:: active_layout
      :type: pyedb.grpc.database.layout.layout.Layout


      Active layout access.

      Returns
      -------
      :class:`Layout <pyedb.grpc.database.layout.layout.Layout>`
          Current layout tools.



   .. py:property:: layout_instance

      Layout instance object.

      Returns
      -------
      :class:`LayoutInstance <ansys.edb.core.layout_instance.layout_instance.LayoutInstance>`
          Current layout instance.



   .. py:method:: get_connected_objects(layout_object_instance) -> list[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance | pyedb.grpc.database.primitive.path.Path | pyedb.grpc.database.primitive.polygon.Polygon]

      Get objects connected to a layout object.

      Parameters
      ----------
      layout_object_instance :
          Target layout object.

      Returns
      -------
      list
          Connected objects (padstacks, paths, polygons, etc.).



   .. py:method:: point_3d(x, y, z=0.0) -> pyedb.grpc.database.geometry.point_3d_data.Point3DData
      :staticmethod:


      Create 3D point.

      This method does not use instance state and is therefore a staticmethod.

      Parameters
      ----------
      x : float, int, str
          X coordinate.
      y : float, int, str
          Y coordinate.
      z : float, int, str, optional
          Z coordinate.

      Returns
      -------
      :class:`Point3DData <pyedb.grpc.database.geometry.point_3d_data.Point3DData>`
          3D point object.



   .. py:method:: point_data(x, y=None)

      Create 2D point.

      This method does not use instance state and is therefore a staticmethod.

      Parameters
      ----------
      x : float, int, str or PointData
          X coordinate or PointData object.
      y : float, int, str, optional
          Y coordinate.

      Returns
      -------
      :class:`PointData <pyedb.grpc.database.geometry.point_data.PointData>`
          2D point object.



   .. py:method:: close_edb() -> bool

      Close EDB and clean up resources.

      ..deprecated:: 0.51.0
         Use :func:`close` instead.

      Returns
      -------
      bool
          True if successful, False otherwise.

      Examples
      --------
      Close the EDB session:
      >>> edb = Edb()
      >>> edb.close()



   .. py:method:: save_edb() -> bool

      Save current EDB database.

      ..deprecated:: 0.51.0
         Use :func:`save` instead.




   .. py:method:: save_edb_as(fname) -> bool

      Save EDB database to new location.

      ..deprecated:: 0.51.0
         Use :func:`save_as` instead.



   .. py:method:: execute(func)

      Execute EDB utility command (Not implemented in gRPC).

      Parameters
      ----------
      func : str
          Command to execute.



   .. py:method:: import_gds_file(input_gds, anstranslator_full_path='', use_ppe=False, control_file=None, tech_file=None, map_file=None, layer_filter=None) -> bool

      Import GDS file.

      .. warning::
          Do not execute this function with untrusted function argument, environment
          variables or pyedb global settings.
          See the :ref:`security guide<ref_security_consideration>` for details.

      Parameters
      ----------
      input_gds : str
          GDS file path.
      anstranslator_full_path : str, optional
          Ansys translator path.
      use_ppe : bool, optional
          Use PPE license. Default False.
      control_file : str, optional
          XML control file.
      tech_file : str, optional
          Technology file.
      map_file : str, optional
          Layer map file.
      layer_filter : str, optional
          Layer filter file.

      Returns
      -------
      bool
          True if import is successful, False otherwise.



   .. py:method:: cutout(signal_nets=None, reference_nets=None, extent_type='ConvexHull', expansion_size=0.002, use_round_corner=False, output_aedb_path=None, open_cutout_at_end=True, use_pyaedt_cutout=True, number_of_threads=1, use_pyaedt_extent_computing=True, extent_defeature=0, remove_single_pin_components=False, custom_extent=None, custom_extent_units='mm', include_partial_instances=False, keep_voids=True, check_terminals=False, include_pingroups=False, expansion_factor=0, maximum_iterations=10, preserve_components_with_model=False, simple_pad_check=True, keep_lines_as_path=False, include_voids_in_extents=False) -> list

      Create a cutout using an approach entirely based on PyAEDT.
      This method replaces all legacy cutout methods in PyAEDT.
      It does in sequence:
      - delete all nets not in list,
      - create a extent of the nets,
      - check and delete all vias not in the extent,
      - check and delete all the primitives not in extent,
      - check and intersect all the primitives that intersect the extent.

      Parameters
      ----------
       signal_nets : list
          List of signal strings.
      reference_nets : list, optional
          List of references to add. The default is ``["GND"]``.
      extent_type : str, optional
          Type of the extension. Options are ``"Conforming"``, ``"ConvexHull"``, and
          ``"Bounding"``. The default is ``"Conforming"``.
      expansion_size : float, str, optional
          Expansion size ratio in meters. The default is ``0.002``.
      use_round_corner : bool, optional
          Whether to use round corners. The default is ``False``.
      output_aedb_path : str, optional
          Full path and name for the new AEDB file. If None, then current aedb will be cutout.
      open_cutout_at_end : bool, optional
          Whether to open the cutout at the end. The default is ``True``.
      use_pyaedt_cutout : bool, optional
          Whether to use new PyAEDT cutout method or EDB API method.
          New method is faster than native API method since it benefits of multithread.
      number_of_threads : int, optional
          Number of thread to use. Default is 4. Valid only if ``use_pyaedt_cutout`` is set to ``True``.
      use_pyaedt_extent_computing : bool, optional
          Whether to use legacy extent computing (experimental) or EDB API.
      extent_defeature : float, optional
          Defeature the cutout before applying it to produce simpler geometry for mesh (Experimental).
          It applies only to Conforming bounding box. Default value is ``0`` which disable it.
      remove_single_pin_components : bool, optional
          Remove all Single Pin RLC after the cutout is completed. Default is `False`.
      custom_extent : list
          Points list defining the cutout shape. This setting will override `extent_type` field.
      custom_extent_units : str
          Units of the point list. The default is ``"mm"``. Valid only if `custom_extend` is provided.
      include_partial_instances : bool, optional
          Whether to include padstack instances that have bounding boxes intersecting with point list polygons.
          This operation may slow down the cutout export.Valid only if `custom_extend` and
          `use_pyaedt_cutout` is provided.
      keep_voids : bool
          Boolean used for keep or not the voids intersecting the polygon used for clipping the layout.
          Default value is ``True``, ``False`` will remove the voids.Valid only if `custom_extend` is provided.
      check_terminals : bool, optional
          Whether to check for all reference terminals and increase extent to include them into the cutout.
          This applies to components which have a model (spice, touchstone or netlist) associated.
      include_pingroups : bool, optional
          Whether to check for all pingroups terminals and increase extent to include them into the cutout.
          It requires ``check_terminals``.
      expansion_factor : int, optional
          The method computes a float representing the largest number between
          the dielectric thickness or trace width multiplied by the expansion_factor factor.
          The trace width search is limited to nets with ports attached. Works only if `use_pyaedt_cutout`.
          Default is `0` to disable the search.
      maximum_iterations : int, optional
          Maximum number of iterations before stopping a search for a cutout with an error.
          Default is `10`.
      preserve_components_with_model : bool, optional
          Whether to preserve all pins of components that have associated models (Spice or NPort).
          This parameter is applicable only for a PyAEDT cutout (except point list).
      simple_pad_check : bool, optional
          Whether to use the center of the pad to find the intersection with extent or use the bounding box.
          Second method is much slower and requires to disable multithread on padstack removal.
          Default is `True`.
      keep_lines_as_path : bool, optional
          Whether to keep the lines as Path after they are cutout or convert them to PolygonData.
          This feature works only in Electronics Desktop (3D Layout).
          If the flag is set to ``True`` it can cause issues in SiWave once the Edb is imported.
          Default is ``False`` to generate PolygonData of cut lines.
      include_voids_in_extents : bool, optional
          Whether to compute and include voids in pyaedt extent before the cutout. Cutout time can be affected.
          It works only with Conforming cutout.
          Default is ``False`` to generate extent without voids.


      Returns
      -------
      List
          List of coordinate points defining the extent used for clipping the design. If it failed return an empty
          list.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb(r"C:\test.aedb", version="2022.2")
      >>> edb.logger.info_timer("Edb Opening")
      >>> edb.logger.reset_timer()
      >>> start = time.time()
      >>> signal_list = []
      >>> for net in edb.nets.netlist:
      >>>      if "3V3" in net:
      >>>           signal_list.append(net)
      >>> power_list = ["PGND"]
      >>> edb.cutout(signal_nets=signal_list, reference_nets=power_list, extent_type="Conforming")
      >>> end_time = str((time.time() - start) / 60)
      >>> edb.logger.info("Total legacy cutout time in min %s", end_time)
      >>> edb.nets.plot(signal_list, None, color_by_net=True)
      >>> edb.nets.plot(power_list, None, color_by_net=True)
      >>> edb.save()
      >>> edb.close()





   .. py:method:: write_export3d_option_config_file(path_to_output, config_dictionaries=None)
      :staticmethod:


      Write the options for a 3D export to a configuration file.

      Parameters
      ----------
      path_to_output : str
          Full path to the configuration file to save 3D export options to.

      config_dictionaries : dict, optional
          Configuration dictionaries. The default is ``None``.




   .. py:method:: export_hfss(path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False) -> str

      Export to HFSS project.

      Parameters
      ----------
      path_to_output : str
          Output directory.
      net_list : list, optional
          Nets to export.
      num_cores : int, optional
          Processing cores to use.
      aedt_file_name : str, optional
          Custom AEDT filename.
      hidden : bool, optional
          Run Siwave in background. Default False.

      Returns
      -------
      str
          Path to generated AEDT file.

      Examples
      --------
      >>> # Create an Edb instance and export to HFSS project:
      >>> edb = Edb()
      >>> edb.export_hfss(r"C:/output", net_list=["SignalNet"])



   .. py:method:: export_q3d(path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False) -> str

      Export to Q3D project.

      Parameters
      ----------
      path_to_output : str
          Output directory.
      net_list : list, optional
          Nets to export.
      num_cores : int, optional
          Processing cores to use.
      aedt_file_name : str, optional
          Custom AEDT filename.
      hidden : bool, optional
          Run Siwave in background. Default False.

      Returns
      -------
      str
          Path to generated AEDT file.

      Examples
      --------
      >>> # Create an Edb instance and export to Q3D project:
      >>> edb = Edb()
      >>> edb.export_q3d(r"C:/output")



   .. py:method:: export_maxwell(path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False) -> str

      Export to Maxwell project.

      Parameters
      ----------
      path_to_output : str
          Output directory.
      net_list : list, optional
          Nets to export.
      num_cores : int, optional
          Processing cores to use.
      aedt_file_name : str, optional
          Custom AEDT filename.
      hidden : bool, optional
          Run Siwave in background. Default False.

      Returns
      -------
      str
          Path to generated AEDT file.

      Examples
      --------
      >>> # Create an Edb instance and export to Maxwell project:
      >>> edb = Edb()
      >>> edb.export_maxwell(r"C:/output")



   .. py:method:: solve_siwave() -> str

      Solve with SIwave.

      Returns
      -------
      str
          Path to SIwave project.

      Examples
      --------
      >>> # Create an Edb instance and solve with SIwave:
      >>> edb = Edb()
      >>> edb.solve_siwave()



   .. py:method:: export_siwave_dc_results(siwave_project, solution_name, output_folder=None, html_report=True, vias=True, voltage_probes=True, current_sources=True, voltage_sources=True, power_tree=True, loop_res=True) -> list[str]

      Export SIwave DC results.

      Parameters
      ----------
      siwave_project : str
          SIwave project path.
      solution_name : str
          DC analysis name.
      output_folder : str, optional
          Custom output folder.
      html_report : bool, optional
          Generate HTML report. Default True.
      vias : bool, optional
          Export vias report. Default True.
      voltage_probes : bool, optional
          Export voltage probes. Default True.
      current_sources : bool, optional
          Export current sources. Default True.
      voltage_sources : bool, optional
          Export voltage sources. Default True.
      power_tree : bool, optional
          Export power tree. Default True.
      loop_res : bool, optional
          Export loop resistance. Default True.

      Returns
      -------
      list[str]
          Generated report files.



   .. py:method:: variable_exists(variable_name) -> bool

      Check if variable exists.

      Parameters
      ----------
      variable_name : str
          Variable name.

      Returns
      -------
      bool
          True if variable exists.



   .. py:method:: get_variable(variable_name) -> pyedb.grpc.database.utility.value.Value | bool

      Get variable value.

      Parameters
      ----------
      variable_name : str
          Variable name.

      Returns
      -------
      float or bool
          Variable value if exists, else False.



   .. py:method:: get_all_variable_names() -> List[str]

      Method added for compatibility with grpc.

      Returns
      -------
      List[str]
          List of variable names.




   .. py:method:: add_project_variable(variable_name, variable_value, description=None) -> bool

      Add project variable.

      Parameters
      ----------
      variable_name : str
          Variable name (auto-prefixed with '$').
      variable_value : str, float
          Variable value with units.
      description : str, optional
          Variable description.

      Returns
      -------
      bool
          True if successful, False if variable exists.



   .. py:method:: add_design_variable(variable_name, variable_value, description: str = '') -> bool

      Add design variable.

      Parameters
      ----------
      variable_name : str
          Variable name.
      variable_value : str, float
          Variable value with units.
      description : str, optional
          Variable description.

      Returns
      -------
      bool
          True if successful, False if variable exists.



   .. py:method:: change_design_variable_value(variable_name, variable_value)

      Update variable value.

      Parameters
      ----------
      variable_name : str
          Variable name.
      variable_value : str, float
          New value with units.



   .. py:method:: get_bounding_box() -> tuple[tuple[float, float], tuple[float, float]]

      Get layout bounding box.

      Returns
      -------
      tuple
          tuple[tuple[min_x, min_y], tuple[max_x, max_y]] in meters.



   .. py:method:: get_statistics(compute_area=False) -> pyedb.grpc.database.utility.layout_statistics.LayoutStatistics

      Get layout statistics.

      Parameters
      ----------
      compute_area : bool, optional
          Calculate net areas. Default False.

      Returns
      -------
      :class:`LayoutStatistics <pyedb.grpc.database.utility.layout_statistics.LayoutStatistics>`
          Layout statistics report.



   .. py:method:: are_port_reference_terminals_connected(common_reference=None) -> bool

      Check if port reference terminals are connected.

      Parameters
      ----------
      common_reference : str, optional
          Reference net name to check.

      Returns
      -------
      bool
          True if all port references are connected.



   .. py:property:: setups
      :type: dict[str, pyedb.grpc.database.simulation_setup.hfss_simulation_setup.HfssSimulationSetup | pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup | pyedb.grpc.database.simulation_setup.siwave_simulation_setup.SiwaveSimulationSetup]


      Get the dictionary of all EDB simulation setups.

      Returns
      -------
      dict[str, object]



   .. py:property:: simulation_setups
      :type: pyedb.grpc.database.simulation_setups.SimulationSetups


      Get all simulation setups object.



   .. py:property:: hfss_setups
      :type: dict[str, pyedb.grpc.database.simulation_setup.hfss_simulation_setup.HfssSimulationSetup]


      Active HFSS setup in EDB.

      .. deprecated:: pyedb 0.67.0
          Use :attr:`simulation_setups.hfss` instead.




   .. py:property:: siwave_dc_setups
      :type: dict[str, pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup]


      Active Siwave DC IR Setups.

      .. deprecated:: pyedb 0.67.0
          Use :attr:`simulation_setups.siwave_dcir` instead.




   .. py:property:: siwave_ac_setups
      :type: dict[str, pyedb.grpc.database.simulation_setup.siwave_simulation_setup.SiwaveSimulationSetup]


      Active Siwave SYZ setups.

      .. deprecated:: pyedb 0.67.0
          Use :attr:`simulation_setups.siwave` instead.



   .. py:method:: create_hfss_setup(name=None, start_frequency='0GHz', stop_frequency='20GHz', step_frequency='10MHz') -> pyedb.grpc.database.simulation_setup.hfss_simulation_setup.HfssSimulationSetup

      Create an HFSS simulation setup from a template.

      . deprecated:: pyedb 0.67.0
      Use :func:`self.simulation_setups.create` instead.



   .. py:method:: create_raptorx_setup(name=None) -> pyedb.grpc.database.simulation_setup.raptor_x_simulation_setup.RaptorXSimulationSetup

      Create RaptorX analysis setup (2024R2+ only).

      ..deprecated:: pyedb 0.67.0
            Use :func:`self.simulation_setups.create` instead.



   .. py:method:: create_siwave_syz_setup(name=None, **kwargs) -> pyedb.grpc.database.simulation_setup.siwave_simulation_setup.SiwaveSimulationSetup

      Create SIwave SYZ analysis setup.

      .. deprecated:: pyedb 0.67.0
          Use :func:`self.simulation_setups.create` instead.



   .. py:method:: create_siwave_dc_setup(name=None, **kwargs) -> pyedb.grpc.database.simulation_setup.siwave_dcir_simulation_setup.SIWaveDCIRSimulationSetup

      Create SIwave DC analysis setup.

      ..deprecated:: pyedb 0.67.0
          Use :func:`self.simulation_setups.create` instead.



   .. py:method:: calculate_initial_extent(expansion_factor) -> float

      Compute a float representing the larger number between the dielectric thickness or trace width
      multiplied by the nW factor. The trace width search is limited to nets with ports attached.

      Parameters
      ----------
      expansion_factor : float
          Value for the width multiplier (nW factor).

      Returns
      -------
      float



   .. py:method:: copy_zones(working_directory=None) -> dict[str, tuple[int, ansys.edb.core.geometry.polygon_data.PolygonData]]

      Copy multi-zone EDB project to one new edb per zone.

      Parameters
      ----------
      working_directory : str
          Directory path where all EDB project are copied, if empty will use the current EDB project.

      Returns
      -------
      dict[str, tuple[int,:class:`PolygonData <ansys.edb.core.geometry.polygon_data.PolygonData>`]]

         Return a dictionary with edb path as key and tuple Zone Id as first item and EDB polygon Data defining
         the region as second item.




   .. py:method:: cutout_multizone_layout(zones, common_reference_net=None) -> tuple[dict[str, str], list[str]]

      Create a multizone project cutout.

      Parameters
      ----------
      zones : dict[str](EDB PolygonData)
          Dictionary with EDB path as key and EDB PolygonData as value defining the zone region.
          This dictionary is returned from the command copy_zones():

      common_reference_net : str
          the common reference net name. This net name must be provided to provide a valid project.

      Returns
      -------
      tuple[dict[str, str], list[str]]
          first dictionary defined_ports with edb name as key and existing port name list as value. Those ports are
          the ones defined before processing the multizone clipping. the second is the list of connected port.




   .. py:method:: create_port(terminal, ref_terminal=None, is_circuit_port=False, name=None)

      Create a port.

      ..deprecated:: 0.51.0
         Use :func:`create_port` has been moved to source_excitation.create_port.




   .. py:method:: create_voltage_probe(terminal, ref_terminal)

      Create a voltage probe.

      ..deprecated:: 0.50.0
         Use :func:`create_voltage_probe` has been moved to edb.excitation_manager.create_voltage_probe.




   .. py:method:: create_voltage_source(terminal, ref_terminal)

      Create a voltage source.

      ..deprecated:: 0.50.0
         Use: func:`create_voltage_source` has been moved to edb.excitation_manager.create_voltage_source.




   .. py:method:: create_current_source(terminal, ref_terminal)

      Create a current source.

      ..deprecated:: 0.50.0
         Use :func:`create_current_source` has been moved to edb.excitation_manager.create_current_source.




   .. py:method:: get_point_terminal(name, net_name, location, layer)

      Place terminal between two points.

      ..deprecated:: 0.50.0
         Use: func:`get_point_terminal` has been moved to edb.excitation_manager.get_point_terminal.



   .. py:method:: auto_parametrize_design(layers=True, materials=True, via_holes=True, pads=True, antipads=True, traces=True, layer_filter=None, material_filter=None, padstack_definition_filter=None, trace_net_filter=None, use_single_variable_for_padstack_definitions=True, use_relative_variables=True, output_aedb_path=None, open_aedb_at_end=True, expand_polygons_size=0, expand_voids_size=0, via_offset=True) -> list[str]

      Automatically parametrize design elements.

      Parameters
      ----------
      layers : bool, optional
          Parametrize layer thicknesses. Default True.
      materials : bool, optional
          Parametrize material properties. Default True.
      via_holes : bool, optional
          Parametrize via holes. Default True.
      pads : bool, optional
          Parametrize pads. Default True.
      antipads : bool, optional
          Parametrize antipads. Default True.
      traces : bool, optional
          Parametrize trace widths. Default True.
      layer_filter : list, optional
          Layers to include. All if None.
      material_filter : list, optional
          Materials to include. All if None.
      padstack_definition_filter : list, optional
          Padstacks to include. All if None.
      trace_net_filter : list, optional
          Nets to parametrize. All if None.
      use_single_variable_for_padstack_definitions : bool, optional
          Single variable per padstack. Default True.
      use_relative_variables : bool, optional
          Use delta variables. Default True.
      output_aedb_path : str, optional
          Output AEDB path.
      open_aedb_at_end : bool, optional
          Open AEDB when finished. Default True.
      expand_polygons_size : float, optional
          Polygon expansion size. Default 0.
      expand_voids_size : float, optional
          Void expansion size. Default 0.
      via_offset : bool, optional
          Parametrize via positions. Default True.

      Returns
      -------
      list[str]
          Created parameter names.

      Examples
      --------
      >>> edb = Edb()
      >>> params = edb.auto_parametrize_design(
      >>>     layers=True,
      >>>     materials=True,
      >>>     trace_net_filter=["Clock"])



   .. py:method:: create_model_for_arbitrary_wave_ports(temp_directory, mounting_side='top', signal_nets=None, terminal_diameter=None, output_edb=None, launching_box_thickness='100um')

      Create simplified model for arbitrary wave port generation.

      Parameters
      ----------
      temp_directory : str
          Working directory.
      mounting_side : str, optional
          Board orientation ("top" or "bottom").
      signal_nets : list, optional
          Nets to include. All if None.
      terminal_diameter : float, optional
          Custom terminal diameter. Auto-calculated if None.
      output_edb : str, optional
          Output AEDB path.
      launching_box_thickness : str, optional
          Wave port box thickness.

      Returns
      -------
      bool
          True if successful, False otherwise.



   .. py:property:: definitions

      EDB definitions access.

      Returns
      -------
      :class:`Definitions <pyedb.grpc.database.definitions.Definitions>`
          Definitions interface.



   .. py:property:: workflow

      Workflow automation interface.

      Returns
      -------
      :class:`Workflow <pyedb.workflow.Workflow>`
          Workflow automation tools.



   .. py:method:: export_gds_comp_xml(comps_to_export, gds_comps_unit='mm', control_path=None)

      Export component data to GDS XML control file.

      Parameters
      ----------
      comps_to_export : list
          Components to export.
      gds_comps_unit : str, optional
          Output units. Default "mm".
      control_path : str, optional
          Output XML path.

      Returns
      -------
      bool
          True if successful, False otherwise.



   .. py:method:: compare(input_file, results='')

      Compares current open database with another one.

      .. warning::
          Do not execute this function with untrusted function argument, environment
          variables or pyedb global settings.
          See the :ref:`security guide<ref_security_consideration>` for details.

      Parameters
      ----------
      input_file : str
          Path to the edb file.
      results: str, optional
          Path to directory in which results will be saved. If no path is given, a new "_compare_results"
          directory will be created with the same naming and path as the .aedb folder.
      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: import_layout_component(component_path) -> ansys.edb.core.hierarchy.layout_component.LayoutComponent

      Import a layout component inside the current layout and place it at the origin.
      This feature is only supported with PyEDB gRPC. Encryption is not yet supported.

      Parameters
      ----------
      component_path : str
          Layout component path (.aedbcomp file).

      Returns
      -------
          class:`LayoutComponent <ansys.edb.core.hierarchy.layout_component.LayoutComponent>`.



   .. py:method:: export_layout_component(component_path) -> bool

      Export a layout component from the current layout.
      This feature is only supported with PyEDB gRPC. Encryption is not yet supported.

      Parameters
      ----------
      component_path : str
          Layout component path (.aedbcomp file).

      Returns
      -------
      bool
          `True` if layout component is successfully exported, `False` otherwise.



   .. py:method:: physical_merge(merged_edb: Union[str, pyedb.Edb], on_top: bool = True, vector: tuple = (0.0, 0.0), prefix: str = 'merged_', show_progress: bool = True)

      Merge two EDBs together by copying the primitives from the merged_edb into the hosting_edb.

      Parameters
      ----------
      merged_edb : str, Edb
          Edb folder path or The EDB that will be merged into the hosting_edb.
      on_top : bool, optional
          If True, the primitives from the merged_edb will be placed on top of the hosting_edb primitives.
          If False, they will be placed below. Default is True.
      vector : tuple, optional
          A tuple (x, y) representing the offset to apply to the primitives from the merged. Default is (0.0, 0.0).
      prefix : str, optional
          A prefix to add to the layer names of the merged primitives to avoid name clashes. Default is "merged_."
      show_progress : bool, optional
          If True, print progress to stdout during long operations (primitives/padstacks merging). Default is True.

      Returns
      -------
      bool
          True if the merge was successful, False otherwise.




   .. py:method:: copy_cell_from_edb(edb_path: Union[pyedb.grpc.database.primitive.path.Path, str])

      Copy Cells from another Edb Database into this Database.



