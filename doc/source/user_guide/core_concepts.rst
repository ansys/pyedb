Core concepts
=============

Understanding the architecture and the EDB object hierarchy is key to working effectively with PyEDB.

PyEDB Architecture and components
---------------------------------

PyEDB is built on top of lower-level APIs and provides a simplified, high-level interface for EDB automation:

**Component Stack:**

1. **Ansys EDB (.NET Libraries):** The core Ansys Electronics Database engine written in .NET, installed with AEDT.
   This contains all the fundamental EDB functionality for layout manipulation, simulation setup, etc.

2. **PyEDB-Core:** A lower-level Python API (not to be confused with ansys-edb-core) that provides direct .NET bindings
   to the EDB libraries. Using PyEDB-Core requires deep knowledge of EDB architecture and class hierarchies.

3. **ansys-edb-core:** A Python package that provides gRPC client capabilities for future client-server architecture.
   Currently installed as a dependency but the gRPC server functionality is not yet active.

4. **PyEDB (This Library):** The high-level, user-friendly Python interface that wraps PyEDB-Core with application-oriented
   classes and methods. PyEDB significantly simplifies EDB workflows and reduces the learning curve.


Current architecture: .NET interoperability
-------------------------------------------

**How PyEDB works:**

*   **PyEDB:** A pure Python library providing high-level API classes (``Edb``, ``Stackup``, ``Components``, etc.)
*   **PythonNET Bridge:** Uses the ``pythonnet`` package to load .NET CLR (Common Language Runtime)
*   **Ansys EDB .NET Libraries:** The actual EDB engine that executes within the .NET runtime
*   **PyEDB-Core:** Lower-level API that PyEDB calls internally for .NET operations

The .NET libraries are loaded directly into the Python process via PythonNET, allowing seamless interoperability
between Python code and .NET EDB objects.

**Important:** The current architecture requires AEDT installation on the same machine where PyEDB runs, as it needs
access to the local EDB .NET assemblies.

The EDB Hierarchy
-----------------
The object model within the .NET runtime remains the same:

* **EDB Project**: The top-level object, representing the entire ``*.edb`` file in the .NET runtime.
  * **Cell**: Represents the PCB design itself.
    * **Layout**: The container for all the physical data.
      * **Stackup**: The definition of layers.
      * **Primitives**: The basic geometric shapes.
    * **Net List**: The collection of all electrical nets.
    * **Component List**: The collection of all components.
  * **Simulation Setup**: Definitions for how to analyze the design.

Key PyEDB client classes (like ``Edb``, ``Nets``, ``Components``) are **Python wrappers** that directly interact with the
corresponding .NET objects through PythonNET.
