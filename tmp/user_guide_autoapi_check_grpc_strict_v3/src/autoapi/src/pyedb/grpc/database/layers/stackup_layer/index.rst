src.pyedb.grpc.database.layers.stackup_layer
============================================

.. py:module:: src.pyedb.grpc.database.layers.stackup_layer


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.layers.stackup_layer.StackupLayer


Module Contents
---------------

.. py:class:: StackupLayer(pedb, core=None)

   .. py:attribute:: core
      :value: None



   .. py:method:: create(layout: pyedb.grpc.database.layout.layout.Layout, name: str, layer_type: str = 'signal', thickness: Union[str, float] = '17um', elevation: Union[str, float] = 0.0, material: str = 'copper') -> StackupLayer
      :classmethod:



   .. py:property:: id

      Layer ID.

      Returns
      -------
      int
          Layer ID.



   .. py:property:: type
      :type: str


      Layer type.

      Returns
      -------
      str
          Layer name.



   .. py:method:: update(**kwargs)


   .. py:property:: lower_elevation
      :type: float


      Lower elevation.

      Returns
      -------
      float
          Lower elevation.



   .. py:property:: fill_material
      :type: Union[str, None]


      The layer's fill material.

      Returns
      -------
      str
          Material name.



   .. py:property:: upper_elevation
      :type: float


      Upper elevation.

      Returns
      -------
      float
          Upper elevation.



   .. py:property:: is_negative
      :type: bool


      Determine whether this layer is a negative layer.

      Returns
      -------
      bool
          True if this layer is a negative layer, False otherwise.



   .. py:property:: name
      :type: str


      Layer name.

      Returns
      -------
      str
          Layer name.




   .. py:property:: is_stackup_layer
      :type: bool


      Testing if layer is stackup layer.

      Returns
      -------
      `True` if layer type is "signal" or "dielectric".



   .. py:property:: material
      :type: str


      Material.

      Returns
      -------
      str
          Material name.



   .. py:property:: conductivity
      :type: float


      Material conductivity.

      Returns
      -------
      float
          Material conductivity value.



   .. py:property:: permittivity
      :type: float


      Material permittivity.

      Returns
      -------
      float
          Material permittivity value.



   .. py:property:: loss_tangent
      :type: float


      Material loss_tangent.

      Returns
      -------
      float
          Material loss tangent value.



   .. py:property:: dielectric_fill
      :type: Union[str, None]


      Material name of the layer dielectric fill.

      Returns
      -------
      str
          Material name.



   .. py:property:: thickness
      :type: float


      Layer thickness.

      Returns
      -------
      float
          Layer thickness.



   .. py:property:: etch_factor_enabled
      :type: bool


      Layer etching factor enable flag.

      Returns
      -------
      bool
          Etching factor flag.



   .. py:property:: etch_factor
      :type: float


      Layer etching factor.

      Returns
      -------
      float
          Etching factor value.



   .. py:property:: top_hallhuray_nodule_radius
      :type: float


      Huray model nodule radius on layer top.

      Returns
      -------
      float
          Nodule radius value.



   .. py:property:: top_hallhuray_surface_ratio
      :type: float


      Huray model surface ratio on layer top.

      Returns
      -------
      float
          Surface ratio.



   .. py:property:: bottom_hallhuray_nodule_radius
      :type: float


      Huray model nodule radius on layer bottom.

      Returns
      -------
      float
          Nodule radius.



   .. py:property:: bottom_hallhuray_surface_ratio
      :type: float


      Huray model surface ratio on layer bottom.

      Returns
      -------
      float
          Surface ratio value.



   .. py:property:: side_hallhuray_nodule_radius
      :type: float


      Huray model nodule radius on layer sides.

      Returns
      -------
      float
          Nodule radius value.




   .. py:property:: side_hallhuray_surface_ratio
      :type: float


      Huray model surface ratio on layer sides.

      Returns
      -------
      float
          surface ratio.



   .. py:property:: top_groisse_roughness
      :type: float


      Groisse model on layer top.

      Returns
      -------
      float
          Roughness value.



   .. py:property:: bottom_groisse_roughness
      :type: float


      Groisse model on layer bottom.

      Returns
      -------
      float
          Roughness value.



   .. py:property:: side_groisse_roughness
      :type: float


      Groisse model on layer bottom.

      Returns
      -------
      float
          Roughness value.



   .. py:property:: color
      :type: tuple[int, int, int]


      Layer color.

      Returns
      -------
      str
          Layer color in hex format.



   .. py:property:: transparency
      :type: int


      Layer transparency.

      Returns
      -------
      float
          Layer transparency value between 0 and 100.



   .. py:property:: top_rouhness_model_type
      :type: str


      Roughness model type on layer top.

      Returns
      -------
      str
          Roughness model type. Options are "huray", "groisse", or "none".



   .. py:property:: bottom_rouhness_model_type
      :type: str


      Roughness model type on layer bottom.

      Returns
      -------
      str
          Roughness model type. Options are "huray", "groisse", or "none".



   .. py:property:: side_rouhness_model_type
      :type: str


      Roughness model type on layer sides.

      Returns
      -------
      str
          Roughness model type. Options are "huray", "groisse", or "none".



   .. py:method:: get_roughness_model_type(location=None) -> str

      Roughness model type.

      Parameters
      ----------
      location : str, optional
          Location of roughness model. The default is None, which returns the roughness model type on the top surface.
          Options are "top", "bottom", "side".

      Returns
      -------
      str
          Roughness model type. Options are "huray", "groisse", or "none".



   .. py:property:: roughness_enabled
      :type: bool


      Roughness model enabled status.

      Returns
      -------
      bool
          True if roughness model is enabled, False otherwise.



   .. py:method:: assign_roughness_model(model_type='huray', huray_radius='0.5um', huray_surface_ratio='2.9', groisse_roughness='1um', apply_on_surface='all') -> bool

      Assign roughness model on this layer.

      Parameters
      ----------
      model_type : str, optional
          Type of roughness model. The default is ``"huray"``. Options are ``"huray"``, ``"groisse"``.
      huray_radius : str, float, optional
          Radius of huray model. The default is ``"0.5um"``.
      huray_surface_ratio : str, float, optional.
          Surface ratio of huray model. The default is ``"2.9"``.
      groisse_roughness : str, float, optional
          Roughness of groisse model. The default is ``"1um"``.
      apply_on_surface : str, optional.
          Where to assign roughness model. The default is ``"all"``. Options are ``"top"``, ``"bottom"``,
           ``"side"``.

      Returns
      -------
      bool



   .. py:property:: properties
      :type: dict[str, dict[str, str]] | bool



