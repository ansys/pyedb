<!-- -->
<a name="readme-top"></a>
<!--
*** PyEDB README
-->


# PyEDB

<p style="text-align: center;">
    <br> English | <a href="README_CN.md">中文</a>
</p>

[![PyAnsys](https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC)](https://docs.pyansys.com/)
[![PythonVersion](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[!

## What is PyEDB ?

ANSYS EDB is very powerful for processing complex and large layout design. EDB-core native API
can be used to automate workflows. However it requires a deep comprehension of the architecture and
classes inheritances, resulting with a learning curve not always compatible with daily work load.

PyEDB was developed to provide high level classes calling EDB-core API to speed up EDB adoption
and improve user experience. Thanks to its application oriented architecture PyEDB, users can
start using EDB faster and easier.

## Install on CPython from PyPI

You can install PyEDB on CPython 3.7 through 3.10 from PyPI with this command:

```sh
  pip install pyansys-edb
```

Install PyEDB with all extra packages (matplotlib, numpy, pandas, pyvista):

```sh
  pip install pyansys-edb[full]
```

## About PyAnsys

PyEDB is part of the larger [PyAnsys](https://docs.pyansys.com "PyAnsys") effort to facilitate the use of Ansys technologies directly from Python.

PyEDB is intended to consolidate and extend all existing
functionalities around scripting for EDB to allow reuse of existing code,
sharing of best practices, and increased collaboration.

## About EDB

[AEDT](https://www.ansys.com/products/electronics) is a database allowing efficient and fast
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
AEDB can also be imported in ANSYS AEDT with PyAEDT for example to display the project, combining 3D design or performing simulation post-processing. AEDB also supports 3D component models.

`PyEDB` is licensed under the [MIT License](https://github.com/ansys/pyedb/blob/main/LICENSE)

PyEDB includes functionality for interacting with the following AEDT tools and Ansys products:

  - HFSS 3D Layout
  - Icepak
  - EDB
  - Icepak

## Documentation and issues

Documentation for the latest stable release of PyEDB is hosted at
[PyEDB documentation](https://aedb.docs.pyansys.com/version/stable/).

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

You can also view or download PyEDB cheat sheets, which are one-page references
providing syntax rules and commands for using the PyEDB API:

- [View](https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.png) or
  [download](https://cheatsheets.docs.pyansys.com/pyedb_API_cheat_sheet.pdf) the
  PyEDB API cheat sheet.


On the [PyEDB Issues](https://github.com/ansys/pyansys-edb/issues) page, you can
create issues to report bugs and request new features. On the
[PyEDB Discussions](https://github.com/ansys/pyansys-edb/discussions) page or the
[Discussions](https://discuss.ansys.com/) page on the Ansys Developer portal,
you can post questions, share ideas, and get community feedback.

To reach the project support team, email [pyansys.core@ansys.com](mailto:pyansys.core@ansys.com).

## Dependencies

To run PyEDB, you must have a local licenced copy of AEDT.
PyEDB supports AEDT versions 2022 R1 or newer.

## Why PyEDB ?

ANSYS EDB is very powerful for processing complex and large layout design. EDB-core native API
can be used to automate workflows. However it requires a deep comprehension of the architecture and
classes inheritances, resulting with a learning curve not always compatible with daily work load.

PyEDB was developed to provide high level classes calling EDB-core API to speed up EDB adoption
and improve user experience. Thanks to its application oriented architecture PyEDB, users can
start using EDB faster and easier.

## Example workflow

 1.
 2.

## Connect to PyEDB from Python IDE

PyEDB works both inside AEDT and as a standalone application. This Python library
automatically detects whether it is running in an IronPython or CPython environment
and initializes AEDT accordingly. PyAEDT also provides advanced error management.
Usage examples follow.

## Explicit AEDT declaration and error management

``` python
# Launch PyEDB 2024 R1

from pyedb import EDB
```

## License

PyEDB is licensed under the MIT license.

PyEDB makes no commercial claim over Ansys whatsoever. This library extends the
functionality of EDB by adding a Python interface to EDB-core without changing the
core behavior or license of the original software. The use of PyEDB requires a
legally licensed local copy of AEDT.

To get a copy of AEDT, see the [Ansys Electronics](https://www.ansys.com/products/electronics)
page on the Ansys website.

<p style="text-align: right;"> <a href="#readme-top">back to top</a> </p>

## Indices and tables

-  [Index](https://edb.docs.pyansys.com/version/stable/genindex.html)
-  [Module Index](https://edb.docs.pyansys.com/version/stable/py-modindex.html)
-  [Search Page](https://edb.docs.pyansys.com/version/stable/search.html)
