hfss_auto_configuration
=======================

.. py:module:: hfss_auto_configuration

.. autoapi-nested-parse::

   HFSS automatic configuration workflow for SI/PI analysis.

   This module provides tools to automatically configure HFSS simulations from EDB designs,
   including net grouping, batch processing, cutout generation, port creation, and
   simulation setup.

   Examples
   --------
   Basic workflow for automatic HFSS configuration:

   >>> from pyedb import Edb
   >>> from pyedb.workflows.sipi.hfss_auto_configuration import HFSSAutoConfiguration
   >>> edb = Edb("design.aedb")
   >>> config = HFSSAutoConfiguration(edb)
   >>> config.source_edb_path = "design.aedb"
   >>> config.target_edb_path = "design_hfss.aedb"
   >>> config.auto_populate_batch_groups()
   >>> config.create_projects()

   Create configuration with specific net groups:

   >>> config = HFSSAutoConfiguration()
   >>> config.source_edb_path = "my_design.aedb"
   >>> config.group_nets_by_prefix(["DDR", "PCIe", "USB"])
   >>> config.add_solder_ball("U1", diameter="0.3mm", height="0.2mm")
   >>> config.create_projects()



Attributes
----------

.. autoapisummary::

   hfss_auto_configuration.ref_patterns
   hfss_auto_configuration.combined_ref


Classes
-------

.. autoapisummary::

   hfss_auto_configuration.SolderBallsInfo
   hfss_auto_configuration.SimulationSetup
   hfss_auto_configuration.BatchGroup
   hfss_auto_configuration.HFSSAutoConfiguration


Functions
---------

.. autoapisummary::

   hfss_auto_configuration.create_hfss_auto_configuration


Module Contents
---------------

