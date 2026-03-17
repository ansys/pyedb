src.pyedb.dotnet.database.cell.hierarchy.component
==================================================

.. py:module:: src.pyedb.dotnet.database.cell.hierarchy.component


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.cell.hierarchy.component.ICDieProperties
   src.pyedb.dotnet.database.cell.hierarchy.component.PortProperty
   src.pyedb.dotnet.database.cell.hierarchy.component.ComponentProperties
   src.pyedb.dotnet.database.cell.hierarchy.component.EDBComponent


Module Contents
---------------

.. py:class:: ICDieProperties(pedb, edb_object)

   .. py:property:: die_orientation


   .. py:property:: die_type


   .. py:property:: height


.. py:class:: PortProperty(edbobj)

   .. py:attribute:: core


   .. py:property:: reference_height


   .. py:method:: get_reference_size()


   .. py:property:: reference_size_auto


.. py:class:: ComponentProperties(edbobj)

   .. py:attribute:: core


   .. py:property:: port_property


.. py:class:: EDBComponent(pedb, edb_object)

   Bases: :py:obj:`pyedb.dotnet.database.cell.hierarchy.hierarchy_obj.Group`


   Manages EDB functionalities for components.

   Parameters
   ----------
   parent : :class:`pyedb.dotnet.database.components.Components`
       Components object.
   component : object
       Edb Component Object



   .. py:attribute:: edbcomponent


   .. py:property:: name

      Name of the definition.



   .. py:property:: group_type


   .. py:property:: layout_instance

      EDB layout instance object.



   .. py:property:: component_instance

      Edb component instance.



   .. py:property:: component_property

      ``ComponentProperty`` object.



   .. py:property:: pin_pairs

      Pin pair model if assigned.



   .. py:property:: model

      Component model.



   .. py:property:: package_def

      Package definition.



   .. py:property:: ic_die_properties

      Adding IC properties for grpc compatibility.



   .. py:method:: create_package_def(name='', component_part_name=None)

      Create a package definition and assign it to the component.

      Parameters
      ----------
      name: str, optional
          Name of the package definition
      component_part_name : str, optional
          Part name of the component.

      Returns
      -------
      bool
          ``True`` if succeeded, ``False`` otherwise.



   .. py:property:: is_enabled

      Get or Set the component to active mode.

      Returns
      -------
      bool
          ``True`` if component is active, ``False`` if is disabled..



   .. py:property:: enabled

      Get or Set the component to active mode.



   .. py:property:: spice_model

      Get assigned Spice model properties.



   .. py:property:: s_param_model

      Get assigned S-parameter model properties.



   .. py:property:: netlist_model

      Get assigned netlist model properties.



   .. py:property:: solder_ball_height

      Solder ball height if available.



   .. py:property:: solder_ball_shape

      Solder ball shape.



   .. py:property:: solder_ball_diameter

      Solder ball diameter.



   .. py:property:: uses_solderball
      :type: bool


      Whether if solderball is enabled or not.



   .. py:property:: solder_ball_placement

      Solder ball placement if available..



   .. py:property:: solder_ball_material


   .. py:property:: refdes

      Reference Designator Name.

      Returns
      -------
      str
          Reference Designator Name.



   .. py:property:: is_null

      Flag indicating if the current object exists.



   .. py:property:: model_type

      Retrieve assigned model type.



   .. py:property:: rlc_values

      Get component rlc values.



   .. py:property:: value

      Retrieve discrete component value.

      Returns
      -------
      str
          Value. ``None`` if not an RLC Type.



   .. py:property:: res_value

      Resistance value.

      Returns
      -------
      str
          Resistance value or ``None`` if not an RLC type.



   .. py:property:: rlc_enable


   .. py:property:: first_pin


   .. py:property:: second_pin


   .. py:property:: cap_value

      Capacitance Value.

      Returns
      -------
      str
          Capacitance Value. ``None`` if not an RLC Type.



   .. py:property:: ind_value

      Inductance Value.

      Returns
      -------
      str
          Inductance Value. ``None`` if not an RLC Type.



   .. py:property:: is_parallel_rlc

      Define if model is Parallel or Series.

      Returns
      -------
      bool
          ``True`` if it is a parallel rlc model. ``False`` for series RLC. ``None`` if not an RLC Type.



   .. py:property:: center

      Compute the component center.

      Returns
      -------
      list



   .. py:property:: bounding_box

      Component's bounding box.

      Returns
      -------
      List[float]
          List of coordinates for the component's bounding box, with the list of
          coordinates in this order: [X lower left corner, Y lower left corner,
          X upper right corner, Y upper right corner].



   .. py:property:: rotation

      Compute the component rotation in radian.

      Returns
      -------
      float



   .. py:property:: pinlist

      Pins of the component.

      Returns
      -------
      list
          List of Pins of Component.



   .. py:property:: nets

      Nets of Component.

      Returns
      -------
      list
          List of Nets of Component.



   .. py:property:: pins

      EDBPadstackInstance of Component.

      Returns
      -------
      dic[str, :class:`dotnet.database.edb_data.definitions.EDBPadstackInstance`]
          Dictionary of EDBPadstackInstance Components.



   .. py:property:: type

      Component type.

      Returns
      -------
      str
          Component type.



   .. py:property:: numpins

      Number of Pins of Component.

      Returns
      -------
      int
          Number of Pins of Component.



   .. py:property:: partname

      Component part name.

      Returns
      -------
      str
          Component Part Name.



   .. py:property:: part_name

      Component part name.

      Returns
      -------
      str
          Component part name.



   .. py:property:: placement_layer

      Placement layer.

      Returns
      -------
      str
         Name of the placement layer.



   .. py:property:: is_top_mounted

      Check if a component is mounted on top or bottom of the layout.

      Returns
      -------
      bool
          ``True`` component is mounted on top, ``False`` on down.



   .. py:property:: lower_elevation

      Lower elevation of the placement layer.

      Returns
      -------
      float
          Lower elevation of the placement layer.



   .. py:property:: upper_elevation

      Upper elevation of the placement layer.

      Returns
      -------
      float
          Upper elevation of the placement layer.




   .. py:property:: top_bottom_association

      Top/bottom association of the placement layer.

      Returns
      -------
      int
          Top/bottom association of the placement layer, where:

          * 0 - Top associated
          * 1 - No association
          * 2 - Bottom associated
          * 4 - Number of top/bottom associations.
          * -1 - Undefined



   .. py:method:: assign_spice_model(file_path: str, name: Optional[str] = None, sub_circuit_name: Optional[str] = None, terminal_pairs: Optional[list] = None)

      Assign Spice model to this component.

      Parameters
      ----------
      file_path : str
          File path of the Spice model.
      name : str, optional
          Name of the Spice model.
      sub_circuit_name : str, optional
          Name of the sub circuit.
      terminal_pairs : list, optional
          list of terminal pairs.

      Returns
      -------




   .. py:method:: assign_netlist_model(netlist)

      Assign Netlist to this component.

      Parameters
      ----------
      netlist : str
         Netlist.

      Returns
      -------




   .. py:method:: assign_s_param_model(file_path, name=None, reference_net=None)

      Assign S-parameter to this component.

      Parameters
      ----------
      file_path : str
          File path of the S-parameter model.
      name : str, optional
          Name of the S-parameter model.
      reference_net : str, optional
          Name of the reference net.
      Returns
      -------




   .. py:method:: use_s_parameter_model(name, reference_net=None)

      Use S-parameter model on the component.

      Parameters
      ----------
      name: str
          Name of the S-parameter model.
      reference_net: str, optional
          Reference net of the model.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> edbapp = Edb()
      >>>comp_def = edbapp.definitions.components["CAPC3216X180X55ML20T25"]
      >>>comp_def.add_n_port_model("c:GRM32_DC0V_25degC_series.s2p", "GRM32_DC0V_25degC_series")
      >>>edbapp.components["C200"].use_s_parameter_model("GRM32_DC0V_25degC_series")



   .. py:method:: assign_rlc_model(res=None, ind=None, cap=None, is_parallel=False)

      Assign RLC to this component.

      Parameters
      ----------
      res : int, float
          Resistance. Default is ``None``.
      ind : int, float
          Inductance. Default is ``None``.
      cap : int, float
          Capacitance. Default is ``None``.
      is_parallel : bool, optional
          Whether it is a parallel or series RLC component. The default is ``False``.



   .. py:method:: create_clearance_on_component(extra_soldermask_clearance=0.0001)

      Create a Clearance on Soldermask layer by drawing a rectangle.

      Parameters
      ----------
      extra_soldermask_clearance : float, optional
          Extra Soldermask value in meter to be applied on component bounding box.

      Returns
      -------
          bool



