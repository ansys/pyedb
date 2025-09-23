.. _archive:

Legacy DotNet API (Archived)
=============================

.. danger::

   **The ``pyedb.dotnet`` module is deprecated and archived.**

   Support for 'pyedb.dotnet`` is ending soon.
It is **strongly encouraged** that you
migrate to the new :ref:`gRPC-based client <comms_protocols>`.

What Was the DotNet API?
------------------------
The original implementation of the ``pyedb.dotnet`` module was
built on the `Microsoft DotNet framework`_.
Future development will use the gRPC client.

.. _Microsoft DotNet framework: https://dotnet.microsoft.com/en-us/learn/dotnet/what-is-dotnet-framework

The new gRPC client addresses numerous cross-platform compatibility issues.

Why It Was Replaced
-------------------
The new architecture, based on a standalone gRPC service (``ansys-edb-core``), provides significant advantages:

*   **Cross-Platform:** The client can run on **Linux, and Windows**.
*   **Headless Operation:** Ideal for servers, Docker, and CI/CD pipelines.
*   **Better Performance:** The gRPC protocol is more efficient.
*   **Modern and Maintainable:** The codebase is cleaner and easier to extend.

Accessing the Archived Code
---------------------------
The code for the deprecated ``dotnet`` module has been moved to a separate, archived branch in the GitHub repository
to avoid confusion and keep the main branch clean.

**You can access the final version of the `dotnet` code here:**

.. toctree::
   :maxdepth: 2

   dotnet_api/index

.. warning::

   This code is provided **as-is** for reference and migration purposes only. Do not use it for
new projects. If you need to maintain an old script that uses the ``dotnet`` API, your goal should be to migrate it to
the gRPC client.

Migration Guide
---------------
If you have existing scripts using `pyedb.dotnet`, see the :doc:`migration_guide` for help porting your code to the
modern gRPC API.