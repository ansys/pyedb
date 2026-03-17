src.pyedb.dotnet.database.Variables
===================================

.. py:module:: src.pyedb.dotnet.database.Variables

.. autoapi-nested-parse::

   This module contains these classes: `CSVDataset`, `DataSet`, `Expression`, `Variable`, and `VariableManager`.

   This module is used to create and edit design and project variables in the 3D tools.

   Examples
   --------
   >>> from ansys.aedt.core import Hfss
   >>> hfss = Hfss()
   >>> hfss["$d"] = "5mm"
   >>> hfss["d"] = "5mm"
   >>> hfss["postd"] = "1W"



Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.Variables.CSVDataset
   src.pyedb.dotnet.database.Variables.VariableManager
   src.pyedb.dotnet.database.Variables.Variable
   src.pyedb.dotnet.database.Variables.DataSet


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.database.Variables.generate_validation_errors


Module Contents
---------------

.. py:class:: CSVDataset(csv_file=None, separator=None, units_dict=None, append_dict=None, valid_solutions=True, invalid_solutions=False)

   Reads in a CSV file and extracts data, which can be augmented with constant values.

   Parameters
   ----------
   csv_file : str, optional
       Input file consisting of delimited data with the first line as the header.
       The CSV value includes the header and data, which supports AEDT units information
       such as ``"1.23Wb"``. You can also augment the data with constant values.
   separator : str, optional
       Value to use for the delimiter. The default is``None`` in which case a comma is
       assumed.
   units_dict : dict, optional
       Dictionary consisting of ``{Variable Name: unit}`` to rescale the data
       if it is not in the desired unit system.
   append_dict : dict, optional
       Dictionary consisting of ``{New Variable Name: value}`` to add variables
       with constant values to all data points. This dictionary is used to add
       multiple sweeps to one result file.
   valid_solutions : bool, optional
       The default is ``True``.
   invalid_solutions : bool, optional
       The default is ``False``.



   .. py:property:: number_of_rows

      Number of rows.



   .. py:property:: number_of_columns

      Number of columns.



   .. py:property:: header

      Header.



   .. py:property:: data

      Data.



   .. py:property:: path

      Path.



   .. py:method:: next()

      Yield the next row.



.. py:function:: generate_validation_errors(property_names, expected_settings, actual_settings)

   From the given property names, expected settings and actual settings, return a list of validation errors.
   If no errors are found, an empty list is returned. The validation of values such as "10mm"
   ensures that they are close to within a relative tolerance.
   For example an expected setting of "10mm", and actual of "10.000000001mm" will not yield a validation error.
   For values with no numerical value, an equivalence check is made.

   Parameters
   ----------
   property_names : List[str]
       List of property names.
   expected_settings : List[str]
       List of the expected settings.
   actual_settings : List[str]
       List of actual settings.

   Returns
   -------
   List[str]
       A list of validation errors for the given settings.


