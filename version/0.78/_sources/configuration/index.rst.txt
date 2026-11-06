Configuration guides
====================

Why a configuration system?
----------------------------

Modern PCB and IC-package designs are highly complex artefacts. A production
board may contain dozens of signal layers, controlled-impedance stackups with
precise dielectric and copper properties, hundreds of component definitions,
thousands of padstack instances, multiple port types, and several solver setups.
All of these must be created correctly, validated, and reproduced bit-for-bit
across projects, design revisions, and team members.

When that complexity is encoded entirely in bespoke Python scripts, several
problems arise quickly:

* Scripts accumulate design-specific magic numbers and become hard to reuse.
* Peer review is difficult because the *intent* is buried inside imperative
  code rather than expressed as readable data.
* Getting new team members up to speed requires deep familiarity with the
  PyEDB API before any productive work can start.
* Integrating with upstream data sources (PLM systems, PDM vaults, Excel
  sign-off sheets) means writing and maintaining glue code for every project.
* Reproducing a past result or auditing a simulation requires tracing through
  scripts rather than diffing a compact data file.

The PyEDB **configuration system** was built to eliminate these friction points
by providing a **declarative, structured, and version-controllable description
of a complete EDB design workflow**. Instead of saying *how* to build the
design step by step, a configuration file says *what* the design should look
like, and PyEDB takes care of the rest.

Key benefits
~~~~~~~~~~~~

* **Repeatability and reproducibility**—A single JSON or TOML file fully
  captures the design intent. Applying it to the same EDB database twice
  always yields an identical result, making simulation results fully
  traceable and verifiable.

* **Readability and cross-discipline collaboration**—The file format is
  intentionally human-readable. Hardware engineers, layout designers, and
  signal-integrity analysts can review, understand, and comment on a
  configuration file without writing or reading a single line of Python.
  Design decisions are visible at a glance.

* **Version control and change tracking**—Because the design intent lives in
  a plain-text file, standard ``git diff`` workflows immediately show *what*
  changed between revisions—a net reassignment, a layer thickness update, a
  new port—without having to compare simulation outputs or screenshot logs.

* **Portability and reuse**—The same configuration file, or sections of it,
  can be applied to different EDB databases, reused as a controlled template
  across product families, or parameterised to generate design variants
  automatically.

* **CI/CD and tool-chain integration**—JSON and TOML are first-class citizens
  in every modern automation ecosystem. Configuration files are trivial to
  generate from upstream sources (PLM, PDM, BOM spreadsheets, in-house
  calculators) and equally easy to consume in Jenkins, GitHub Actions, or any
  other pipeline without any Python expertise in the CI layer.

* **Lightweight object-oriented builder**—For users who prefer to work in
  Python, every configuration section is also exposed through a concise,
  object-oriented builder API. The builder covers the full breadth of
  day-to-day automation tasks—stackup definition, material assignment,
  component configuration, padstack editing, port and excitation creation,
  HFSS/SIwave solver setup, and more—with a clean, discoverable interface.
  Users can be productive in minutes without needing to understand the
  underlying EDB object model or the PyEDB API surface.

When to go beyond the configuration system
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The configuration system is intentionally optimised for **breadth and
accessibility**. It is the right tool for the overwhelming majority of
day-to-day design automation tasks.

However, some advanced workflows demand a level of granularity that goes beyond
what a declarative system can reasonably express:

* Fine-grained geometry editing or custom via-structure creation.
* Net-class scripting driven by complex electrical rules.
* Dynamic, algorithmically generated layout modifications.
* Deep EDB object-level inspection or repair operations.

For these scenarios it is recommended to use the **PyEDB Python APIs directly**.
The two approaches are fully complementary: a typical production workflow might
load and apply a configuration file to handle the bulk of the setup, then call
PyEDB API methods for the handful of steps that require finer control—all
within the same Python session.

Use the sections below to choose the view that best matches how you work:

* :doc:`file_architecture` explains the serialized JSON and TOML structure,
  supported sections, and field intent.
* :doc:`configuration_api_guide` is the API guide: core objects, section
  mapping, session-aware ``get()`` helpers, persist methods, and a complete
  example incorporating all recent additions.
* :doc:`configuration_api_examples` provides hands-on worked examples covering
  ports, setups, padstacks, stackup, modeler geometry, and more.

.. grid:: 3

    .. grid-item-card:: Configuration file architecture :fa:`file-code`
        :link: file_architecture
        :link-type: doc

        Understand the JSON and TOML schema, supported sections, and how
        configuration data is applied to a design.

    .. grid-item-card:: Configuration API guide :fa:`code`
        :link: configuration_api_guide
        :link-type: doc

        Core objects, session-aware ``get()`` helpers, persist methods
        (``save_to_json`` / ``to_json``), and a complete end-to-end example.

    .. grid-item-card:: Practical examples :fa:`flask`
        :link: configuration_api_examples
        :link-type: doc

        Thirteen worked examples from coax ports and wave ports to stackup
        materials and modeler geometry, with inline commentary.


.. toctree::
    :hidden:
    :maxdepth: 2

    file_architecture
    configuration_api_guide
    configuration_api_examples
    ../autoapi/pyedb/configuration/index

