src.pyedb.configuration.cfg_modeler
===================================

.. py:module:: src.pyedb.configuration.cfg_modeler


Classes
-------

.. autoapisummary::

   src.pyedb.configuration.cfg_modeler.CfgTrace
   src.pyedb.configuration.cfg_modeler.CfgPlane
   src.pyedb.configuration.cfg_modeler.PrimitivesToDeleteDict
   src.pyedb.configuration.cfg_modeler.CfgModeler


Module Contents
---------------

.. py:class:: CfgTrace

   .. py:attribute:: name
      :type:  str


   .. py:attribute:: layer
      :type:  str


   .. py:attribute:: path
      :type:  List[List[Union[float, str]]]


   .. py:attribute:: width
      :type:  str


   .. py:attribute:: net_name
      :type:  str


   .. py:attribute:: start_cap_style
      :type:  str


   .. py:attribute:: end_cap_style
      :type:  str


   .. py:attribute:: corner_style
      :type:  str


   .. py:attribute:: incremental_path
      :type:  List[List[Union[float, str]]]


.. py:class:: CfgPlane

   .. py:attribute:: name
      :type:  str
      :value: ''



   .. py:attribute:: layer
      :type:  str
      :value: ''



   .. py:attribute:: net_name
      :type:  str
      :value: ''



   .. py:attribute:: type
      :type:  str
      :value: 'rectangle'



   .. py:attribute:: lower_left_point
      :type:  List[Union[float, str]]
      :value: []



   .. py:attribute:: upper_right_point
      :type:  List[Union[float, str]]
      :value: []



   .. py:attribute:: corner_radius
      :type:  Union[float, str]
      :value: 0



   .. py:attribute:: rotation
      :type:  Union[float, str]
      :value: 0



   .. py:attribute:: voids
      :type:  List[Any]
      :value: []



   .. py:attribute:: points
      :type:  List[List[float]]
      :value: []



   .. py:attribute:: radius
      :type:  Union[float, str]
      :value: 0



   .. py:attribute:: position
      :type:  List[float]
      :value: [0, 0]



.. py:class:: PrimitivesToDeleteDict

   Bases: :py:obj:`TypedDict`


   dict() -> new empty dictionary
   dict(mapping) -> new dictionary initialized from a mapping object's
       (key, value) pairs
   dict(iterable) -> new dictionary initialized as if via:
       d = {}
       for k, v in iterable:
           d[k] = v
   dict(**kwargs) -> new dictionary initialized with the name=value pairs
       in the keyword argument list.  For example:  dict(one=1, two=2)


   .. py:attribute:: layer_name
      :type:  List[str]


   .. py:attribute:: name
      :type:  List[str]


   .. py:attribute:: net_name
      :type:  List[str]


.. py:class:: CfgModeler(pedb, data: Dict)

   Manage configuration general settings.


   .. py:attribute:: traces
      :type:  List[CfgTrace]
      :value: []



   .. py:attribute:: planes
      :type:  List[CfgPlane]
      :value: []



   .. py:attribute:: padstack_defs


   .. py:attribute:: padstack_instances


   .. py:attribute:: components


   .. py:attribute:: primitives_to_delete
      :type:  PrimitivesToDeleteDict


   .. py:method:: add_trace(layer: str, width: str, name: str, net_name: str = '', start_cap_style: str = 'round', end_cap_style: str = 'round', corner_style: str = 'sharp', path: Optional[Any] = None, incremental_path: Optional[Any] = None)

      Add a trace from a dictionary of parameters.



   .. py:method:: add_rectangular_plane(layer: str, name: str = '', net_name: str = '', lower_left_point: List[float] = '', upper_right_point: List[float] = '', corner_radius: float = 0, rotation: float = 0, voids: Optional[List[Any]] = '')


   .. py:method:: add_circular_plane(layer: str, name: str = '', net_name: str = '', corner_radius: float = 0, rotation: float = 0, voids: Optional[List[Any]] = '', radius: Union[float, str] = 0, position: List[Union[float, str]] = '')


   .. py:method:: add_polygon_plane(layer: str, name: str = '', net_name: str = '', corner_radius: float = 0, rotation: float = 0, voids: Optional[List[Any]] = '', points: List[List[float]] = '')


