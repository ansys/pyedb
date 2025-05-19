# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# lazy imports
def Edb(
    edbpath=None,
    cellname=None,
    isreadonly=False,
    edbversion=None,
    isaedtowned=False,
    oproject=None,
    student_version=False,
    use_ppe=False,
    technology_file=None,
    grpc=False,
    control_file=None,
):
    """Provides the EDB application interface.

    This module inherits all objects that belong to EDB.

    Parameters
    ----------
    edbpath : str, optional
        Full path to the ``aedb`` folder. The variable can also contain
        the path to a layout to import. Allowed formats are BRD,
        XML (IPC2581), GDS, and DXF. The default is ``None``.
        For GDS import, the Ansys control file (also XML) should have the same
        name as the GDS file. Only the file extension differs.
    cellname : str, optional
        Name of the cell to select. The default is ``None``.
    isreadonly : bool, optional
        Whether to open EBD in read-only mode when it is
        owned by HFSS 3D Layout. The default is ``False``.
    edbversion : str, optional
        Version of EDB to use. The default is ``"2021.2"``.
    isaedtowned : bool, optional
        Whether to launch EDB from HFSS 3D Layout. The
        default is ``False``.
    oproject : optional
        Reference to the AEDT project object.
    student_version : bool, optional
        Whether to open the AEDT student version. The default is ``False.``
    technology_file : str, optional
        Full path to technology file to be converted to xml before importing or xml. Supported by GDS format only.
    grpc : bool, optional
        Whether to enable gRPC. Default value is ``False``.

    Returns
    -------
    :class:`Edb <pyedb.dotnet.edb.Edb>` or :class:`Edb <pyedb.grpc.edb.Edb>`

    Note
    ----
    PyEDB gRPC will be released starting ANSYS release 2025R2. For legacy purpose, the gRPC will not be activated by
    default. However, PyEDB gRPC will be the lon term supported version. The legacy PyEDB .NET will be deprecated and
    at some point all new features will only be implemented in PyEDB gRPC. We highly encourage users moving to gRPC
    starting release 2025R2, we tried keeping gRPC version backward compatible with legace .NET as much as possible and
    only minor adjustments are required to be compatible.

    Examples
    --------
    Create an ``Edb`` object and a new EDB cell.

    >>> from pyedb import Edb
    >>> app = Edb()

    Add a new variable named "s1" to the ``Edb`` instance.

    >>> app['s1'] = "0.25 mm"
    >>> app['s1'].tofloat
    >>> 0.00025
    >>> app['s1'].tostring
    >>> "0.25mm"

    or add a new parameter with description:

    >>> app['s2'] = ["20um", "Spacing between traces"]
    >>> app['s2'].value
    >>> 1.9999999999999998e-05
    >>> app['s2'].description
    >>> 'Spacing between traces'


    Create an ``Edb`` object and open the specified project.

    >>> app = Edb("myfile.aedb")

    Create an ``Edb`` object from GDS and control files.
    The XML control file resides in the same directory as the GDS file: (myfile.xml).

    >>> app = Edb("/path/to/file/myfile.gds")

    """

    # Use EDB legacy (default choice)
    if grpc:
        from pyedb.grpc.edb import Edb as app
    else:
        from pyedb.dotnet.edb import Edb as app
    return app(
        edbpath=edbpath,
        cellname=cellname,
        isreadonly=isreadonly,
        edbversion=edbversion,
        isaedtowned=isaedtowned,
        oproject=oproject,
        student_version=student_version,
        use_ppe=use_ppe,
        technology_file=technology_file,
        control_file=control_file,
    )


def Siwave(
    specified_version=None,
):
    """Siwave Class."""
    from pyedb.siwave import Siwave as app

    return app(
        specified_version=specified_version,
    )


app_map = {"EDB": Edb}
