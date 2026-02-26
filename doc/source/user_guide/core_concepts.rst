Core Concepts
=============

Understanding the client-server architecture and the EDB object hierarchy is key to working effectively with PyEDB.

Architecture: Decoupled COM Model
---------------------------------
PyEDB operates on a decoupled architecture using COM (Component Object Model):

1.  **Client (Your Script):** The lightweight `pyedb` Python package. It contains the high-level API and sends commands.
2.  **Server (The Engine):** The COM service (ansys-edb-core). It holds the actual EDB data, performs all computations on EDB.

Your EDB project exists in the **COM service**. The client is a remote control. This is why PyEDB can be so lightweight and
run with a separation between the Python interface and the computational engine.


The EDB Hierarchy
-----------------
The object model within the EDB COM service remains the same:

* **EDB Project**: The top-level object, representing the entire ``*.edb`` file in the COM service.
  * **Cell**: Represents the PCB design itself.
    * **Layout**: The container for all the physical data.
      * **Stackup**: The definition of layers.
      * **Primitives**: The basic geometric shapes.
    * **Net List**: The collection of all electrical nets.
    * **Component List**: The collection of all components.
  * **Simulation Setup**: Definitions for how to analyze the design.

Key PyEDB client classes (like `Edb`, `Nets`, `Components`) are **handles** or **proxies** that send commands to the
corresponding objects inside the COM service.
