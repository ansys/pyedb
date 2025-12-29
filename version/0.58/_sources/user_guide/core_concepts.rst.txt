Core Concepts
=============

Understanding the client-server architecture and the EDB object hierarchy is key to working effectively with PyEDB.

Architecture: Client-Server Model
---------------------------------
PyEDB operates on a client-server model:

1.  **Client (Your Script):** The lightweight `pyedb` Python package. It contains the high-level API and sends commands.
2.  **Server (The Engine):** The RPC service. It holds the actual EDB data, performs all computations on EDB.

Your EDB project exists on the **server**. The client is a remote control. This is why PyEDB can be so lightweight and
run on systems without the full Ansys computational engine.

The EDB Hierarchy
-----------------
The object model within the EDB server remains the same:

*   **EDB Project**: The top-level object, representing the entire *.edb* file on the server.
    *   **Cell**: Represents the PCB design itself.
        *   **Layout**: The container for all the physical data.
            *   **Stackup**: The definition of layers.
            *   **Primitives**: The basic geometric shapes.
        *   **Net List**: The collection of all electrical nets.
        *   **Component List**: The collection of all components.
    *   **Simulation Setup**: Definitions for how to analyze the design.

Key PyEDB client classes (like `Edb`, `Nets`, `Components`) are **handles** or **proxies** that send commands to the
corresponding objects inside the server.