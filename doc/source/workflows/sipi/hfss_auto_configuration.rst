.. _ref_hfss_auto_configuration:

HFSS automatic configuration
============================

.. contents::
   :local:
   :depth: 3

Purpose
-------
The ``HFSSAutoConfiguration`` class (and its factory function ``create_hfss_auto_configuration``) is a
**production-ready, declarative helper** that turns a **full-board EDB** into **analysis-ready HFSS cut-out
projects** without manual intervention.

Typical use-cases
~~~~~~~~~~~~~~~~~
*  Post-layout signal-integrity sign-off for high-speed digital interfaces (PCIe, DDR, USB, Ethernet, etc.)
*  Automated impedance, insertion-loss and return-loss validation for every active net in the design
*  Regression testing across design spins—every net is simulated with identical boundary conditions, mesh
   settings, and port types
*  Design-of-experiments (DoE) where the same schematic is re-simulated with different stack-ups, materials, or
   solder-ball geometries

What the helper does
~~~~~~~~~~~~~~~~~~~~
1. Opens the source EDB (board layout)
2. Identifies **signal** and **power/ground** nets automatically
3. Picks the **best reference net** (GND, VSS, AGND …) using a curated regex table
4. Optionally **groups nets into batches** (differential pairs are never split)
5. Creates a **cut-out** for every batch (bounding box or convex-hull)
6. Places **coaxial or circuit ports** on every component that touches the signal nets
7. Applies **solder-ball geometry** when supplied (cylinder, sphere, spheroid)
8. Writes a **ready-to-solve HFSS setup** (adaptive mesh, broadband sweep, auto-seeding)
9. Saves an **independent EDB project** per batch so that simulations can be distributed on a compute farm

The user only supplies:

* path to the source EDB
* (optionally) a list of nets or prefix patterns—everything else is auto-discovered

Design philosophy
-----------------
* **No manual GUI work**—100 % script driven
* **Repeatable**—identical settings for every net, every run
* **Scalable**—cut-outs + batching keep problem size small enough for overnight turnaround on a 32-core box
* **Extensible**—every numeric setting, port type or mesh strategy is exposed as a dataclass field

Minimal quick-start
-------------------
.. code-block:: python

   from pyedb import Edb
   from pyedb.workflows.sipi.hfss_auto_configuration import create_hfss_auto_configuration

   cfg = create_hfss_auto_configuration(
       source_edb_path=r"../release/board.aedb",
       target_edb_path=r"../hfss/serdes.aedb",
       batch_size=50,  # max 50 nets per cut-out
       port_type="coaxial",
   )
   cfg.auto_populate_batch_groups()  # discover nets and group them
   cfg.create_projects()  # write one EDB + HFSS setup per batch

The snippet above produces a folder ``../hfss/serdes.aedb`` that contains:

* a cut-out with ≤ 50 nets
* coaxial ports on every component pin
* adaptive mesh 10 GHz–40 GHz sweep
* ready to be solved

Class and data model
--------------------

HFSSAutoConfiguration
~~~~~~~~~~~~~~~~~~~~~
.. autoclass:: pyedb.workflows.sipi.hfss_auto_configuration.HFSSAutoConfiguration
   :members:
   :undoc-members:
   :exclude-members: __init__, __post_init__

Simulation setup
~~~~~~~~~~~~~~~~
.. autoclass:: pyedb.workflows.sipi.hfss_auto_configuration.SimulationSetup
   :members:
   :undoc-members:

BatchGroup
~~~~~~~~~~
.. autoclass:: pyedb.workflows.sipi.hfss_auto_configuration.BatchGroup
   :members:
   :undoc-members:

SolderBallsInfo
~~~~~~~~~~~~~~~
.. autoclass:: pyedb.workflows.sipi.hfss_auto_configuration.SolderBallsInfo
   :members:
   :undoc-members:

Factory function
----------------
.. autofunction:: pyedb.hfss_auto_configuration.create_hfss_auto_configuration

Net grouping logic
------------------
Differential-pair preservation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The helper recognises the suffixes ``_P/_N``, ``_M/_P``, ``_+/-`` (case-insensitive) and keeps those nets in the **same
batch** regardless of the requested ``batch_size``.

Prefix patterns
~~~~~~~~~~~~~~~
* **Auto-discovery mode** (``pattern=None``)
  Nets are clustered by longest common prefix; each cluster is then split into chunks of size ``batch_size``.

