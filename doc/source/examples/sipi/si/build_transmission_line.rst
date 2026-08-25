.. _build_transmission_line_example:

Build a controlled-impedance transmission-line model
====================================================

This example creates a small EDB from scratch to introduce the PyEDB stackup,
modeler, net, and padstack APIs. It is deterministic and does not require the
generic system-example board.

Learning objectives
-------------------

* Create an empty EDB in a temporary directory.
* Define conductor and dielectric layers.
* Create signal and reference geometry.
* Place endpoint pads or vias.
* Inspect the resulting layout before closing the EDB.

Workflow
--------

#. Create an empty EDB.
#. Add the stackup and materials.
#. Create ``SIG`` and ``GND`` nets.
#. Draw the signal trace and reference geometry.
#. Create and place the required padstack instances.
#. Save, close, and reopen the EDB for verification.

Run the example
---------------

.. literalinclude:: ../../../../tests/system_examples/sipi/si/build_transmission_line.py
   :language: python
   :linenos:
   :caption: build_transmission_line.py

Expected output
---------------

.. code-block:: text

   <output_directory>/simple_si_line.aedb

Validation checks
-----------------

Verify that:

* The expected conductor and dielectric layers exist.
* ``SIG`` and ``GND`` exist.
* The signal trace is assigned to ``SIG``.
* The reference geometry is assigned to ``GND``.
* The expected padstack instances exist.
* The generated EDB reopens successfully.

.. note::

   This example creates geometry and prepares an EDB. It does not calculate
   characteristic impedance or solve the structure. Use a PyAEDT continuation
   when solver execution or result plots are required.

Related APIs
------------

See the API reference for :class:`pyedb.Edb` and the stackup, modeler, net, and
padstack managers exposed by the EDB session.
