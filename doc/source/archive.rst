.. _archive:

Legacy DotNet API (Archived)
=============================

.. danger::

   **The ``pyedb.dotnet`` module is deprecated and archived.**
   It is no longer maintained and will not receive any updates or bug fixes. All users are **strongly encouraged** to migrate to the modern :ref:`gRPC-based client <comms_protocols>`, which is the future of PyEDB.

What Was the DotNet API?
------------------------
The ``pyedb.dotnet`` module was the original implementation of PyEDB. It was a Python wrapper around the Ansys Electronics Desktop (AEDT) COM API, which required:

*   A full installation of **AEDT on Windows**.
*   A **licensed copy** of AEDT.
*   The Python process to run on **Windows** only.

This approach was limited to client machines with AEDT installed and could not be used for headless server automation.

Why It Was Replaced
-------------------
The new architecture, based on a standalone gRPC service (``ansys-edb-core``), provides significant advantages:

*   **No AEDT Required:** Runs without AEDT installed.
*   **Cross-Platform:** The client can run on **Linux, macOS, and Windows**.
*   **Headless Operation:** Ideal for servers, Docker, and CI/CD pipelines.
*   **Better Performance:** The gRPC protocol is more efficient than COM.
*   **Modern and Maintainable:** The codebase is cleaner and easier to extend.

Accessing the Archived Code
---------------------------
The code for the deprecated ``dotnet`` module has been moved to a separate, archived branch in the GitHub repository to avoid confusion and keep the main branch clean.

**You can access the final version of the `dotnet` code here:**

.. toctree::
   :maxdepth: 2

   dotnet_api/index

.. warning::

   This code is provided **as-is** for reference and migration purposes only. It will not be updated. Do not use it for new projects. If you need to maintain an old script that uses the ``dotnet`` API, your goal should be to migrate it to the gRPC client.

Migration Guide
---------------
If you have existing scripts using `pyedb.dotnet`, see the :doc:`migration_guide` for help porting your code to the modern gRPC API.