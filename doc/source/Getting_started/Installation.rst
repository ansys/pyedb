Installation
============
PyEDB consolidates and extends all existing capital around scripting for AEDB,
allowing re-use of existing code, sharing of best practices, and collaboration.

This PyAnsys library has been tested on HFSS, Icepak, SIWave.

Requirements
~~~~~~~~~~~~
In addition to the runtime dependencies listed in the installation information, PyEDB
requires Ansys Electronics Desktop (AEDT) 2023 R2 or later.



Install from a Python file
~~~~~~~~~~~~~~~~~~~~~~~~~~
AEDT already includes CPython 3.7, which can be used to run PyEDB.
It is also possible to use CPython 3.7 (3.10 from AEDT 2023R2) as a virtual environment to run PyEDB.


Offline install is also possible using wheelhouses.
A wheelhouse is a zip containing all needed packages that can be installed offline.
PyEDB wheelhouse can be found at `Releases <https://github.com/ansys/pyedb/releases>`_.
After downloading the wheelhouse zip specific for your distribution and Python release,
run the script from Python terminal with providing the zip full path as argument.


Install on CPython from PyPI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
You can install PyEDB on CPython 3.7 through 3.10 from PyPI:

.. code:: python

    pip install pyansys-edb


Linux support
~~~~~~~~~~~~~

PyEDB works with CPython 3.7 through 3.10 on Linux in AEDT 2022 R2 and later.
However, you must set up the following environment variables:

.. code::

    export ANSYSEM_ROOT222=/path/to/AedtRoot/AnsysEM/v222/Linux64
    export LD_LIBRARY_PATH=$ANSYSEM_ROOT222/common/mono/Linux64/lib64:$ANSYSEM_ROOT222/Delcross:$LD_LIBRARY_PATH


Install offline from a wheelhouse
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Using a wheelhouse can be helpful if you work for a company that restricts access to external networks.
Wheelhouses for CPython 3.7, 3.8, and 3.9 are available in the releases for PyEDB v1.0
and later for both Windows and Linux. From the `Releases <https://github.com/ansys/pyansys-edb/releases>`_
page in the PyEDB repository, you can find the wheelhouses for a particular release in its
assets and download the wheelhouse specific to your setup.

You can then install PyEDB and all of its dependencies from one single entry point that can be shared internally,
which eases the security review of the PyEDB package content.

For example, on Windows with Python 3.7, install PyEDB and all its dependencies from a wheelhouse with code like this:

.. code::

    pip install --no-cache-dir --no-index --find-links=file:///<path_to_wheelhouse>/PyEDB-v<release_version>-wheelhouse-Windows-3.7 pyedb


Upgrade PyEDB to the latest version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    pip install -U pyedb-edb
