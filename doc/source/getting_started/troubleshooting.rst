Troubleshooting
===============

Common Issues and Solutions
---------------------------

Cannot connect to ansys-edb-core service
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*   **Cause:** The ``ansys-edb-core`` service is not installed or running.
*   **Solution:**
    *   On Windows with AEDT: Ensure AEDT is properly installed.
    *   On Linux/Windows standalone: Ensure the standalone ``ansys-edb-core`` service is installed and running. Contact Ansys support for the installer.


The gPRC channel is in state TRANSIENT_FAILURE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*   **Cause:** The connection to the gRPC server failed or was interrupted.
*   **Solution:**
    *   Check if the server process is running.
    *   Restart the service or your machine.
    *   Check firewall settings that might be blocking gRPC communication.


EDBError: Operation not permitted" or permission errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*   **Cause:** The client doesn't have permission to access the specified EDB directory.
*   **Solution:** Check filesystem permissions on the EDB path, especially when running in Docker or on Linux servers.


Script runs slowly when creating many geometries
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*   **Cause:** Using many individual ``create_rectangle`` or ``create_path`` calls is inefficient.
*   **Solution:** Use batch operations where possible, or create complex polygons instead of many simple shapes.

Error with uv-created virtual environments on Windows
-----------------------------------------------------
When using `uv <https://github.com/astral-sh/uv>`_ to create virtual environments on Windows, you may
encounter SSL-related errors when using PyEDB:

.. code:: text

    legacy Provider loading failed
    EVP_DecryptInit. could not load the shared library

**Root cause**

This issue stems from a DLL naming conflict in OpenSSL libraries on Windows. When CPython distributes
OpenSSL 3.0.X using the DLL name ``libssl-3.dll``, and a CPython extension module (such as PyEDB)
links against OpenSSL 3.0.Y using a different DLL name ``libssl-3-x64.dll``, both versions coexist
without conflict because they have different names.

However, when using ``uv`` created virtual environments with Python from
`python-build-standalone <https://github.com/astral-sh/python-build-standalone>`_, the Python distribution
uses the same DLL name ``libssl-3-x64.dll`` as the extension modules. This creates a conflict in Windows:
only one version of ``libssl-3-x64.dll`` can be loaded into the process at a time. For more details, see
`python-build-standalone #596 <https://github.com/astral-sh/python-build-standalone/issues/596>`_

**Workaround**

To avoid this issue, create the virtual environment manually using the standard Python ``venv`` module
instead of ``uv venv``. You can then install ``uv`` inside the environment and continue using it for
package management:

.. code:: bash

    # Create virtual environment with standard Python
    python -m venv .venv

    # Activate the virtual environment
    .venv\Scripts\activate

    # Install uv inside the environment
    pip install uv

    # Now you can use uv for package management
    uv pip install pyedb

Getting Help
------------
If you encounter an issue not covered here:

1.  **Search existing issues:** Check the `GitHub Issues <https://github.com/ansys/pyedb/issues>`_ to see if your problem has already been reported.
2.  **Create a new issue:** Provide a minimal reproducible example, error messages, and information about your environment (OS, PyEDB version, ansys-edb-core version).
3.  **Ask the community:** Start a discussion on `GitHub Discussions <https://github.com/ansys/pyedb/discussions>`_.