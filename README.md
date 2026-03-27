<!-- -->
<a name="readme-top"></a>
<!--
*** PyEDB README
-->

# PyEDB

[![PyAnsys](https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC)](https://docs.pyansys.com/)
[![PythonVersion](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/ansys/pyedb)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/cadfeebb7d8346eeb4c3373cbcdffa64)](https://app.codacy.com/gh/ansys/pyedb/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

## What is PyEDB?

PyEDB is a **high-level Python API** for processing complex and large layout designs in the
Ansys Electronics Database (EDB) format, which stores information describing designs for
[Ansys Electronics Desktop](https://www.ansys.com/products/electronics) (AEDT).

PyEDB is designed to make EDB automation easier to learn and faster to use. It provides
high-level, application-oriented workflows for common layout tasks such as:

- opening and creating EDB projects,
- editing stackups and materials,
- working with components, nets, padstacks, and ports,
- building cutouts,
- and preparing designs for solver workflows.

For most users, the key point is simple:

> PyEDB exposes high-level APIs intended to stay consistent across supported backends.

This means that most users can focus on the public PyEDB API and do not need to think about
backend implementation details while getting started.

## New user path

If you are new to PyEDB, follow this path:

1. **Install PyEDB**
2. **Open or create a design with `Edb`**
3. **Use the Getting started guide and examples**
4. **Move to the User guide and API reference as needed**

### Install

```bash
pip install pyedb
```

### Open an EDB project

```python
from pyedb import Edb

edb = Edb(edbpath="myedb.aedb", version="2026.1")

# Your workflow here
# stackup, materials, components, nets, ports, padstacks, cutouts, ...

edb.close()
```

### Advanced: explicitly choose a backend

Most users can work directly with the high-level PyEDB API and do not need to care about
backend details.

If needed, backend selection is available through the `grpc` flag:

```python
from pyedb import Edb

edb = Edb(edbpath="myedb.aedb", version="2026.1", grpc=False)
```

For backend-specific guidance, compatibility notes, and migration recommendations, see the
dedicated backend / compatibility / migration documentation page.

## About PyEDB

PyEDB is part of the larger [PyAnsys](https://docs.pyansys.com/) effort to facilitate the use
of Ansys technologies directly from Python. It is intended to consolidate and extend existing
functionalities around scripting for EDB to allow reuse of existing code, sharing of best practices,
and increased collaboration.

PyEDB includes functionality for interacting with Ansys electromagnetic simulators such as:

- HFSS,
- HFSS 3D Layout,
- Icepak,
- Maxwell,
- Q3D,
- and SIwave.

## What is EDB?

EDB provides a proprietary database file format (AEDB) for efficient and fast layout design
handling and processing for building ready-to-solve projects. EDB addresses signal integrity
(SI), power integrity (PI-DC), and electro-thermal workflows.

You can import an AEDB file into AEDT to modify the layout, assign materials, and define ports,
simulations, and constraints. You can then launch any of the Ansys electromagnetic simulators.

EDB runs as a standalone API, which means that you do not need to open a user interface (UI).
Because EDB opens the `aedb` folder for directly querying and manipulating layout design in
memory, it provides a fast and efficient way to handle large and complex layouts.

You can also parse an AEDB file from a command line in batch in an Ansys electromagnetic simulator
such as HFSS or SIwave. Thus, you can deploy completely non-graphical flows, from layout
translation through simulation results.

Additionally, you can use PyAEDT to import an AEDB file into AEDT to view a project,
combine 3D designs, or perform simulation postprocessing. EDB also supports 3D component models.

## Documentation and issues

Documentation for the latest stable release of PyEDB is hosted at
[PyEDB documentation](https://edb.docs.pyansys.com/version/stable/index.htmldex.html):
  Learn how to install PyEDB, understand the basic concepts, and get started quickly.
- [Installation](https://edb.docs.pyansys.com/version/stable/getting_started/installation.html):
  Install PyEDB and verify your environment.
- [User guide](https://edb.docs.pyansys.com/version/stable/user_guide/index.html#user-guidews.
- [API reference](https://edb.docs.pyansys.com/version/stable/api/index.html descriptions and usage details.
- [Examples](https://examples.aedt.docs.pyansys.com/version/dev/examples/high_frequency/layout/index.html):
  Explore end-to-end workflow examples for PyEDB.
- [Contribute](https://edb.docs.pyansys.com/version/stable/contributing.html mode and contribute to the codebase or documentation.

If you need backend-specific guidance, platform recommendations, or migration planning, see the
backend / compatibility / migration page in the documentation.

In the upper right corner of the documentation title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

On the [PyEDB Issues](https://github.com/ansys/pyedb/issues you can
create issues to report bugs and request new features.

On the [PyEDB Discussions](https://github.com/ansys/pyedb/discussionse
[Discussions](https://discuss.ansys.com/) page on the Ansys Developer portal,
you can post questions, share ideas, and get community feedback.

To reach the project support team, email [pyansys.core@ansys.com](mailto:pyansys.core@ansys.com).

## Backend guidance

PyEDB exposes **high-level APIs intended to be backend agnostic**.

For most users, backend selection should remain a secondary concern. Beginner workflows and
examples should focus on the public PyEDB API rather than backend implementation details.

Use the dedicated backend / compatibility / migration documentation page if you need guidance on:

- backend selection,
- platform considerations,
- compatibility validation,
- or migration planning.

## License

PyEDB is licensed under the [MIT License](https://github.com/ansys/pyedb/blob/main/LICENSEbrary extends the
functionality of EDB by adding a Python interface without changing the
core behavior or license of the original software.

The use of PyEDB requires a legally licensed local copy of AEDT.
To get a copy of AEDT, see the [Ansys Electronics](https://www.ansys.com/products/electronics)
page on the Ansys website.

<p style="text-align: right;"> <a href="#readme-top">back to top</a> </p>
