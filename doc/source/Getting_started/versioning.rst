.. _versions_and_interfaces:

=======================
Versions and interfaces
=======================

The PyEDB project attempts to maintain compatibility with legacy
versions of EDB while allowing for support of faster and better
interfaces with the latest versions of EDB.

There are two interfaces PyEDB can use to connect to EDB.
You can see a table with the AEDT version and the supported interfaces
in `Table of supported versions <table_versions_>`_


gRPC interface
==============

This is the default and preferred interface to connect to AEDT.
Ansys 2024 R2 and later support the latest gRPC interface, allowing
for remote management of MAPDL with rapid streaming of mesh, results,
and files from the MAPDL service.


Legacy interfaces
=================

Microsoft development framework interface
-----------------------------------------

PyEDB supports the legacy .NET interface, enabled with the settings option.

This interface works both on Windows and Linux.


.. code:: python


    from pyaedt import settings

    settings.use_grpc_api = False



Compatibility between AEDT and interfaces
=========================================

The following table shows the supported versions of Ansys EDT and the recommended interface for each one of them in PyAEDT.


**Table of supported versions**

.. _table_versions:

+---------------------------+------------------------+-----------------------------------------------+
| Ansys Version             | Recommended interface  | Support                                       |
|                           |                        +-----------------------+-----------------------+
|                           |                        | gRPC                  | .NET                   |
+===========================+========================+=======================+=======================+
| AnsysEM 2024 R1           | gRPC                   |        YES            |        YES*            |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2023 R2           | .NET                   |        NO             |        YES           |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2023 R1           | .NET                   |        NO             |        YES           |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2022 R2           | .NET                   |        NO             |        YES            |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2022 R1           | .NET                   |        NO             |        YES            |
+---------------------------+------------------------+-----------------------+-----------------------+
| AnsysEM 2021 R2           | .NET                   |        NO            |         YES            |
+---------------------------+------------------------+-----------------------+-----------------------+

Where:

* YES means that the interface is supported and recommended.
* YES* means that the interface is supported, but not recommended. Their support might be dropped in the future.
* NO means that the interface is not supported.
* NO* means that the interface is still supported but it is deprecated.
