.. _versions_and_interfaces:

=======================
Versions and interfaces
=======================

PyEDB attempts to maintain compatibility with legacy versions of EDB
while allowing for support of faster and better interfaces with the
latest versions of EDB.

Currently, there is only one interface PyEDB can use to connect to EDB.

gRPC interface
==============

The gRPC interface is under development and should be available soon.

Legacy interface
================

PyEDB currently connects to EDB using the native C# interface for the EDB API.
You do not need to set the ``PYEDB_USE_LEGACY`` environment variable to ``0`` to
use the legacy interface because it is the default value. Once the gRPC interface is
available, to use it, simply set the ``PYEDB_USE_LEGACY`` environment variable to ``1``. 

.. code:: python


    # Set gRPC interface (future implementation)
    import os

    os.environ["PYEDB_USE_LEGACY"] = "1"

    # Set DotNet interface (actual implementation)
    import os

    os.environ["PYEDB_USE_LEGACY"] = "0"

