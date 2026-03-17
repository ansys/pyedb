src.pyedb.extensions.via_design_backend
=======================================

.. py:module:: src.pyedb.extensions.via_design_backend


Classes
-------

.. autoapisummary::

   src.pyedb.extensions.via_design_backend.StitchingVias
   src.pyedb.extensions.via_design_backend.Trace
   src.pyedb.extensions.via_design_backend.GroundVia
   src.pyedb.extensions.via_design_backend.Via
   src.pyedb.extensions.via_design_backend.Signal
   src.pyedb.extensions.via_design_backend.DiffSignal
   src.pyedb.extensions.via_design_backend.Board
   src.pyedb.extensions.via_design_backend.ViaDesignBackend


Functions
---------

.. autoapisummary::

   src.pyedb.extensions.via_design_backend.create_variable


Module Contents
---------------

.. py:function:: create_variable(obj, name_suffix, value)

.. py:class:: StitchingVias(p_via, start_angle, step_angle, number_of_vias, distance, clockwise=True)

   .. py:attribute:: p_via


   .. py:attribute:: name


   .. py:attribute:: start_angle


   .. py:attribute:: step_angle


   .. py:attribute:: number_of_vias


   .. py:attribute:: distance


   .. py:attribute:: clockwise
      :value: True



   .. py:attribute:: vias
      :value: []



   .. py:method:: populate_config(cfg)


.. py:class:: Trace(p_via, name, net_name, layer, width, clearance, incremental_path: list[list], flip_dx, flip_dy, end_cap_style, port: Union[dict, None])

   .. py:attribute:: p_via


   .. py:attribute:: variables
      :value: []



   .. py:attribute:: name


   .. py:attribute:: net_name


   .. py:attribute:: layer


   .. py:attribute:: width


   .. py:attribute:: clearance


   .. py:attribute:: flip_dx


   .. py:attribute:: flip_dy


   .. py:attribute:: end_cap_style


   .. py:attribute:: port


   .. py:attribute:: incremental_path


   .. py:attribute:: path


   .. py:method:: populate_config(cfg)


   .. py:method:: get_port_cfg()


.. py:class:: GroundVia(p_signal, name, net_name, padstack_def, start_layer, stop_layer, base_x, base_y, dx, dy, flip_dx, flip_dy, connection_trace: Union[dict, Trace], with_solder_ball, backdrill_parameters, conductor_layers: list, **kwargs)

   .. py:property:: x


   .. py:property:: y


   .. py:attribute:: p_signal


   .. py:attribute:: variables
      :value: []



   .. py:attribute:: name


   .. py:attribute:: net_name


   .. py:attribute:: padstack_def


   .. py:attribute:: start_layer


   .. py:attribute:: stop_layer


   .. py:attribute:: base_x


   .. py:attribute:: base_y


   .. py:attribute:: flip_dx


   .. py:attribute:: flip_dy


   .. py:attribute:: dx


   .. py:attribute:: dy


   .. py:attribute:: with_solder_ball


   .. py:attribute:: backdrill_parameters


   .. py:attribute:: conductor_layers


   .. py:attribute:: traces
      :value: []



   .. py:attribute:: fanout_traces
      :value: []



   .. py:method:: populate_config(cfg)


.. py:class:: Via(anti_pad_diameter, fanout_trace: list[Union[dict, Trace]], stitching_vias: Union[dict, None], **kwargs)

   Bases: :py:obj:`GroundVia`


   .. py:attribute:: anti_pad_diameter


   .. py:attribute:: stitching_vias


   .. py:method:: populate_config(cfg)


.. py:class:: Signal(p_board, signal_name, name_suffix: Union[None, str], base_x, base_y, stacked_vias, flip_x, flip_y)

   vias and traces.


   .. py:attribute:: p_board


   .. py:attribute:: net_name


   .. py:attribute:: name_suffix


   .. py:attribute:: base_x


   .. py:attribute:: base_y


   .. py:attribute:: vias
      :value: []



   .. py:method:: populate_config(cfg_modeler)


.. py:class:: DiffSignal(p_board, name, signals, fanout_trace, stacked_vias)

   .. py:attribute:: p_board


   .. py:attribute:: name


   .. py:attribute:: fanout_trace


   .. py:attribute:: stacked_vias


   .. py:attribute:: variables
      :value: []



   .. py:attribute:: diff_ports
      :value: []



   .. py:attribute:: signal_p


   .. py:attribute:: signal_n


   .. py:method:: populate_config(cfg)


.. py:class:: Board(stackup, padstack_defs, outline_extent, pitch, pin_map, signals, differential_signals)

   .. py:property:: conductor_layers


   .. py:attribute:: voids
      :value: []



   .. py:attribute:: variables


   .. py:attribute:: stackup


   .. py:attribute:: padstack_defs


   .. py:attribute:: outline_extent


   .. py:attribute:: pin_map


   .. py:attribute:: signals
      :value: []



   .. py:attribute:: differential_signals
      :value: []



   .. py:method:: get_signal_location(signal_name)


   .. py:method:: parser_signals(data)


   .. py:method:: parser_differential_signals(data)


   .. py:method:: populate_config(cfg)


.. py:class:: ViaDesignBackend(cfg, grpc=False)

   .. py:property:: output_dir


   .. py:attribute:: version


   .. py:attribute:: app
      :value: None



