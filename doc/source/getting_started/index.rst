.. _migration_guide:

Getting started
===============

.. grid:: 2

   .. grid-item-card:: Installation
            :link: installation
            :link-type: doc
            :margin: 2 2 0 0

            Learn how to install PyEDB.

   .. grid-item-card:: Troubleshooting
            :link: troubleshooting
            :link-type: doc
            :margin: 2 2 0 0

            Any questions? Refer to Q&A before submitting an issue.

   .. grid-item-card:: Contribution
            :link: contribution_guide
            :link-type: doc
            :margin: 2 2 0 0

            Learn how to contribute to the PyEDB codebase or documentation.

   .. grid-item-card:: Glossary
            :link: glossary
            :link-type: doc
            :margin: 2 2 0 0

            Glossary of terms and definitions used in PyEDB.


Why PyEDB?
----------

PyEDB represents a modern approach to PCB design automation using Python, offering significant advantages over traditional methods.


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


Performance and Integration
---------------------------
*   **Performance:** Direct .NET interoperability (current) provides efficient access to EDB functionality.
    The upcoming gRPC architecture enables distributed computing and parallel processing.

*   **Python Ecosystem:** Being a pure Python library, PyEDB integrates seamlessly with the vast Python data science and
machine learning stack (NumPy, Pandas, Matplotlib, Scikit-learn, PyTorch, etc.). You can easily post-process simulation
results or use AI/ML to guide design decisions.

Use Cases
---------
*   **Automated Design Rule Checking (DRC):** Script checks for your team's specific design rules.
*   **Regression Testing:** Ensure a new design change doesn't break SI/PI/thermal performance.
*   **Parameter Sweeping:** Automatically analyze hundreds of variations of a design (for example via spacing, layer
    thickness).
*   **Batch Processing:** Extract S-parameters from a library of interconnects.
*   **Report Generation:** Automatically generate standardized PDF/HTML reports with plots and tables.


PyEDB cheat sheets
------------------

**EDB cheat sheet:** `EDB API <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.pdf>`_


Get help
--------

**Development issues:** For PyEDB development-related matters, see the
`PyAEDT Issues <https://github.com/ansys/pyedb/issues>`_ page.
You can create issues to report bugs and request new features.

**User questions:** The best way to get help is to post your question on the `PyEDV Discussions
<https://github.com/ansys/pyedb/discussions>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal. You can post questions, share ideas, and get community feedback.


License
-------
PyEDB is licensed under the MIT license.

PyEDB makes no commercial claim over Ansys whatsoever. This library extends the
functionality of AEDT by adding a Python interface to AEDT without changing the
core behavior or license of the original software. The use of PyAEDT requires a
legally licensed local copy of AEDT.

To get a copy of AEDT, see the `Ansys Electronics <https://www.ansys.com/products/electronics>`_
page on the Ansys website.



.. toctree::
   :hidden:
   :maxdepth: 2

   installation
   troubleshooting
   contribution_guide
   glossary
