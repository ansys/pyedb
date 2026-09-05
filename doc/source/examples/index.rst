.. _pyedb_examples:

Examples
========

High-Frequency Layout Examples (PyAEDT + PyEDB)
-----------------------------------------------

These examples show how PyEDB and PyAEDT work together to create solve and post-process high-frequency PCB/IC packages and RF boards.
They are maintained in the main PyAEDT example gallery and include:

* Import and modification of EDB layout
* HFSS 3D and HFSS 3D Layout set-ups
* Frequency sweeps, field plots, S-parameter export
* Parametric studies and optimization loops

.. raw:: html

   <div style="margin-bottom:1.5em;">
     <a class="reference external"
        href="https://examples.aedt.docs.pyansys.com/version/dev/examples/high_frequency/layout/index.html">
        <button style="background:#0076CE;color:white;border:0;border-radius:4px;padding:.6em 1em;margin-right:.5em">
          📖 Browse Examples
        </button>
     </a>

     <a class="reference external"
        href="https://github.com/ansys/pyaedt-examples/tree/main/examples/high_frequency/layout">
        <button style="background:#24292f;color:white;border:0;border-radius:4px;padding:.6em 1em">
          📁 View on GitHub
        </button>
     </a>
   </div>

Feel free to open an issue or pull request if you would like to add new PyEDB-focused examples to this collection.

This examples are focused on using PyEDB to create, modify, and analyze PCB/IC packages and RF boards. The basic
section covers fundamental tasks, while the advanced section demonstrates more complex workflows for Si-PI.

For a full catalog of PyEDB-only examples (configuration API and workflow examples) with metadata
(objective, difficulty, backend, and public entry points), see :doc:`example_inventory`.


PyEDB workflows
===============

PyEDB provides a powerful interface for automating PCB design tasks.
The following sections contain examples that illustrate various workflows using PyEDB.

.. grid-item-card:: Workflows :fa:`diagram-project`
    :link: pyedb_workflows
    :link-type: ref

    Explore PyEDB workflows for SIPI, utilities, and DRC features.

.. toctree::
   :hidden:
   :maxdepth: 1

   example_inventory
