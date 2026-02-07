.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the project.

.. vale off

.. towncrier release notes start

`0.68.3 <https://github.com/ansys/pyedb/releases/tag/v0.68.3>`_ - February 06, 2026
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - HFSS REGION
          - `#1813 <https://github.com/ansys/pyedb/pull/1813>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Issue#1800 #1810
          - `#1811 <https://github.com/ansys/pyedb/pull/1811>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.68.2
          - `#1808 <https://github.com/ansys/pyedb/pull/1808>`_


`0.68.2 <https://github.com/ansys/pyedb/releases/tag/v0.68.2>`_ - February 04, 2026
===================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump ansys/actions from 10.2.3 to 10.2.4
          - `#1786 <https://github.com/ansys/pyedb/pull/1786>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Mapping nap file with Edb grpc
          - `#1790 <https://github.com/ansys/pyedb/pull/1790>`_

        * - Edb cfg freq sweep typos
          - `#1797 <https://github.com/ansys/pyedb/pull/1797>`_

        * - Class MultiFrequencyAdaptSolution grpc
          - `#1798 <https://github.com/ansys/pyedb/pull/1798>`_

        * - CFG use Q3D for DC
          - `#1799 <https://github.com/ansys/pyedb/pull/1799>`_

        * - CFG setup minor
          - `#1801 <https://github.com/ansys/pyedb/pull/1801>`_

        * - Raptor fix
          - `#1804 <https://github.com/ansys/pyedb/pull/1804>`_

        * - Issue #1803 fix
          - `#1805 <https://github.com/ansys/pyedb/pull/1805>`_

        * - #1800 fix
          - `#1806 <https://github.com/ansys/pyedb/pull/1806>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.68.0
          - `#1781 <https://github.com/ansys/pyedb/pull/1781>`_

        * - Bump release 0.69.0
          - `#1782 <https://github.com/ansys/pyedb/pull/1782>`_

        * - Update missing or outdated files
          - `#1795 <https://github.com/ansys/pyedb/pull/1795>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Removing cfg file 1.0 test and deprecating entire class.
          - `#1783 <https://github.com/ansys/pyedb/pull/1783>`_

        * - Test_edb_materials.py
          - `#1802 <https://github.com/ansys/pyedb/pull/1802>`_


`0.68.0 <https://github.com/ansys/pyedb/releases/tag/v0.68.0>`_ - January 27, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - XML Parser - stackup and nets
          - `#1774 <https://github.com/ansys/pyedb/pull/1774>`_

        * - Grpc simulation setup refactoring
          - `#1776 <https://github.com/ansys/pyedb/pull/1776>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 6.0.1 to 6.0.2
          - `#1775 <https://github.com/ansys/pyedb/pull/1775>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update gRPC message.
          - `#1773 <https://github.com/ansys/pyedb/pull/1773>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.67.3
          - `#1770 <https://github.com/ansys/pyedb/pull/1770>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Terminal post processing
          - `#1756 <https://github.com/ansys/pyedb/pull/1756>`_

        * - Cfg setup enhancement
          - `#1771 <https://github.com/ansys/pyedb/pull/1771>`_

        * - Renaming grpc import
          - `#1780 <https://github.com/ansys/pyedb/pull/1780>`_


`0.67.3 <https://github.com/ansys/pyedb/releases/tag/v0.67.3>`_ - January 21, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Grpc wave port tests resurrected
          - `#1761 <https://github.com/ansys/pyedb/pull/1761>`_

        * - Grpc source bug fix + consolidation
          - `#1763 <https://github.com/ansys/pyedb/pull/1763>`_

        * - Grpc layers consolidation
          - `#1764 <https://github.com/ansys/pyedb/pull/1764>`_

        * - Create port from padstack instance name bug fix
          - `#1765 <https://github.com/ansys/pyedb/pull/1765>`_

        * - Sweep property
          - `#1769 <https://github.com/ansys/pyedb/pull/1769>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.67.1
          - `#1759 <https://github.com/ansys/pyedb/pull/1759>`_

        * - Bump_release_0.68.dev0
          - `#1760 <https://github.com/ansys/pyedb/pull/1760>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Edb cfg setup dotnet only
          - `#1766 <https://github.com/ansys/pyedb/pull/1766>`_


