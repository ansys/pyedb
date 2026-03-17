src.pyedb.dotnet.database.stackup
=================================

.. py:module:: src.pyedb.dotnet.database.stackup

.. autoapi-nested-parse::

   This module contains the `EdbStackup` class.



Attributes
----------

.. autoapisummary::

   src.pyedb.dotnet.database.stackup.logger


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.stackup.LayerCollection
   src.pyedb.dotnet.database.stackup.Stackup


Module Contents
---------------

.. py:data:: logger

.. py:class:: LayerCollection(pedb, edb_object=None)

   Bases: :py:obj:`object`


   .. py:method:: update_layout()

      Set layer collection into edb.

      Parameters
      ----------
      stackup



   .. py:method:: refresh_layer_collection()

      Refresh layer collection from Edb. This method is run on demand after all edit operations on stackup.



   .. py:method:: add_layer_top(name, layer_type='signal', **kwargs)

      Add a layer on top of the stackup.

      Parameters
      ----------
      name : str
          Name of the layer.
      layer_type: str, optional
          Type of the layer. The default to ``"signal"``. Options are ``"signal"``, ``"dielectric"``
      kwargs

      Returns
      -------




   .. py:method:: add_layer_bottom(name, layer_type='signal', **kwargs)

      Add a layer on bottom of the stackup.

      Parameters
      ----------
      name : str
          Name of the layer.
      layer_type: str, optional
          Type of the layer. The default to ``"signal"``. Options are ``"signal"``, ``"dielectric"``
      kwargs

      Returns
      -------




   .. py:method:: add_layer_below(name, base_layer_name, layer_type='signal', **kwargs)

      Add a layer below a layer.

      Parameters
      ----------
      name : str
          Name of the layer.
      base_layer_name: str
          Name of the base layer.
      layer_type: str, optional
          Type of the layer. The default to ``"signal"``. Options are ``"signal"``, ``"dielectric"``
      kwargs

      Returns
      -------




   .. py:method:: add_layer_above(name, base_layer_name, layer_type='signal', **kwargs)

      Add a layer above a layer.

      Parameters
      ----------
      name : str
          Name of the layer.
      base_layer_name: str
          Name of the base layer.
      layer_type: str, optional
          Type of the layer. The default to ``"signal"``. Options are ``"signal"``, ``"dielectric"``
      kwargs

      Returns
      -------




   .. py:method:: add_document_layer(name, layer_type='user', **kwargs)

      Add a document layer.

      Parameters
      ----------
      name : str
          Name of the layer.
      layer_type: str, optional
          Type of the layer. The default is ``"user"``. Options are ``"user"``, ``"outline"``
      kwargs

      Returns
      -------




   .. py:method:: set_layer_clone(layer_clone)


   .. py:property:: stackup_layers

      Retrieve the dictionary of signal and dielectric layers.



   .. py:property:: non_stackup_layers

      Retrieve the dictionary of signal layers.



   .. py:property:: all_layers


   .. py:property:: layers_by_id

      Retrieve the list of layers with their ids.



   .. py:property:: layers

      Retrieve the dictionary of layers.

      Returns
      -------
      Dict[str, :class:`pyedb.dotnet.database.edb_data.layer_data.LayerEdbClass`]



   .. py:method:: find_layer_by_name(name: str)

      Finds a layer with the given name.



