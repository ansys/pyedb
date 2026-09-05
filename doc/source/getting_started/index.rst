Getting started
===============

.. grid:: 2

   .. grid-item-card:: Installation
            :link: installation
            :link-type: doc
            :margin: 2 2 0 0

            Learn how to install PyEDB.

   .. grid-item-card:: Quick start
            :link: quick_start
            :link-type: doc
            :margin: 2 2 0 0

            Install, open an EDB, inspect it, make a change, and save it in about 10 minutes.

   .. grid-item-card:: Object model
            :link: object_model
            :link-type: doc
            :margin: 2 2 0 0

            How the ``Edb`` entry point exposes stackup, materials, components, nets, and more.

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

PyEDB is built on top of lower-level APIs and provides a simplified, high-level interface for EDB automation.
It has a **dual-backend** architecture; PyEDB selects one automatically based on the resolved AEDT version
(see :doc:`backend_compatibility_migration` for the exact rule), or you can select it explicitly with the
``grpc`` constructor argument.

**gRPC backend (long-term supported, default for Ansys release 2026.1 and later):**

1. **Ansys EDB (gRPC service):** The ``ansys-edb-core`` service exposes the EDB engine over gRPC. It can run
   locally or on a remote/headless machine (Linux, Docker, CI) without a GUI.
2. **ansys-edb-core (Python client):** The Python gRPC client package, installed automatically as a base
   dependency of ``pyedb``.
3. **PyEDB (this library):** The high-level, user-friendly Python interface that wraps the gRPC client with
   app-oriented classes and methods (``Edb``, ``Stackup``, ``Components``, ``Nets``, and so on).

**DotNet backend (deprecated, requires the** ``pyedb[dotnet]`` **extra):**

1. **Ansys EDB (.NET libraries):** The original EDB engine, written in .NET and installed with AEDT.
2. **PythonNET bridge:** Uses the ``pythonnet`` package to load the .NET CLR (Common Language Runtime)
   directly into the Python process.
3. **PyEDB (this library):** The same high-level API surface as the gRPC backend, so user scripts written
   against public PyEDB APIs generally do not need to change when switching backends.

The DotNet backend requires AEDT to be installed on the same machine where PyEDB runs, because it loads the
local EDB .NET assemblies directly. The gRPC backend does not have this constraint and can connect to a
service running on a different machine.

Performance and integration
----------------------------
*   **Performance:** The gRPC backend is the long-term supported implementation and is recommended for new
    automation, especially on Linux or headless environments. See :doc:`backend_compatibility_migration` for
    the fast-mode performance notes.

*   **Python ecosystem:** Being a pure Python library, PyEDB integrates seamlessly with the vast Python data
    science and machine learning stack (NumPy, Pandas, Matplotlib, Scikit-learn, PyTorch, etc.). You can easily
    post-process simulation results or use AI/ML to guide design decisions.

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
features of AEDT by adding a Python interface to AEDT without changing the
core behavior or license of the original software. The use of PyAEDT requires a
legally licensed local copy of AEDT.

To get a copy of AEDT, see the `Ansys Electronics <https://www.ansys.com/products/electronics>`_
page on the Ansys website.



.. toctree::
   :hidden:
   :maxdepth: 2

   installation
   quick_start
   object_model
   cli
   backend_compatibility_migration
   troubleshooting
   contribution_guide
   glossary