* **Explicit mode** (``pattern=["PCIe", "USB"]``)
  One batch group **per pattern** is created; ``batch_size`` is ignored.
  Patterns are automatically treated as POSIX ERE anchored at the start: ``PCIe.*``, ``USB.*``.

Reference-net selection
~~~~~~~~~~~~~~~~~~~~~~~
The first net that matches any of the following regexes (case-insensitive) is used as reference:

.. code-block:: text

   ^GND\d*$          ^VSS\w*          ^DGND$          ^AGND$
   ^PGND$            ^EGND$           ^SGND$          ^REF$
   ^VREF[A-Z0-9]*    ^VR[A-Z0-9]*     ^VTT$           ^0V$
   ^GND_plane$       ^GROUND$         ^SENSE\d*$      ^KSENSE\w*
   … (≈ 30 patterns in total)

If multiple candidates exist, the one whose name contains the substring “GND” is preferred; the rest become power nets.

Port creation details
---------------------
Coaxial ports
~~~~~~~~~~~~~
A coaxial cylinder is constructed **normal to the component pin**.
The outer radius is derived from the pad-stack anti-pad; the inner radius from the finished hole size.
When ``solder_balls`` are supplied the 3-D model is extended by the ball height and diameter.

Circuit ports
~~~~~~~~~~~~~
A two-pin circuit port is placed between the signal pin and the nearest reference (ground) pin on the **same component**.
If ``create_pin_group=True`` all pins of the same net are shorted into a single pin-group before the port is attached.

Mesh and sweep defaults
-----------------------
.. list-table::
   :header-rows: 1

   * - Attribute
     - Default
     - Remark
   * meshing_frequency
     10 GHz
     Adaptive mesh frequency
   * maximum_pass_number
     15
     Adaptive passes
   * start_frequency
     0 Hz
     Sweep start
   * stop_frequency
     40 GHz
     Sweep stop
   * frequency_step
     0.05 GHz
     Linear step

All values can be overridden globally (``simulation_setup``) or per batch (``BatchGroup.simulation_setup``).

File and folder layout
----------------------
After ``create_projects()`` finishes you obtain:

.. code-block:: text

   <target_edb_parent>/
   └── batch_groups/
       ├── PCIe_RX0.aedb/          # cut-out, 43 nets
       ├── PCIe_TX0.aedb/          # cut-out, 37 nets
       ├── USB3.aedb/              # cut-out,  8 nets
       └── DDR4_A0_A07.aedb/       # cut-out, 50 nets

Each ``*.aedb`` folder is an independent HFSS project that can be opened, solved and post-processed separately.

Logging and error handling
--------------------------
* Every operation is logged through the native EDB logger (INFO level)
* Missing components, duplicate net names or impossible cut-outs raise **before** any file is written
* If a batch group ends up with **only one net**, it is automatically merged into the largest compatible group to avoid degenerate simulations

Performance notes
-----------------
* Typical cut-out + port creation time: **2–5 s per batch** (201 GB DDR4 board, 3000 nets, 32 cores)
* Memory footprint: **< 2 GB** per batch because only the clipped geometry is kept in memory
* Scales linearly with number of batches—jobs can be dispatched to an HPC cluster independently

API reference index
-------------------
* :class:`.HFSSAutoConfiguration`
* :class:`.SimulationSetup`
* :class:`.BatchGroup`
* :class:`.SolderBallsInfo`
* :func:`.create_hfss_auto_configuration`

Examples
--------
Complete PCIe Gen-4 sign-off
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: python

   cfg = create_hfss_auto_configuration(
       source_edb_path=r"../../design/PCIE_gen4.aedb",
       batch_group_folder=r"../../hfss_gen4",
       batch_size=30,
       port_type="coaxial",
       solder_balls=[
           {
               "ref_des": "U1",
               "shape": "spheroid",
               "diameter": "0.35mm",
               "mid_diameter": "0.45mm",
               "height": "0.25mm",
           },
       ],
   )
   cfg.auto_populate_batch_groups(pattern=["PCIe"])  # only PCIe nets
   cfg.create_projects()

Troubleshooting
---------------
**“No reference net found”**
→ Add your ground name to ``ref_patterns`` or set ``reference_net`` manually.

**“Empty batch group”**
→ Check that ``signal_nets`` is non-empty and that the supplied prefix patterns actually match net names in the design.

**“Project fails to solve”**
→ Inspect the cut-out in AEDT: look for overlapping ports or missing reference pins; reduce ``batch_size`` to isolate the problematic net.

License
-------
MIT License – see file header for full text.