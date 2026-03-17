src.pyedb.dotnet.database.edb_data.layer_data
=============================================

.. py:module:: src.pyedb.dotnet.database.edb_data.layer_data


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.layer_data.LayerEdbClass
   src.pyedb.dotnet.database.edb_data.layer_data.StackupLayerEdbClass


Functions
---------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.layer_data.layer_cast


Module Contents
---------------

.. py:function:: layer_cast(pedb, edb_object)

.. py:class:: LayerEdbClass(pedb, edb_object=None, name='', layer_type='undefined', **kwargs)

   Bases: :py:obj:`object`


   Manages Edb Layers. Replaces EDBLayer.


   .. py:method:: update(**kwargs)


   .. py:property:: id


   .. py:property:: fill_material

      The layer's fill material.



   .. py:property:: is_stackup_layer

      Determine whether this layer is a stackup layer.

      Returns
      -------
      bool
          True if this layer is a stackup layer, False otherwise.



   .. py:property:: is_via_layer

      Determine whether this layer is a via layer.

      Returns
      -------
      bool
          True if this layer is a via layer, False otherwise.



   .. py:property:: color

      Color of the layer.

      Returns
      -------
      tuple
          RGB.



   .. py:property:: transparency

      Retrieve transparency of the layer.

      Returns
      -------
      int
          An integer between 0 and 100 with 0 being fully opaque and 100 being fully transparent.



   .. py:property:: name

      Retrieve name of the layer.

      Returns
      -------
      str



   .. py:property:: type

      Retrieve type of the layer.



   .. py:property:: properties


.. py:class:: StackupLayerEdbClass(pedb, edb_object=None, name='', layer_type='signal', **kwargs)

   Bases: :py:obj:`LayerEdbClass`


   Manages Edb Layers. Replaces EDBLayer.


   .. py:attribute:: core
      :value: None



   .. py:property:: lower_elevation

      Lower elevation.

      Returns
      -------
      float
          Lower elevation.



   .. py:property:: upper_elevation

      Upper elevation.

      Returns
      -------
      float
          Upper elevation.



   .. py:property:: is_negative

      Determine whether this layer is a negative layer.

      Returns
      -------
      bool
          True if this layer is a negative layer, False otherwise.



   .. py:property:: material

      Get/Set the material loss_tangent.

      Returns
      -------
      float



   .. py:property:: conductivity

      Get the material conductivity.

      Returns
      -------
      float



   .. py:property:: permittivity

      Get the material permittivity.

      Returns
      -------
      float



   .. py:property:: loss_tangent

      Get the material loss_tangent.

      Returns
      -------
      float



   .. py:property:: dielectric_fill

      Retrieve material name of the layer dielectric fill.



   .. py:property:: thickness

      Retrieve thickness of the layer.

      Returns
      -------
      float



   .. py:property:: etch_factor

      Retrieve etch factor of this layer.

      Returns
      -------
      float



   .. py:property:: roughness_enabled

      Determine whether roughness is enabled on this layer.

      Returns
      -------
      bool



   .. py:property:: top_hallhuray_nodule_radius

      Retrieve huray model nodule radius on top of the conductor.



   .. py:property:: top_hallhuray_surface_ratio

      Retrieve huray model surface ratio on top of the conductor.



   .. py:property:: bottom_hallhuray_nodule_radius

      Retrieve huray model nodule radius on bottom of the conductor.



   .. py:property:: bottom_hallhuray_surface_ratio

      Retrieve huray model surface ratio on bottom of the conductor.



   .. py:property:: side_hallhuray_nodule_radius

      Retrieve huray model nodule radius on sides of the conductor.



   .. py:property:: side_hallhuray_surface_ratio

      Retrieve huray model surface ratio on sides of the conductor.



   .. py:method:: get_roughness_model(surface='top')

      Get roughness model of the layer.

      Parameters
      ----------
      surface : str, optional
          Where to fetch roughness model. The default is ``"top"``. Options are ``"top"``, ``"bottom"``, ``"side"``.

      Returns
      -------
      ``"Ansys.Ansoft.Edb.Cell.RoughnessModel"``




   .. py:method:: assign_roughness_model(model_type='huray', huray_radius='0.5um', huray_surface_ratio='2.9', groisse_roughness='1um', apply_on_surface='all')

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




   .. py:property:: properties


