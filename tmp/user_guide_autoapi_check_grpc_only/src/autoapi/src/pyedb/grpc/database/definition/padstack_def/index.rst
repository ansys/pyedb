src.pyedb.grpc.database.definition.padstack_def
===============================================

.. py:module:: src.pyedb.grpc.database.definition.padstack_def


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.definition.padstack_def.PadProperties
   src.pyedb.grpc.database.definition.padstack_def.PadstackDef


Module Contents
---------------

.. py:class:: PadProperties(core, layer_name, pad_type, p_edb_padstack)

   Manages EDB functionalities for pad properties.

   Parameters
   ----------
   edb_padstack :

   layer_name : str
       Name of the layer.
   pad_type :
       Type of the pad.
   pedbpadstack : str
       Inherited AEDT object.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", version="2026.1")
   >>> edb_pad_properties = edb.padstacks.definitions["MyPad"].pad_by_layer["TOP"]


   .. py:attribute:: layer_name


   .. py:attribute:: pad_type


   .. py:property:: geometry_type
      :type: float


      Geometry type.

      Returns
      -------
      int
          Type of the geometry.



   .. py:property:: shape
      :type: str


      Pad shape.

      Returns
      -------
      str
          pad shape.



   .. py:property:: parameters_values

      Parameters.

      Returns
      -------
      list
          List of parameters.



   .. py:property:: parameters_values_string

      Parameters value in string format.



   .. py:property:: polygon_data
      :type: ansys.edb.core.geometry.polygon_data.PolygonData


      Parameters.

      Returns
      -------
      PolygonData
          PolygonData object.



   .. py:property:: offset_x
      :type: float


      Offset for the X axis.

      Returns
      -------
      str
          Offset for the X axis.



   .. py:property:: offset_y
      :type: float


      Offset for the Y axis.

      Returns
      -------
      str
          Offset for the Y axis.



   .. py:property:: rotation
      :type: float


      Rotation.

      Returns
      -------
      str
          Value for the rotation.