.. py:class:: VariableManager(app)

   Bases: :py:obj:`object`


   Manages design properties and project variables.

   Design properties are the local variables in a design. Project
   variables are defined at the project level and start with ``$``.

   This class provides access to all variables or a subset of the
   variables. Manipulation of the numerical or string definitions of
   variable values is provided in the
   :class:`pyedb.dotnet.database.Variables.Variable` class.

   Parameters
   ----------
   variables : dict
       Dictionary of all design properties and project variables in
       the active design.
   design_variables : dict
       Dictionary of all design properties in the active design.
   project_variables : dict
       Dictionary of all project variables available to the active
       design (key by variable name).
   dependent_variables : dict
       Dictionary of all dependent variables available to the active
       design (key by variable name).
   independent_variables : dict
      Dictionary of all independent variables (constant numeric
      values) available to the active design (key by variable name).
   independent_design_variables : dict

   independent_project_variables : dict

   variable_names : str or list
       One or more variable names.
   project_variable_names : str or list
       One or more project variable names.
   design_variable_names : str or list
       One or more design variable names.
   dependent_variable_names : str or list
       All dependent variable names within the project.
   independent_variable_names : list of str
       All independent variable names within the project. These can
       be sweep variables for optimetrics.
   independent_project_variable_names : str or list
       All independent project variable names within the
       project. These can be sweep variables for optimetrics.
   independent_design_variable_names : str or list
       All independent design properties (local variables) within the
       project. These can be sweep variables for optimetrics.

   See Also
   --------
   pyedb.dotnet.database.Variables.Variable

   Examples
   --------

   >>> from ansys.aedt.core.maxwell import Maxwell3d
   >>> from ansys.aedt.core.desktop import Desktop
   >>> d = Desktop()
   >>> aedtapp = Maxwell3d()

   Define some test variables.

   >>> aedtapp["Var1"] = 3
   >>> aedtapp["Var2"] = "12deg"
   >>> aedtapp["Var3"] = "Var1 * Var2"
   >>> aedtapp["$PrjVar1"] = "pi"

   Get the variable manager for the active design.

   >>> v = aedtapp.variable_manager

   Get a dictionary of all project and design variables.

   >>> v.variables
   {'Var1': <pyedb.dotnet.database.Variables.Variable at 0x2661f34c448>,
    'Var2': <pyedb.dotnet.database.Variables.Variable at 0x2661f34c308>,
    'Var3': <pyedb.dotnet.database.Variables.Expression at 0x2661f34cb48>,
    '$PrjVar1': <pyedb.dotnet.database.Variables.Expression at 0x2661f34cc48>}

   Get a dictionary of only the design variables.

   >>> v.design_variables
   {'Var1': <pyedb.dotnet.database.Variables.Variable at 0x2661f339508>,
    'Var2': <pyedb.dotnet.database.Variables.Variable at 0x2661f3415c8>,
    'Var3': <pyedb.dotnet.database.Variables.Expression at 0x2661f341808>}

   Get a dictionary of only the independent design variables.

   >>> v.independent_design_variables
   {'Var1': <pyedb.dotnet.database.Variables.Variable at 0x2661f335d08>,
    'Var2': <pyedb.dotnet.database.Variables.Variable at 0x2661f3557c8>}



   .. py:property:: variables

      Variables.

      Returns
      -------
      dict
          Dictionary of the `Variable` objects for each project variable and each
          design property in the active design.

      References
      ----------

      >>> oProject.GetVariables
      >>> oDesign.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:method:: decompose(variable_value)

      Decompose a variable string to a floating with its unit.

      Parameters
      ----------
      variable_value : str

      Returns
      -------
      tuple
          The float value of the variable and the units exposed as a string.

      Examples
      --------
      >>> hfss = Hfss()
      >>> print(hfss.variable_manager.decompose("5mm"))
      >>> (5.0, "mm")
      >>> hfss["v1"] = "3N"
      >>> print(hfss.variable_manager.decompose("v1"))
      >>> (3.0, "N")
      >>> hfss["v2"] = "2*v1"
      >>> print(hfss.variable_manager.decompose("v2"))
      >>> (6.0, "N")



   .. py:property:: design_variables

      Design variables.

      Returns
      -------
      dict
          Dictionary of the design properties (local properties) in the design.

      References
      ----------

      >>> oDesign.GetVariables
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: project_variables

      Project variables.

      Returns
      -------
      dict
          Dictionary of the project properties.

      References
      ----------

      >>> oProject.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames



   .. py:property:: post_processing_variables

      Post Processing variables.

      Returns
      -------
      dict
          Dictionary of the post processing variables (constant numeric
          values) available to the design.

      References
      ----------

      >>> oProject.GetVariables
      >>> oDesign.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: independent_variables

      Independent variables.

      Returns
      -------
      dict
          Dictionary of the independent variables (constant numeric
          values) available to the design.

      References
      ----------

      >>> oProject.GetVariables
      >>> oDesign.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: independent_project_variables

      Independent project variables.

      Returns
      -------
      dict
          Dictionary of the independent project variables available to the design.

      References
      ----------

      >>> oProject.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames



   .. py:property:: independent_design_variables

      Independent design variables.

      Returns
      -------
      dict
          Dictionary of the independent design properties (local
          variables) available to the design.

      References
      ----------

      >>> oDesign.GetVariables
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: dependent_variables

      Dependent variables.

      Returns
      -------
      dict
          Dictionary of the dependent design properties (local
          variables) and project variables available to the design.

      References
      ----------

      >>> oProject.GetVariables
      >>> oDesign.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: dependent_project_variables

      Dependent project variables.

      Returns
      -------
      dict
          Dictionary of the dependent project variables available to the design.

      References
      ----------

      >>> oProject.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames



   .. py:property:: dependent_design_variables

      Dependent design variables.

      Returns
      -------
      dict
          Dictionary of the dependent design properties (local
          variables) available to the design.

      References
      ----------

      >>> oDesign.GetVariables
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: variable_names

      List of variables.



   .. py:property:: project_variable_names

      List of project variables.

      References
      ----------

      >>> oProject.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames



   .. py:property:: design_variable_names

      List of design variables.

      References
      ----------

      >>> oDesign.GetVariables
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: independent_project_variable_names

      List of independent project variables.

      References
      ----------

      >>> oProject.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames



   .. py:property:: independent_design_variable_names

      List of independent design variables.

      References
      ----------

      >>> oDesign.GetVariables
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: independent_variable_names

      List of independent variables.

      References
      ----------

      >>> oProject.GetVariables
      >>> oDesign.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: dependent_project_variable_names

      List of dependent project variables.

      References
      ----------

      >>> oProject.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames



   .. py:property:: dependent_design_variable_names

      List of dependent design variables.

      References
      ----------

      >>> oDesign.GetVariables
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:property:: dependent_variable_names

      List of dependent variables.

      References
      ----------

      >>> oProject.GetVariables
      >>> oDesign.GetVariables
      >>> oProject.GetChildObject("Variables").GetChildNames
      >>> oDesign.GetChildObject("Variables").GetChildNames



   .. py:method:: get_expression(variable_name)

      Retrieve the variable value of a project or design variable as a string.

      References
      ----------

      >>> oProject.GetVariableValue
      >>> oDesign.GetVariableValue



   .. py:method:: aedt_object(variable)

      Retrieve an AEDT object.

      Parameters
      ----------
      variable : str
      Name of the variable.




   .. py:method:: set_variable(variable_name, expression=None, readonly=False, hidden=False, description=None, overwrite=True, postprocessing=False, circuit_parameter=True)

      Set the value of a design property or project variable.

      Parameters
      ----------
      variable_name : str
          Name of the design property or project variable
          (``$var``). If this variable does not exist, a new one is
          created and a value is set.
      expression : str
          Valid string expression within the AEDT design and project
          structure.  For example, ``"3*cos(34deg)"``.
      readonly : bool, optional
          Whether to set the design property or project variable to
          read-only. The default is ``False``.
      hidden :  bool, optional
          Whether to hide the design property or project variable. The
          default is ``False``.
      description : str, optional
          Text to display for the design property or project variable in the
          ``Properties`` window. The default is ``None``.
      overwrite : bool, optional
          Whether to overwrite an existing value for the design
          property or project variable. The default is ``False``, in
          which case this method is ignored.
      postprocessing : bool, optional
          Whether to define a postprocessing variable.
           The default is ``False``, in which case the variable is not used in postprocessing.
      circuit_parameter : bool, optional
          Whether to define a parameter in a circuit design or a local parameter.
           The default is ``True``, in which case a circuit variable is created as a parameter default.

      Returns
      -------
      bool
           ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> oProject.ChangeProperty
      >>> oDesign.ChangeProperty

      Examples
      --------
      Set the value of design property ``p1`` to ``"10mm"``,
      creating the property if it does not already eixst.

      >>> aedtapp.variable_manager.set_variable("p1", expression="10mm")

      Set the value of design property ``p1`` to ``"20mm"`` only if
      the property does not already exist.

      >>> aedtapp.variable_manager.set_variable("p1", expression="20mm", overwrite=False)

      Set the value of design property ``p2`` to ``"10mm"``,
      creating the property if it does not already exist. Also make
      it read-only and hidden and add a description.

      >>> aedtapp.variable_manager.set_variable(
      ...     variable_name="p2",
      ...     expression="10mm",
      ...     readonly=True,
      ...     hidden=True,
      ...     description="This is the description of this variable.",
      ... )

      Set the value of the project variable ``$p1`` to ``"30mm"``,
      creating the variable if it does not exist.

      >>> aedtapp.variable_manager.set_variable["$p1"] == "30mm"




   .. py:method:: delete_separator(separator_name)

      Delete a separator from either the active project or design.

      Parameters
      ----------
      separator_name : str
          Value to use for the delimiter.

      Returns
      -------
      bool
          ``True`` when the separator exists and can be deleted, ``False`` otherwise.

      References
      ----------

      >>> oProject.ChangeProperty
      >>> oDesign.ChangeProperty



   .. py:method:: delete_variable(var_name)

      Delete a variable.

      Parameters
      ----------
      var_name : str
          Name of the variable.


      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> oProject.ChangeProperty
      >>> oDesign.ChangeProperty



