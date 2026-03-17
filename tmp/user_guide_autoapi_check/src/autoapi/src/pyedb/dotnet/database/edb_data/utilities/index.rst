src.pyedb.dotnet.database.edb_data.utilities
============================================

.. py:module:: src.pyedb.dotnet.database.edb_data.utilities


Classes
-------

.. autoapisummary::

   src.pyedb.dotnet.database.edb_data.utilities.EDBStatistics


Module Contents
---------------

.. py:class:: EDBStatistics

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


   .. py:property:: stackup_thickness


   .. py:property:: num_vias


   .. py:property:: occupying_ratio


   .. py:property:: occupying_surface


   .. py:property:: layout_size


   .. py:property:: num_polygons


   .. py:property:: num_traces


   .. py:property:: num_nets


   .. py:property:: num_discrete_components


   .. py:property:: num_inductors


   .. py:property:: num_capacitors


   .. py:property:: num_resistors


