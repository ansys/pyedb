src.pyedb.grpc.database.definition.component_def
================================================

.. py:module:: src.pyedb.grpc.database.definition.component_def


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.definition.component_def.ComponentDef


Module Contents
---------------

.. py:class:: ComponentDef(pedb: pyedb.grpc.edb.Edb, core: ansys.edb.core.definition.component_def.ComponentDef)

   Manages EDB functionalities for component definitions.

   Parameters
   ----------
   pedb : :class:`pyedb.grpc.edb.Edb`
       EDB database object.
   core : :class:`ansys.edb.core.definition.component_def.ComponentDef`
       Core component definition object.


   .. py:attribute:: core


   .. py:property:: part_name
      :type: str


      Component definition name.

      Returns
      -------
      str
          Component part name.




   .. py:property:: type
      :type: str


      Component definition type.

      Returns
      -------
      str
          Component definition type.



   .. py:property:: components
      :type: dict[str, pyedb.grpc.database.hierarchy.component.Component]


      Component instances belonging to the definition.

      Returns
      -------
      dict[str, :class:`Component <pyedb.grpc.database.hierarchy.component.Component>`]



   .. py:property:: is_null
      :type: bool


      Check if the component definition is null.

      Returns
      -------
      bool
          True if the component definition is null, False otherwise.




   .. py:property:: component_pins
      :type: list[pyedb.grpc.database.definition.component_pin.ComponentPin]


      Component pins.

      Returns
      -------
      list[:class:`ComponentPin <pyedb.grpc.database.definition.component_pin.ComponentPin>`]




   .. py:method:: find(edb, name) -> ComponentDef | None
      :classmethod:


      Find component definition by name.

      Parameters
      ----------
      edb : :class:`pyedb.grpc.edb.Edb`
          EDB database object.
      name : str
          Component definition name.

      Returns
      -------
      :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>` or None



   .. py:method:: create(edb, name, fp=None) -> ComponentDef
      :classmethod:


      Create a new component definition.

      Parameters
      ----------
      edb : :class:`pyedb.grpc.edb.Edb`
          EDB database object.
      name : str
          Component definition name.
      fp : str, optional
         Footprint cell name.

      Returns
      -------
      :class:`ComponentDef <pyedb.grpc.database.definition.component_def.ComponentDef>`



   .. py:method:: assign_rlc_model(res=None, ind=None, cap=None, is_parallel=False) -> bool

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

      Returns
      -------
      bool




   .. py:method:: assign_s_param_model(file_path, model_name=None, reference_net=None) -> bool

      Assign S-parameter to all components under this part name.

      Parameters
      ----------
      file_path : str
          File path of the S-parameter model.
      model_name : str, optional
          Name of the S-parameter model.

      reference_net : str, optional
          Name of the reference net.

      Returns
      -------
      bool




   .. py:method:: assign_spice_model(file_path, model_name=None) -> bool

      Assign Spice model to all components under this part name.

      Parameters
      ----------
      file_path : str
          File path of the Spice model.
      model_name : str, optional
          Name of the Spice model.

      Returns
      -------
      bool



   .. py:property:: reference_file
      :type: list[str]


      Model reference file.

      Returns
      -------
      list[str]
          List of reference files.




   .. py:property:: component_models
      :type: dict[str, pyedb.grpc.database.definition.component_model.ComponentModel]


      Component models.

      Returns
      -------
      dict[str, :class:`ComponentModel <ansys.edb.core.definition.component_model.ComponentModel>`]




   .. py:property:: name
      :type: str


      Component definition name.

      Returns
      -------
      str
          Component definition name.




   .. py:method:: add_n_port_model(fpath, name=None) -> ansys.edb.core.definition.component_model.NPortComponentModel

      Add N-port model.

      Returns
      -------
      Nport model : :class:`NPortComponentModel <ansys.edb.core.definition.component_model.NPortComponentModel>`




   .. py:method:: get_properties() -> dict


   .. py:method:: set_properties(**kwargs)


