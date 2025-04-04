.. _install_pyedb:

Installation
============

PyEDB consolidates and extends all existing capital around scripting for EDB,
allowing reuse of existing code, sharing of best practices, and collaboration.

PyEDB has been tested on HFSS, Icepak, and SIWave.

Requirements
~~~~~~~~~~~~

To use PyEDB, you must have a licensed copy of AEDT 2023 R2 or later.

PyEDB also supports the AEDT Student version 2023 R2 or later. For more information, see the
`Ansys Electronics Desktop Student  - Free Software Download <https://www.ansys.com/academic/students/ansys-e
lectronics-desktop-student>`_ page on the Ansys website.

Any additional runtime dependencies are listed in the following installation topics.

Install from a Python file
~~~~~~~~~~~~~~~~~~~~~~~~~~

The AEDT installation already provides a Python interpreter that you can use to run PyEDB. In a virtual environment,
you can run PyEDB using CPython 3.9 through 3.11. Note that AEDT 2024 R1 installs CPython 3.10.

You can install PyEDB offline using a wheelhouse, which is a ZIP file containing all
the needed packages. The `Releases <https://github.com/ansys/pyedb/releases>`_
page of the PyEDB repository provides an **Assets** ares with the PyEDB wheelhouses for
various Python releases on different operating system.

After downloading the wheelhouse for your Python release and operating system,
run the script from the Python terminal, providing the full path to the ZIP file
as an argument.

Install on CPython from PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install PyEDB on CPython 3.8 through 3.11 from PyPI, the Python Package Index,
with this command:

.. code:: shell

    pip install pyedb

Linux support
~~~~~~~~~~~~~

PyEDB works with CPython 3.8 through 3.10 on Linux in AEDT 2022 R2 and later.
However, you must set up the following environment variables:

.. code::

    export ANSYSEM_ROOT222=/path/to/AedtRoot/AnsysEM/v222/Linux64
    export LD_LIBRARY_PATH=$ANSYSEM_ROOT222/common/mono/Linux64/lib64:$ANSYSEM_ROOT222/Delcross:$LD_LIBRARY_PATH

.. _install_pyedb_from_wheelhouse:

Install offline from a wheelhouse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using a wheelhouse can be helpful if you work for a company that restricts access
to external networks. A wheelhouse is a ZIP file that contains all dependencies
for package and allows full installation without a need to download additional files.
Having a single file eases the security review of the package content and allows for
easy sharing with others who need to install it.

On the `Releases <https://github.com/ansys/pyedb/releases>`_ page of the PyEDB repository,
the **Assets** area shows the wheelhouses that are available. After downloading the wheelhouse for your setup,
extract the files to a folder and run the command for installing PyEDB and all of its dependencies
from your Python terminal, providing the full path to the ZIP file as an argument.

.. code:: shell

   pip install --no-cache-dir --no-index --find-links=/path/to/pyedb/wheelhouse pyedb

For example, on Windows with Python 3.8, install PyEDB and all its dependencies from a
wheelhouse with code like this:

.. code::

    pip install --no-cache-dir --no-index --find-links=file:///<path_to_wheelhouse>/PyEDB-v<release_version>-wheelhouse-Windows-3.8 pyedb


Update PyEDB to the latest version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After installing PyEDB, upgrade it to the latest version with this command:

.. code:: bash

    pip install -U pyedb
