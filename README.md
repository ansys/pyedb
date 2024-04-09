<!-- -->
<a name="readme-top"></a>
<!--
*** PyEDB README
-->


# PyEDB

[![PyAnsys](https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC)](https://docs.pyansys.com/)
[![PythonVersion](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is PyEDB?

PyEDB is Python client library for processing complex and large layout designs in the
Ansys Electronics Database (EDB) format, which stores information describing designs for
[Ansys Electronics Desktop](https://www.ansys.com/products/electronics) (AEDT).

While you can also use the [PyEDB-Core](https://github.com/ansys/pyedb-core) API to automate EDB workflows,
using it requires a deep comprehension of the EDB architecture and class inheritances, resulting in
a learning curve not always compatible with daily work loads.

To speed up EDB adoption and improve user experience, PyEDB provides high-level classes that call
the PyEDB-Core API. Thanks to PyEDB's application-oriented architecture, you can start using EDB
faster and easier.

## About PyEDB

PyEDB is part of the larger [PyAnsys](https://docs.pyansys.com "PyAnsys") effort to facilitate the use
of Ansys technologies directly from Python. It is intended to consolidate and extend all existing
functionalities around scripting for EDB to allow reuse of existing code, sharing of best practices,
and increased collaboration.

PyEDB includes functionality for interacting with Ansys electromagnetic simulators: : HFSS,
HFSS 3D Layout, Icepak, Maxwell, Q3D, and SIwave.

## What is EDB?

EDB provides a proprietary database file format (AEDB) for efficient and fast layout design
handling and processing for building ready-to-solve projects. EDB addresses signal integrity
(SI), power integrity (PI-DC), and electro-thermal work flows. You can import an AEDB file
into AEDT to modify the layout, assign materials, and define ports, simulations, and constraints.
You can then launch any of the Ansys electromagnetic simulators.

EDB runs as a standalone API, which means that you don't need to open a user interface (UI).
Because EDB opens the ``aedb`` folder for directly querying and manipulating layout design in
memory, it provides the fastest and most efficient way to handle a large and complex layout.

You can also parse an AEDB file from a command line in batch in an Ansys electromagnetic simulator
like HFSS or SIwave. Thus, you can deploy completely non-graphical flows, from layout
translation through simulatiom results.

Additionally, you can use PyAEDT to import an AEDB file into AEDT to view a project,
combine 3D designs, or perform simulation postprocessing. EDB also supports 3D component models.

## Documentation and issues

Documentation for the latest stable release of PyEDB is hosted at
[PyEDB documentation](https://edb.docs.pyansys.com/version/stable/index.html).
The documentation has five sections:

- [Getting started](https://edb.docs.pyansys.com/version/version/stable/getting_started/index.html): Describes
  how to install PyEDB in user mode.
- [User guide](https://edb.docs.pyansys.com/version/version/stable/user_guide/index.html): Describes how to
  use PyEDB.
- [API reference](https://edb.docs.pyansys.com/version/version/stable/api/index.html): Provides API member descriptions
  and usage examples.
- [Examples](https://edb.docs.pyansys.com/version/version/stable/examples/index.html): Provides examples showing
  end-to-end workflows for using PyEDB.
- [Contribute](https://edb.docs.pyansys.com/version/version/stable/contribute.html): Describes how to install
  PyEDB in developer mode and how to contribute to this PyAnsys library.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

On the [PyEDB Issues](https://github.com/ansys/pyedb/issues) page, you can
create issues to report bugs and request new features. On the
[PyEDB Discussions](https://github.com/ansys/pyedb/discussions) page or the
[Discussions](https://discuss.ansys.com/) page on the Ansys Developer portal,
you can post questions, share ideas, and get community feedback.

To reach the project support team, email [pyansys.core@ansys.com](mailto:pyansys.core@ansys.com).

## License

PyEDB is licensed under the [MIT License](https://github.com/ansys/pyedb/blob/main/LICENSE).

PyEDB makes no commercial claim over Ansys whatsoever. This library extends the
functionality of EDB by adding a Python interface to PyEDB-Core without changing the
core behavior or license of the original software. The use of PyEDB requires a
legally licensed local copy of AEDT.

To get a copy of AEDT, see the [Ansys Electronics](https://www.ansys.com/products/electronics)
page on the Ansys website.

<p style="text-align: right;"> <a href="#readme-top">back to top</a> </p>
