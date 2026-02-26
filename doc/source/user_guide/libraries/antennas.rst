Planar Antennas Libraries
=========================

The planar antenna libraries provide parametric generators for common microstrip patch antenna geometries.
These functions automatically calculate antenna dimensions based on operating frequency and substrate properties,
eliminating tedious manual calculations.

Purpose
-------

Patch antennas are widely used in wireless systems due to their:

* Low profile and conformability
* Ease of fabrication using standard PCB processes
* Integration with microstrip feed networks
* Dual-frequency and circular polarization capabilities

The PyEDB antenna libraries automate the design of these antennas by:

* Calculating resonant patch dimensions from target frequency
* Accounting for substrate properties (εr, thickness)
* Generating feed point locations for optimal matching
* Creating the complete geometry ready for simulation


API Reference
-------------

.. currentmodule:: pyedb.libraries.rf_libraries.planar_antennas

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

    RectangularPatch
    CircularPatch
    TriangularPatch