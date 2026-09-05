.. _simulation_setups:

Simulation setups
====================

Create HFSS and SIwave simulation setups for the current cell.

Prerequisites
-------------

- An open ``Edb`` instance with ports created (see :doc:`ports_and_sources`).

Public API entry points
-------------------------

- :attr:`Edb.simulation_setups <pyedb.grpc.edb.Edb.simulation_setups>` — returns
  :class:`SimulationSetups <pyedb.grpc.database.simulation_setups.SimulationSetups>`.

Procedure
---------

1. Create a SIwave frequency-sweep (SYZ) setup.

   .. code-block:: python

      setup = edb.simulation_setups.create_siwave_setup(
          name="GHz_Setup", start_freq="1GHz", stop_freq="10GHz"
      )

2. Create a SIwave DCIR setup.

   .. code-block:: python

      dc_setup = edb.simulation_setups.create_siwave_dcir_setup(name="DC_Analysis")

3. Create an HFSS 3D Layout setup with a sweep.

   .. code-block:: python

      hfss_setup = edb.simulation_setups.create_hfss_setup(
          name="HFSS_Setup", start_freq="0Hz", stop_freq="20GHz", step_freq="0.05GHz"
      )

4. List all setups on the current cell.

   .. code-block:: python

      print(list(edb.setups.keys()))

Complete example
-----------------

.. code-block:: python

   import tempfile
   from pathlib import Path

   from pyedb import Edb

   input_path = str(Path(tempfile.gettempdir()) / "setup_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   setup = edb.simulation_setups.create_siwave_setup(
       name="GHz_Setup", start_freq="1GHz", stop_freq="10GHz"
   )
   print("Created setup:", setup.name)
   print("All setups:", list(edb.setups.keys()))

   output_path = str(Path(tempfile.gettempdir()) / "setup_output.aedb")
   edb.save_as(output_path)
   edb.close()

Expected result
----------------

``edb.simulation_setups.create_siwave_setup(...)`` returns a setup object whose ``.name`` matches the
requested name, and that name appears as a key in ``edb.setups``.

Backend and version notes
---------------------------

- ``edb.simulation_setups`` is available on both backends with the same property name.
- ``SimulationSetups.create(name=None, solver="hfss")`` accepts the solver strings ``"hfss"``,
  ``"siwave"``, ``"siwave_dcir"``, ``"raptor_x"``, ``"q3d"``, and ``"hfss_pi"``. Any other string
  silently falls back to ``"hfss"`` — pass a listed value to avoid unexpected setup types.
- ``Edb.create_siwave_syz_setup(...)`` and ``Edb.create_siwave_dc_setup(...)`` (directly on ``Edb``)
  still exist but are deprecated thin wrappers around ``edb.simulation_setups.create_siwave_setup``
  and ``create_siwave_dcir_setup``. Prefer the ``simulation_setups`` interface in new code.

.. note::

   Simulation setups can also be created declaratively through the configuration system
   (``cfg.setups.add_hfss_setup(...)``), alongside stackup, components, and ports, and applied in
   one call with ``edb.configuration.run(cfg)``. See
   :doc:`../configuration/configuration_api_examples` for a complete worked example that combines a
   stackup, a component, ports, and an HFSS setup in a single configuration object.

Common problems
-----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``create(...)`` returns ``None``
     - A setup with the requested name already exists on the cell.
     - Choose a different name, or look up and edit the existing setup via ``edb.setups["name"]``.
   * - Setup created with unexpected solver type
     - An unrecognized ``solver=`` string was passed to ``create(...)``.
     - Use one of ``"hfss"``, ``"siwave"``, ``"siwave_dcir"``, ``"raptor_x"``, ``"q3d"``, ``"hfss_pi"``;
       any other value silently creates an HFSS setup instead of raising an error.

See also
--------

- :doc:`ports_and_sources` — creating the ports referenced by a simulation setup.
- :doc:`../getting_started/object_model` — the ``edb.simulation_setups`` section.
- :doc:`../workflows/sipi/hfss_auto_configuration` — a higher-level HFSS 3D Layout configuration workflow.