.. py:class:: Variable(expression, units=None, si_value=None, full_variables=None, name=None, app=None, readonly=False, hidden=False, description=None, postprocessing=False, circuit_parameter=True)

   Bases: :py:obj:`object`


   Stores design properties and project variables and provides operations to perform on them.

   Parameters
   ----------
   value : float, str
       Numerical value of the variable in SI units.
   units : str
       Units for the value.

   Examples
   --------

   >>> from pyedb.dotnet.database.Variables import Variable

   Define a variable using a string value consistent with the AEDT properties.

   >>> v = Variable("45mm")

   Define an unitless variable with a value of 3.0.

   >>> v = Variable(3.0)

   Define a variable defined by a numeric result and a unit string.

   >>> v = Variable(3.0 * 4.5, units="mm")
   >>> assert v.numeric_value = 13.5
   >>> assert v.units = "mm"



   .. py:property:: name

      Variable name.



   .. py:property:: is_optimization_enabled

      "Check if optimization is enabled.



   .. py:property:: optimization_min_value

      "Optimization min value.



   .. py:property:: optimization_max_value

      "Optimization max value.



   .. py:property:: is_sensitivity_enabled

      Check if Sensitivity is enabled.



   .. py:property:: sensitivity_min_value

      "Sensitivity min value.



   .. py:property:: sensitivity_max_value

      "Sensitivity max value.



   .. py:property:: sensitivity_initial_disp

      "Sensitivity initial value.



   .. py:property:: is_tuning_enabled

      Check if tuning is enabled.



   .. py:property:: tuning_min_value

      "Tuning min value.



   .. py:property:: tuning_max_value

      "Tuning max value.



   .. py:property:: tuning_step_value

      "Tuning Step value.



   .. py:property:: is_statistical_enabled

      Check if statistical is enabled.



   .. py:property:: read_only

      Read-only flag value.



   .. py:property:: hidden

      Hidden flag value.



   .. py:property:: description

      Description value.



   .. py:property:: post_processing

      Postprocessing flag value.



   .. py:property:: circuit_parameter

      Circuit parameter flag value.



   .. py:property:: expression

      Expression.



   .. py:property:: numeric_value

      Numeric part of the expression as a float value.



   .. py:property:: unit_system

      Unit system of the expression as a string.



   .. py:property:: units

      Units.



   .. py:property:: value

      Value.



   .. py:property:: evaluated_value

      String value.

      The numeric value with the unit is concatenated and returned as a string. The numeric display
      in the modeler and the string value can differ. For example, you might see ``10mm`` in the
      modeler and see ``10.0mm`` returned as the string value.




   .. py:method:: decompose()

      Decompose a variable value to a floating with its unit.

      Returns
      -------
      tuple
          The float value of the variable and the units exposed as a string.

      Examples
      --------
      >>> hfss = Hfss()
      >>> hfss["v1"] = "3N"
      >>> print(hfss.variable_manager["v1"].decompose("v1"))
      >>> (3.0, "N")




   .. py:method:: rescale_to(units)

      Rescale the expression to a new unit within the current unit system.

      Parameters
      ----------
      units : str
          Units to rescale to.

      Examples
      --------
      >>> from pyedb.dotnet.database.Variables import Variable

      >>> v = Variable("10W")
      >>> assert v.numeric_value == 10
      >>> assert v.units == "W"
      >>> v.rescale_to("kW")
      >>> assert v.numeric_value == 0.01
      >>> assert v.units == "kW"




   .. py:method:: format(format)

      Retrieve the string value with the specified numerical formatting.

      Parameters
      ----------
      format : str
          Format for the numeric value of the string. For example, ``'06.2f'``. For
          more information, see the `PyFormat documentation <https://pyformat.info/>`_.

      Returns
      -------
      str
          String value with the specified numerical formatting.

      Examples
      --------
      >>> from pyedb.dotnet.database.Variables import Variable

      >>> v = Variable("10W")
      >>> assert v.format("f") == "10.000000W"
      >>> assert v.format("06.2f") == "010.00W"
      >>> assert v.format("6.2f") == " 10.00W"




