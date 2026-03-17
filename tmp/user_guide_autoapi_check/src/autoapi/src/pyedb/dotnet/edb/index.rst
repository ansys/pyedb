src.pyedb.dotnet.edb
====================

.. py:module:: src.pyedb.dotnet.edb

.. autoapi-nested-parse::

   This module contains the ``Edb`` class.

   This module is implicitly loaded in HFSS 3D Layout when launched.



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.edb.Edb


Module Contents
---------------

.. py:class:: Edb(edbpath: Union[str, pathlib.Path] = None, cellname: str = None, isreadonly: bool = False, isaedtowned: bool = False, oproject=None, use_ppe: bool = False, control_file: str = None, map_file: str = None, technology_file: str = None, layer_filter: str = None, remove_existing_aedt: bool = False)

   Provides the EDB application interface.

   This module inherits all objects that belong to EDB.

   Parameters
   ----------
   edbpath : str, optional
       Full path to the ``aedb`` folder. The variable can also contain
       the path to a layout to import. Allowed formats are BRD, MCM,
       XML (IPC2581), GDS, ODB++(TGZ and ZIP) and DXF. The default is ``None``.
       For GDS import, the Ansys control file (also XML) should have the same
       name as the GDS file. Only the file extension differs.
   cellname : str, optional
       Name of the cell to select. The default is ``None``.
   isreadonly : bool, optional
       Whether to open EBD in read-only mode when it is
       owned by HFSS 3D Layout. The default is ``False``.
   version : str, int, float, optional
       Version of EDB to use. The default is ``None``.
       Examples of input values are ``232``, ``23.2``, ``2023.2``, ``"2023.2"``.
   isaedtowned : bool, optional
       Whether to launch EDB from HFSS 3D Layout. The
       default is ``False``.
   oproject : optional
       Reference to the AEDT project object.
   student_version : bool, optional
       Whether to open the AEDT student version. The default is ``False.``
   control_file : str, optional
           Path to the XML file. The default is ``None``, in which case an attempt is made to find
           the XML file in the same directory as the board file. To succeed, the XML file and board file
           must have the same name. Only the extension differs.
   map_file : str, optional
       Layer map .map file.
   technology_file : str, optional
       Full path to technology file to be converted to xml before importing or xml.
       Supported by GDS format only.
   layer_filter:str,optional
       Layer filter .txt file.

   Examples
   --------
   Create an ``Edb`` object and a new EDB cell.

   >>> from pyedb import Edb
   >>> app = Edb()

   Add a new variable named "s1" to the ``Edb`` instance.

   >>> app["s1"] = "0.25 mm"
   >>> app["s1"].tofloat
   >>> 0.00025
   >>> app["s1"].tostring
   >>> "0.25mm"

   or add a new parameter with description:

   >>> app["s2"] = ["20um", "Spacing between traces"]
   >>> app["s2"].value
   >>> 1.9999999999999998e-05
   >>> app["s2"].description
   >>> "Spacing between traces"

   Create an ``Edb`` object and open the specified project.

   >>> app = Edb("myfile.aedb")

   Create an ``Edb`` object from GDS and control files.
   The XML control file resides in the same directory as the GDS file: (myfile.xml).

   >>> app = Edb("/path/to/file/myfile.gds")



   .. py:property:: logger
      :type: pyedb.edb_logger.EdbLogger


      PyEDB logger.
      Returns
      -------
      EdbLogger object.



   .. py:property:: version
      :type: str


      EDB API version.
      Returns
      -------
          str: version of the edb object.



   .. py:property:: base_path
      :type: str


      Base path for EDB installation.
      Returns
      -------
          str: path to the edb installation.



   .. py:attribute:: standalone
      :value: True



   .. py:attribute:: oproject
      :value: None



   .. py:attribute:: isaedtowned
      :value: False



   .. py:attribute:: isreadonly
      :value: False



   .. py:attribute:: cellname
      :value: None



   .. py:attribute:: edbpath
      :value: None



   .. py:attribute:: log_name
      :value: None



   .. py:property:: pedb_class


   .. py:method:: value(val) -> pyedb.dotnet.database.utilities.value.Value

      Convert a value into a pyedb value.
      Returns
      -------
          class:`Value <pyedb.dotnet.database.utility.Value>`



   .. py:property:: grpc
      :type: bool


      grpc flag.



   .. py:property:: cell_names
      :type: List[str]


      Cell name container.

      Returns
      -------
      list of cell names : List[str]



   .. py:property:: design_variables
      :type: Dict[str, pyedb.dotnet.database.edb_data.variables.Variable]


      Get all edb design variables.

      Returns
      -------
      variable dictionary : Dict[str, :class:`pyedb.dotnet.database.edb_data.variables.Variable`]



   .. py:property:: ansys_em_path
      :type: str


      Base path for EDB installation.
      Returns
      -------
          str: path to the edb installation.



   .. py:property:: project_variables
      :type: Dict[str, pyedb.dotnet.database.edb_data.variables.Variable]


      Get all project variables.

      Returns
      -------
      variables dictionary : Dict[str, :class:`pyedb.dotnet.database.edb_data.variables.Variable`]




   .. py:property:: layout_validation
      :type: pyedb.dotnet.database.layout_validation.LayoutValidation


      :class:`pyedb.dotnet.database.edb_data.layout_validation.LayoutValidation`.

      Returns
      -------
      layout validation object : :class: 'pyedb.dotnet.database.layout_validation.LayoutValidation'



   .. py:property:: variables
      :type: Dict[str, pyedb.dotnet.database.edb_data.variables.Variable]


      Get all Edb variables.

      Returns
      -------
      variables dictionary : Dict[str, :class:`pyedb.dotnet.database.edb_data.variables.Variable`]




   .. py:property:: terminals
      :type: Dict[str, pyedb.dotnet.database.cell.terminal.terminal.Terminal]


      Get terminals belonging to active layout.

      Returns
      -------
      Dict[str, :class:`pyedb.dotnet.database.edb_data.ports.Terminal`]
          Dictionary of terminal names to terminal objects.



   .. py:property:: excitations
      :type: Dict[str, Union[pyedb.dotnet.database.edb_data.ports.BundleWavePort, pyedb.dotnet.database.edb_data.ports.GapPort, pyedb.dotnet.database.edb_data.ports.CircuitPort, pyedb.dotnet.database.edb_data.ports.CoaxPort, pyedb.dotnet.database.edb_data.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,]]




   .. py:property:: ports
      :type: Dict[str, Union[pyedb.dotnet.database.edb_data.ports.BundleWavePort, pyedb.dotnet.database.edb_data.ports.GapPort, pyedb.dotnet.database.edb_data.ports.CircuitPort, pyedb.dotnet.database.edb_data.ports.CoaxPort, pyedb.dotnet.database.edb_data.ports.WavePort]]


      Get all ports.

      Returns
      -------
      port dictionary : Dict[str, [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CircuitPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.CoaxPort`,
                 :class:`pyedb.dotnet.database.edb_data.ports.BundleWavePort`]]




   .. py:property:: excitations_nets
      :type: List[str]


      Get all excitations net names.



   .. py:property:: sources
      :type: Dict[str, pyedb.dotnet.database.edb_data.ports.ExcitationSources]


      Get all layout sources.



   .. py:property:: voltage_regulator_modules
      :type: Dict[str, pyedb.dotnet.database.cell.voltage_regulator.VoltageRegulator]


      Get all voltage regulator modules



   .. py:property:: probes
      :type: Dict[str, Union[pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal, pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal, pyedb.grpc.database.terminal.bundle_terminal.BundleTerminal, pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal, pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal]]


      Get all layout probes.



   .. py:method:: open_edb() -> bool

      Open EDB.

      Returns
      -------
      ``True`` when succeed ``False`` if failed : bool



   .. py:property:: core

      Edb Dotnet Api class.

      Returns
      -------
      :class:`pyedb.dotnet.database.dotnet.database.CellDotNet`



   .. py:method:: create_edb()

      Create EDB.

      Returns
      -------
      ``True`` when succeed ``False`` if failed : bool



   .. py:method:: import_layout_file(input_file, working_dir='', anstranslator_full_path='', use_ppe=False, control_file=None, map_file=None, tech_file=None, layer_filter=None) -> str

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
      Full path to the AEDB file : str




   .. py:method:: import_vlctech_stackup(vlctech_file, working_dir='', export_xml=None)

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
      Full path to the AEDB file : str




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
      >>> # Export to IPC2581 format:
      >>> edb.export_to_ipc2581("output.xml")



   .. py:property:: configuration

      Edb project configuration from file.



   .. py:method:: edb_exception(ex_value, tb_data)

      Write the trace stack to AEDT when a Python error occurs.

      Parameters
      ----------
      ex_value :

      tb_data :


      Returns
      -------
      None




   .. py:property:: active_db
      :type: Any



   .. py:property:: active_cell
      :type: Any


      Active cell.



   .. py:property:: components
      :type: pyedb.dotnet.database.components.Components


      Edb Components methods and properties.

      Returns
      -------
      Instance of :class:`pyedb.dotnet.database.components.Components`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
      >>> comp = edbapp.components.get_component_by_name("J1")



   .. py:property:: design_options
      :type: pyedb.dotnet.database.edb_data.design_options.EdbDesignOptions


      Edb Design Settings and Options.

      Returns
      -------
      Instance of :class:`pyedb.dotnet.database.edb_data.design_options.EdbDesignOptions`



   .. py:property:: stackup
      :type: pyedb.dotnet.database.stackup.Stackup


      Stackup manager.

      Returns
      -------
      Instance of :class: 'pyedb.dotnet.database.Stackup`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
      >>> edbapp.stackup.layers["TOP"].thickness = 4e-5
      >>> edbapp.stackup.layers["TOP"].thickness == 4e-05
      >>> edbapp.stackup.add_layer("Diel", "GND", layer_type="dielectric", thickness="0.1mm", material="FR4_epoxy")



   .. py:property:: source_excitation
      :type: pyedb.dotnet.database.source_excitations.SourceExcitation


      Source excitation management.

      .. deprecated:: 0.70
         Use: func:`excitation_manager` property instead.
      Returns
      -------
      :class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`
          Source and port creation tools.



   .. py:property:: excitation_manager
      :type: None | pyedb.dotnet.database.source_excitations.SourceExcitation


      Source excitation manager.

      Returns
      -------
      :class:`SourceExcitation <pyedb.grpc.database.source_excitations.SourceExcitation>`
          Source and port creation tools.



   .. py:property:: materials
      :type: pyedb.dotnet.database.materials.Materials | None


      Material Database.

      Returns
      -------
      Instance of :class: `pyedb.dotnet.database.Materials`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb()
      >>> edbapp.materials.add_material("air", permittivity=1.0)
      >>> edbapp.materials.add_debye_material("debye_mat", 5, 3, 0.02, 0.05, 1e5, 1e9)
      >>> edbapp.materials.add_djordjevicsarkar_material("djord_mat", 3.3, 0.02, 3.3)



   .. py:property:: padstacks
      :type: pyedb.dotnet.database.padstack.EdbPadstacks | None


      Core padstack.


      Returns
      -------
      Instance of :class: `legacy.database.padstack.EdbPadstack`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
      >>> p = edbapp.padstacks.create(padstackname="myVia_bullet", antipad_shape="Bullet")
      >>> edbapp.padstacks.get_pad_parameters(
      >>> ... p, "TOP", edbapp.padstacks.pad_type.RegularPad
      >>> ... )



   .. py:property:: siwave
      :type: pyedb.dotnet.database.siwave.EdbSiwave | None


      Core SIWave methods and properties.

      Returns
      -------
      Instance of :class: `pyedb.dotnet.database.siwave.EdbSiwave`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
      >>> p2 = edbapp.excitation_manager.create_circuit_port_on_net("U2A5", "V3P3_S0", "U2A5", "GND", 50, "test")



   .. py:property:: hfss
      :type: pyedb.dotnet.database.hfss.EdbHfss | None


      Core HFSS methods and properties.

      Returns
      -------
      :class:`pyedb.dotnet.database.hfss.EdbHfss`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")




   .. py:property:: nets
      :type: None | pyedb.dotnet.database.nets.EdbNets


      Core nets.

      Returns
      -------
      :class:`legacy.database.nets.EdbNets`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb"myproject.aedb")
      >>> edbapp.nets.find_or_create_net("GND")
      >>> edbapp.nets.find_and_fix_disjoint_nets("GND", keep_only_main_net=True)



   .. py:property:: net_classes
      :type: pyedb.dotnet.database.net_class.EdbNetClasses | None


      Get all net classes.

      Returns
      -------
      :class:`legacy.database.nets.EdbNetClasses`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
      >>> edbapp.net_classes



   .. py:property:: extended_nets
      :type: pyedb.dotnet.database.net_class.EdbExtendedNets | None


      Get all extended nets.

      Returns
      -------
      :class:`legacy.database.nets.EdbExtendedNets`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
      >>> edbapp.extended_nets



   .. py:property:: differential_pairs
      :type: pyedb.dotnet.database.net_class.EdbDifferentialPairs | None


      Get all differential pairs.

      Returns
      -------
      :class:`legacy.database.nets.EdbDifferentialPairs`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
      >>> edbapp.differential_pairs



   .. py:property:: modeler
      :type: pyedb.dotnet.database.modeler.Modeler | None


      Core primitives modeler.

      Returns
      -------
      Instance of :class: `legacy.database.layout.EdbLayout`

      Examples
      --------
      >>> from pyedb import Edb
      >>> edbapp = Edb("myproject.aedb")
      >>> top_prims = edbapp.modeler.primitives_by_layer["TOP"]



   .. py:property:: layout
      :type: pyedb.dotnet.database.cell.layout.Layout


      Layout object.

      Returns
      -------
      :class:`legacy.database.dotnet.layout.Layout`



   .. py:property:: active_layout
      :type: Any


      Active layout.

      Returns
      -------
      Instance of EDB API Layout Class.



   .. py:property:: layout_instance

      Edb Layout Instance.



   .. py:property:: layout_bounding_box
      :type: list[float]


      Get the bounding box of the active layout.

      Returns
      -------
      list[float]
          Bounding box coordinates as [xmin, ymin, xmax, ymax].



   .. py:method:: get_connected_objects(layout_object_instance) -> List[Union[pyedb.dotnet.database.edb_data.padstacks_data.EDBPadstackInstance, pyedb.dotnet.database.cell.primitive.path.Path, pyedb.dotnet.database.edb_data.primitives_data.EdbRectangle, pyedb.dotnet.database.edb_data.primitives_data.EdbCircle, pyedb.dotnet.database.edb_data.primitives_data.EdbPolygon]]

      Get connected objects.

      Returns
      -------
      list



   .. py:class:: Boundaries

      Boundaries Enumerator.

      Returns
      -------
      int



   .. py:method:: edb_value(value, var_server=None) -> Any

      Convert a value to an EDB value. Value can be a string, float or integer. Mainly used in internal calls.

      Parameters
      ----------
      value : str, float, int


      Returns
      -------
      Instance of `Edb.Utility.Value`




   .. py:method:: point_3d(x, y, z=0.0) -> Any

      Compute the Edb 3d Point Data.

      Parameters
      ----------
      x : float, int or str
          X value.
      y : float, int or str
          Y value.
      z : float, int or str, optional
          Z value.

      Returns
      -------
      ``Geometry.Point3DData``.



   .. py:method:: copy_cells(cells_to_copy) -> Any

      Copy Cells from other Databases or this Database into this Database.

      Parameters
      ----------
      cells_to_copy : list[:class:`Cell <ansys.edb.layout.Cell>`]
          Cells to copy.

      Returns
      -------
      list[:class:`Cell <ansys.edb.layout.Cell>`]
          New Cells created in this Database.



   .. py:method:: point_data(x, y=None) -> Any

      Compute the Edb Point Data.

      Parameters
      ----------
      x : float, int or str
          X value.
      y : float, int or str, optional
          Y value.


      Returns
      -------
      ``Geometry.PointData``.



   .. py:method:: close_edb() -> bool

      Close EDB and cleanup variables.

      . deprecated:: pyedb 0.47.0
      Use: func:`close` instead.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: close(**kwargs) -> bool

      Close EDB and cleanup variables.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: save_edb() -> bool

      Save the EDB file.

      . deprecated:: pyedb 0.47.0
      Use: func:`save` instead.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: save() -> bool

      Save the EDB file.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: save_edb_as(path) -> bool

      Save the EDB file as another file.

      . deprecated:: pyedb 0.47.0
      Use: func:`save_as` instead.


      Parameters
      ----------
      path : str
          Name of the new file to save to.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: save_as(path: str | pathlib.Path) -> bool

      Save the EDB file as another file.

      Parameters
      ----------
      path : str
          Name of the new file to save to.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: execute(func)

      Execute a function.

      Parameters
      ----------
      func : str
          Function to execute.


      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: import_cadence_file(inputBrd, WorkDir=None, anstranslator_full_path='', use_ppe=False) -> bool

      Import a board file and generate an ``edb.def`` file in the working directory.

      Parameters
      ----------
      inputBrd : str
          Full path to the board file.
      WorkDir : str, optional
          Directory in which to create the ``aedb`` folder. The default value is ``None``,
          in which case the AEDB file is given the same name as the board file. Only
          the extension differs.
      anstranslator_full_path : str, optional
          Full path to the Ansys translator.
      use_ppe : bool, optional
          Whether to use the PPE License. The default is ``False``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.




   .. py:method:: cutout(signal_nets=None, reference_nets=None, extent_type='ConvexHull', expansion_size=0.002, use_round_corner=False, output_aedb_path=None, open_cutout_at_end=True, use_pyaedt_cutout=True, number_of_threads=1, use_pyaedt_extent_computing=True, extent_defeature=0, remove_single_pin_components=False, custom_extent=None, custom_extent_units='mm', include_partial_instances=False, keep_voids=True, check_terminals=False, include_pingroups=False, expansion_factor=0, maximum_iterations=10, preserve_components_with_model=False, simple_pad_check=True, keep_lines_as_path=False, include_voids_in_extents=False) -> list[list[float | complex | Any]] | list | list[list] | None

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





   .. py:method:: get_conformal_polygon_from_netlist(netlist=None)

      Return an EDB conformal polygon based on a netlist.

      Parameters
      ----------

      netlist : List of net names.
          list[str]

      Returns
      -------
      :class:`Edb.Cell.Primitive.Polygon`
          Edb polygon object.




   .. py:method:: number_with_units(value, units=None)

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




   .. py:method:: write_export3d_option_config_file(path_to_output, config_dictionaries=None)

      Write the options for a 3D export to a configuration file.

      Parameters
      ----------
      path_to_output : str
          Full path to the configuration file to save 3D export options to.

      config_dictionaries : dict, optional
          Configuration dictionaries. The default is ``None``.




   .. py:method:: export_hfss(path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False)

      Export EDB to HFSS.

      Parameters
      ----------
      path_to_output : str
          Full path and name for saving the AEDT file.
      net_list : list, optional
          List of nets to export if only certain ones are to be exported.
          The default is ``None``, in which case all nets are eported.
      num_cores : int, optional
          Number of cores to use for the export. The default is ``None``.
      aedt_file_name : str, optional
          Name of the AEDT output file without the ``.aedt`` extension. The default is ``None``,
          in which case the default name is used.
      hidden : bool, optional
          Open Siwave in embedding mode. User will only see Siwave Icon but UI will be hidden.

      Returns
      -------
      str
          Full path to the AEDT file.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edb = Edb(edbpath="C:\temp\myproject.aedb", version="2023.2")

      >>> options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
      >>> edb.write_export3d_option_config_file(r"C:\temp", options_config)
      >>> edb.export_hfss(r"C:\temp")



   .. py:method:: export_q3d(path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False)

      Export EDB to Q3D.

      Parameters
      ----------
      path_to_output : str
          Full path and name for saving the AEDT file.
      net_list : list, optional
          List of nets to export only if certain ones are to be exported.
          The default is ``None``, in which case all nets are eported.
      num_cores : int, optional
          Number of cores to use for the export. The default is ``None``.
      aedt_file_name : str, optional
          Name of the AEDT output file without the ``.aedt`` extension. The default is ``None``,
          in which case the default name is used.
      hidden : bool, optional
          Open Siwave in embedding mode. User will only see Siwave Icon but UI will be hidden.

      Returns
      -------
      str
          Full path to the AEDT file.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edb = Edb(edbpath="C:\temp\myproject.aedb", version="2021.2")
      >>> options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
      >>> edb.write_export3d_option_config_file("C:\temp", options_config)
      >>> edb.export_q3d("C:\temp")



   .. py:method:: export_maxwell(path_to_output, net_list=None, num_cores=None, aedt_file_name=None, hidden=False)

      Export EDB to Maxwell 3D.

      Parameters
      ----------
      path_to_output : str
          Full path and name for saving the AEDT file.
      net_list : list, optional
          List of nets to export only if certain ones are to be
          exported. The default is ``None``, in which case all nets are exported.
      num_cores : int, optional
          Number of cores to use for the export. The default is ``None.``
      aedt_file_name : str, optional
          Name of the AEDT output file without the ``.aedt`` extension. The default is ``None``,
          in which case the default name is used.
      hidden : bool, optional
          Open Siwave in embedding mode. User will only see Siwave Icon but UI will be hidden.

      Returns
      -------
      str
          Full path to the AEDT file.

      Examples
      --------

      >>> from pyedb import Edb

      >>> edb = Edb(edbpath="C:\temp\myproject.aedb", version="2021.2")

      >>> options_config = {"UNITE_NETS": 1, "LAUNCH_Q3D": 0}
      >>> edb.write_export3d_option_config_file("C:\temp", options_config)
      >>> edb.export_maxwell("C:\temp")



   .. py:method:: solve_siwave()

      Close EDB and solve it with Siwave.

      Returns
      -------
      str
          Siwave project path.



   .. py:method:: export_siwave_dc_results(siwave_project, solution_name, output_folder=None, html_report=True, vias=True, voltage_probes=True, current_sources=True, voltage_sources=True, power_tree=True, loop_res=True)

      Close EDB and solve it with Siwave.

      Parameters
      ----------
      siwave_project : str
          Siwave full project name.
      solution_name : str
          Siwave DC Analysis name.
      output_folder : str, optional
          Ouptu folder where files will be downloaded.
      html_report : bool, optional
          Either if generate or not html report. Default is `True`.
      vias : bool, optional
          Either if generate or not vias report. Default is `True`.
      voltage_probes : bool, optional
          Either if generate or not voltage probe report. Default is `True`.
      current_sources : bool, optional
          Either if generate or not current source report. Default is `True`.
      voltage_sources : bool, optional
          Either if generate or not voltage source report. Default is `True`.
      power_tree : bool, optional
          Either if generate or not power tree image. Default is `True`.
      loop_res : bool, optional
          Either if generate or not loop resistance report. Default is `True`.

      Returns
      -------
      list
          List of files generated.



   .. py:method:: variable_exists(variable_name)

      Check if a variable exists or not.

      Returns
      -------
      tuple of bool and VariableServer
          It returns a booleand to check if the variable exists and the variable
          server that should contain the variable.



   .. py:method:: get_all_variable_names()

      Method added for compatibility with grpc.

      Returns
      -------
      List[Str]
          List of variables name.




   .. py:method:: get_variable(variable_name)

      Return Variable Value if variable exists.

      Parameters
      ----------
      variable_name

      Returns
      -------
      :class:`pyedb.dotnet.database.edb_data.edbvalue.EdbValue`



   .. py:method:: add_project_variable(variable_name, variable_value, description='')

      Add a variable to edb database (project). The variable will have the prefix `$`.

      ..note::
          User can use also the setitem to create or assign a variable. See example below.

      Parameters
      ----------
      variable_name : str
          Name of the variable. Name can be provided without ``$`` prefix.
      variable_value : str, float
          Value of the variable with units.
      description : str, optional
          Description of the variable.

      Returns
      -------
      tuple
          Tuple containing the ``AddVariable`` result and variable server.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edb_app = Edb()
      >>> boolean_1, ant_length = edb_app.add_project_variable("my_local_variable", "1cm")
      >>> print(edb_app["$my_local_variable"])  # using getitem
      >>> edb_app["$my_local_variable"] = "1cm"  # using setitem




   .. py:method:: add_design_variable(variable_name, variable_value, is_parameter=False, description='')

      Add a variable to edb. The variable can be a design one or a project variable (using ``$`` prefix).

      ..note::
          User can use also the setitem to create or assign a variable. See example below.

      Parameters
      ----------
      variable_name : str
          Name of the variable. To added the variable as a project variable, the name
          must begin with ``$``.
      variable_value : str, float
          Value of the variable with units.
      is_parameter : bool, optional
          Whether to add the variable as a local variable. The default is ``False``.
          When ``True``, the variable is added as a parameter default.
      description : str, optional
          Description of the variable.
      Returns
      -------
      tuple
          Tuple containing the ``AddVariable`` result and variable server.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edb_app = Edb()
      >>> boolean_1, ant_length = edb_app.add_design_variable("my_local_variable", "1cm")
      >>> print(edb_app["my_local_variable"])  # using getitem
      >>> edb_app["my_local_variable"] = "1cm"  # using setitem
      >>> boolean_2, para_length = edb_app.change_design_variable_value("my_parameter", "1m", is_parameter=True
      >>> boolean_3, project_length = edb_app.change_design_variable_value("$my_project_variable", "1m")





   .. py:method:: change_design_variable_value(variable_name, variable_value)

      Change a variable value.

      ..note::
          User can use also the getitem to read the variable value. See example below.

      Parameters
      ----------
      variable_name : str
          Name of the variable.
      variable_value : str, float
          Value of the variable with units.

      Returns
      -------
      tuple
          Tuple containing the ``SetVariableValue`` result and variable server.

      Examples
      --------

      >>> from pyedb import Edb
      >>> edb_app = Edb()
      >>> boolean, ant_length = edb_app.add_design_variable("ant_length", "1cm")
      >>> boolean, ant_length = edb_app.change_design_variable_value("ant_length", "1m")
      >>> print(edb_app["ant_length"])  # using getitem



   .. py:method:: get_bounding_box()

      Get the layout bounding box.

      Returns
      -------
      list of list of double
          Bounding box as a [lower-left X, lower-left Y], [upper-right X, upper-right Y]) pair in meters.



   .. py:method:: get_statistics(compute_area=False)

      Get the EDBStatistics object.

      Returns
      -------
      EDBStatistics object from the loaded layout.



   .. py:method:: are_port_reference_terminals_connected(common_reference=None)

      Check if all terminal references in design are connected.
      If the reference nets are different, there is no hope for the terminal references to be connected.
      After we have identified a common reference net we need to loop the terminals again to get
      the correct reference terminals that uses that net.

      Parameters
      ----------
      common_reference : str, optional
          Common Reference name. If ``None`` it will be searched in ports terminal.
          If a string is passed then all excitations must have such reference assigned.

      Returns
      -------
      bool
          Either if the ports are connected to reference_name or not.

      Examples
      --------
      >>> from pyedb import Edb
      >>>edb = Edb()
      >>> edb.excitation_manager.create_edge_port_vertical(prim_1_id, ["-66mm", "-4mm"], "port_ver")
      >>> edb.excitation_manager.create_edge_port_horizontal(
      >>> ... prim_1_id, ["-60mm", "-4mm"], prim_2_id, ["-59mm", "-4mm"], "port_hori", 30, "Lower"
      >>> ... )
      >>> edb.excitation_manager.create_wave_port(traces[0].id, trace_paths[0][0], "wave_port")
      >>> edb.cutout(["Net1"])
      >>> assert edb.are_port_reference_terminals_connected()



   .. py:property:: setups

      Get the dictionary of all EDB HFSS and SIwave setups.

      Returns
      -------
      Dict[str, :class:`legacy.database.edb_data.hfss_simulation_setup_data.HfssSimulationSetup`] or
      Dict[str, :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveDCSimulationSetup`] or
      Dict[str, :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`]




   .. py:property:: hfss_setups

      Active HFSS setup in EDB.

      Returns
      -------
      Dict[str, :class:`legacy.database.edb_data.hfss_simulation_setup_data.HfssSimulationSetup`]




   .. py:property:: siwave_dc_setups

      Active Siwave DC IR Setups.

      Returns
      -------
      Dict[str, :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveDCSimulationSetup`]



   .. py:property:: siwave_ac_setups

      Active Siwave SYZ setups.

      Returns
      -------
      Dict[str, :class:`legacy.database.edb_data.siwave_simulation_setup_data.SiwaveSYZSimulationSetup`]



   .. py:method:: create_hfss_setup(name=None)

      Create an HFSS simulation setup from a template.



   .. py:method:: create_raptorx_setup(name=None)

      Create a RaptorX simulation setup.



   .. py:method:: create_hfsspi_setup(name=None)

      Create an HFSS PI simulation setup from a template.

      .. deprecated:: 0.70.0
              Use :func:`legacy.simulation_setups.create_hfss_pi_setup` instead.

      Parameters
      ----------
      name : str, optional
          Setup name.

      Returns
      -------
      :class:`legacy.database.edb_data.hfss_pi_simulation_setup_data.HFSSPISimulationSetup when succeeded, ``False``
      when failed.




   .. py:method:: create_siwave_syz_setup(name=None, **kwargs)

      Create a Siwave SYZ setup from a template.



   .. py:method:: create_siwave_dc_setup(name=None, **kwargs)

      Create a Siwave DC IR setup from a template.



   .. py:method:: calculate_initial_extent(expansion_factor)

      Compute a float representing the larger number between the dielectric thickness or trace width
      multiplied by the nW factor. The trace width search is limited to nets with ports attached.

      Parameters
      ----------
      expansion_factor : float
          Value for the width multiplier (nW factor).

      Returns
      -------
      float



   .. py:method:: copy_zones(working_directory=None)

      Copy multizone EDB project to one new edb per zone.

      Parameters
      ----------
      working_directory : str
          Directory path where all EDB project are copied, if empty will use the current EDB project.

      Returns
      -------
         dict[str](int, EDB PolygonData)
         Return a dictionary with edb path as key and tuple Zone Id as first item and EDB polygon Data defining
         the region as second item.




   .. py:method:: cutout_multizone_layout(zone_dict, common_reference_net=None)

      Create a multizone project cutout.

      Parameters
      ----------
      zone_dict : dict[str](EDB PolygonData)
          Dictionary with EDB path as key and EDB PolygonData as value defining the zone region.
          This dictionary is returned from the command copy_zones():
          >>> edb = Edb(edb_file)
          >>> zone_dict = edb.copy_zones("C:/Temp/test")

      common_reference_net : str
          the common reference net name. This net name must be provided to provide a valid project.

      Returns
      -------
      dict[str][str] , list of str
      first dictionary defined_ports with edb name as key and existing port name list as value. Those ports are the
      ones defined before processing the multizone clipping.
      second is the list of connected port.




   .. py:method:: create_port(terminal: pyedb.dotnet.database.cell.terminal.edge_terminal.EdgeTerminal | pyedb.dotnet.database.cell.terminal.padstack_instance_terminal.PadstackInstanceTerminal | pyedb.dotnet.database.cell.terminal.point_terminal.PointTerminal | pyedb.dotnet.database.cell.terminal.pingroup_terminal.PinGroupTerminal, ref_terminal=None, is_circuit_port=False, name=None)

      Create a port.

      ..deprecated:: 0.70.0
         :func:`create_port` has been moved to edb.excitation_manager.create_port.

      Parameters
      ----------
      terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
          Positive terminal of the port.
      ref_terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
          class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
          optional
          Negative terminal of the port.
      is_circuit_port : bool, optional
          Whether it is a circuit port. The default is ``False``.
      name: str, optional
          Name of the created port. The default is None, a random name is generated.
      Returns
      -------
      list: [:class:`pyedb.dotnet.database.edb_data.ports.GapPort`,
          :class:`pyedb.dotnet.database.edb_data.ports.WavePort`,].



   .. py:method:: create_voltage_probe(terminal, ref_terminal)

      Create a voltage probe.

      ..deprecated:: 0.70.0
         :func:`create_voltage_probe` has been moved to edb.excitation_manager.create_voltage_probe.

      Parameters
      ----------
      terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
          Positive terminal of the port.
      ref_terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,
          :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`,
          Negative terminal of the probe.

      Returns
      -------
      pyedb.dotnet.database.edb_data.terminals.Terminal



   .. py:method:: create_voltage_source(terminal, ref_terminal)

      Create a voltage source.

      ..deprecated:: 0.70.0
         :func:`create_voltage_source` has been moved to edb.excitation_manager.create_voltage_source.

      Parameters
      ----------
      terminal : :class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`
          Positive terminal of the port.
      ref_terminal : class:`pyedb.dotnet.database.edb_data.terminals.EdgeTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PadstackInstanceTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PointTerminal`,             :class:`pyedb.dotnet.database.edb_data.terminals.PinGroupTerminal`
          Negative terminal of the source.

      Returns
      -------
      class:`legacy.database.edb_data.ports.ExcitationSources`



   .. py:method:: create_current_source(terminal, ref_terminal)

      Create a current source.

      ..deprecated:: 0.70.0
         :func:`create_current_source` has been moved to edb.excitation_manager.create_current_source.

      Parameters
      ----------
      terminal : :class:`legacy.database.edb_data.terminals.EdgeTerminal`,
          :class:`legacy.database.edb_data.terminals.PadstackInstanceTerminal`,
          :class:`legacy.database.edb_data.terminals.PointTerminal`,
          :class:`legacy.database.edb_data.terminals.PinGroupTerminal`,
          Positive terminal of the port.
      ref_terminal : class:`legacy.database.edb_data.terminals.EdgeTerminal`,
          :class:`legacy.database.edb_data.terminals.PadstackInstanceTerminal`,
          :class:`legacy.database.edb_data.terminals.PointTerminal`,
          :class:`legacy.database.edb_data.terminals.PinGroupTerminal`,
          Negative terminal of the source.

      Returns
      -------
      :class:`legacy.edb_core.edb_data.ports.ExcitationSources`



   .. py:method:: get_point_terminal(name, net_name, location, layer)

      Place a voltage probe between two points.

      ..deprecated:: 0.70.0
         :func:`get_point_terminal` has been moved to edb.excitation_manager.get_point_terminal.

      Parameters
      ----------
      name : str,
          Name of the terminal.
      net_name : str
          Name of the net.
      location : list
          Location of the terminal.
      layer : str,
          Layer of the terminal.

      Returns
      -------
      :class:`legacy.edb_core.edb_data.terminals.PointTerminal`



   .. py:method:: auto_parametrize_design(layers=True, materials=True, via_holes=True, pads=True, antipads=True, traces=True, layer_filter=None, material_filter=None, padstack_definition_filter=None, trace_net_filter=None, use_single_variable_for_padstack_definitions=True, use_relative_variables=True, output_aedb_path=None, open_aedb_at_end=True, expand_polygons_size=0, expand_voids_size=0, via_offset=True)

      Assign automatically design and project variables with current values.

      Parameters
      ----------
      layers : bool, optional
          Enable layer thickness parametrization. Default value is ``True``.
      materials : bool, optional
          Enable material parametrization. Default value is ``True``.
      via_holes : bool, optional
          Enable via diameter parametrization. Default value is ``True``.
      pads : bool, optional
          Enable pads size parametrization. Default value is ``True``.
      antipads : bool, optional
          Enable anti pads size parametrization. Default value is ``True``.
      traces : bool, optional
          Enable trace width parametrization. Default value is ``True``.
      layer_filter : str, List(str), optional
          Enable layer filter. Default value is ``None``, all layers are parametrized.
      material_filter : str, List(str), optional
          Enable material filter. Default value is ``None``, all material are parametrized.
      padstack_definition_filter : str, List(str), optional
          Enable padstack definition filter. Default value is ``None``, all padsatcks are parametrized.
      trace_net_filter : str, List(str), optional
          Enable nets filter for trace width parametrization. Default value is ``None``, all layers are parametrized.
      use_single_variable_for_padstack_definitions : bool, optional
          Whether to use a single design variable for each padstack definition or a variable per pad layer.
          Default value is ``True``.
      use_relative_variables : bool, optional
          Whether if use an absolute variable for each trace, padstacks and layers or a delta variable instead.
          Default value is ``True``.
      output_aedb_path : str, optional
          Full path and name for the new AEDB file. If None, then current aedb will be cutout.
      open_aedb_at_end : bool, optional
          Whether to open the cutout at the end. The default is ``True``.
      expand_polygons_size : float, optional
          Expansion size on polygons. Polygons will be expanded in all directions. The default is ``0``.
      expand_voids_size : float, optional
          Expansion size on polygon voids. Polygons voids will be expanded in all directions. The default is ``0``.
      via_offset : bool, optional
          Whether if offset the via position or not. The default is ``True``.

      Returns
      -------
      List(str)
          List of all parameters name created.



   .. py:method:: create_model_for_arbitrary_wave_ports(temp_directory, mounting_side='top', signal_nets=None, terminal_diameter=None, output_edb=None, launching_box_thickness='100um')

      Generate EDB design to be consumed by PyAEDT to generate arbitrary wave ports shapes.
      This model has to be considered as merged onto another one. The current opened design must have voids
      surrounding the pad-stacks where wave ports terminal will be created. THe open design won't be edited, only
      primitives like voids and pads-stack definition included in the voids are collected to generate a new design.

      Parameters
      ----------
      temp_directory : str
          Temporary directory used during the method execution.

      mounting_side : str
          Gives the orientation to be considered for the current design. 2 options are available ``"top"`` and
          ``"bottom". Default value is ``"top"``. If ``"top"`` is selected the method will voids at the top signal
          layer, and the bottom layer if ``"bottom"`` is used.

      signal_nets : List[str], optional
          Provides the nets to be included for the model creation. Default value is ``None``. If None is provided,
          all nets will be included.

      terminal_diameter : float, str, optional
          When ``None``, the terminal diameter is evaluated at each pads-tack instance found inside the voids. The top
          or bottom layer pad diameter will be taken, depending on ``mounting_side`` selected. If value is provided,
          it will overwrite the evaluated diameter.

      output_edb : str, optional
          The output EDB absolute. If ``None`` the edb is created in the ``temp_directory`` as default name
          `"waveport_model.aedb"``

      launching_box_thickness : float, str, optional
          Launching box thickness  used for wave ports. Default value is ``"100um"``.

      Returns
      -------
      bool
          ``True`` when succeeded, ``False`` if failed.



   .. py:property:: definitions

      Definitions class.



   .. py:property:: workflow

      Workflow class.



   .. py:method:: export_gds_comp_xml(comps_to_export, gds_comps_unit='mm', control_path=None)

      Exports an XML file with selected components information for use in a GDS import.

      Parameters
      ----------
      comps_to_export : list
          List of components whose information will be exported to xml file.
      gds_comps_unit : str, optional
          GDS_COMPONENTS section units. Default is ``"mm"``.
      control_path : str, optional
          Path for outputting the XML file.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



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



   .. py:property:: simulation_setups
      :type: pyedb.dotnet.database.simulation_setups.SimulationSetups


      Get all simulation setups object.



