.. _archive:

Legacy DotNet API (deprecated)
===============================

.. warning::

   **The ``pyedb.dotnet`` module is deprecated.**

   ``pyedb.dotnet`` is still present, importable, and functional in this release (behind
   ``grpc=False`` or automatically for Ansys releases 2025.2 and earlier), but it is planned to be
   deprecated in a future release. gRPC (``grpc=True``) is the long-term supported implementation.
   It is **strongly encouraged** that you migrate to the
   :ref:`gRPC-based client <comms_protocols>`.

What is the DotNet API?
------------------------
The ``pyedb.dotnet`` implementation is built on the `Microsoft DotNet framework`_ and loads the EDB
.NET libraries directly into the Python process through the ``pythonnet`` bridge. It requires the
``pyedb[dotnet]`` optional dependency and a local AEDT installation.

.. _Microsoft DotNet framework: https://dotnet.microsoft.com/en-us/learn/dotnet/what-is-dotnet-framework

Future development targets the gRPC client, which addresses numerous cross-platform compatibility
issues that the DotNet implementation has on Linux.

Why gRPC is preferred
---------------------
The gRPC architecture, based on a standalone service (``ansys-edb-core``), provides significant
advantages over the DotNet backend:

*   **Cross-platform:** The client runs on both **Linux and Windows** without a local .NET bridge.
*   **Headless operation:** Ideal for servers, Docker, and CI/CD pipelines.
*   **Better performance:** The gRPC protocol is more efficient, especially with fast mode
    (Ansys release 2026.1 Service Pack 2 and later).
*   **Modern and maintainable:** The codebase is cleaner and easier to extend.

Current status of the DotNet code
----------------------------------
The ``pyedb.dotnet`` source and its API reference remain part of this repository and are not
excluded from the published documentation build. If a future release removes or archives this
module, this page will be updated to reflect that change; until then, treat the module as
**deprecated but supported**, not yet removed.

The ``doc/source/grpc_migration/dotnet_api`` files referenced by earlier revisions of this page
are internal archival placeholders excluded from the documentation build; they are unrelated to the
currently shipping ``pyedb.dotnet`` source code.

.. warning::

   Do not build new projects against ``pyedb.dotnet``. If you maintain an existing script that uses
   it, plan to migrate it to the gRPC client.

Migration guide
----------------
If you have existing scripts using ``pyedb.dotnet``, see the
:ref:`DotNet to gRPC migration guide <migration_guide>` for help porting your code to the modern
gRPC API.