`0.67.1 <https://github.com/ansys/pyedb/releases/tag/v0.67.1>`_ - January 16, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Wirebond def management added
          - `#1746 <https://github.com/ansys/pyedb/pull/1746>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Extend troubleshooting with uv venv on Windows
          - `#1754 <https://github.com/ansys/pyedb/pull/1754>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Test modifying edb test file fixed
          - `#1750 <https://github.com/ansys/pyedb/pull/1750>`_

        * - Terminal hfss type
          - `#1757 <https://github.com/ansys/pyedb/pull/1757>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.67.0
          - `#1747 <https://github.com/ansys/pyedb/pull/1747>`_

        * - Codecov component model
          - `#1751 <https://github.com/ansys/pyedb/pull/1751>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Source excitation
          - `#1744 <https://github.com/ansys/pyedb/pull/1744>`_

        * - Ide error fix
          - `#1748 <https://github.com/ansys/pyedb/pull/1748>`_

        * - Add dependency xmltodict
          - `#1752 <https://github.com/ansys/pyedb/pull/1752>`_

        * - Edb cfg cutout arguments
          - `#1753 <https://github.com/ansys/pyedb/pull/1753>`_

        * - Edb_object replaced by core
          - `#1755 <https://github.com/ansys/pyedb/pull/1755>`_


`0.67.0 <https://github.com/ansys/pyedb/releases/tag/v0.67.0>`_ - January 12, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Generate auto hfss regions
          - `#1714 <https://github.com/ansys/pyedb/pull/1714>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 6.0.0 to 6.0.1
          - `#1696 <https://github.com/ansys/pyedb/pull/1696>`_

        * - Bump ansys/actions from 10.1.5 to 10.2.2
          - `#1697 <https://github.com/ansys/pyedb/pull/1697>`_

        * - Update ansys-edb-core requirement from <0.2.3,>=0.2.0 to >=0.2.0,<0.2.4
          - `#1700 <https://github.com/ansys/pyedb/pull/1700>`_

        * - Bump codecov/codecov-action from 5.5.1 to 5.5.2
          - `#1705 <https://github.com/ansys/pyedb/pull/1705>`_

        * - Bump actions/download-artifact from 6.0.0 to 7.0.0
          - `#1708 <https://github.com/ansys/pyedb/pull/1708>`_

        * - Bump ansys/actions from 10.2.2 to 10.2.3
          - `#1720 <https://github.com/ansys/pyedb/pull/1720>`_

        * - Update pytest requirement from <8.5,>=7.4.0 to >=7.4.0,<9.1
          - `#1733 <https://github.com/ansys/pyedb/pull/1733>`_

        * - Update sphinx requirement from <8.3,>=7.1.0 to >=7.1.0,<9.1
          - `#1734 <https://github.com/ansys/pyedb/pull/1734>`_

        * - Bump numpydoc from 1.5.0 to 1.10.0
          - `#1735 <https://github.com/ansys/pyedb/pull/1735>`_

        * - Update sphinx-gallery requirement from <0.20,>=0.14.0 to >=0.14.0,<0.21
          - `#1736 <https://github.com/ansys/pyedb/pull/1736>`_

        * - Bump ansys-api-edb to 0.2.5
          - `#1743 <https://github.com/ansys/pyedb/pull/1743>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Change PyEDB documentation style
          - `#1721 <https://github.com/ansys/pyedb/pull/1721>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Reuse terminal
          - `#1738 <https://github.com/ansys/pyedb/pull/1738>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.66.0
          - `#1712 <https://github.com/ansys/pyedb/pull/1712>`_

        * - Bump release 0.67.dev0
          - `#1715 <https://github.com/ansys/pyedb/pull/1715>`_

        * - Fix \`\`zizmor\`\` warnings in relation with \`\`ansys/actions/check-actions-security\`\` action
          - `#1723 <https://github.com/ansys/pyedb/pull/1723>`_

        * - Update CHANGELOG for v0.66.1
          - `#1732 <https://github.com/ansys/pyedb/pull/1732>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Remove cell from layout.py
          - `#1713 <https://github.com/ansys/pyedb/pull/1713>`_

        * - Dependencies updated
          - `#1716 <https://github.com/ansys/pyedb/pull/1716>`_

        * - Edb core refactoring
          - `#1717 <https://github.com/ansys/pyedb/pull/1717>`_

        * - Edb grpc main class warning fix
          - `#1729 <https://github.com/ansys/pyedb/pull/1729>`_

        * - Components refactoring
          - `#1740 <https://github.com/ansys/pyedb/pull/1740>`_

        * - Hfss refactoring
          - `#1741 <https://github.com/ansys/pyedb/pull/1741>`_


