src.pyedb.grpc.database.stackup
===============================

.. py:module:: src.pyedb.grpc.database.stackup

.. autoapi-nested-parse::

   This module contains the `EdbStackup` class.



Attributes
----------

.. autoapisummary::

   src.pyedb.grpc.database.stackup.logger


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.stackup.LayerCollection
   src.pyedb.grpc.database.stackup.Stackup


Module Contents
---------------

.. py:data:: logger

.. py:class:: LayerCollection(pedb=None, core=None)

   Manages layer collections in an EDB database.

   Parameters
   ----------
   pedb : :class:`pyedb.Edb`
       EDB object.
   edb_object : :class:`ansys.edb.core.layer.LayerCollection`
       EDB layer collection object.


   .. py:attribute:: core
      :value: None



   .. py:method:: create(mode: str = 'laminate') -> LayerCollection
      :classmethod:


      Create layer collection.

      Parameters
      ----------
      mode : str, optional
          layer mode. Valid values, `"laminate"`, `"overlapping"`. Default value is `"laminate"`

      Returns
      -------
      LayerCollection



   .. py:method:: update_layout()

      Update the layout with the current layer collection.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.stackup.update_layout()



   .. py:method:: add_layer_top(name: str, layer_type: str = 'signal', **kwargs) -> Union[pyedb.grpc.database.layers.layer.Layer, None]

      Add a layer on top of the stackup.

      Parameters
      ----------
      name : str
          Name of the layer.
      layer_type : str, optional
          Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
      **kwargs : dict, optional
          Additional keyword arguments. Possible keys are:
          - ``thickness`` : float, layer thickness.
          - ``material`` : str, layer material.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
          Layer object created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> top_layer = edb.stackup.add_layer_top(
      ...     "NewTopLayer", layer_type="signal", thickness="0.1mm", material="copper"
      ... )



   .. py:method:: add_layer_bottom(name: str, layer_type: str = 'signal', **kwargs) -> Union[pyedb.grpc.database.layers.layer.Layer, None]

      Add a layer at the bottom of the stackup.

      Parameters
      ----------
      name : str
          Name of the layer.
      layer_type : str, optional
          Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
      **kwargs : dict, optional
          Additional keyword arguments. Possible keys are:
          - ``thickness`` : float, layer thickness.
          - ``material`` : str, layer material.
          - ``fill_material`` : str, fill material.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
          Layer object created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> bot_layer = edb.stackup.add_layer_bottom(
      ...     "NewBottomLayer", layer_type="signal", thickness="0.1mm", material="copper"
      ... )



   .. py:method:: add_layer_below(name: str, base_layer_name: str, layer_type: str = 'signal', **kwargs) -> Union[pyedb.grpc.database.layers.layer.Layer, None]

      Add a layer below a specified layer.

      Parameters
      ----------
      name : str
          Name of the layer.
      base_layer_name : str
          Name of the base layer.
      layer_type : str, optional
          Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
      **kwargs : dict, optional
          Additional keyword arguments. Possible keys are:
          - ``thickness`` : float, layer thickness.
          - ``material`` : str, layer material.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
          Layer object created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> new_layer = edb.stackup.add_layer_below("NewLayer", "TopLayer", layer_type="dielectric", thickness="0.05mm")



   .. py:method:: add_layer_above(name: str, base_layer_name: str, layer_type: str = 'signal', **kwargs) -> Union[pyedb.grpc.database.layers.layer.Layer, None]

      Add a layer above a specified layer.

      Parameters
      ----------
      name : str
          Name of the layer.
      base_layer_name : str
          Name of the base layer.
      layer_type : str, optional
          Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
      **kwargs : dict, optional
          Additional keyword arguments. Possible keys are:
          - ``thickness`` : float, layer thickness.
          - ``material`` : str, layer material.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
          Layer object created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> new_layer = edb.stackup.add_layer_above("NewLayer", "BottomLayer", layer_type="signal", thickness="0.05mm")



   .. py:property:: non_stackup_layers
      :type: Dict[str, pyedb.grpc.database.layers.layer.Layer]


      Retrieve the dictionary of non-stackup layers.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.layer.Layer`]
          Dictionary of non-stackup layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> non_stackup = edb.stackup.non_stackup_layers



   .. py:property:: all_layers
      :type: Dict[str, pyedb.grpc.database.layers.layer.Layer]


      Retrieve all layers.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.layer.Layer`]
          Dictionary of all layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> all_layers = edb.stackup.all_layers



   .. py:property:: signal_layers
      :type: Dict[str, pyedb.grpc.database.layers.stackup_layer.StackupLayer]


      Retrieve the dictionary of signal layers.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
          Dictionary of signal layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> signal_layers = edb.stackup.signal_layers



   .. py:property:: dielectric_layers
      :type: Dict[str, pyedb.grpc.database.layers.stackup_layer.StackupLayer]


      Retrieve the dictionary of dielectric layers.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
          Dictionary of dielectric layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> dielectric_layers = edb.stackup.dielectric_layers



   .. py:property:: layers_by_id
      :type: List[List[Union[int, str]]]


      Retrieve the list of layers with their IDs.

      Returns
      -------
      list[list[int, str]]
          List of layers with their IDs and names.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> layers_by_id = edb.stackup.layers_by_id



   .. py:property:: layers
      :type: Dict[str, pyedb.grpc.database.layers.stackup_layer.StackupLayer]


      Retrieve the dictionary of stackup layers (signal and dielectric).

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
          Dictionary of stackup layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> layers = edb.stackup.layers



