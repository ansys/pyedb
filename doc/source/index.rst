Welcome to PyEDB |version|
==========================

.. note::

    - **Default backend selection:** When the ``grpc`` argument is omitted, PyEDB selects the backend
      automatically from the resolved AEDT version: gRPC for Ansys release 2026.1 and later, DotNet for
      Ansys release 2025.2 and earlier. Pass ``grpc=True`` or ``grpc=False`` explicitly to override this.
      For the full compatibility matrix, see
      :doc:`getting_started/backend_compatibility_migration`.
    - **gRPC compatibility:** Requesting ``grpc=True`` against Ansys release 2025.2 or earlier raises a
      ``RuntimeError`` because gRPC is not supported on those releases.
    - **Fast mode (Service Pack 2026.1.2):** The gRPC backend automatically enables an in-memory "fast mode"
      when connecting to Ansys release 2026.1 Service Pack 2 or later, which improves performance by bypassing
      the network socket for local client/server pairs. On earlier service packs, gRPC still works but without
      this speed-up.
    - **Optional DotNet dependency:** The DotNet backend is optional. Running ``pip install pyedb`` installs
      only the base package (gRPC-capable). Using ``grpc=False`` without also installing the ``dotnet`` extra
      fails because the required ``ansys-pythonnet`` bridge and native DLLs are missing, not because the
      version is unsupported. To use the DotNet backend, run ``pip install pyedb[dotnet]``.

**Useful links**:
`Installation <https://edb.docs.pyansys.com/version/stable/getting_started/installation.html>`_ |
`Source Repository <https://github.com/ansys/pyedb>`_ |
`Issues <https://github.com/ansys/pyedb/issues>`_

PyEDB is a Python client library that provides a high-level interface to create, modify,
and analyze PCB designs by communicating with the `PyEDB-Core <https://github.com/ansys/pyedb-core>`_.


.. grid:: 2

    .. grid-item-card:: Getting started :fa:`person-running`
        :link: getting_started/index
        :link-type: doc

        New to PyEDB? This section provides the information that you need to get started with PyEDB.

    .. grid-item-card:: User guide :fa:`book-open-reader`
        :link: user_guide/index
        :link-type: doc

        This section provides in-depth information on PyEDB key concepts.

.. grid:: 2

    .. grid-item-card::  API reference :fa:`book-bookmark`
        :link: grpc_api/index
        :link-type: doc

        This section contains descriptions of the functions and modules included in PyEDB.
        It describes how the methods work and the parameters that can be used.

    .. grid-item-card:: Examples :fa:`scroll`
        :link: examples/index
        :link-type: doc

        Explore examples that show how to use PyEDB to perform different types of automations.

.. grid:: 2

    .. grid-item-card:: Contribute :fa:`people-group`
        :link: getting_started/contribution_guide
        :link-type: doc

        Learn how to contribute to the PyEDB codebase or documentation.

    .. grid-item-card:: Configuration guides :fa:`sliders`
        :link: configuration/index
        :link-type: doc

        Learn the configuration-file architecture and the programmatic builder API.

.. grid:: 2

    .. grid-item-card:: Workflows :fa:`diagram-project`
        :link: workflows/index
        :link-type: doc

        Explore ready-to-use PyEDB workflows for SIPI, utilities, and DRC.


.. toctree::
    :hidden:


    getting_started/index
    user_guide/index
    configuration/index
    workflows/index
    grpc_api/index
    examples/index
    changelog
