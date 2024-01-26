.. _versions_and_interfaces:

=======================
Versions and interfaces
=======================

The PyEDB project attempts to maintain compatibility with legacy
versions of EDB while allowing for support of faster and better
interfaces with the latest versions of EDB.

Currently, there is only one interface PyEDB can use to connect to EDB.

gRPC interface
==============

The gRPC interface is currently under development and should be available soon.


Legacy interface
================

EDB API is natively written in C#.

This is the interface actually used in pyansys-edb.
Interfaces are changed by simply setting an environment variable.
You do not need to set the ``PYEDB_USE_LEGACY`` variable to ``0`` as this is the default value.

.. code:: python


    # Set gRPC interface (future implementation)
    import os

    os.environ["PYEDB_USE_LEGACY"] = "1"

    # Set DotNet interface (actual implementation)
    import os

    os.environ["PYEDB_USE_LEGACY"] = "0"