.. py:class:: PadstackDef(pedb, edb_object)

   Manages EDB functionalities for a padstack.

   Parameters
   ----------
   edb_padstack :

   ppadstack : str
       Inherited AEDT object.

   Examples
   --------
   >>> from pyedb import Edb
   >>> edb = Edb("myedb", version="2026.1")
   >>> edb_padstack = edb.padstacks.definitions["MyPad"]


   .. py:attribute:: core


   .. py:property:: id
      :type: int


      Padstack definition ID.



   .. py:property:: is_null

      Check if the padstack definition is null.



   .. py:method:: create(edb, name: str)
      :classmethod:


      Create a new padstack definition.



   .. py:property:: instances
      :type: list[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance]


      Definitions Instances.

      Returns
      -------
      List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]
          Dict of PadstackInstance objects.



   .. py:property:: name

      Padstack definition name.



   .. py:property:: data

      Padstack definition data.

      Returns
      -------
      PadstackDef
          Padstack definition data object.



   .. py:property:: layers
      :type: list[str]


      Layers.

      Returns
      -------
      list[str]
          List of layer names.



   .. py:property:: start_layer

      Starting layer.

      Returns
      -------
      str
          Name of the starting layer.



   .. py:property:: via_start_layer

      Via starting layer.

      .deprecated
      Use: :method:`start_layer <pyedb.grpc.database.definition.padstack_def.PadstackDef.start_layer>`
      instead.

      Returns
      -------
      str
          Name of the via starting layer.



   .. py:property:: stop_layer

      Stopping layer.

      Returns
      -------
      str
          Name of the stopping layer.



   .. py:property:: via_stop_layer

      Via stop layer.

      .deprecated
      Use :method:`stop_layer <pyedb.grpc.database.definition.padstack_def.PadstackDef.stop_layer>`
      instead.

      Returns
      -------
      str
          Name of the via stop layer.



   .. py:property:: material

      Return hole material name.

      Returns
      -------
      str
          Hole material name.



   .. py:property:: hole_diameter
      :type: float | None


      Hole diameter.

      Returns
      -------
      float
          Diameter value.




   .. py:property:: hole_type
      :type: float


      Holy type.

      Returns
      -------
      float
          hole type.




   .. py:property:: edb_hole_type

      EDB hole type.

      Returns
      -------
      str
          Hole type.




   .. py:property:: hole_offset_x
      :type: float


      Hole offset for the X axis.

      Returns
      -------
      float
          Hole offset value for the X axis.



   .. py:property:: hole_offset_y
      :type: float


      Hole offset for the Y axis.

      Returns
      -------
      float
          Hole offset value for the Y axis.



   .. py:property:: hole_rotation
      :type: float


      Hole rotation.

      Returns
      -------
      float
          Value for the hole rotation.



   .. py:property:: pad_by_layer
      :type: dict[str, PadProperties]


      Pad by layer.

      Returns
      -------
      Dict[str, :class:`PadProperties <pyedb.grpc.database.definition.padstack_def.PadProperties>`]
          Dictionary with layer as key and PadProperties as value.



   .. py:property:: antipad_by_layer
      :type: dict[str, PadProperties]


      Antipad by layer.

      Returns
      -------
      Dict[str, :class:`PadProperties <pyedb.grpc.database.definition.padstack_def.PadProperties>`]
          Dictionary with layer as key and PadProperties as value.



   .. py:property:: thermalpad_by_layer
      :type: dict[str, PadProperties]


      Thermal by layer.

      Returns
      -------
      Dict[str, :class:`PadProperties <pyedb.grpc.database.definition.padstack_def.PadProperties>`]
          Dictionary with layer as key and PadProperties as value.



   .. py:property:: hole_plating_ratio
      :type: float


      Hole plating ratio.

      Returns
      -------
      float
          Percentage for the hole plating.



   .. py:property:: hole_plating_thickness
      :type: float


      Hole plating thickness.

      Returns
      -------
       float
          Thickness of the hole plating if present.



   .. py:property:: hole_finished_size
      :type: float


      Finished hole size.

      Returns
      -------
      float
          Finished size of the hole (Total Size + PlatingThickess*2).



   .. py:property:: hole_range
      :type: str | None


      Get hole range value from padstack definition.

      Returns
      -------
      str
          Possible returned values are ``"through"``, ``"begin_on_upper_pad"``,
          ``"end_on_lower_pad"``, ``"upper_pad_to_lower_pad"``, and ``"undefined"``.



   .. py:method:: convert_to_3d_microvias(convert_only_signal_vias=True, hole_wall_angle=15, delete_padstack_def=True) -> bool

      Convert actual padstack instance to microvias 3D Objects with a given aspect ratio.

      Parameters
      ----------
      convert_only_signal_vias : bool, optional
          Either to convert only vias belonging to signal nets or all vias. Defaults is ``True``.
      hole_wall_angle : float, optional
          Angle of laser penetration in degrees. The angle defines the lowest hole diameter with this formula:
          HoleDiameter -2*tan(laser_angle* Hole depth). Hole depth is the height of the via (dielectric thickness).
          The default is ``15``.
          The lowest hole is ``0.75*HoleDepth/HoleDiam``.
      delete_padstack_def : bool, optional
          Whether to delete the padstack definition. The default is ``True``.
          If ``False``, the padstack definition is not deleted and the hole size is set to zero.

      Returns
      -------
          ``True`` when successful, ``False`` when failed.



   .. py:method:: split_to_microvias() -> list[pyedb.grpc.database.primitive.padstack_instance.PadstackInstance] | bool

      Convert actual padstack definition to multiple microvias definitions.

      Returns
      -------
      List[:class:`PadstackInstance <pyedb.grpc.database.primitive.padstack_instance.PadstackInstance>`]



   .. py:method:: get_pad_parameters()

      Pad parameters.

      Returns
      -------
      dict
          params = {
          'regular_pad': [
              {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0.1mm', 'offset_y': '0',
              'rotation': '0', 'diameter': '0.5mm'}
          ],
          'anti_pad': [
              {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0', 'offset_y': '0', 'rotation': '0',
              'diameter': '1mm'}
          ],
          'thermal_pad': [
              {'layer_name': '1_Top', 'shape': 'round90', 'offset_x': '0', 'offset_y': '0', 'rotation': '0',
              'inner': '1mm', 'channel_width': '0.2mm', 'isolation_gap': '0.3mm'},
          ],
          'hole': [
              {'layer_name': '1_Top', 'shape': 'circle', 'offset_x': '0', 'offset_y': '0', 'rotation': '0',
               'diameter': '0.1499997mm'},
          ]
      }



   .. py:method:: set_pad_parameters(param)


   .. py:method:: get_hole_parameters()


   .. py:method:: set_hole_parameters(params)


   .. py:method:: get_solder_parameters()


   .. py:method:: set_solder_parameters(parameters)


   .. py:attribute:: PAD_SHAPE_PARAMETERS


   .. py:attribute:: PAD_SHAPE_KEYS


   .. py:attribute:: SOLDER_SHAPE_TYPE


   .. py:attribute:: SOLDER_PLACEMENT


