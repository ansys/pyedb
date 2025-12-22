Welcome to PyEDB |version|
==========================

**Useful links**:
`Installation <https://edb.docs.pyansys.com/version/stable/getting_started/installation.html>`_ |
`Source Repository <https://github.com/ansys/pyedb>`_ |
`Issues <https://github.com/ansys/pyedb/issues>`_

.. figure:: _static/logo.png
    :align: center
    :width: 640px

PyEDB is a Python client library that provides a high-level interface to create, modify,
and analyze PCB designs by communicating with the ``ansys-edb-core`` gRPC service.

.. note::

   **Architecture Notice: Standalone gRPC Service**
   PyEDB is a standalone Python client library that connects to the ``ansys-edb-core`` gRPC service.

.. admonition:: For users of the legacy `pyedb.dotnet` API
   :class: danger

   The ``dotnet`` module is **deprecated and archived** with Ansys release 2026R1.
   You can find more information :ref:`here <archive>`.


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

        Explore examples that show how to use PyEDB to perform different types of simulations.

.. grid:: 2

    .. grid-item-card:: Contribute :fa:`people-group`
        :link: getting_started/contribution_guide
        :link-type: doc

        Learn how to contribute to the PyEDB codebase or documentation.


.. toctree::
    :hidden:


    getting_started/index
    user_guide/index
    grpc_api/index
    examples/index
    changelog
