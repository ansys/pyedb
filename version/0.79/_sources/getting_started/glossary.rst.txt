Glossary
========

.. glossary::
   :sorted:

   Cell
      Represents the PCB design itself within an EDB project. A project has one active cell. Adding multiple cells
      is actually adding multiple designs to the same project.

   ansys-edb-core
      The standalone gRPC service that performs all EDB operations. PyEDB connects to this service as a client.
      It is also called PyEDB-core.

   gRPC
      A modern, high-performance open-source RPC framework. It is the communication protocol between PyEDB and the ansys-edb-core service.

   Layout
      The container within a Cell for all the physical data of the PCB (stackup, geometries, components).

   Net
      A collection of electrically connected pins and primitives (traces, pads) in a layout. Equivalent to a "signal" in schematic terms.

   Primitive
      A basic geometric shape (polygon, path, rectangle, circle) in an EDB layout.

   Stackup
      The vertical arrangement of conductive and dielectric layers that make up a PCB.