`0.66.1 <https://github.com/ansys/pyedb/releases/tag/v0.66.1>`_ - January 06, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update test path and extend with other tests
          - `#1731 <https://github.com/ansys/pyedb/pull/1731>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix type hints and code warnings in padstacks.py
          - `#1726 <https://github.com/ansys/pyedb/pull/1726>`_


`0.66.1 <https://github.com/ansys/pyedb/releases/tag/v0.66.1>`_ - January 01, 2026
==================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Generate auto hfss regions
          - `#1714 <https://github.com/ansys/pyedb/pull/1714>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 6.0.0 to 6.0.1
          - `#1696 <https://github.com/ansys/pyedb/pull/1696>`_

        * - Bump ansys/actions from 10.1.5 to 10.2.2
          - `#1697 <https://github.com/ansys/pyedb/pull/1697>`_

        * - Update ansys-edb-core requirement from <0.2.3,>=0.2.0 to >=0.2.0,<0.2.4
          - `#1700 <https://github.com/ansys/pyedb/pull/1700>`_

        * - Bump codecov/codecov-action from 5.5.1 to 5.5.2
          - `#1705 <https://github.com/ansys/pyedb/pull/1705>`_

        * - Bump actions/download-artifact from 6.0.0 to 7.0.0
          - `#1708 <https://github.com/ansys/pyedb/pull/1708>`_

        * - Bump ansys/actions from 10.2.2 to 10.2.3
          - `#1720 <https://github.com/ansys/pyedb/pull/1720>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Change PyEDB documentation style
          - `#1721 <https://github.com/ansys/pyedb/pull/1721>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.66.0
          - `#1712 <https://github.com/ansys/pyedb/pull/1712>`_

        * - Bump release 0.67.dev0
          - `#1715 <https://github.com/ansys/pyedb/pull/1715>`_

        * - Fix \`\`zizmor\`\` warnings in relation with \`\`ansys/actions/check-actions-security\`\` action
          - `#1723 <https://github.com/ansys/pyedb/pull/1723>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Remove cell from layout.py
          - `#1713 <https://github.com/ansys/pyedb/pull/1713>`_

        * - Dependencies updated
          - `#1716 <https://github.com/ansys/pyedb/pull/1716>`_

        * - Edb core refactoring
          - `#1717 <https://github.com/ansys/pyedb/pull/1717>`_


`0.66.0 <https://github.com/ansys/pyedb/releases/tag/v0.66.0>`_ - December 19, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/upload-artifact from 5.0.0 to 6.0.0
          - `#1707 <https://github.com/ansys/pyedb/pull/1707>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fix typo in AUTHORS
          - `#1695 <https://github.com/ansys/pyedb/pull/1695>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fixing static folder creation
          - `#1711 <https://github.com/ansys/pyedb/pull/1711>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump release 0.66.dev0
          - `#1682 <https://github.com/ansys/pyedb/pull/1682>`_

        * - Update CHANGELOG for v0.65.1
          - `#1684 <https://github.com/ansys/pyedb/pull/1684>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Component_def refactoring
          - `#1686 <https://github.com/ansys/pyedb/pull/1686>`_

        * - Material refactoring
          - `#1688 <https://github.com/ansys/pyedb/pull/1688>`_

        * - Nport component def refactoring
          - `#1689 <https://github.com/ansys/pyedb/pull/1689>`_

        * - Package def refactoring
          - `#1690 <https://github.com/ansys/pyedb/pull/1690>`_

        * - Edb cfg padstacks
          - `#1692 <https://github.com/ansys/pyedb/pull/1692>`_

        * - Random failure test
          - `#1694 <https://github.com/ansys/pyedb/pull/1694>`_

        * - Move control_file.py to generic folder
          - `#1701 <https://github.com/ansys/pyedb/pull/1701>`_

        * - Edb configure terminal
          - `#1702 <https://github.com/ansys/pyedb/pull/1702>`_

        * - Configure cfg_padstacks.py
          - `#1703 <https://github.com/ansys/pyedb/pull/1703>`_

        * - EDB CFG cutout
          - `#1706 <https://github.com/ansys/pyedb/pull/1706>`_

        * - Removing edb-core inheritance
          - `#1710 <https://github.com/ansys/pyedb/pull/1710>`_


