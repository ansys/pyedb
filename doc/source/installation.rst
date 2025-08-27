Installation
============

Prerequisites
-------------
PyEDB requires the ``ansys-edb-core`` gRPC client service to be running.

.. admonition:: Looking for the old DotNet API?
   :class: seealso

   The legacy ``pyedb.dotnet`` module, which required AEDT, will be deprecated and moved to an `archived branch <https://github.com/ansys/pyedb/tree/archive/dotnet-legacy>`_. All new projects must use the gRPC client described below.

** Use AEDT Installation (Windows-Linux)**
You must have AEDT installed, the ``ansys-edb-core`` server service is included.
The PyEDB client is a python package automatically installed with PyEDB and will automatically find and connect to the
server.

Make sure you are running the latest ansys-edb-core client version compatible with your AEDT version.

.. code-block:: bash

    pip install --upgrade ansys-edb-core


Install the PyEDB Client
------------------------
The PyEDB Python client is installed via pip. It is highly recommended to use a virtual environment.

.. code-block:: bash

    # Install the latest release from PyPI
    pip install pyedb

    # Install the latest development version from GitHub
    pip install git+https://github.com/ansys/pyedb

Verifying the Installation
--------------------------
To test your installation and connection to the ``ansys-edb-core`` service, run the following Python script:

.. code-block:: python
   :caption: test_installation.py

   from pyedb import Edb

   # Note a new grpc flag is added to the Edb class. Set it to True to use gRPC.
   # This will attempt to connect to the ansys-edb-core service
   # If successful, it will print the client and server versions.
   edb = Edb(version="2025.2", grpc=True)