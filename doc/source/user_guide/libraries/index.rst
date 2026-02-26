Advanced libraries
==================

PyEDB provides a comprehensive set of pre-built libraries that significantly improve user experience by offering
reusable building blocks for common PCB and RF design tasks. These libraries eliminate the need to manually define
complex geometries, materials, and stackups from scratch.

Overview
--------

The PyEDB library system consists of three main categories:

**1. Common Libraries**
   Foundation classes for defining materials, substrates, and layer stackups. These provide standardized ways to
   specify dielectric materials, conductors, and multi-layer stackups commonly used in PCB design.

**2. RF Basic Libraries**
   Pre-built RF/microwave components and transmission line structures. These include parametric generators for
   common passive elements like inductors, capacitors, transmission lines, and impedance matching structures.

**3. Planar Antenna Libraries**
   Parametric antenna generators for common planar antenna types. These allow rapid prototyping of patch antennas
   with automatically calculated dimensions based on frequency and substrate properties.


Library Reference
-----------------

.. toctree::
   :maxdepth: 1

   common
   rf_basic
   antennas
