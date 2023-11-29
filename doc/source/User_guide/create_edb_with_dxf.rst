Create EDB with DXF file
========================
This section describes how to create EDB from DXF file.

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.legacy.edb import EdbLegacy

    dxf_path = os.path.join(local_path, "edb_test.dxf")
    edb = EdbLegacy(dxf_path, edbversion="2023.2")
    edb.close()
