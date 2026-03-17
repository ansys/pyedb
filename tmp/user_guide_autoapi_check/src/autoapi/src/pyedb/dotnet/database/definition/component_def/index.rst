src.pyedb.dotnet.database.definition.component_def
==================================================

.. py:module:: src.pyedb.dotnet.database.definition.component_def


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.definition.component_def.EDBComponentDef


Module Contents
---------------

.. py:class:: EDBComponentDef(pedb, edb_object=None)

   Bases: :py:obj:`pyedb.dotnet.database.utilities.obj_base.ObjBase`


   Manages EDB functionalities for component definitions.

   Parameters
   ----------
   pedb : :class:`pyedb.edb`
       Inherited AEDT object.
   edb_object : object
       Edb ComponentDef Object


   .. py:property:: part_name

      Retrieve component definition name.



   .. py:property:: type

      Retrieve the component definition type.

      Returns
      -------
      str



   .. py:property:: components

      Get the list of components belonging to this component definition.

      Returns
      -------
      dict of :class:`EDBComponent`



   .. py:method:: assign_rlc_model(res=None, ind=None, cap=None, is_parallel=False)

      Assign RLC to all components under this part name.

      Parameters
      ----------
      res : int, float
          Resistance. Default is ``None``.
      ind : int, float
          Inductance. Default is ``None``.
      cap : int, float
          Capacitance. Default is ``None``.
      is_parallel : bool, optional
          Whether it is parallel or series RLC component.



   .. py:method:: assign_s_param_model(file_path, name=None, reference_net=None)

      Assign S-parameter to all components under this part name.

      Parameters
      ----------
      file_path : str
          File path of the S-parameter model.
      name : str, optional
          Name of the S-parameter model.
      reference_net : str, optional
          Reference net for the S-parameter model.

      Returns
      -------




   .. py:method:: assign_spice_model(file_path, model_name=None, sub_circuit_name=None, terminal_pairs=None)

      Assign Spice model to all components under this part name.

      Parameters
      ----------
      file_path : str
          File path of the Spice model.
      model_name : str, optional
          Name of the Spice model.
      sub_circuit_name : str, optional
          Name of the sub circuit.
      terminal_pairs : list, optional
          list of terminal pairs.

      Returns
      -------




   .. py:property:: reference_file


   .. py:property:: component_models


   .. py:method:: add_n_port_model(fpath, name=None)


   .. py:method:: create(name)


   .. py:method:: get_properties()


   .. py:method:: set_properties(**kwargs)