.. py:class:: Stackup(pedb, core=None)

   Manages EDB methods for stackup operations.

   Parameters
   ----------
   pedb : :class:`pyedb.Edb`
       EDB object.
   edb_object : :class:`ansys.edb.core.layer.LayerCollection`, optional
       EDB layer collection object. The default is ``None``.


   .. py:attribute:: core
      :value: None



   .. py:attribute:: layer_collection


   .. py:property:: signal_layers

      Retrieve the dictionary of signal layers.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
          Dictionary of signal layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> signal_layers = edb.stackup.signal_layers



   .. py:property:: dielectric_layers

      Retrieve the dictionary of dielectric layers.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
          Dictionary of dielectric layers.



   .. py:property:: layers

      Retrieve the dictionary of stackup layers (signal and dielectric).

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`]
          Dictionary of stackup layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> layers = edb.stackup.layers



   .. py:property:: non_stackup_layers

      Retrieve the dictionary of non-stackup layers.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.layer.Layer`]
          Dictionary of non-stackup layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> non_stackup = edb.stackup.non_stackup_layers



   .. py:property:: all_layers

      Retrieve all the dictionary layers.

      Returns
      -------
      dict[str, :class:`pyedb.grpc.database.layers.layer.Layer`]
          Dictionary of all layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> all_layers = edb.stackup.all_layers



   .. py:property:: thickness
      :type: float


      Retrieve the stackup thickness.

      Returns
      -------
      float
          Stackup thickness.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> thickness = edb.stackup.thickness



   .. py:property:: num_layers
      :type: int


      Retrieve the number of layers in the stackup.

      Returns
      -------
      int
          Number of layers.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> num_layers = edb.stackup.num_layers



   .. py:method:: create_symmetric_stackup(layer_count: int, inner_layer_thickness: str = '17um', outer_layer_thickness: str = '50um', dielectric_thickness: str = '100um', dielectric_material: str = 'FR4_epoxy', soldermask: bool = True, soldermask_thickness: str = '20um') -> bool

      Create a symmetric stackup.

      Parameters
      ----------
      layer_count : int
          Number of layers. Must be even.
      inner_layer_thickness : str, float, optional
          Thickness of inner conductor layer.
      outer_layer_thickness : str, float, optional
          Thickness of outer conductor layer.
      dielectric_thickness : str, float, optional
          Thickness of dielectric layer.
      dielectric_material : str, optional
          Material of dielectric layer.
      soldermask : bool, optional
          Whether to create soldermask layers. The default is ``True``.
      soldermask_thickness : str, optional
          Thickness of soldermask layer.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.stackup.create_symmetric_stackup(layer_count=4)



   .. py:property:: mode
      :type: str


      Stackup mode.

      Returns
      -------
      str
          Type of the stackup mode. Options are:
          - ``"laminate"``
          - ``"overlapping"``
          - ``"multizone"``

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> mode = edb.stackup.mode



   .. py:method:: add_outline_layer(name: str = 'Outline') -> bool

      Add an outline layer named "Outline" if it is not present.

      Returns
      -------
      bool
          ``True`` when successful.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.stackup.add_outline_layer()



   .. py:method:: add_document_layer(name: str, layer_type: str = 'user', **kwargs: Any) -> Optional[pyedb.grpc.database.layers.layer.Layer]

      Add a document layer.

      Parameters
      ----------
      name : str
          Name of the layer.
      layer_type : str, optional
          Type of the layer. The default is ``"user"``. Options are ``"user"`` and ``"outline"``.
      **kwargs : dict, optional
          Additional keyword arguments.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.layer.Layer`
          Layer object created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> outline_layer = edb.stackup.add_document_layer("Outline", layer_type="outline")



   .. py:method:: add_layer(layer_name: str, base_layer: Optional[str] = None, method: str = 'add_on_top', layer_type: str = 'signal', material: str = 'copper', filling_material: str = 'FR4_epoxy', thickness: Union[str, float] = '35um', etch_factor: Optional[float] = None, is_negative: bool = False, enable_roughness: bool = False, elevation: Optional[float] = None) -> bool

      Insert a layer into stackup.

      Parameters
      ----------
      layer_name : str
          Name of the layer.
      base_layer : str, optional
          Name of the base layer.
      method : str, optional
          Where to insert the new layer. The default is ``"add_on_top"``. Options are:
          - ``"add_on_top"``
          - ``"add_on_bottom"``
          - ``"insert_above"``
          - ``"insert_below"``
          - ``"add_at_elevation"``
      layer_type : str, optional
          Type of layer. The default is ``"signal"``. Options are:
          - ``"signal"``
          - ``"dielectric"``
          - ``"conducting"``
          - ``"air_lines"``
          - ``"error"``
          - ``"symbol"``
          - ``"measure"``
          - ``"assembly"``
          - ``"silkscreen"``
          - ``"solder_mask"``
          - ``"solder_paste"``
          - ``"glue"``
          - ``"wirebond"``
          - ``"hfss_region"``
          - ``"user"``
      material : str, optional
          Material of the layer.
      filling_material : str, optional
          Fill material of the layer.
      thickness : str, float, optional
          Thickness of the layer.
      etch_factor : int, float, optional
          Etch factor of the layer.
      is_negative : bool, optional
          Whether the layer is negative.
      enable_roughness : bool, optional
          Whether roughness is enabled.
      elevation : float, optional
          Elevation of new layer. Only valid for Overlapping Stackup.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
          Layer object created.



   .. py:method:: add_layer_top(name: str, layer_type: str = 'signal', **kwargs) -> Union[pyedb.grpc.database.layers.layer.Layer, None]

      Add a layer on top of the stackup.

      Parameters
      ----------
      name : str
          Name of the layer.
      layer_type : str, optional
          Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
      **kwargs : dict, optional
          Additional keyword arguments. Possible keys are:
          - ``thickness`` : float, layer thickness.
          - ``material`` : str, layer material.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
          Layer object created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> top_layer = edb.stackup.add_layer_top(
      ...     "NewTopLayer", layer_type="signal", thickness="0.1mm", material="copper"
      ... )



   .. py:method:: add_layer_bottom(name: str, layer_type: str = 'signal', **kwargs) -> Union[pyedb.grpc.database.layers.layer.Layer, None]

      Add a layer at the bottom of the stackup.

      Parameters
      ----------
      name : str
          Name of the layer.
      layer_type : str, optional
          Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
      **kwargs : dict, optional
          Additional keyword arguments. Possible keys are:
          - ``thickness`` : float, layer thickness.
          - ``material`` : str, layer material.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
          Layer object created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> bot_layer = edb.stackup.add_layer_bottom(
      ...     "NewBottomLayer", layer_type="signal", thickness="0.1mm", material="copper"
      ... )



   .. py:method:: add_layer_below(name: str, base_layer_name: str, layer_type: str = 'signal', **kwargs) -> Union[pyedb.grpc.database.layers.layer.Layer, None]

      Add a layer below a specified layer.

      Parameters
      ----------
      name : str
          Name of the layer.
      base_layer_name : str
          Name of the base layer.
      layer_type : str, optional
          Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
      **kwargs : dict, optional
          Additional keyword arguments. Possible keys are:
          - ``thickness`` : float, layer thickness.
          - ``material`` : str, layer material.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
          Layer object created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> new_layer = edb.stackup.add_layer_below("NewLayer", "TopLayer", layer_type="dielectric", thickness="0.05mm")



   .. py:method:: add_layer_above(name: str, base_layer_name: str, layer_type: str = 'signal', **kwargs) -> Union[pyedb.grpc.database.layers.layer.Layer, None]

      Add a layer above a specified layer.

      Parameters
      ----------
      name : str
          Name of the layer.
      base_layer_name : str
          Name of the base layer.
      layer_type : str, optional
          Type of the layer. The default is ``"signal"``. Options are ``"signal"`` and ``"dielectric"``.
      **kwargs : dict, optional
          Additional keyword arguments. Possible keys are:
          - ``thickness`` : float, layer thickness.
          - ``material`` : str, layer material.

      Returns
      -------
      :class:`pyedb.grpc.database.layers.stackup_layer.StackupLayer`
          Layer object created.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> new_layer = edb.stackup.add_layer_above("NewLayer", "BottomLayer", layer_type="signal", thickness="0.05mm")



   .. py:property:: layers_by_id
      :type: List[List[Union[int, str]]]


      Retrieve the list of layers with their IDs.

      Returns
      -------
      list[list[int, str]]
          List of layers with their IDs and names.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> layers_by_id = edb.stackup.layers_by_id



   .. py:method:: remove_layer(name: str) -> bool

      Remove a layer from stackup.

      Parameters
      ----------
      name : str
          Name of the layer to remove.

      Returns
      -------
      bool
          ``True`` when successful.



   .. py:method:: export(fpath: str, file_format: str = 'xml', include_material_with_layer: bool = False) -> bool

      Export stackup definition to a file.

      Parameters
      ----------
      fpath : str
          File path to export to.
      file_format : str, optional
          Format of the file to export. The default is ``"xml"``. Options are:
          - ``"csv"``
          - ``"xlsx"``
          - ``"json"``
          - ``"xml"``
      include_material_with_layer : bool, optional
          Whether to include the material definition inside layer objects. This parameter is only used
          when a JSON file is exported. The default is ``False``.

      Returns
      -------
      bool
          ``True`` when successful.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.stackup.export("stackup.xml")



   .. py:method:: limits(only_metals: bool = False) -> Tuple[any, any, any, any]

      Retrieve stackup limits.

      Parameters
      ----------
      only_metals : bool, optional
          Whether to retrieve only metals. The default is ``False``.

      Returns
      -------
      tuple
          Tuple containing:
          - Upper layer name
          - Upper layer top elevation
          - Lower layer name
          - Lower layer bottom elevation



   .. py:method:: flip_design() -> bool

      Flip the current design of a layout.

      Returns
      -------
      bool
          ``True`` when successful.




   .. py:method:: get_layout_thickness() -> float

      Return the layout thickness.

      Returns
      -------
      float
          Thickness value.



   .. py:method:: adjust_solder_dielectrics() -> bool

      Adjust the stack-up by adding or modifying dielectric layers that contain solder balls.

      This method identifies the solder-ball height and adjusts the dielectric thickness on top (or bottom)
      to fit the thickness in order to merge another layout.

      Returns
      -------
      bool
          ``True`` when successful.



   .. py:method:: place_in_layout(edb: pyedb.Edb, angle: float = 0.0, offset_x: float = 0.0, offset_y: float = 0.0, flipped_stackup: bool = True, place_on_top: bool = True) -> bool

      Place current cell into another cell using layer placement method.

      Flip the current layer stackup of a layout if requested.

      Parameters
      ----------
      edb : :class:`pyedb.Edb`
          Target Edb object.
      angle : float, optional
          Rotation angle in degrees. The default is ``0.0``.
      offset_x : float, optional
          X offset value. The default is ``0.0``.
      offset_y : float, optional
          Y offset value. The default is ``0.0``.
      flipped_stackup : bool, optional
          Whether to flip the current layout. The default is ``True``.
      place_on_top : bool, optional
          Whether to place the current layout on top of the destination layout. The default is ``True``.

      Returns
      -------
      bool
          ``True`` when successful.

      Examples
      --------
      >>> edb1 = Edb(edbpath=targetfile1, edbversion="2021.2")
      >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")

      >>> hosting_cmp = edb1.components.get_component_by_name("U100")
      >>> mounted_cmp = edb2.components.get_component_by_name("BGA")

      >>> vector, rotation, solder_ball_height = edb1.components.get_component_placement_vector(
      ...     mounted_component=mounted_cmp,
      ...     hosting_component=hosting_cmp,
      ...     mounted_component_pin1="A12",
      ...     mounted_component_pin2="A14",
      ...     hosting_component_pin1="A12",
      ...     hosting_component_pin2="A14",
      ... )
      >>> edb2.stackup.place_in_layout(
      ...     edb1.active_cell,
      ...     angle=0.0,
      ...     offset_x=vector[0],
      ...     offset_y=vector[1],
      ...     flipped_stackup=False,
      ...     place_on_top=True,
      ... )



   .. py:method:: place_in_layout_3d_placement(edb: pyedb.Edb, angle: float = 0.0, offset_x: float = 0.0, offset_y: float = 0.0, flipped_stackup: bool = True, place_on_top: bool = True, solder_height: float = 0) -> bool

      Place current cell into another cell using 3D placement method.

      Flip the current layer stackup of a layout if requested.

      Parameters
      ----------
      edb : :class:`pyedb.Edb`
          Target Edb object.
      angle : float, optional
          Rotation angle in degrees. The default is ``0.0``.
      offset_x : float, optional
          X offset value. The default is ``0.0``.
      offset_y : float, optional
          Y offset value. The default is ``0.0``.
      flipped_stackup : bool, optional
          Whether to flip the current layout. The default is ``True``.
      place_on_top : bool, optional
          Whether to place the current layout on top of the destination layout. The default is ``True``.
      solder_height : float, optional
          Solder ball or bumps height. This value will be added to the elevation to align the two layouts.

      Returns
      -------
      bool
          ``True`` when successful.

      Examples
      --------
      >>> edb1 = Edb(edbpath=targetfile1, edbversion="2021.2")
      >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")
      >>> hosting_cmp = edb1.components.get_component_by_name("U100")
      >>> mounted_cmp = edb2.components.get_component_by_name("BGA")
      >>> edb2.stackup.place_in_layout(
      ...     edb1.active_cell,
      ...     angle=0.0,
      ...     offset_x="1mm",
      ...     offset_y="2mm",
      ...     flipped_stackup=False,
      ...     place_on_top=True,
      ... )



   .. py:method:: place_instance(component_edb: pyedb.Edb, angle: float = 0.0, offset_x: float = 0.0, offset_y: float = 0.0, offset_z: float = 0.0, flipped_stackup: bool = True, place_on_top: bool = True, solder_height: float = 0) -> ansys.edb.core.hierarchy.cell_instance.CellInstance

      Place a component instance in the layout using 3D placement.

      Parameters
      ----------
      component_edb : :class:`pyedb.Edb`
          Component Edb object to place.
      angle : float, optional
          Rotation angle in degrees. The default is ``0.0``.
      offset_x : float, optional
          X offset value. The default is ``0.0``.
      offset_y : float, optional
          Y offset value. The default is ``0.0``.
      offset_z : float, optional
          Z offset value (elevation offset). The default is ``0.0``.
      flipped_stackup : bool, optional
          Whether to flip the component stackup. The default is ``True``.
      place_on_top : bool, optional
          Whether to place the component on top of the target layout. The default is ``True``.
      solder_height : float, optional
          Solder ball or bumps height. The default is ``0``.

      Returns
      -------
      :class:`ansys.edb.core.hierarchy.CellInstance`
          Cell instance created.



   .. py:method:: place_a3dcomp_3d_placement(a3dcomp_path: str, angle: float = 0.0, offset_x: float = 0.0, offset_y: float = 0.0, offset_z: float = 0.0, place_on_top: bool = True) -> bool

      Place a 3D component into the current layout.

      3D Component ports are not visible via EDB. They will be visible after the EDB has been opened in Ansys
      Electronics Desktop as a project.

      Parameters
      ----------
      a3dcomp_path : str
          Path to the 3D Component file (``*.a3dcomp``) to place.
      angle : float, optional
          Clockwise rotation angle applied to the a3dcomp.
      offset_x : float, optional
          X offset value. The default is ``0.0``.
      offset_y : float, optional
          Y offset value. The default is ``0.0``.
      offset_z : float, optional
          Z offset value (elevation). The default is ``0.0``.
      place_on_top : bool, optional
          Whether to place the 3D component on the top or the bottom of this layout. If ``False``, the 3D component
          will be flipped over around its X axis.

      Returns
      -------
      bool
          ``True`` if successful, ``False`` if not.

      Examples
      --------
      >>> edb1 = Edb(edbpath=targetfile1, edbversion="2021.2")
      >>> a3dcomp_path = "connector.a3dcomp"
      >>> edb1.stackup.place_a3dcomp_3d_placement(
      ...     a3dcomp_path,
      ...     angle=0.0,
      ...     offset_x="1mm",
      ...     offset_y="2mm",
      ...     flipped_stackup=False,
      ...     place_on_top=True,
      ... )



   .. py:method:: residual_copper_area_per_layer() -> Dict[str, float]

      Report residual copper area per layer in percentage.

      Returns
      -------
      dict
          Dictionary of copper area per layer.

      Examples
      --------
      >>> edb = Edb(edbpath=targetfile1, edbversion="2021.2")
      >>> edb.stackup.residual_copper_area_per_layer()



   .. py:method:: load(file_path: Union[str, Dict], rename: bool = False) -> bool

      Import stackup from a file.

      Supported formats: XML, CSV, JSON.

      Parameters
      ----------
      file_path : str or dict
          Path to stackup file or dictionary with stackup details.
      rename : bool, optional
          If ``False``, layers in layout not found in the stackup file are deleted.
          If ``True`` and the number of layers in the stackup file equals the number of stackup layers
          in the layout, layers are renamed according to the file.

      Returns
      -------
      bool
          ``True`` when successful.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.stackup.load("stackup.xml")



   .. py:method:: plot(save_plot: Optional[str] = None, size: Tuple[int, int] = (2000, 1500), plot_definitions: Optional[Union[str, List[str]]] = None, first_layer: Optional[Union[str, pyedb.grpc.database.layers.layer.Layer]] = None, last_layer: Optional[Union[str, pyedb.grpc.database.layers.layer.Layer]] = None, scale_elevation: bool = True, show: bool = True) -> Any

      Plot the current stackup and optionally overlap padstack definitions.

      Only supports 'Laminate' and 'Overlapping' stackup types.

      Parameters
      ----------
      save_plot : str, optional
          Path to save the plot image. If provided, ``show`` is ignored.
      size : tuple, optional
          Image size in pixels (width, height). Default is ``(2000, 1500)``.
      plot_definitions : str or list, optional
          List of padstack definitions to plot on the stackup. Only supported for Laminate mode.
      first_layer : str or :class:`pyedb.grpc.database.layers.layer.Layer`, optional
          First layer to plot from the bottom. Default is ``None`` (start from bottom).
      last_layer : str or :class:`pyedb.grpc.database.layers.layer.Layer`, optional
          Last layer to plot from the bottom. Default is ``None`` (plot up to top layer).
      scale_elevation : bool, optional
          Scale real layer thickness so that max_thickness = 3 * min_thickness. Default is ``True``.
      show : bool, optional
          Whether to show the plot. Default is ``True``.

      Returns
      -------
      :class:`matplotlib.pyplot`
          Matplotlib plot object.



