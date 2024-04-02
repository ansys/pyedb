About PyEDB
===========

PyEDB is part of the larger `PyAnsys <https://docs.pyansys.com>`_ effort to facilitate the use
of Ansys technologies directly from Python. It is intended to consolidate and extend all existing
functionalities around scripting for the Ansys Electronics Database (EDB) to allow reuse
of existing code, sharing of best practices, and increased collaboration.

PyEDB includes functionality for interacting with these
`Ansys Electronics Desktop <https://www.ansys.com/products/electronics>`_ (AEDT) products:

- EDB
- HFSS 3D Layout
- Icepak

What is EDB?
------------

EDB provides a proprietary database file format (AEDB) for efficient and fast layout design
handling and processing for building ready-to-solve projects. EDB addresses signal integrity
(SI), power integrity (PI-DC), and electro-thermal workflows. You can import an AEDB file
into AEDT to modify the layout, assign materials, and define ports, simulations, and constraints.
You can then launch any of the Ansys electromagnetic simulators: HFSS, HFSS 3D Layout, Icepak,
Maxwell, Q3D, and SIwave.

EDB runs as a standalone API, which means that you don't need to open a user interface (UI).
Because EDB opens the ``aedb`` folder for directly querying and manipulating layout design in
memory, it provides the fastest and most efficient way to handle a large and complex layout.

You can also parse an AEDB file from a command line in batch in an Ansys electromagnetic simulator
like HFSS or SIwave. Thus, you can deploy completely non-graphical flows, from layout
translation through simulation results.

Additionally, you can use PyAEDT to import an AEDB file into AEDT to view a project,
combine 3D designs, or perform simulation postprocessing. EDB also supports 3D component models.

.. image:: https://images.ansys.com/is/image/ansys/ansys-electronics-technology-collage?wid=941&op_usm=0.9,1.0,20,0&fit=constrain,0
  :width: 800
  :alt: AEDT Applications
  :target: https://www.ansys.com/products/electronics

Why use PyEDB?
--------------
PyEDB interacts with the `PyEDB-Core <https://github.com/ansys/pyedb-core>`_ API to make scripting simpler.
It provides application-oriented, high-level methods and properties. The PyEDB API's ``Edb`` class and methods
simplify operations while reusing information as much as possible across the API.

Because PyEDB runs in memory, it does not require a user interface. Its API is extremely efficient at
handling and editing large and complex layout designs. PyEDB is the best choice for addressing layout
design automation. Its headless architecture also makes it well suited on both Windows and Linux.

PyEDB loads and saves AEDB files, which can natively be read by AEDT and Ansys SIwave to visualize
and edit projects, run simulations, or perform postprocessing. AEDB files are project self-contained,
meaning that ready-to-solve projects can be written with PyEDB. Therefore Ansys solvers can directly
load AEDB files graphically or in batch non-graphically to support submission for job scheduling on a cluster.

.. image:: ../Resources/aedt_3.png
  :width: 800
  :alt: AEDT Applications
  :target: https://www.ansys.com/products/electronics

For more information, see `Ansys Electronics <https://www.ansys.com/products/electronics>`_
on the Ansys website.
