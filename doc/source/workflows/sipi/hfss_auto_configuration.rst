HFSS Auto Configuration
=======================

Purpose
-------

The ``HFSSAutoConfiguration`` module streamlines the creation of HFSS 3-D electromagnetic projects from an existing EDB (Electronics Database).  It encapsulates the entire workflow—cut-out, port creation, solder-ball modelling, mesh seeding, and frequency-sweep definition—behind a compact, declarative API.  The class is especially useful for:

* Batch-processing large designs that must be split into manageable pieces (e.g. 100 nets at a time)
* Preserving differential pairs during partitioning
* Automatically placing coaxial or solder-ball ports on ICs and connectors
* Generating reusable simulation templates for regression testing or design-of-experiments

Typical use-cases
------------------

* **Signal-integrity sweep** – export 40 GHz broadband S-parameter models for every SERDES channel
* **Power-integrity cut-out** – create a localised model around a PMIC with explicit solder-ball geometry
* **What-if exploration** – quickly regenerate projects after swapping stack-ups or component values
* **Regression testing** – compare S-parameters across software builds with identical mesh/sweep settings

Design philosophy
-----------------

1. **Immutability by default** – helper methods return new dataclass instances; the caller decides where to store them
2. **Fail early** – every parameter is validated before the EDB is touched; the original file is never modified
3. **Transparent diffs** – the configuration object is serialisable (dataclasses + built-in types) so that two setups can be compared with ``==`` or exported to JSON/YAML
4. **Minimal boiler-plate** – one factory function plus a handful of high-level calls produce a ready-to-solve project

Quick start
-----------

.. code-block:: python

   from pyedb.hfss_auto_config import create_hfss_auto_configuration

   cfg = create_hfss_auto_configuration(
       source_edb_path=r"Y:\designs\main_board.aedb",
       signal_nets=["PCIe_RX0_P", "PCIe_RX0_N", "DDR4_A0"],
       power_ground_nets=["GND", "VCC"],
       batch_size=50,
   )

   cfg.auto_populate_batch_groups()  # heuristic grouping
   cfg.create_projects()  # yields Y:\designs\bacth_groups\*.aedb

   # launch HFSS and solve
   import pyedb

   for prj in Path(cfg.batch_group_folder).glob("*.aedb"):
       edb = pyedb.Edb(edbpath=prj)
       edb.solve()
       edb.close()

Class overview
--------------

.. autosummary::
   :toctree: _autosummary
   :template: custom-class-template.rst
   :nosignatures:

   HFSSAutoConfiguration
   BatchGroup
   SimulationSetup
   SolderBallsInfo

Factory helpers
---------------

.. autofunction:: create_hfss_auto_configuration

Core workflow methods
---------------------

.. automethod:: HFSSAutoConfiguration.auto_populate_batch_groups
.. automethod:: HFSSAutoConfiguration.group_nets_by_prefix
.. automethod:: HFSSAutoConfiguration.add_batch_group
.. automethod:: HFSSAutoConfiguration.add_solder_ball
.. automethod:: HFSSAutoConfiguration.add_simulation_setup
.. automethod:: HFSSAutoConfiguration.create_projects

Dataclass details
-----------------

.. autoclass:: BatchGroup
   :members:
   :undoc-members:

.. autoclass:: SimulationSetup
   :members:
   :undoc-members:

.. autoclass:: SolderBallsInfo
   :members:
   :undoc-members:

Advanced examples
-----------------

Differential-aware SERDES bundle
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create one project per high-speed interface while keeping diff-pairs intact:

.. code-block:: python

   cfg = create_hfss_auto_configuration(
       source_edb_path=r"Y:\designs\backplane.aedb",
       batch_size=150,
   )

   # only PCIe and 100 GbE nets, ignore everything else
   cfg.auto_populate_batch_groups(pattern=["PCIe", "CAUI"])

   # override global sim setup for the entire run
   cfg.add_simulation_setup(
       meshing_frequency="28GHz",
       stop_frequency="60GHz",
       replace=True,
   )

   cfg.create_projects()

PMIC power-integrity island
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cut out a 2 mm region around a PMIC and attach explicit solder-ball geometry:

.. code-block:: python

   cfg = create_hfss_auto_configuration(
       source_edb_path=r"Y:\designs\pkg.aedb",
       signal_nets=["VIN", "SW"],
       power_ground_nets=["GND", "VOUT"],
       extent_type="convex_hull",
       cutout_expansion="2mm",
   )

   cfg.add_solder_ball(
       ref_des="U1",
       shape="spheroid",
       diameter="0.3mm",
       mid_diameter="0.35mm",
       height="0.2mm",
   )

   cfg.create_projects()

Batch comparison with custom sweep
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate two independent configurations and compare them:

.. code-block:: python

   cfg_coarse = create_hfss_auto_configuration(
       source_edb_path=r"Y:\designs\dut.aedb",
       signal_nets=[...],
       simulation_setup=SimulationSetup(
           meshing_frequency="5GHz",
           frequency_step="0.2GHz",
       ),
   )

   cfg_fine = create_hfss_auto_configuration(
       source_edb_path=r"Y:\designs\dut.aedb",
       signal_nets=[...],
       simulation_setup=SimulationSetup(
           meshing_frequency="15GHz",
           frequency_step="0.02GHz",
       ),
   )

   for label, cfg in ("coarse", cfg_coarse), ("fine", cfg_fine):
       cfg.auto_populate_batch_groups()
       cfg.create_projects()
       # store S-parameter files for later delta plotting

Notes & best practices
----------------------

* Always place the ``batch_group_folder`` on a local SSD; copying and solving over the network is usually slower
* Keep ``batch_size`` below 200 nets for broadband sweeps – HFSS adaptive passes scale super-linearly
* When you supply explicit ``prefix_patterns`` the ``batch_size`` argument is **ignored**; exactly one project is created per pattern
* The original EDB is never modified; all edits happen in the copied ``target_edb_path``
* If ``components`` is left empty the tool automatically selects every component that touches at least one signal net and is **not** a discrete RLC

Troubleshooting
---------------

**Empty project list after create_projects()**
   Verify that ``signal_nets`` is non-empty and that ``source_edb_path`` points to a valid *.aedb* directory.

**Ports missing in HFSS**
   Ensure the chosen components actually touch the nets listed in ``signal_nets``.  Enable logging and inspect the console:

   .. code-block:: python

      cfg._pedb.logger.setLevel("INFO")

**Differential pairs split across projects**
   Check that the suffixes match the built-in regex ``_[PN]$|_[ML]$|_[+-]$``.  Add custom suffixes if necessary.

API reference index
-------------------

* :ref:`genindex`
* :ref:`modindex`