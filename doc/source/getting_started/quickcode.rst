Quick code
==========

Documentation and issues
------------------------
Documentation for the latest stable release of PyEDB is hosted at
`PyEDB documentation <https://edb.docs.pyansys.com/version/stable/>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

You can also view or download PyEDB cheat sheets, which are one-page references
providing syntax rules and commands for using the PyEDB API and PyEDB API:

- `View PyEDB cheat sheet <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.png>`_ or
  `download PyEDB cheat sheet  <https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.pdf>`_ the
  PyEDB API cheat sheet.


On the `PyEDB Issues <https://github.com/ansys/pyedb/issues>`_ page, you can
create issues to report bugs and request new features. On the `PyEDB Discussions
<https://github.com/ansys/pyedb/discussions>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.


Example workflow
----------------
Here’s a brief example of how PyEDB works:

Connect to EDB from a Python IDE
---------------------------------
PyEDB works both inside AEDT and as a standalone app.
PyEDB also provides advanced error management. Usage examples follow.

Explicit PyEDB declaration and error management
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    # Start EDB

    from pyedb.dotnet.edb import Edb

    edb_file = pyedb.layout_examples.ANSYS - HSD_V1.aedb
    edb = Edb(edbversion="2023.2", edbpath=edb_file)


Variables
~~~~~~~~~

.. code:: python

    from pyedb.dotnet.edb import Edb

    edb_file = pyedb.layout_examples.ANSYS - HSD_V1.aedb
    edb = Edb(edbversion="2023.2", edbpath=edb_file)
    edb["dim"] = "1mm"  # design variable
    edb["$dim"] = "1mm"  # project variable
