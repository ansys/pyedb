Backend, compatibility, and migration
=====================================

PyEDB provides a **high-level Python API** for EDB workflows.

For most users, the most important fact is this:

.. epigraph::

   The exposed PyEDB high-level APIs are intended to be **backend agnostic**.

In other words, most user automation should focus on the PyEDB API itself rather than on backend implementation details.

Why this page exists
--------------------

Most users do **not** need to think about backend selection during normal use.

However, backend details can matter when you are:

- migrating existing workflows,
- troubleshooting platform-specific issues,
- validating deployment environments,
- comparing long-term support expectations,
- or explicitly selecting a backend in advanced workflows.

This page is the authoritative place for those details.

Recommended guidance for most users
-----------------------------------

If you are new to PyEDB:

#. Install ``pyedb``
#. Start with the Edb entry point (the Edb class in the pyedb package).
#. Learn the high-level API through the Getting started guide, User guide, and Examples
#. Ignore backend details unless you have a specific compatibility or deployment reason to care

High-level API stability goal
-----------------------------

PyEDB is designed so that the user-facing, high-level APIs remain consistent across supported backends.

This means that:

- the same automation concepts should apply,
- the same high-level objects and workflows should remain valid,
- and backend choice should be a secondary implementation detail for most users.

Backend overview
----------------

PyEDB supports backend selection through the ``Edb`` constructor.

Example:

.. code-block:: python

   from pyedb import Edb

   edb = Edb(edbpath="myedb.aedb", version="2026.1", grpc=False)

The ``grpc`` flag allows advanced users to explicitly choose the backend when needed.

Current direction
-----------------

The long-term direction is to standardize on the **gRPC backend** as the long-term supported backend.

Why:

- it is pure Python from the user point of view,
- it is better aligned with long-term maintainability,
- and it avoids the ongoing friction associated with .NET-based deployment, especially on Linux.

The current backend default may remain unchanged for compatibility during a transition period, but the long-term recommendation is to move toward gRPC.

Platform guidance
-----------------

Linux
~~~~~

If you are deploying on Linux, prefer the gRPC backend when possible.

Existing workflows that use .NET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Existing workflows can continue to use the current backend behavior during the transition period, especially when compatibility validation is still in progress.

New automation
~~~~~~~~~~~~~~

For new automation, write your code against the high-level PyEDB APIs and avoid embedding backend-specific assumptions.

Migration guidance
------------------

If your code already uses PyEDB high-level APIs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Your migration path should be simple:

- keep using the same high-level PyEDB APIs,
- validate your workflow with the target backend,
- and avoid depending on backend-specific internals.

If your code depends on backend-specific behavior
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Refactor toward:

- public PyEDB APIs,
- documented behaviors,
- and explicit compatibility checks only where absolutely necessary.

If you maintain examples or internal automation templates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Prefer examples that:

- demonstrate the high-level PyEDB API first,
- keep backend selection optional,
- and isolate backend-specific notes in small callouts instead of central workflow text.

Compatibility policy
--------------------

The compatibility goal is:

- **User-facing high-level APIs:** should remain stable and backend agnostic
- **Backend selection details:** should remain an advanced topic
- **Migration guidance:** should be documented here, not scattered across tutorials
- **Long-term recommendation:** prefer gRPC for future-facing workflows

Frequently asked questions
---

Do you need to care about the backend to start using PyEDB?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

No. Most users should start with the high-level API and only consult this page if they hit a platform, compatibility, or migration question.

Is backend selection part of the public high-level user experience?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only as an advanced option. For most tutorials and examples, backend details should remain secondary.

Which backend is recommended for the long term?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

gRPC is the long-term supported direction.

Should backend details appear in beginner documentation?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only minimally. Beginner documentation should focus on the high-level PyEDB API and common workflows.

Related pages
-------------

- :doc:`index`
- :doc:`installation`
- :doc:`../user_guide/index`