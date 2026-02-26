RF Basic Libraries
==================

The RF basic libraries provide parametric generators for common RF and microwave passive components.
These pre-built functions automate the creation of complex geometries that would otherwise require
manual calculation and drawing.

Summary
-------

These libraries enable rapid prototyping of RF circuits by providing:

* **Transmission Lines**: Coplanar waveguide (CPW), differential pairs, and meandered lines
* **Passive Components**: Spiral inductors, MIM capacitors, interdigital capacitors
* **Matching Networks**: Radial stubs and other impedance transformation structures
* **Power Dividers**: Rat-race couplers and other power splitting/combining circuits
* **Ground Structures**: Hatched ground planes for controlled impedance


API Reference
-------------

.. currentmodule:: pyedb.libraries.rf_libraries.base_functions

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   HatchGround
   Meander
   MIMCapacitor
   SpiralInductor
   CPW
   RadialStub
   RatRace
   InterdigitalCapacitor
   DifferentialTLine