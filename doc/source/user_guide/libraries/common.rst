Common Libraries
================

The common libraries provide fundamental building blocks for PCB design, including material definitions,
substrate specifications, and layer stackup configurations.

Typical Workflow
----------------

1. Define substrate properties using the ``Substrate`` dataclass
2. Create or reference materials (copper, FR4, etc.) using ``Material`` classes
3. Build layer stackup using ``Layer`` classes
4. Apply stackup to your EDB design

API Reference
-------------

.. currentmodule:: pyedb.libraries.common

.. autosummary::
   :toctree: _autosummary
   :nosignatures:

   Substrate
   Material
   Conductor
   Dielectric
   Layer
   MetalLayer
   DielectricLayer
   MicroStripTechnologyStackup