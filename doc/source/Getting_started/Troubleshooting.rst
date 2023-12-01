Troubleshooting
===============
This section contains common issues and suggestions related to installation and use of PyEDB.

Installation
~~~~~~~~~~~~

Error installing Python or Conda
--------------------------------
Sometimes companies do not allow installation of a Python interpreter.
In this case, you can use the Python interpreter available in the AEDT installation.

.. note::

   Python 3.7 is available in AEDT 2023 R1 and earlier. Python 3.10 is available in AEDT 2023 R2.

Here is the path to the Python 3.7 interpreter for the 2023 R1 installation:

.. code:: python

   "path\to\AnsysEM\v231\commonfiles\CPython\3_7\winx64\Release\python"


Error installing PyEDB using pip
---------------------------------
- **Proxy server**: If your company uses a proxy server, you may have to update proxy
  settings at the command line. For more information, see the `Using a Proxy
  Server <https://pip.pypa.io/en/stable/user_guide/#using-a-proxy-server>`_ in the pip
  documentation.
- **Install permission**: Make sure that you have write access to the directory where the
   Python interpreter is
   installed. The use of a `virtual environment <https://docs.python.org/3/library/venv.html>`_ helps
   mitigate this issue by placing the Python interpreter and dependencies in a location that is owned
   by the user.
- **Firewall**: Some corporate firewalls may block pip. If you face this issue, you'll have to work with your IT
   administrator to enable pip. The proxy server settings (described earlier) allow you to explicitly define
   the ports used by pip.

If downloads from `pypi <https://pypi.org/>`_ are not allowed, you may use a
`wheelhouse <https://pypi.org/project/Wheelhouse/>`_.
The wheelhouse file contains all dependencies for PyAEDT and allows full installation without a need to
download additional files.
The wheelhouse for PyAEDT can be found `here <https://github.com/ansys/pyaedt/releases>`_.
After downloading the wheelhouse for your distribution and Python release, unzip the file to a folder and
run the Python command:

.. code:: shell

   pip install --no-cache-dir --no-index --find-links=/path/to/pyansys-edb/wheelhouse pyansys-edb


Run PyEDB with gRPC
~~~~~~~~~~~~~~~~~~~
`gRPC <https://grpc.io/>`_ is a modern open source high performance Remote Procedure Call (RPC)
framework that can run in any environment and supports client/server remote calls.
Starting from 2024R1 the EDB-core API has replaced the .NET interface with a gRPC interface.


.. list-table:: *gRPC Compatibility:*
   :widths: 65 65 65
   :header-rows: 1

   * - < 2022 R2
     - 2024 R1
     - > 2024 R1
   * - Only ``Python.NET``
     - | ``Python.NET``: *Default*
       | Enable gRPC: ``pyaedt.settings.use_grpc_api = True``
     - | gRPC: *Default*