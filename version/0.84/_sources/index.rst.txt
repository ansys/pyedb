Welcome to PyEDB |version|
==========================

.. note::

    - **Default gRPC Backend:** PyEDB now selects the gRPC backend by default if no flag is specified.
    - **gRPC Compatibility:** PyEDB gRPC support requires Ansys release 2026.1 or higher. If you specify gRPC with
      Ansys release 2025.2 or lower, an error message stating that this backend is not supported for this version.
    - **Fast Mode (Service Pack 2026.1.2):** PyEDB gRPC introduced "fast mode" with Service Pack 2026.1.2. Speed is
      significantly improved thanks to bypassing network traffic and treating all processing in memory.
    - **Optional DotNet Dependency:** The PyEDB DotNet library is now optional. Running ``pip install pyedb``
      installs only the base package. If ``grpc=False``, an error is issued saying
      installs only the base package. If you try to set ``grpc=False``, you are going to get an error
      saying that the DLL failed to initialize. To use the DotNet backend, run ``pip install pyedb[dotnet]``.

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


.. toctree::
    :hidden:


    getting_started/index
    user_guide/index
    configuration/index
    grpc_api/index
    examples/index
    changelog