.. py:class:: DataSet(app, name, x, y, z=None, v=None, xunit='', yunit='', zunit='', vunit='')

   Bases: :py:obj:`object`


   Manages datasets.

   Parameters
   ----------
   app :
   name : str
       Name of the app.
   x : list
       List of X-axis values for the dataset.
   y : list
       List of Y-axis values for the dataset.
   z : list, optional
       List of Z-axis values for a 3D dataset only. The default is ``None``.
   v : list, optional
       List of V-axis values for a 3D dataset only. The default is ``None``.
   xunit : str, optional
       Units for the X axis. The default is ``""``.
   yunit : str, optional
       Units for the Y axis. The default is ``""``.
   zunit : str, optional
       Units for the Z axis for a 3D dataset only. The default is ``""``.
   vunit : str, optional
       Units for the V axis for a 3D dataset only. The default is ``""``.



   .. py:attribute:: name


   .. py:attribute:: x


   .. py:attribute:: y


   .. py:attribute:: z
      :value: None



   .. py:attribute:: v
      :value: None



   .. py:attribute:: xunit
      :value: ''



   .. py:attribute:: yunit
      :value: ''



   .. py:attribute:: zunit
      :value: ''



   .. py:attribute:: vunit
      :value: ''



   .. py:method:: create()

      Create a dataset.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> oProject.AddDataset
      >>> oDesign.AddDataset



   .. py:method:: add_point(x, y, z=None, v=None)

      Add a point to the dataset.

      Parameters
      ----------
      x : float
          X coordinate of the point.
      y : float
          Y coordinate of the point.
      z : float, optional
          The default is ``None``.
      v : float, optional
          The default is ``None``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> oProject.EditDataset
      >>> oDesign.EditDataset



   .. py:method:: remove_point_from_x(x)

      Remove a point from an X-axis value.

      Parameters
      ----------
      x : float

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> oProject.EditDataset
      >>> oDesign.EditDataset



   .. py:method:: remove_point_from_index(id_to_remove)

      Remove a point from an index.

      Parameters
      ----------
      id_to_remove : int
          ID of the index.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> oProject.EditDataset
      >>> oDesign.EditDataset



   .. py:method:: update()

      Update the dataset.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> oProject.EditDataset
      >>> oDesign.EditDataset



   .. py:method:: delete()

      Delete the dataset.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> oProject.DeleteDataset
      >>> oDesign.DeleteDataset



   .. py:method:: export(dataset_path=None)

      Export the dataset.

      Parameters
      ----------
      dataset_path : str, optional
          Path to export the dataset to. The default is ``None``, in which
          case the dataset is exported to the working_directory path.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      References
      ----------

      >>> oProject.ExportDataset
      >>> oDesign.ExportDataset



