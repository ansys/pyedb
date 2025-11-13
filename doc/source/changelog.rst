.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.64.0 <https://github.com/ansys/pyedb/releases/tag/v0.64.0>`_ - November 13, 2025
===================================================================================
No significant changes.
`0.64.0 <https://github.com/ansys/pyedb/releases/tag/v0.64.0>`_ - November 12, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Adding CLI for batch submission
          - `#1635 <https://github.com/ansys/pyedb/pull/1635>`_

        * - Job manager concurrent job bug
          - `#1640 <https://github.com/ansys/pyedb/pull/1640>`_

        * - Siwave log parser
          - `#1646 <https://github.com/ansys/pyedb/pull/1646>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.1.4 to 10.1.5
          - `#1623 <https://github.com/ansys/pyedb/pull/1623>`_

        * - Update pypandoc requirement from <1.16,>=1.10.0 to >=1.10.0,<1.17
          - `#1643 <https://github.com/ansys/pyedb/pull/1643>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Introduce \`\`sphinx-autoapi\`\` for API documentation
          - `#1632 <https://github.com/ansys/pyedb/pull/1632>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bux fixed
          - `#1626 <https://github.com/ansys/pyedb/pull/1626>`_

        * - Create port on component (grpc) bug fixed
          - `#1628 <https://github.com/ansys/pyedb/pull/1628>`_

        * - Cfg_ports_sources.py
          - `#1644 <https://github.com/ansys/pyedb/pull/1644>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.63.0
          - `#1624 <https://github.com/ansys/pyedb/pull/1624>`_

        * - Bump release 0.64.dev0
          - `#1634 <https://github.com/ansys/pyedb/pull/1634>`_


`0.63.0 <https://github.com/ansys/pyedb/releases/tag/v0.63.0>`_ - November 03, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Hatched ground plane with angle support
          - `#1620 <https://github.com/ansys/pyedb/pull/1620>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.62.0
          - `#1614 <https://github.com/ansys/pyedb/pull/1614>`_

        * - Run PyAEDT test with PYAEDT_LOCAL_SETTINGS_PATH env var
          - `#1622 <https://github.com/ansys/pyedb/pull/1622>`_


`0.62.0 <https://github.com/ansys/pyedb/releases/tag/v0.62.0>`_ - October 28, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add functionality for geometry swapping from DXF file
          - `#1529 <https://github.com/ansys/pyedb/pull/1529>`_

        * - Adding DRC inside pyedb
          - `#1600 <https://github.com/ansys/pyedb/pull/1600>`_

        * - Layout file warnings
          - `#1602 <https://github.com/ansys/pyedb/pull/1602>`_

        * - Design mode
          - `#1607 <https://github.com/ansys/pyedb/pull/1607>`_

        * - Job manager lsf support
          - `#1609 <https://github.com/ansys/pyedb/pull/1609>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/labeler from 5.0.0 to 6.0.1
          - `#1578 <https://github.com/ansys/pyedb/pull/1578>`_

        * - Bump actions/download-artifact from 5.0.0 to 6.0.0
          - `#1610 <https://github.com/ansys/pyedb/pull/1610>`_

        * - Bump actions/upload-artifact from 4.6.2 to 5.0.0
          - `#1611 <https://github.com/ansys/pyedb/pull/1611>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add the changelog feature
          - `#1593 <https://github.com/ansys/pyedb/pull/1593>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Job manager default values
          - `#1597 <https://github.com/ansys/pyedb/pull/1597>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Adding artifact attestations and fix warnings related to coverage upload
          - `#1601 <https://github.com/ansys/pyedb/pull/1601>`_


.. vale on


Changelog
=========

All notable changes to PyEDB are documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------
### Added
-

### Changed
-

### Deprecated
-

### Fixed
-

### Removed
-

[0.9.0] - 2024-XX-YY
--------------------
### Added
- Initial release of the gRPC-based PyEDB client.
- Comprehensive documentation including user guides, migration guide, and examples.
- Core functionality for EDB creation, modification, and simulation setup.

### Removed
- Legacy `pyedb.dotnet` module (moved to archived branch).