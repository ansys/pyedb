src.pyedb.grpc.database.hierarchy.pin_pair_model
================================================

.. py:module:: src.pyedb.grpc.database.hierarchy.pin_pair_model


Classes
-------

.. autoapisummary::

   src.pyedb.grpc.database.hierarchy.pin_pair_model.PinPair
   src.pyedb.grpc.database.hierarchy.pin_pair_model.PinPairModel


Module Contents
---------------

.. py:class:: PinPair(model, edb_pin_pair)

   .. py:attribute:: core


   .. py:property:: first_pin
      :type: str


      First pin name.

      This attribute is read-only since pin pair model is defined between two pins,
      and changing pin names will change the pin pair itself.

      Returns
      -------
      str
          First pin name.




   .. py:property:: second_pin
      :type: str


      Second pin name.

      This attribute is read-only since pin pair model is defined between two pins,
      and changing pin names will change the pin pair itself.

      Returns
      -------
      str
          Second pin name.




   .. py:property:: rlc_enable
      :type: tuple[bool, bool, bool]


      Enable model.

      Returns
      -------
      tuple[r_enabled(bool), l_enabled(bool), c_enabled(bool)].




   .. py:property:: resistance
      :type: float


      Resistance.

      Returns
      -------
      float
          Resistance value.




   .. py:property:: inductance
      :type: float


      Inductance.

      Returns
      -------
      float
          Inductance value.




   .. py:property:: capacitance
      :type: float


      Capacitance.

      Returns
      -------
      float
          Capacitance value.




   .. py:property:: rlc_values
      :type: list[float]


      Rlc value.

      Returns
      -------
      List[float, float, float]
          [R value, L value, C value].




   .. py:property:: is_parallel
      :type: bool


      Check if the pin pair model is parallel.

      Returns
      -------
      bool
          True if the pin pair model is parallel, False otherwise.




.. py:class:: PinPairModel(component: pyedb.grpc.database.hierarchy.component.Component)

   Manage pin-pair model.


   .. py:attribute:: core


   .. py:method:: create(component: pyedb.grpc.database.hierarchy.component.Component, resistance: float | None = None, inductance: float | None = None, capacitance: float | None = None, pin1_name: str | None = None, pin2_name: str | None = None, is_parallel: bool = False) -> PinPairModel
      :classmethod:


      Create pin pair model. Pin pair model is defined between two pins, and it can be used to define the RLC model
      between two pins. Adding optional RLC values will enable the RLC model for the pin pair.

      Parameters
      ----------
      component : Component
          Edb instance.
      resistance : float, optional
          Resistance value. If not provided, the default value will be used. Default value is 0.
      inductance : float, optional
          Inductance value. If not provided, the default value will be used. Default value is 0.
      capacitance : float, optional
          Capacitance value. If not provided, the default value will be used. Default value is 0.
      pin1_name : str, optional
          First pin name. If not provided, the default name will be used. Default name is `1`.
      pin2_name : str, optional
          Second pin name. If not provided, the default name will be used. Default name is `2`.
      is_parallel : bool, optional
          Whether the RLC model is parallel. If not provided, the default value will be used

      Returns
      -------
      PinPairModel
          The created pin pair model.




   .. py:property:: pin_pairs
      :type: list[PinPair]


      Get all pin pairs.

      Returns
      -------
      List[Tuple[str, str]]
          List of pin pairs.




   .. py:property:: is_null
      :type: bool


      Check if the pin pair model is null.

      Returns
      -------
      bool
          True if the pin pair model is null, False otherwise.




   .. py:property:: rlc
      :type: ansys.edb.core.utility.rlc.Rlc | None


      Retrieve RLC model given pin pair.

      If pin pair is not provided, the first pin pair will be used by default.
      If there is no pin pair, ``None`` will be returned.

      Parameters
      ----------
      pin_pair : Tuple[str, str], optional
          Tuple of pin names (first_pin, second_pin). If not provided, the first pin pair will be used by default.
          If not provided and there is no pin pair, the first pin will be taken.

      Returns
      -------
      CoreRlc
          RLC model for the pin pair.



   .. py:method:: set_rlc(pin_pair: tuple[str, str], rlc: ansys.edb.core.utility.rlc.Rlc)

      Set RLC model for the pin pair.

      Parameters
      ----------
      pin_pair : Tuple[str, str]
          Tuple of pin names (first_pin, second_pin).
      rlc : CoreRlc
          RLC model to set for the pin pair.




   .. py:method:: delete_rlc(pin_pair: tuple[str, str])

      Delete RLC model for the pin pair.

      Parameters
      ----------
      pin_pair : Tuple[str, str]
          Tuple of pin names (first_pin, second_pin).




   .. py:method:: add_pin_pair(r: float | None = None, l: float | None = None, c: float | None = None, r_enabled: bool | None = None, l_enabled: bool | None = None, c_enabled: bool | None = None, first_pin: str | None = None, second_pin: str | None = None, is_parallel: bool = False)

      Add a pin pair definition.

      Parameters
      ----------
      r: float | None
      l: float | None
      c: float | None
      r_enabled: bool
      l_enabled: bool
      c_enabled: bool
      first_pin: str
      second_pin: str
      is_parallel: bool

      Returns
      -------




