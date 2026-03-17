src.pyedb.grpc.database.hierarchy.component
===========================================

.. py:module:: src.pyedb.grpc.database.hierarchy.component


Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.hierarchy.component.component_type_mapping


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.hierarchy.component.ComponentProperty
   src.pyedb.grpc.database.hierarchy.component.Component
   src.pyedb.grpc.database.hierarchy.component.ICDieProperty


Module Contents
---------------

.. py:data:: component_type_mapping

.. py:class:: ComponentProperty(core)

   Class managing component properties.


.. py:class:: Component(pedb, edb_object)

   Manages EDB functionalities for components.

   Parameters
   ----------
   pedb : Edb
       An instance of the Edb class.
   edb_object : ansys.edb.core.hierarchy.component.Component
           An instance of the EDB component object.


   .. py:attribute:: core


   .. py:property:: pin_pairs
      :type: List[tuple[str, str]] | None


      Pinpairs of the model.



   .. py:property:: group_type


   .. py:property:: is_null

      Check if the component is null.

      Returns
      -------
      bool
          True if the component is null, False otherwise.



   .. py:property:: component_type
      :type: str


      Component type.

      Returns
      -------
      str



   .. py:property:: layout_instance

      Layout instance object.

      Returns
      -------
      :class:`LayoutInstance <ansys.edb.core.layout_instance.layout_instance.LayoutInstance>`



   .. py:property:: component_instance

      Component instance.

      Returns
      -------
      :class:`LayoutObjInstance <ansys.edb.core.layout_instance.layout_obj_instance.LayoutObjInstance>`



   .. py:property:: is_enabled
      :type: bool


      Component enable.

      Returns
      -------
      bool




   .. py:property:: ic_die_properties
      :type: ICDieProperty | None


      IC Die property.

      returns
      -------
      :class:`ICDieProperty <pyedb.grpc.database.hierarchy.component.ICDieProperty>`



   .. py:property:: component_definition

      Component definition.

      Returns
      -------
      :class:`ComponentDef <ansys.edb.core.definition.component_def.ComponentDef>`




   .. py:property:: component_def

      Component definition.

      deprecated: use `component_definition` instead.




   .. py:property:: component_property

      Component property.

      Returns
      -------
      :class:`ComponentProperty <ansys.edb.core.hierarchy.component_property.ComponentProperty>`




   .. py:property:: model
      :type: pyedb.grpc.database.hierarchy.s_parameter_model.SparamModel | pyedb.grpc.database.hierarchy.spice_model.SpiceModel | pyedb.grpc.database.hierarchy.pin_pair_model.PinPairModel


      Component model.

      Returns
      -------
      :class:`Model <ansys.edb.core.hierarchy.model.Model>`




   .. py:property:: package_def

      Package definition.

      Returns
      -------
      :class:`PackageDef <ansys.edb.core.definition.package_def.PackageDef>`



   .. py:property:: is_mcad
      :type: bool


      MCad component.

      Returns
      -------
      bool




   .. py:property:: is_mcad_3d_comp
      :type: bool


      Mcad 3D component.

      Returns
      -------
      bool




   .. py:property:: is_mcad_hfss
      :type: bool


      MCad HFSS.

      Returns
      -------
      bool




   .. py:property:: is_mcad_stride
      :type: bool


      MCar stride.

      Returns
      -------
      bool




   .. py:method:: create_package_def(name=None, component_part_name=None) -> bool

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



   .. py:property:: enabled
      :type: bool


      Component active mode.

      Returns
      -------
      bool




   .. py:property:: spice_model
      :type: pyedb.grpc.database.hierarchy.spice_model.SpiceModel | None


      Assigned Spice model.

      Returns
      -------
      :class:`SpiceModel <pyedb.grpc.database.hierarchy.spice_model.SpiceModel>`



   .. py:property:: s_param_model
      :type: pyedb.grpc.database.hierarchy.s_parameter_model.SparamModel | None


      Assigned S-parameter model.

      Returns
      -------
      :class:`SParameterModel <ansys.edb.core.hierarchy.sparameter_model.SParameterModel>`



   .. py:property:: netlist_model
      :type: pyedb.grpc.database.hierarchy.netlist_model.NetlistModel | None


      Assigned netlist model.

      Returns
      -------
      :class:`NetlistModel <ansys.edb.core.hierarchy.netlist_mode.NetlistModel>`



   .. py:property:: solder_ball_height
      :type: float


      Solder ball height if available.

      Returns
      -------
      float
          Balls height value.



   .. py:property:: solder_ball_shape
      :type: str | None


      Solder ball shape.

      Returns
      -------
      str
          Solder balls shapes, ``none``, ``cylinder`` or ``spheroid``.



   .. py:property:: solder_ball_diameter
      :type: Union[tuple[float, float], None]


      Solder ball diameter.

      Returns
      -------
      float
          diameter value.



   .. py:property:: solder_ball_material
      :type: str


      Solderball material name.



   .. py:property:: uses_solderball
      :type: bool


      Whether if solderball is enabled or not.



   .. py:property:: solder_ball_placement

      Solder ball placement if available..



   .. py:property:: refdes
      :type: str


      Reference Designator Name.

      Returns
      -------
      str
          Reference Designator Name.



   .. py:property:: model_type
      :type: str


      Retrieve assigned model type.

      Returns
      -------
      str
          Model type, ``RLC``, `` SParameterModel`` or ``SPICEModel``.



   .. py:property:: rlc_values
      :type: Union[List[list[float]], List[float]]


      Get component rlc values.

      Returns
      -------
      list[list[Rvalue(float), Lvalue(float), Cvalue(float)]].



   .. py:property:: value
      :type: float


      Retrieve discrete component value.

      Returns
      -------
      float
          Value. ``None`` if not an RLC Type.



   .. py:property:: res_value
      :type: float


      Resistance value.

      Returns
      -------
      float
          Resistance value or ``None`` if not an RLC type.



   .. py:property:: rlc_enable
      :type: list[bool]


      RLC enabled flag.

      Returns
      -------
      bool
          ``True`` if RLC is enabled.



   .. py:property:: res_enabled
      :type: bool


      Resistance enabled flag.

      Returns
      -------
      bool
          ``True`` if resistor is enabled.



   .. py:property:: cap_enabled
      :type: bool


      Capacitance enabled flag.

      Returns
      -------
      bool
          ``True`` if capacitance is enabled.



   .. py:property:: ind_enabled
      :type: bool


      Inductance enabled flag.

      Returns
      -------
      bool
          ``True`` if inductance is enabled.



   .. py:property:: cap_value
      :type: float


      Capacitance Value.

      Returns
      -------
      float
          Capacitance Value. ``None`` if not an RLC Type.



   .. py:property:: ind_value

      Inductance Value.

      Returns
      -------
      float
          Inductance Value. ``None`` if not an RLC Type.



   .. py:property:: is_parallel_rlc
      :type: bool


      Define if model is Parallel or Series.

      Returns
      -------
      bool
          `True´ if parallel rlc model.
          `False` series RLC.
          `None` if not RLC Type.



   .. py:property:: center
      :type: tuple[float, float]


      Compute the component center.

      Returns
      -------
      list
          [x value, y value].



   .. py:property:: location
      :type: tuple[float, float]


      Component center.

      Returns
      -------
      List[float, float]
          [x, y].




   .. py:property:: bounding_box
      :type: list[float, float, float, float]


      Component's bounding box.

      Returns
      -------
      List[float]
          List of coordinates for the component's bounding box, with the list of
          coordinates in this order: [X lower left corner, Y lower left corner,
          X upper right corner, Y upper right corner].



   .. py:property:: rotation
      :type: float


      Compute the component rotation in radian.

      Returns
      -------
      float
          Rotation value.



   .. py:property:: pinlist
      :type: list[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      Pins of the component.

      Returns
      -------
      list
          List of Pins of Component.



   .. py:property:: nets

      Nets of Component.

      Returns
      -------
      list[str]
          Component nets names.



   .. py:property:: pins
      :type: dict[str, pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      Component pins.

      Returns
      -------
      Dic[str,:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
          Component dictionary pins.



   .. py:property:: num_pins

      Number of Pins of Component.

      Returns
      -------
      int
          Component pins number.



   .. py:property:: type
      :type: str


      Component type.

      Returns
      -------
      str
          Type of the component. Options are ``"resistor"``, ``"inductor"``, ``"capacitor"``,
          ``"ic"``, ``"io"`` and ``"other"``.



   .. py:property:: numpins
      :type: int


      Number of Pins of Component.

      ..deprecated:: 0.51.0
         Use: func:`num_pins` instead.
      Returns
      -------
      int
          Component pins number.



   .. py:property:: partname
      :type: str


      Component part name.

      Returns
      -------
      str
          Component part name.



   .. py:property:: name

      Component part name.

      Returns
      -------
      str
          Component part name.



   .. py:property:: ref_des

      Reference Designator Name.

      Returns
      -------
      str
          Reference Designator Name.



   .. py:property:: part_name
      :type: str


      Component part name.

      Returns
      -------
      str
          Component part name.



   .. py:property:: placement_layer
      :type: str


      Placement layern name.

      Returns
      -------
      str
         Placement layer name.



   .. py:property:: layer
      :type: pyedb.grpc.database.layers.stackup_layer.StackupLayer


      Placement layern object.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
         Placement layer.



   .. py:property:: is_top_mounted
      :type: bool


      Check if a component is mounted on top or bottom of the layout.

      Returns
      -------
      bool
          ``True`` component is mounted on top, ``False`` on down.



   .. py:property:: lower_elevation
      :type: float


      Lower elevation of the placement layer.

      Returns
      -------
      float
          Placement layer lower elevation.



   .. py:property:: upper_elevation
      :type: float


      Upper elevation of the placement layer.

      Returns
      -------
      float
          Placement layer upper elevation.




   .. py:property:: top_bottom_association
      :type: int


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



   .. py:method:: delete()

      Delete the component from the EDB.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: assign_spice_model(file_path: str, name: Optional[str] = None, sub_circuit_name: Optional[str] = None, terminal_pairs: Optional[list] = None) -> pyedb.grpc.database.hierarchy.spice_model.SpiceModel | bool

      Assign Spice model to this component.

      Parameters
      ----------
      file_path : str
          File path of the Spice model.
      name : str, optional
          Name of the Spice model.
      sub_circuit_name : str, optional
          Sub-circuit name in the Spice file. If not provided, the first sub-circuit will be assigned.
      terminal_pairs : list, optional
          List of terminal pairs. Each pair should be in the format of [pin_name, pin_number].
          If not provided, the pin order in the Spice file will be used.

      Returns
      -------
      :class:`SpiceModel <pyedb.grpc.database.hierarchy.spice_model.SpiceModel>`
          Spice model.




   .. py:method:: assign_netlist_model(netlist)

      Assign Netlist to this component.

      Parameters
      ----------
      netlist : str
          Netlist.

      Returns
      -------




   .. py:method:: assign_s_param_model(file_path, name=None, reference_net=None) -> ansys.edb.core.definition.component_model.NPortComponentModel | bool

      Assign S-parameter to this component.

      Parameters
      ----------
      file_path : str
          File path of the S-parameter model.
      name : str, optional
          Name of the S-parameter model.

      reference_net : str, optional
          Reference net.

      Returns
      -------
      :class:`NPortComponentModel <ansys.edb.core.definition.component_model.ComponentModel>`
          ComponentModel.




   .. py:method:: use_s_parameter_model(name, reference_net=None) -> bool

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
      >>>comp_def = edbapp.definitions.components["CAPC3216X180X55ML20T25"]
      >>>comp_def.add_n_port_model("c:GRM32_DC0V_25degC_series.s2p", "GRM32_DC0V_25degC_series")
      >>>edbapp.components["C200"].use_s_parameter_model("GRM32_DC0V_25degC_series")



   .. py:method:: assign_rlc_model(res=None, ind=None, cap=None, is_parallel=False) -> pyedb.grpc.database.hierarchy.pin_pair_model.PinPairModel | bool

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

      Returns
      -------
      :class:`Model <ansys.edb.core.hierarchy.model.Model>`
          Component Model.




   .. py:method:: create_clearance_on_component(extra_soldermask_clearance=0.0001) -> bool

      Create a Clearance on Soldermask layer by drawing a rectangle.

      Parameters
      ----------
      extra_soldermask_clearance : float, optional
          Extra Soldermask value in meter to be applied on component bounding box.

      Returns
      -------
          bool



.. py:class:: ICDieProperty(component)

   .. py:property:: die_orientation
      :type: str


      Die orientation.

      Returns
      -------
      str
          Die orientation, ``chip_up`` or ``chip_down``.




   .. py:property:: die_type
      :type: str


      Die type.

      Returns
      -------
      str
          Die type, ``none``, ``flipchip``, ``wirebond``.




   .. py:property:: height
      :type: float


      Die height.

      Returns
      -------
      float
          Die height.




   .. py:property:: is_null
      :type: bool


      Test is die is null.

      Returns
      -------
      bool