.. py:data:: ref_patterns
   :value: ['^GND\\d*$', '^GND_\\w+', '^GND$', '^VSS\\d*$', '^VSS\\w*', '^DGND$', '^AGND$', '^PGND$',...


.. py:data:: combined_ref

.. py:class:: SolderBallsInfo

   Solder ball configuration for component modeling.

   This dataclass stores geometric parameters for solder ball definitions
   used in HFSS port creation and component modeling.

   Attributes
   ----------
   ref_des : str
       Reference designator of the component. The default is ``""``.
   shape : str
       Geometric shape of the solder ball: ``"cylinder"``, ``"sphere"``,
       or ``"spheroid"``. The default is ``"cylinder"``.
   diameter : str or float or None
       Nominal diameter of the solder ball. The default is ``None``.
   mid_diameter : str or float or None
       Middle diameter for spheroid shapes only. The default is ``None``.
   height : str or float or None
       Height of the solder ball. The default is ``None``.

   Examples
   --------
   >>> ball = SolderBallsInfo(ref_des="U1", shape="cylinder", diameter="0.3mm", height="0.2mm")
   >>> ball.ref_des
   'U1'
   >>> ball.diameter
   '0.3mm'


   .. py:attribute:: ref_des
      :type:  str
      :value: ''



   .. py:attribute:: shape
      :type:  str
      :value: 'cylinder'



   .. py:attribute:: diameter
      :type:  str | float | None
      :value: None



   .. py:attribute:: mid_diameter
      :type:  str | float | None
      :value: None



   .. py:attribute:: height
      :type:  str | float | None
      :value: None



.. py:class:: SimulationSetup

   HFSS simulation setup parameters.

   This dataclass defines the simulation configuration including meshing
   frequency, convergence criteria, and frequency sweep settings.

   Attributes
   ----------
   meshing_frequency : str or float
       Driven frequency used during mesh generation. The default is ``"10GHz"``.
   maximum_pass_number : int
       Maximum number of adaptive passes. The default is ``15``.
   start_frequency : str or float
       Lower bound of the frequency sweep. The default is ``0``.
   stop_frequency : str or float
       Upper bound of the frequency sweep. The default is ``"40GHz"``.
   frequency_step : str or float
       Linear step size for the frequency sweep. The default is ``"0.05GHz"``.

   Examples
   --------
   >>> setup = SimulationSetup(meshing_frequency="5GHz", maximum_pass_number=20, stop_frequency="60GHz")
   >>> setup.maximum_pass_number
   20
   >>> setup.stop_frequency
   '60GHz'


   .. py:attribute:: meshing_frequency
      :type:  str | float
      :value: '10GHz'



   .. py:attribute:: maximum_pass_number
      :type:  int
      :value: 15



   .. py:attribute:: start_frequency
      :type:  str | float
      :value: 0



   .. py:attribute:: stop_frequency
      :type:  str | float
      :value: '40GHz'



   .. py:attribute:: frequency_step
      :type:  str | float
      :value: '0.05GHz'



.. py:class:: BatchGroup

   Group of nets to be processed together in a batch simulation.

   This dataclass represents a collection of signal nets that will be
   simulated together with optional custom simulation settings.

   Attributes
   ----------
   name : str
       Descriptive name for the batch group. The default is ``""``.
   nets : list of str
       List of net names to include in this batch. The default is an empty list.
   simulation_setup : SimulationSetup or None
       Custom simulation settings for this batch. If ``None``, the global
       configuration settings are used. The default is ``None``.

   Examples
   --------
   >>> group = BatchGroup(
   ...     name="DDR4_Signals",
   ...     nets=["DDR4_DQ0", "DDR4_DQ1", "DDR4_CLK"],
   ...     simulation_setup=SimulationSetup(stop_frequency="20GHz"),
   ... )
   >>> group.name
   'DDR4_Signals'
   >>> len(group.nets)
   3


   .. py:attribute:: name
      :type:  str
      :value: ''



   .. py:attribute:: nets
      :type:  list[str]
      :value: []



   .. py:attribute:: simulation_setup
      :type:  SimulationSetup | None
      :value: None



.. py:class:: HFSSAutoConfiguration(edb=None)

   Automatic HFSS simulation configuration from EDB designs.

   This class automates the process of configuring HFSS simulations including
   net grouping, cutout creation, port generation, and simulation setup.

   Parameters
   ----------
   edb : Edb or None, optional
       Existing EDB object instance. If ``None``, a new instance will be created
       from the source path. The default is ``None``.

   Attributes
   ----------
   ansys_version : str
       ANSYS Electronics Desktop version to use. The default is ``"2025.2"``.
   grpc : bool
       Whether to use gRPC API mode. The default is ``True``.
   source_edb_path : str
       Path to the source EDB file.
   target_edb_path : str
       Path where the configured EDB will be saved.
   batch_group_folder : str
       Folder path for storing batch group projects.
   signal_nets : list
       List of signal net names to include in the simulation.
   power_nets : list
       List of power net names.
   reference_net : str
       Name of the reference (ground) net.
   batch_size : int
       Maximum number of nets per batch group. The default is ``100``.
   batch_groups : list of BatchGroup
       Configured batch groups for simulation.
   components : list of str
       Component reference designators to include.
   solder_balls : list of SolderBallsInfo
       Solder ball configurations for components.
   simulation_setup : SimulationSetup
       Global simulation settings.
   extent_type : str
       Cutout extent algorithm: ``"bounding_box"``, ``"convex_hull"``,
       or ``"conformal"``. The default is ``"bounding_box"``.
   cutout_expansion : str or float
       Cutout expansion margin. The default is ``"2mm"``.
   auto_mesh_seeding : bool
       Enable automatic mesh seeding. The default is ``True``.
   port_type : str
       Port type to create: ``"coaxial"`` or ``"circuit_port"``.
       The default is ``"coaxial"``.
   create_pin_group : bool
       Whether to create pin groups for circuit ports. The default is ``False``.

   Examples
   --------
   Basic configuration:

   >>> from pyedb import Edb
   >>> config = HFSSAutoConfiguration()
   >>> config.source_edb_path = "design.aedb"
   >>> config.target_edb_path = "design_hfss.aedb"
   >>> config.auto_populate_batch_groups()
   >>> config.create_projects()

   Configure with existing EDB:

   >>> edb = Edb("design.aedb")
   >>> config = HFSSAutoConfiguration(edb)
   >>> config.signal_nets = ["DDR4_DQ0", "DDR4_CLK"]
   >>> config.reference_net = "GND"
   >>> config.add_solder_ball("U1", diameter="0.3mm", height="0.2mm")


   .. py:attribute:: ansys_version
      :type:  str
      :value: '2025.2'



   .. py:attribute:: grpc
      :type:  bool
      :value: True



   .. py:attribute:: source_edb_path
      :type:  str
      :value: ''



   .. py:attribute:: target_edb_path
      :type:  str
      :value: ''



   .. py:attribute:: batch_group_folder
      :type:  str
      :value: ''



   .. py:attribute:: signal_nets
      :type:  list
      :value: []



   .. py:attribute:: power_nets
      :type:  list
      :value: []



   .. py:attribute:: reference_net
      :type:  str
      :value: ''



   .. py:attribute:: batch_size
      :type:  int
      :value: 100



   .. py:attribute:: batch_groups
      :type:  list[BatchGroup]
      :value: []



   .. py:attribute:: components
      :type:  list[str]
      :value: []



   .. py:attribute:: solder_balls
      :type:  list[SolderBallsInfo]
      :value: []



   .. py:attribute:: simulation_setup
      :type:  SimulationSetup


   .. py:attribute:: extent_type
      :type:  str
      :value: 'bounding_box'



   .. py:attribute:: cutout_expansion
      :type:  float | str
      :value: '2mm'



   .. py:attribute:: auto_mesh_seeding
      :type:  bool
      :value: True



   .. py:attribute:: port_type
      :type:  str
      :value: 'coaxial'



   .. py:attribute:: create_pin_group
      :type:  bool
      :value: False



   .. py:method:: auto_populate_batch_groups(pattern: str | list[str] | None = None) -> None

      Automatically create and populate batch groups from signal nets.

      This method discovers signal nets, identifies reference nets, and groups
      nets by prefix patterns. It is a convenience wrapper around
      ``group_nets_by_prefix()``.

      Parameters
      ----------
      pattern : str or list of str or None, optional
          POSIX ERE prefix pattern(s) controlling which nets are grouped:

          - ``None`` (default) - Auto-discovery mode: nets are clustered
            heuristically and split into chunks of size ``batch_size``.
          - str - Single string prefix pattern (automatically anchored:
            ``pattern + ".*"``).
          - list of str - Each element becomes its own prefix pattern;
            one ``BatchGroup`` created per list entry, regardless of
            ``batch_size``.

      Examples
      --------
      Auto-discovery with automatic grouping:

      >>> config = HFSSAutoConfiguration()
      >>> config.source_edb_path = "design.aedb"
      >>> config.auto_populate_batch_groups()
      >>> len(config.batch_groups)
      5

      Group by specific prefixes:

      >>> config = HFSSAutoConfiguration()
      >>> config.source_edb_path = "design.aedb"
      >>> config.auto_populate_batch_groups(["DDR4", "PCIe", "USB"])
      >>> [g.name for g in config.batch_groups]
      ['DDR4', 'PCIe', 'USB']

      Notes
      -----
      - Clears and repopulates ``batch_groups`` in-place
      - Automatically identifies reference nets (typically GND variants)
      - Opens and closes the EDB internally



   .. py:method:: add_batch_group(name: str, nets: list[str] | None = None, *, simulation_setup: SimulationSetup | None = None) -> BatchGroup

      Append a new BatchGroup to the configuration.

      Parameters
      ----------
      name : str
          Descriptive name for the group. Will also become the regex pattern
          when the group is built automatically.
      nets : list of str or None, optional
          List of net names that belong to this batch. If ``None``, an empty
          list is assumed and can be filled later. The default is ``None``.
      simulation_setup : SimulationSetup or None, optional
          Per-batch simulation settings. When ``None``, the global
          ``self.simulation_setup`` is used. The default is ``None``.

      Returns
      -------
      BatchGroup
          The freshly created instance (already appended to ``batch_groups``)
          for further manipulation if desired.

      Examples
      --------
      >>> config = HFSSAutoConfiguration()
      >>> group = config.add_batch_group("DDR4", nets=["DDR4_DQ0", "DDR4_CLK"])
      >>> group.name
      'DDR4'
      >>> len(group.nets)
      2

      Add group with custom setup:

      >>> setup = SimulationSetup(stop_frequency="30GHz")
      >>> group = config.add_batch_group("PCIe", simulation_setup=setup)
      >>> group.simulation_setup.stop_frequency
      '30GHz'



   .. py:method:: add_solder_ball(ref_des: str, shape: str = 'cylinder', diameter: str | float | None = None, mid_diameter: str | float | None = None, height: str | float | None = None) -> SolderBallsInfo

      Append a new solder ball definition to the configuration.

      Parameters
      ----------
      ref_des : str
          Reference designator of the component to which the solder ball
          definition applies (e.g., ``"U1"``).
      shape : str, optional
          Geometric model used for the solder ball. Supported values are
          ``"cylinder"``, ``"sphere"``, ``"spheroid"``. The default is
          ``"cylinder"``.
      diameter : str or float or None, optional
          Nominal diameter. When ``None``, HFSS auto-evaluates the value
          from the footprint. The default is ``None``.
      mid_diameter : str or float or None, optional
          Middle diameter required only for spheroid shapes. Ignored for
          all other geometries. The default is ``None``.
      height : str or float or None, optional
          Ball height. When ``None``, HFSS computes an appropriate value
          automatically. The default is ``None``.

      Returns
      -------
      SolderBallsInfo
          The newly created instance (already appended to ``solder_balls``).
          The object can be further edited in-place if desired.

      Examples
      --------
      Add cylinder solder balls:

      >>> config = HFSSAutoConfiguration()
      >>> config.add_solder_ball("U1", diameter="0.3mm", height="0.2mm")
      >>> config.solder_balls[0].ref_des
      'U1'

      Add spheroid solder balls:

      >>> config.add_solder_ball("U2", shape="spheroid", diameter="0.25mm", mid_diameter="0.35mm", height="0.18mm")
      >>> config.solder_balls[1].shape
      'spheroid'



   .. py:method:: add_simulation_setup(meshing_frequency: str | float | None = '10GHz', maximum_pass_number: int = 15, start_frequency: str | float | None = 0, stop_frequency: str | float | None = '40GHz', frequency_step: str | float | None = '0.05GHz', replace: bool = True) -> SimulationSetup

      Create a SimulationSetup instance and attach it to the configuration.

      Parameters
      ----------
      meshing_frequency : str or float or None, optional
          Driven frequency used during mesh generation. The default is ``"10GHz"``.
      maximum_pass_number : int, optional
          Maximum number of adaptive passes. The default is ``15``.
      start_frequency : str or float or None, optional
          Lower bound of the sweep window. The default is ``0``.
      stop_frequency : str or float or None, optional
          Upper bound of the sweep window. The default is ``"40GHz"``.
      frequency_step : str or float or None, optional
          Linear step size for the frequency sweep. The default is ``"0.05GHz"``.
      replace : bool, optional
          Placement strategy for the new setup:

          - ``False`` - Append a per-batch setup by creating an auxiliary
            ``BatchGroup`` (``name="extra_setup"``) whose ``simulation_setup``
            points to the new object.
          - ``True`` - Overwrite the global ``simulation_setup`` attribute of
            the current instance. The default is ``True``.

      Returns
      -------
      SimulationSetup
          The newly created instance (already stored inside the configuration).

      Examples
      --------
      Create global setup:

      >>> config = HFSSAutoConfiguration()
      >>> config.add_simulation_setup(stop_frequency="60GHz", replace=True)
      >>> config.simulation_setup.stop_frequency
      '60GHz'

      Create per-batch setup:

      >>> config.add_simulation_setup(frequency_step="0.1GHz", replace=False)
      >>> config.batch_groups[-1].name
      'extra_setup'



   .. py:method:: group_nets_by_prefix(prefix_patterns: list[str] | None = None) -> dict[str, list[list[str]]]

      Group signal nets into disjoint batches while preserving differential pairs.

      This method organizes signal nets into batches based on prefix patterns,
      ensuring differential pairs (e.g., ``_P``/``_N``, ``_M``/``_L``) stay together.

      Parameters
      ----------
      prefix_patterns : list of str or None, optional
          POSIX ERE patterns that define the prefixes to be grouped.
          Example: ``["PCIe", "USB"]`` → interpreted as ``["PCIe.*", "USB.*"]``.
          If ``None``, patterns are derived heuristically from the data set.

      Returns
      -------
      dict[str, list[list[str]]]
          Keys are the original or generated pattern strings.
          Values are lists of batches; each batch is an alphabetically sorted
          list of net names. When ``prefix_patterns`` was supplied, the list
          contains exactly one element (the complete group); in auto-discovery
          mode, the list may contain multiple slices sized according to
          ``batch_size``.

      Examples
      --------
      Explicit grouping:

      >>> config = HFSSAutoConfiguration()
      >>> config.signal_nets = ["PCIe_RX0_P", "PCIe_RX0_N", "USB3_DP", "DDR4_A0"]
      >>> config.group_nets_by_prefix(["PCIe", "USB"])
      {'PCIe': [['PCIe_RX0_N', 'PCIe_RX0_P']], 'USB': [['USB3_DP']]}

      Auto-discovery with batching:

      >>> config.batch_size = 2
      >>> config.group_nets_by_prefix()
      {'PCIe': [['PCIe_RX0_N', 'PCIe_RX0_P']], 'USB': [['USB3_DP']], 'DDR4': [['DDR4_A0']]}

      Notes
      -----
      - Differential recognition strips the suffixes ``_[PN]``, ``_[ML]``, ``_[+-]``
        (case-insensitive).
      - The function updates the instance attribute ``batch_groups`` in place.
      - Every net is assigned to exactly one batch.
      - No batch contains only a single net; orphans are merged into the largest
        compatible group.



   .. py:method:: create_projects()

      Generate HFSS projects from configured batch groups.

      This method executes the complete workflow for each batch group including:

      1. Copying source EDB to target location
      2. Creating cutout with specified nets
      3. Creating ports on components
      4. Setting up simulation parameters
      5. Saving configured project

      When multiple batch groups exist, each group is processed into a separate
      project file stored in the ``batch_group_folder`` directory.

      Examples
      --------
      Create single project:

      >>> config = HFSSAutoConfiguration()
      >>> config.source_edb_path = "design.aedb"
      >>> config.target_edb_path = "design_hfss.aedb"
      >>> config.signal_nets = ["DDR4_DQ0", "DDR4_CLK"]
      >>> config.reference_net = "GND"
      >>> config.components = ["U1"]
      >>> config.create_projects()

      Create multiple batch projects:

      >>> config = HFSSAutoConfiguration()
      >>> config.source_edb_path = "design.aedb"
      >>> config.auto_populate_batch_groups(["DDR4", "PCIe"])
      >>> config.create_projects()
      >>> # Creates projects in batch_groups/DDR4.aedb and batch_groups/PCIe.aedb

      Notes
      -----
      - For multiple batch groups, projects are saved in ``batch_group_folder``
      - Each batch can have custom simulation settings
      - Automatically handles EDB session management



.. py:function:: create_hfss_auto_configuration(edb: pyedb.Edb | None = None, ansys_version: str | None = None, grpc: bool | None = None, source_edb_path: str | None = None, target_edb_path: str | None = None, signal_nets: list | None = None, power_nets: list | None = None, reference_net: str | None = None, batch_size: int | None = None, batch_groups: list | None = None, components: list[str] | None = None, solder_balls: list | None = None, simulation_setup: SimulationSetup | None = None, extent_type: str | None = None, cutout_expansion: str | float | None = None, auto_mesh_seeding: bool | None = None, port_type: str | None = None, create_pin_group: bool | None = None) -> HFSSAutoConfiguration

   Factory function to create an HFSSAutoConfiguration instance with optional overrides.

   This function creates a configuration object with all specified parameters,
   providing a convenient alternative to manual attribute assignment.

   Parameters
   ----------
   edb : Edb or None, optional
       Existing EDB object instance. The default is ``None``.
   ansys_version : str or None, optional
       ANSYS Electronics Desktop version. The default is ``None``.
   grpc : bool or None, optional
       Whether to use gRPC API mode. The default is ``None``.
   source_edb_path : str or None, optional
       Path to the source EDB file. The default is ``None``.
   target_edb_path : str or None, optional
       Path where configured EDB will be saved. The default is ``None``.
   signal_nets : list or None, optional
       List of signal net names. The default is ``None``.
   power_nets : list or None, optional
       List of power net names. The default is ``None``.
   reference_net : str or None, optional
       Name of reference (ground) net. The default is ``None``.
   batch_size : int or None, optional
       Maximum nets per batch group. The default is ``None``.
   batch_groups : list or None, optional
       Pre-configured batch groups. The default is ``None``.
   components : list of str or None, optional
       Component reference designators. The default is ``None``.
   solder_balls : list or None, optional
       Solder ball configurations. The default is ``None``.
   simulation_setup : SimulationSetup or None, optional
       Global simulation settings. The default is ``None``.
   extent_type : str or None, optional
       Cutout extent algorithm. The default is ``None``.
   cutout_expansion : str or float or None, optional
       Cutout expansion margin. The default is ``None``.
   auto_mesh_seeding : bool or None, optional
       Enable automatic mesh seeding. The default is ``None``.
   port_type : str or None, optional
       Port type to create. The default is ``None``.
   create_pin_group : bool or None, optional
       Whether to create pin groups. The default is ``None``.

   Returns
   -------
   HFSSAutoConfiguration
       Fully configured instance ready for use.

   Examples
   --------
   Create with basic settings:

   >>> config = create_hfss_auto_configuration(
   ...     source_edb_path="design.aedb",
   ...     target_edb_path="design_hfss.aedb",
   ...     signal_nets=["DDR4_DQ0", "DDR4_CLK"],
   ...     reference_net="GND",
   ... )
   >>> config.source_edb_path
   'design.aedb'

   Create with custom simulation setup:

   >>> setup = SimulationSetup(stop_frequency="60GHz")
   >>> config = create_hfss_auto_configuration(
   ...     source_edb_path="design.aedb", simulation_setup=setup, port_type="circuit_port"
   ... )
   >>> config.simulation_setup.stop_frequency
   '60GHz'


