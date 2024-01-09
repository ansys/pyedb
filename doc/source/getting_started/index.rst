Getting started
===============

.. grid:: 2

   .. grid-item-card:: About PyAnsys and EDB
            :link: About
            :link-type: doc

            Learn more about PyAnsys and Ansys Electronics Desktop.

   .. grid-item-card:: Installation
            :link: Installation
            :link-type: doc
            :margin: 2 2 0 0

            Learn how to install PyEDB from PyPi or conda.

   .. grid-item-card:: Quick code
            :link: Quickcode
            :link-type: doc
            :margin: 2 2 0 0

            Here's a brief example of how PyEDB works.


   .. grid-item-card:: Versions and interfaces
            :link: versioning
            :link-type: doc
            :margin: 2 2 0 0

            Discover the compatibility between PyEDB and Ansys AEDT versions.

   .. grid-item-card:: Troubleshooting
            :link: Troubleshooting
            :link-type: doc
            :margin: 2 2 0 0

            Any questions? Refer to Q&A before submitting an issue.


What is PyEDB ?
---------------
PyEDB is a Python library that interacts with the PyEDB-core API to make scripting simpler
with providing application oriented high level methods and properties.
The PyEDB class and method structures simplify operation while reusing information as much
as possible across the API. PyEDB is being run in memory and does not require user interface.
This api is extremely efficient on handling and editing large and complex layout designs. PyEDB
is the best choice for addressing layout design automation and its headless architecture makes it
well suited both on Windows and Linux.

PyEDB load and save AEDB files which stands for Ansys Electronic Data Base. AEDB files can
natively be read by ANSYS Electronics Desktop (AEDT) and ANSYS SIwave to visualize and edit
projects, run simulation or perform post processing. AEDB file are project self contained, meaning
ready to solve projects can be written with PyEDB. Therefore ANSYS solvers can directly load
AEDB file graphically or in batch non graphically with also supporting cluster Scheduler job submission.


To run PyEDB, you must have a licensed copy of Ansys Electronics
Desktop (AEDT) installed.

.. image:: ../Resources/aedt_3.png
  :width: 800
  :alt: AEDT Applications
  :target: https://www.ansys.com/products/electronics

For more information, see `Ansys Electronics <https://www.ansys.com/products/electronics>`_
on the Ansys website.


License
-------
PyEDB is licensed under the MIT license.

PyEDB makes no commercial claim over Ansys whatsoever. This library extends the
functionality of EDB by adding a Python interface to AEDT without changing the
core behavior or license of the original software. The use of PyEDB requires a
legally licensed local copy of AEDT.

To get a copy of AEDT, see the `Ansys Electronics <https://www.ansys.com/products/electronics>`_
page on the Ansys website.



.. toctree::
   :maxdepth: 1
   :includehidden:

   installation
   troubleshooting
   versioning
   contributing
   quickcode
   about

