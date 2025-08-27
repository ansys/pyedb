Troubleshooting
===============

Common Issues and Solutions
---------------------------

### "Cannot connect to ansys-edb-core service"
*   **Cause:** The ``ansys-edb-core`` service is not installed or running.
*   **Solution:**
    *   On Windows with AEDT: Ensure AEDT is properly installed.
    *   On Linux/Windows standalone: Ensure the standalone ``ansys-edb-core`` service is installed and running. Contact Ansys support for the installer.

### "The grpc channel is in state TRANSIENT_FAILURE"
*   **Cause:** The connection to the gRPC server failed or was interrupted.
*   **Solution:**
    *   Check if the server process is running.
    *   Restart the service or your machine.
    *   Check firewall settings that might be blocking gRPC communication.

### "EDBError: Operation not permitted" or permission errors
*   **Cause:** The client doesn't have permission to access the specified EDB directory.
*   **Solution:** Check filesystem permissions on the EDB path, especially when running in Docker or on Linux servers.

### Script runs slowly when creating many geometries
*   **Cause:** Using many individual ``create_rectangle`` or ``create_path`` calls is inefficient.
*   **Solution:** Use batch operations where possible, or create complex polygons instead of many simple shapes.

Getting Help
------------
If you encounter an issue not covered here:

1.  **Search existing issues:** Check the `GitHub Issues <https://github.com/ansys/pyedb/issues>`_ to see if your problem has already been reported.
2.  **Create a new issue:** Provide a minimal reproducible example, error messages, and information about your environment (OS, PyEDB version, ansys-edb-core version).
3.  **Ask the community:** Start a discussion on `GitHub Discussions <https://github.com/ansys/pyedb/discussions>`_.