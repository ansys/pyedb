.. _comms_protocols:

Communication Protocol: gRPC
============================

PyEDB exclusively uses the **gRPC Remote Procedure Calls (gRPC)** protocol to communicate with the ``ansys-edb-core`` service.

This modern framework is the foundation of PyEDB's architecture and offers key benefits:

*   **Headless Operation:** Enables operation on servers without a GUI (e.g., Linux, Docker).
*   **Performance:** High-speed communication, ideal for processing large, complex designs.
*   **Reliability:** Robust connection handling and error reporting.
*   **Decoupled Development:** The Python client and the core service can be updated independently.

Checking the Connection
-----------------------
You can always check the status and version of the connection from your Python script.

.. code-block:: python

   import pyedb

   with pyedb.Edb() as edb:
       print(f"Connected to server version: {edb.core_server_version}")
       print(f"Server is running on: {edb.core_server_process}")