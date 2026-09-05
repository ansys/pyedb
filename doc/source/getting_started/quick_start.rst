.. _quick_start:

Quick start
===========

This page gets you from an empty environment to a modified, saved EDB file in about 10 minutes.
Every command shown here has been verified against the current PyEDB source code.

Prerequisites
-------------

- Python 3.10 or later (PyEDB supports 3.10-3.14).
- A licensed local copy of Ansys Electronics Desktop (AEDT). PyEDB does not work without an AEDT
  installation because the ``ansys-edb-core`` service (gRPC backend) or the EDB .NET libraries
  (DotNet backend) ship with AEDT.
- For the default gRPC backend: AEDT release 2026.1 or later. For details on backend selection, see
  :doc:`backend_compatibility_migration`.

1. Install PyEDB
----------------

.. code-block:: bash

   pip install pyedb

This installs the base package, which is capable of using the gRPC backend out of the box. You do not
need any optional extra unless you specifically need the deprecated DotNet backend
(``pip install pyedb[dotnet]``).

2. Verify the installation
---------------------------

.. code-block:: python

   import pyedb

   print(pyedb.__version__)

This should print the installed PyEDB version (for example ``0.83.0``) with no errors. If it raises an
``ImportError``, re-check step 1.

3. Create an EDB and inspect it
---------------------------------

The following script creates a new, empty EDB database in a temporary folder, inspects basic
information about it, makes one safe modification, saves the result to a **new** location so the
original is never overwritten, and closes the session cleanly.

.. code-block:: python
   :caption: quick_start.py

   import tempfile
   from pathlib import Path

   from pyedb import Edb

   # Create a new, empty EDB in a temporary folder.
   input_path = str(Path(tempfile.gettempdir()) / "quick_start_input.aedb")
   edb = Edb(edbpath=input_path, version="2026.1")

   # Inspect basic database information.
   print("Active cell:", edb.active_cell)
   print("Cell names:", edb.cell_names)
   print("Existing layers:", list(edb.stackup.layers.keys()))
   print("Existing nets:", edb.nets.netlist)

   # Perform one safe modification: add a new signal layer to the stackup.
   edb.stackup.add_layer(
       layer_name="TOP", layer_type="signal", material="copper", thickness="35um"
   )
   print("Layers after modification:", list(edb.stackup.layers.keys()))

   # Save to a new output location. The input database above is never overwritten.
   output_path = str(Path(tempfile.gettempdir()) / "quick_start_output.aedb")
   edb.save_as(output_path)

   # Always close the session to release the RPC server and file locks.
   edb.close()

   print(f"Done. Modified database saved to {output_path}")

Expected output
---------------

Running the script prints something similar to:

.. code-block:: console

   Active cell: <ansys.edb.core.layout.cell.Cell object at 0x...>
   Cell names: ['Cell_a1b2c3d4']
   Existing layers: []
   Existing nets: []
   Layers after modification: ['TOP']
   Done. Modified database saved to /tmp/quick_start_output.aedb

Exact object representations, the auto-generated cell name (PyEDB generates a unique ``Cell_<hash>``
name when none is provided), and the temporary path differ depending on your platform, installed AEDT
version, and run. You should see two file paths (input and output), a layer list that grows from empty
to ``['TOP']``, and no traceback.

Using a context manager
------------------------

``Edb`` supports the context-manager protocol, which guarantees ``close()`` is called even if an
exception occurs partway through your script:

.. code-block:: python

   from pyedb import Edb

   with Edb(edbpath=input_path, version="2026.1") as edb:
       edb.stackup.add_layer(layer_name="TOP", layer_type="signal")
       edb.save_as(output_path)
   # edb.close() has already been called here.

Common problems
----------------

.. list-table::
   :header-rows: 1
   :widths: 30 35 35

   * - Symptom
     - Likely cause
     - Resolution
   * - ``RuntimeWarning: AEDT is not properly installed``
     - No AEDT installation was found, or the requested ``version`` is not installed.
     - Install AEDT, or omit ``version`` to let PyEDB use the latest installed release.
   * - ``RuntimeError`` mentioning gRPC is not supported
     - ``version`` resolves to an Ansys release earlier than 2026.1 with ``grpc=True`` (explicit or
       via a script that hard-codes it).
     - Use ``version="2026.1"`` or later for gRPC, or pass ``grpc=False`` to use the DotNet backend
       (requires ``pip install pyedb[dotnet]``).
   * - Backend fails to initialize with ``grpc=False``
     - The ``dotnet`` optional dependency is not installed.
     - Run ``pip install pyedb[dotnet]``.

Next steps
----------

- Learn how the ``Edb`` entry point exposes stackup, materials, components, nets, and other objects in
  :doc:`object_model`.
- Browse task-oriented recipes in :doc:`../user_guide/common_tasks`.
- Understand backend selection and migration in :doc:`backend_compatibility_migration`.
- Explore the full architecture and navigation guide in :doc:`../user_guide/design_navigation`.
