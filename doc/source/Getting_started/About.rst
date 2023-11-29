About PyEDB
===========

PyEDB
-------

PyEDB is part of the larger `PyAnsys <https://docs.pyansys.com>`_
effort to facilitate the use of Ansys technologies directly from Python.

PyEDB is intended to consolidate and extend all existing
functionalities around scripting for ANSYS Electronic DataBase (EDB) to allow reuse of existing code,
sharing of best practices, and increased collaboration.


About AEDB
----------

`ANSYS EDB (AEDB) <https://www.ansys.com/products/electronics>`_ is a database allowing efficient and fast
layout design handling and processing for building ready to solve projects. EDB is addressing Signal
Integrity (SI), Power Integrity (PI-DC) and also Electro-Thermal work flows. The EDB can be
imported into Electromagnetic Desktop which enables a user to modify layout,
assign materials, define ports, simulations and constraints and then launch any of
the various electromagnetic simulators: HFSS, HFSS3Dlayout, SIwave, Icepak, Maxwell, Q3D.

AEDB is running as stand alone API and opens aedb folder for directly querying and manipulating
layout design in memory and does not require opening any User Interface (UI). Hence AEDB is the fastest
and most efficient way to handle large and complex layout.

AEDB can also been parsed with and Electromagnetic simulator command line like HFSS or SIwave in bacth.
Therefore completely non graphical flows can be deployed from layout translation up to simulatiom results.
AEDB can also be imported in ANSYS AEDT with PyAEDT for example to display the project, combining 3D design
or performing simulation post-processing. AEDB also supports 3D component models.

.. image:: https://images.ansys.com/is/image/ansys/ansys-electronics-technology-collage?wid=941&op_usm=0.9,1.0,20,0&fit=constrain,0
  :width: 800
  :alt: AEDT Applications
  :target: https://www.ansys.com/products/electronics


PyEDB is licensed under the `MIT License
<https://github.com/ansys/pyedb/blob/main/LICENSE>`_.


Dependencies
------------
To run PyEDB, you must have a local licensed copy of AEDT.

Student version
---------------

PyEDB supports AEDT Student versions 2022 R2 and later. For more information, see the
`Ansys Electronics Desktop Student  - Free Software Download <https://www.ansys.com/academic/students/ansys-e
lectronics-desktop-student>`_ page on the Ansys website.


Why PyEDB?
-----------
ANSYS EDB is very powerful for processing complex and large layout design. EDB-core native API
can be used to automate workflows. However it requires a deep comprehension of the architecture and
classes inheritances, resulting with a learning curve not always compatible with daily work load.

PyEDB was developed to provide high level classes calling EDB-core API to speed up EDB adoption
and improve user experience. Thanks to its application oriented architecture PyEDB, users can
start using EDB faster and easier.

