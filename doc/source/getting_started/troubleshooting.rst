Troubleshooting
===============
In addition to explaining how to create PyEDB discussions or issues, this section describes 
how to troubleshoot some common issues related to installing and using PyEDB.

Issues and discussions
----------------------

On the `PyEDB Issues <https://github.com/ansys/Pansys-edb/issues>`_ page, you can
create issues to report bugs and request new features.

On the `PyEDB Discussions
<https://github.com/ansys/pyansys-edb/discussions>`_ page or the `Discussions <https://discuss.ansys.com/>`_
page on the Ansys Developer portal, you can post questions, share ideas, and get community feedback.

To reach the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.Example

Installation troubleshooting
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Error installing Python or Conda
--------------------------------
Some companies do not allow installation of a Python interpreter. In this case, you can
use the Python interpreter available in the AEDT installation.

.. note::

   Python 3.7 is available in AEDT 2023 R1 and earlier. Python 3.10 is available in AEDT 2023 R2
   and later.

Here is the path to the Python 3.7 interpreter for the 2023 R1 installation:

.. code:: python

   "path\to\AnsysEM\v231\commonfiles\CPython\3_7\winx64\Release\python"


Error installing PyEDB using ``pip``
-----------------------------------
According to `Installing Python modules <https://docs.python.org/3/installing/index.html>`_
in the official Python documentation, `pip <https://pip.pypa.io/en/stable/>`_ is the preferred
installer program and is included by default with the Python binary installers. If you have issues
using ``pip``, check for these issues:

- **Proxy server**: If your company uses a proxy server, you may have to update proxy
  settings at the command line. For more information, see the `Using a Proxy
  Server <https://pip.pypa.io/en/stable/user_guide/#using-a-proxy-server>`_ in the pip
  documentation.
- **Install permission**: Make sure that you have write access to the directory where the
  Python interpreter is installed. The use of a `virtual environment <https://docs.python.org/3/library/venv.html>`_
  helps mitigate this issue by placing the Python interpreter and dependencies in a location that is owned
  by the user.
- **Firewall**: Some corporate firewalls may block ``pip``. In this case, you must work with your IT
  administrator to enable it. The proxy server settings (described earlier) allow you to explicitly define
  the ports that ``pip`` is to use.

If downloads from `PyPI <https://pypi.org/>`_, the Python Package Index, are not allowed, you may use a
`wheelhouse <https://pypi.org/project/Wheelhouse/>`_. A wheelhouse is a ZIP file that contains all dependencies
for package and allows full installation without a need to download additional files.

You can find wheelhouses for PyEDB in the **Assets** are on the `Releases <https://github.com/ansys-internal/pyansys-edb/releases>`
page of the PyEDB repository. After downloading the wheelhouse for your setup, extract the files to a folder and
run the command for installing PyEDB and all of its dependencies from your Python terminal, providing the full path to the ZIP file as an argument:

.. code:: shell

   pip install --no-cache-dir --no-index --find-links=/path/to/pyansys-edb/wheelhouse pyansys-edb

Run PyEDB with gRPC
~~~~~~~~~~~~~~~~~~~
`gRPC <https://grpc.io/>`_ is a modern open source, high-performance RPC (remote procedure call)
framework that can run in any environment and supports client/server remote calls.
Starting from 202 4R1, the EDB-Core API has replaced the .NET interface with a gRPC interface.

.. list-table:: *gRPC compatibility:*
   :widths: 65 65 65
   :header-rows: 1

   * - < 2022 R2
     - 2024 R1
     - > 2024 R1
   * - Only ``Python.NET``
     - | ``Python.NET``: *Default*
     - | gRPC: *Default*