.. py:class:: Stackup(pedb, edb_object=None)

   Bases: :py:obj:`LayerCollection`


   Manages EDB methods for stackup accessible from `Edb.stackup` property.


   .. py:property:: layer_types

      Layer types.

      Returns
      -------
      type
          Types of layers.



   .. py:property:: thickness

      Retrieve Stackup thickness.

      Returns
      -------
      float
          Layout stackup thickness.




   .. py:property:: num_layers

      Retrieve the stackup layer number.

      Returns
      -------
      int
          layer number.




   .. py:method:: create_symmetric_stackup(layer_count, inner_layer_thickness='17um', outer_layer_thickness='50um', dielectric_thickness='100um', dielectric_material='FR4_epoxy', soldermask=True, soldermask_thickness='20um')

      Create a symmetric stackup.

      Parameters
      ----------
      layer_count : int
          Number of layer count.
      inner_layer_thickness : str, float, optional
          Thickness of inner conductor layer.
      outer_layer_thickness : str, float, optional
          Thickness of outer conductor layer.
      dielectric_thickness : str, float, optional
          Thickness of dielectric layer.
      dielectric_material : str, optional
          Material of dielectric layer.
      soldermask : bool, optional
          Whether to create soldermask layers. The default is``True``.
      soldermask_thickness : str, optional
          Thickness of soldermask layer.

      Returns
      -------
      bool



   .. py:property:: mode

      Stackup mode.

      Returns
      -------
      int, str
          Type of the stackup mode, where:

          * 0 - Laminate
          * 1 - Overlapping
          * 2 - MultiZone



   .. py:property:: signal_layers

      Retrieve the dictionary of signal layers.

      Returns
      -------
      Dict[str, :class:`pyedb.dotnet.database.edb_data.layer_data.LayerEdbClass`]



   .. py:property:: dielectric_layers

      Dielectric layers.

      Returns
      -------
      dict[str, :class:`dotnet.database.edb_data.layer_data.EDBLayer`]
          Dictionary of dielectric layers.



   .. py:method:: add_outline_layer(outline_name='Outline')

      Add an outline layer named ``"Outline"`` if it is not present.

      Returns
      -------
      bool
          "True" if successful, ``False`` if failed.



   .. py:method:: add_layer(layer_name, base_layer=None, method='add_on_top', layer_type='signal', material='copper', fillMaterial='FR4_epoxy', thickness='35um', etch_factor=None, is_negative=False, enable_roughness=False, elevation=None)

      Insert a layer into stackup.

      Parameters
      ----------
      layer_name : str
          Name of the layer.
      base_layer : str, optional
          Name of the base layer.
      method : str, optional
          Where to insert the new layer. The default is ``"add_on_top"``. Options are ``"add_on_top"``,
          ``"add_on_bottom"``, ``"insert_above"``, ``"insert_below"``, ``"add_at_elevation"``,.
      layer_type : str, optional
          Type of layer. The default is ``"signal"``. Options are ``"signal"``, ``"dielectric"``, ``"conducting"``,
           ``"air_lines"``, ``"error"``, ``"symbol"``, ``"measure"``, ``"assembly"``, ``"silkscreen"``,
           ``"solder_mask"``, ``"solder_paste"``, ``"glue"``, ``"wirebond"``, ``"hfss_region"``, ``"user"``.
      material : str, optional
          Material of the layer.
      fillMaterial : str, optional
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
      :class:`pyedb.dotnet.database.edb_data.layer_data.LayerEdbClass`



   .. py:method:: remove_layer(name)

      Remove a layer from stackup.

      Parameters
      ----------
      name : str
          Name of the layer to remove.

      Returns
      -------




   .. py:method:: export(fpath, file_format='xml', include_material_with_layer=False)

      Export stackup definition to a CSV or JSON file.

      Parameters
      ----------
      fpath : str
          File path to csv or json file.
      file_format : str, optional
          Format of the file to export. The default is ``"csv"``. Options are ``"csv"``, ``"xlsx"``,
          ``"json"``.
      include_material_with_layer : bool, optional.
          Whether to include the material definition inside layer ones. This parameter is only used
          when a JSON file is exported. The default is ``False``, which keeps the material definition
          section in the JSON file. If ``True``, the material definition is included inside the layer ones.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.stackup.export("stackup.xml")



   .. py:method:: limits(only_metals=False)

      Retrieve stackup limits.

      Parameters
      ----------
      only_metals : bool, optional
          Whether to retrieve only metals. The default is ``False``.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



   .. py:method:: flip_design()

      Flip the current design of a layout.

      Returns
      -------
      bool
          ``True`` when succeed ``False`` if not.

      Examples
      --------
      >>> edb = Edb(edbpath=targetfile, edbversion="2021.2")
      >>> edb.stackup.flip_design()
      >>> edb.save()
      >>> edb.close_edb()



   .. py:method:: get_layout_thickness()

      Return the layout thickness.

      Returns
      -------
      float
          The thickness value.



   .. py:method:: adjust_solder_dielectrics()

      Adjust the stack-up by adding or modifying dielectric layers that contains Solder Balls.
      This method identifies the solder-ball height and adjust the dielectric thickness on top (or bottom) to fit
      the thickness in order to merge another layout.

      Returns
      -------
      bool



   .. py:method:: place_in_layout(edb, angle=0.0, offset_x=0.0, offset_y=0.0, flipped_stackup=True, place_on_top=True)

      Place current Cell into another cell using layer placement method.
      Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

      Parameters
      ----------
      edb : Edb
          Cell on which to place the current layout. If None the Cell will be applied on an empty new Cell.
      angle : double, optional
          The rotation angle applied on the design.
      offset_x : double, optional
          The x offset value.
      offset_y : double, optional
          The y offset value.
      flipped_stackup : bool, optional
          Either if the current layout is inverted.
          If `True` and place_on_top is `True` the stackup will be flipped before the merge.
      place_on_top : bool, optional
          Either if place the current layout on Top or Bottom of destination Layout.

      Returns
      -------
      bool
          ``True`` when succeed ``False`` if not.

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



   .. py:method:: place_in_layout_3d_placement(edb, angle=0.0, offset_x=0.0, offset_y=0.0, flipped_stackup=True, place_on_top=True, solder_height=0)

      Place current Cell into another cell using 3d placement method.
      Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

      Parameters
      ----------
      edb : Edb
          Cell on which to place the current layout. If None the Cell will be applied on an empty new Cell.
      angle : double, optional
          The rotation angle applied on the design.
      offset_x : double, optional
          The x offset value.
      offset_y : double, optional
          The y offset value.
      flipped_stackup : bool, optional
          Either if the current layout is inverted.
          If `True` and place_on_top is `True` the stackup will be flipped before the merge.
      place_on_top : bool, optional
          Either if place the current layout on Top or Bottom of destination Layout.
      solder_height : float, optional
          Solder Ball or Bumps eight.
          This value will be added to the elevation to align the two layouts.

      Returns
      -------
      bool
          ``True`` when succeed ``False`` if not.

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



   .. py:method:: place_instance(component_edb, angle=0.0, offset_x=0.0, offset_y=0.0, offset_z=0.0, flipped_stackup=True, place_on_top=True, solder_height=0)

      Place current Cell into another cell using 3d placement method.
      Flip the current layer stackup of a layout if requested. Transform parameters currently not supported.

      Parameters
      ----------
      component_edb : Edb
          Cell to place in the current layout.
      angle : double, optional
          The rotation angle applied on the design.
      offset_x : double, optional
          The x offset value.
          The default value is ``0.0``.
      offset_y : double, optional
          The y offset value.
          The default value is ``0.0``.
      offset_z : double, optional
          The z offset value. (i.e. elevation offset for placement relative to the top layer conductor).
          The default value is ``0.0``, which places the cell layout on top of the top conductor
          layer of the target EDB.
      flipped_stackup : bool, optional
          Either if the current layout is inverted.
          If `True` and place_on_top is `True` the stackup will be flipped before the merge.
      place_on_top : bool, optional
          Either if place the component_edb layout on Top or Bottom of destination Layout.
      solder_height : float, optional
          Solder Ball or Bumps eight.
          This value will be added to the elevation to align the two layouts.

      Returns
      -------
      bool
          ``True`` when succeed ``False`` if not.

      Examples
      --------
      >>> edb1 = Edb(edbpath=targetfile1, edbversion="2021.2")
      >>> edb2 = Edb(edbpath=targetfile2, edbversion="2021.2")
      >>> hosting_cmp = edb1.components.get_component_by_name("U100")
      >>> mounted_cmp = edb2.components.get_component_by_name("BGA")
      >>> edb1.stackup.place_instance(
      ...     edb2,
      ...     angle=0.0,
      ...     offset_x="1mm",
      ...     offset_y="2mm",
      ...     flipped_stackup=False,
      ...     place_on_top=True,
      ... )



   .. py:method:: place_a3dcomp_3d_placement(a3dcomp_path, angle=0.0, offset_x=0.0, offset_y=0.0, offset_z=0.0, place_on_top=True)

      Place a 3D Component into current layout.
       3D Component ports are not visible via EDB. They will be visible after the EDB has been opened in Ansys
       Electronics Desktop as a project.

      Parameters
      ----------
      a3dcomp_path : str
          Path to the 3D Component file (\*.a3dcomp) to place.
      angle : double, optional
          Clockwise rotation angle applied to the a3dcomp.
      offset_x : double, optional
          The x offset value.
          The default value is ``0.0``.
      offset_y : double, optional
          The y offset value.
          The default value is ``0.0``.
      offset_z : double, optional
          The z offset value. (i.e. elevation)
          The default value is ``0.0``.
      place_on_top : bool, optional
          Whether to place the 3D Component on the top or the bottom of this layout.
          If ``False`` then the 3D Component will also be flipped over around its X axis.

      Returns
      -------
      bool
          ``True`` if successful and ``False`` if not.

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



   .. py:method:: residual_copper_area_per_layer()

      Report residual copper area per layer in percentage.

      Returns
      -------
      dict
          Copper area per layer.

      Examples
      --------
      >>> edb = Edb(edbpath=targetfile1, edbversion="2021.2")
      >>> edb.stackup.residual_copper_area_per_layer()



   .. py:method:: load(file_path, rename=False)

      Import stackup from a file. The file format can be XML, CSV, or JSON. Valid control file must
      have the same number of signal layers. Signals layers can be renamed. Dielectric layers can be
      added and deleted.


      Parameters
      ----------
      file_path : str, dict
          Path to stackup file or dict with stackup details.
      rename : bool
          If rename is ``False`` then layer in layout not found in the stackup file are deleted.
          Otherwise, if the number of layer in the stackup file equals the number of stackup layer
          in the layout, layers are renamed according the file.
          Note that layer order matters, and has to be writtent from top to bottom layer in the file.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.

      Examples
      --------
      >>> from pyedb import Edb
      >>> edb = Edb()
      >>> edb.stackup.load("stackup.xml")



   .. py:method:: plot(save_plot=None, size=(2000, 1500), plot_definitions=None, first_layer=None, last_layer=None, scale_elevation=True, show=True)

      Plot current stackup and, optionally, overlap padstack definitions.
      Plot supports only 'Laminate' and 'Overlapping' stackup types.

      Parameters
      ----------
      save_plot : str, optional
          If a path is specified the plot will be saved in this location.
          If ``save_plot`` is provided, the ``show`` parameter is ignored.
      size : tuple, optional
          Image size in pixel (width, height). Default value is ``(2000, 1500)``
      plot_definitions : str, list, optional
          List of padstack definitions to plot on the stackup.
          It is supported only for Laminate mode.
      first_layer : str or :class:`pyedb.dotnet.database.edb_data.layer_data.LayerEdbClass`
          First layer to plot from the bottom. Default is `None` to start plotting from bottom.
      last_layer : str or :class:`pyedb.dotnet.database.edb_data.layer_data.LayerEdbClass`
          Last layer to plot from the bottom. Default is `None` to plot up to top layer.
      scale_elevation : bool, optional
          The real layer thickness is scaled so that max_thickness = 3 * min_thickness.
          Default is `True`.
      show : bool, optional
          Whether to show the plot or not. Default is `True`.

      Returns
      -------
      :class:`matplotlib.plt`



   .. py:method:: load_from_xml(file_path)

      Load stackup from a XML file.

      Parameters
      ----------
      file_path: str
          Path to external XML file.

      Returns
      -------
      bool
          ``True`` when successful, ``False`` when failed.



