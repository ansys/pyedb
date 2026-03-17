src.pyedb.grpc.database.utility.layout_statistics
=================================================

.. py:module:: src.pyedb.grpc.database.utility.layout_statistics


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.utility.layout_statistics.LayoutStatistics


Module Contents
---------------

.. py:class:: LayoutStatistics

   Bases: :py:obj:`object`


   Statistics object

   Object properties example.
   >>> stat_model = EDBStatistics()
   >>> stat_model.num_capacitors
   >>> stat_model.num_resistors
   >>> stat_model.num_inductors
   >>> stat_model.layout_size
   >>> stat_model.num_discrete_components
   >>> stat_model.num_inductors
   >>> stat_model.num_resistors
   >>> stat_model.num_capacitors
   >>> stat_model.num_nets
   >>> stat_model.num_traces
   >>> stat_model.num_polygons
   >>> stat_model.num_vias
   >>> stat_model.stackup_thickness
   >>> stat_model.occupying_surface
   >>> stat_model.occupying_ratio


   .. py:property:: num_layers
      :type: int


      Layer number.

      Returns
      -------
      int
          Number of layers.




   .. py:property:: stackup_thickness
      :type: float


      Stackup total thickness.

      Returns
      -------
      float
          Stack up total thickness value.




   .. py:property:: num_vias
      :type: int


      Via number.

      Returns
      -------
      int
          Total number of vias.




   .. py:property:: occupying_ratio
      :type: float


      Occupying ratio.

      Returns
      -------
      float
          Occupying ration value.
          Value representing metal coverage versus total layout surface.




   .. py:property:: occupying_surface
      :type: bool


      Occupying surface.

      Returns
      -------
      float
          Occupying surface value.




   .. py:property:: layout_size
      :type: list[float]


      Layout size.

      Returns
      -------
      List[(float, float), (float, float)]
          Layout bounding box, lower left corner (x, y) upper right corner (x, y).




   .. py:property:: num_polygons
      :type: int


      Polygon number.

      Returns
      -------
      int
          Total number of polygons.




   .. py:property:: num_traces
      :type: int


      Trace number.

      Returns
      -------
      int
          Total number of traces.




   .. py:property:: num_nets
      :type: int


      Net number.

      Returns
      -------
      int
          Total number og nets.




   .. py:property:: num_discrete_components
      :type: int


      Discrete component number.

      Returns
      -------
      int
          Total number of discrete components.




   .. py:property:: num_inductors
      :type: int


      Inductor number.

      Returns
      -------
      int
          Total number of inductors.




   .. py:property:: num_capacitors
      :type: int


      Capacitor number.

      Returns
      -------
      int
          Total number of capacitors.




   .. py:property:: num_resistors
      :type: int


      Resistor number.

      Returns
      -------
      int
          Total number of resistors.