`0.65.1 <https://github.com/ansys/pyedb/releases/tag/v0.65.1>`_ - November 27, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Insert 3d layout gRPC
          - `#1667 <https://github.com/ansys/pyedb/pull/1667>`_

        * - Place layout component enhancement
          - `#1680 <https://github.com/ansys/pyedb/pull/1680>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Working fine on local reverting test on grpc and cicd to check
          - `#1664 <https://github.com/ansys/pyedb/pull/1664>`_

        * - GRPC boundaries
          - `#1670 <https://github.com/ansys/pyedb/pull/1670>`_

        * - Remove try-except from property position
          - `#1679 <https://github.com/ansys/pyedb/pull/1679>`_

        * - Remove LD_LIBRARY_PATH need
          - `#1683 <https://github.com/ansys/pyedb/pull/1683>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.65.0
          - `#1681 <https://github.com/ansys/pyedb/pull/1681>`_


`0.65.0 <https://github.com/ansys/pyedb/releases/tag/v0.65.0>`_ - November 27, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 5.0.1 to 6.0.0
          - `#1665 <https://github.com/ansys/pyedb/pull/1665>`_

        * - Bump actions/setup-python from 6.0.0 to 6.1.0
          - `#1674 <https://github.com/ansys/pyedb/pull/1674>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Fixing hatched ground plane bug with grpc
          - `#1675 <https://github.com/ansys/pyedb/pull/1675>`_

        * - Issue 1621 fix
          - `#1677 <https://github.com/ansys/pyedb/pull/1677>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.64.1
          - `#1669 <https://github.com/ansys/pyedb/pull/1669>`_


`0.64.1 <https://github.com/ansys/pyedb/releases/tag/v0.64.1>`_ - November 24, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Add grpc padstack instance bounding box property
          - `#1642 <https://github.com/ansys/pyedb/pull/1642>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump actions/checkout from 5.0.0 to 5.0.1
          - `#1655 <https://github.com/ansys/pyedb/pull/1655>`_

        * - Update jupyterlab requirement from <4.5,>=4.0.0 to >=4.0.0,<4.6
          - `#1656 <https://github.com/ansys/pyedb/pull/1656>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Remove JobManager from Edb class
          - `#1657 <https://github.com/ansys/pyedb/pull/1657>`_

        * - Fixing hfss extent
          - `#1660 <https://github.com/ansys/pyedb/pull/1660>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update CHANGELOG for v0.64.0
          - `#1652 <https://github.com/ansys/pyedb/pull/1652>`_

        * - Bump dev version into v0.65.dev0
          - `#1653 <https://github.com/ansys/pyedb/pull/1653>`_

        * - Delete accidentally added files
          - `#1661 <https://github.com/ansys/pyedb/pull/1661>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Edb cfg boundaries
          - `#1659 <https://github.com/ansys/pyedb/pull/1659>`_

        * - Add docstring to edb cfg boundaries
          - `#1663 <https://github.com/ansys/pyedb/pull/1663>`_


`0.64.0 <https://github.com/ansys/pyedb/releases/tag/v0.64.0>`_ - November 13, 2025
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

        * - Leverage new \`\`vtk-osmesa\`\` logic in CI
          - `#1651 <https://github.com/ansys/pyedb/pull/1651>`_


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