import re
import sys


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
):
    """Provides the EDB application interface.

    This module inherits all objects that belong to EDB.

    Parameters
    ----------
    edbpath : str, int, float optional
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

    Returns
    -------
    :class:`pyaedt.edb.Edb`

    Examples
    --------
    Create an ``Edb`` object and a new EDB cell.

    >>> from pyaedt import Edb
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
    from pyaedt.edb import Edb as app

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
    )


app_map = {"EDB": Edb,}


def get_pyaedt_app(project_name=None, design_name=None):
    """Returns the Pyaedt Object of specific project_name and design_name.

    Parameters
    ----------
    project_name
    design_name

    Returns
    -------
    :def :`pyaedt.Hfss`
        Any of the Pyaedt App initialized.
    """
    main = sys.modules["__main__"]
    if "oDesktop" in dir(main):
        if project_name and project_name not in main.oDesktop.GetProjectList():
            raise AttributeError("Project  {} doesn't exist in current Desktop.".format(project_name))
        if not project_name:
            oProject = main.oDesktop.GetActiveProject()
        else:
            oProject = main.oDesktop.SetActiveProject(project_name)
        if not oProject:
            raise AttributeError("No Project Present.")
        design_names = []
        deslist = list(oProject.GetTopDesignList())
        for el in deslist:
            m = re.search(r"[^;]+$", el)
            design_names.append(m.group(0))
        if design_name and design_name not in design_names:
            raise AttributeError("Design  {} doesn't exists in current Project.".format(design_name))
        if not design_name:
            oDesign = oProject.GetActiveDesign()
        else:
            oDesign = oProject.SetActiveDesign(design_name)
        if not oDesign:
            raise AttributeError("No Design Present.")
        design_type = oDesign.GetDesignType()
        if design_type in list(app_map.keys()):
            version = main.oDesktop.GetVersion().split(".")
            v = ".".join([version[0], version[1]])
            return app_map[design_type](project_name, design_name, specified_version=v)
    return None
