Audit DDR5 return-path transitions
==================================

Finds the nearest reference via for every selected DDR5 signal via and exports a CSV review list.

Engineering problem
-------------------

This standalone example addresses a real SI/PI design-review or model-preparation task. It uses direct PyEDB managers and does not use the Configuration Builder or an automatic-configuration workflow.

PyEDB APIs used
---------------

The complete source below shows the direct API calls, input validation, reliable EDB closure, and generated engineering report.

Run the example
---------------

Use ``python examples/ddr5_return_path_audit.py --help`` to see the required board-specific arguments. All component, net, and layer names are supplied on the command line, so no external profile or helper file is required.

Complete standalone source
--------------------------

.. literalinclude:: ../../../../../tests/system_examples/advanced/ddr5_return_path_audit.py
   :language: python
   :linenos:
   :caption: ddr5_return_path_audit.py

Review the result
-----------------

Review every generated report and AEDB before solving. Numerical distances, margins, currents, material properties, and acceptance limits are example inputs and must be selected for the actual design.
