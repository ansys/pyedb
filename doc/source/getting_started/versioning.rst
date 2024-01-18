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

gRPC interface is currently under development and will be available soon.


Legacy interface
================

EDB API is natively written in C#.

This is the interface actually used in pyansys-edb.
Interfaces will be changed by simply setting an environment variable.
It is not needed to set the ``PYEDB_USE_LEGACY`` variable to 0 as it is the default value.

.. code:: python


    # Set gRPC interface (future implementation)
    import os
    os.environ["PYEDB_USE_LEGACY"] = "1"

    # Set DotNet interface (actual implementation)
    import os
    os.environ["PYEDB_USE_LEGACY"] = "0"
