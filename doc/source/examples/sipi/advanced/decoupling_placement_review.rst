Review local decoupling placement
=================================

Finds capacitors connected between the selected rail and reference net and measures their proximity to load power pins.

Engineering problem
-------------------

This standalone example addresses a real SI/PI design-review or model-preparation task. It uses direct PyEDB managers and does not use the Configuration Builder or an automatic-configuration workflow.

PyEDB APIs used
---------------

The complete source below shows the direct API calls, input validation, reliable EDB closure, and generated engineering report.

Run the example
---------------

Use ``python examples/decoupling_placement_review.py --help`` to see the required board-specific arguments. All component, net, and layer names are supplied on the command line, so no external profile or helper file is required.

Complete standalone source
--------------------------

.. literalinclude:: ../../../../../tests/system_examples/advanced/decoupling_placement_review.py
   :language: python
   :linenos:
   :caption: decoupling_placement_review.py

Review the result
-----------------

Review every generated report and AEDB before solving. Numerical distances, margins, currents, material properties, and acceptance limits are example inputs and must be selected for the actual design.
