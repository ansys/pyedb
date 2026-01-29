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

PyEDB represents a modern, decoupled approach to PCB design automation, offering significant advantages over traditional methods.


Server-Side Automation & Headless Operation
-------------------------------------------
The core innovation of PyEDB is its client-server architecture:

*   **PyEDB (Client):** A pure Python library you install and run in your environment.
*   **ansys-edb-core (Server):** A separate, high-performance gRPC service that handles all EDB operations.

This means you can **run PyEDB on a machine without a graphical user interface (GUI)**, such as:

*   **Linux servers** and high-performance computing (HPC) clusters.
*   **Docker containers** for consistent, reproducible environments.
*   **Cloud platforms** like AWS, Azure, or GCP.

This enables true **CI/CD (Continuous Integration/Continuous Deployment) for PCB design**. You can automate checks,
simulations, and reports every time a design change is committed.

Performance and Integration
---------------------------
*   **Performance:** The gRPC protocol is fast and efficient, ideal for automating complex tasks and processing large
designs.
*   **Python Ecosystem:** Being a pure Python client, PyEDB integrates seamlessly with the vast Python data science and
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
