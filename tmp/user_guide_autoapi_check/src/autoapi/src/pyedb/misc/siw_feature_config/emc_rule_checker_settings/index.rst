src.pyedb.misc.siw_feature_config.emc_rule_checker_settings
===========================================================

.. py:module:: src.pyedb.misc.siw_feature_config.emc_rule_checker_settings


Classes
-------

.. autoapisummary::

   src.pyedb.misc.siw_feature_config.emc_rule_checker_settings.EMCRuleCheckerSettings


Functions
---------

.. autoapisummary::

   src.pyedb.misc.siw_feature_config.emc_rule_checker_settings.kwargs_parser


Module Contents
---------------

.. py:function:: kwargs_parser(kwargs: dict) -> dict[str, str]

   Parse and convert keyword arguments to string format.

   Parameters
   ----------
   kwargs : dict
       Dictionary of keyword arguments to parse.

   Returns
   -------
   dict[str, str]
       Dictionary with all values converted to strings.

   Examples
   --------
   >>> from pyedb.misc.siw_feature_config.emc_rule_checker_settings import kwargs_parser
   >>> kwargs = {"key1": True, "key2": 123, "key3": "test"}
   >>> result = kwargs_parser(kwargs)
   >>> result
   {'key1': '1', 'key2': '123', 'key3': 'test'}



.. py:class:: EMCRuleCheckerSettings

   Manages EMI scanner settings.

   Examples
   --------
   >>> from pyedb.misc.siw_feature_config.emc_rule_checker_settings import EMCRuleCheckerSettings
   >>> settings = EMCRuleCheckerSettings()
   >>> settings.add_net("net1", is_clock=True)



   .. py:attribute:: version
      :value: '1.0'



   .. py:attribute:: encoding
      :value: 'UTF-8'



   .. py:attribute:: standalone
      :value: 'no'



   .. py:attribute:: tag_library


   .. py:attribute:: net_tags


   .. py:attribute:: component_tags


   .. py:method:: read_xml(fpath: str) -> None

      Read settings from an XML file.

      Parameters
      ----------
      fpath : str
          Path to file.

      Examples
      --------
      >>> settings = EMCRuleCheckerSettings()
      >>> settings.read_xml("config.xml")




   .. py:method:: write_xml(fpath: str) -> None

      Write settings to a file in XML format.

      Parameters
      ----------
      fpath : str
          Path to file.

      Examples
      --------
      >>> settings = EMCRuleCheckerSettings()
      >>> settings.write_xml("config.xml")




   .. py:method:: write_json(fpath: str) -> None

      Write settings to a file in JSON format.

      Parameters
      ----------
      fpath : str
          Path to file.

      Examples
      --------
      >>> settings = EMCRuleCheckerSettings()
      >>> settings.write_json("config.json")




   .. py:method:: read_json(fpath: str) -> None

      Read settings from a JSON file.

      Parameters
      ----------
      fpath : str
          Path to file.

      Examples
      --------
      >>> settings = EMCRuleCheckerSettings()
      >>> settings.read_json("config.json")




   .. py:method:: add_net(name: str, is_bus: bool | str | int = False, is_clock: bool | str | int = False, is_critical: bool | str = False, net_type: str = 'Single-Ended', diff_mate_name: str = '') -> None

      Assign tags to a net.

      Parameters
      ----------
      name : str
          Name of the net.
      is_bus : bool, str or int, optional
          Whether the net is a bus.
          The default is ``False``.
      is_clock : bool, str or int, optional
          Whether the net is a clock.
          The default is ``False``.
      is_critical : bool or str, optional
          Whether the net is critical.
          The default is ``False``.
      net_type : str, optional
          Type of the net.
          The default is ``"Single-Ended"``.
      diff_mate_name : str, optional
          Differential mate name.
          The default is ``""``.

      Examples
      --------
      >>> settings = EMCRuleCheckerSettings()
      >>> settings.add_net("CLK_100M", is_clock=True, is_critical=True)
      >>> settings.add_net("USB_DP", net_type="Differential", diff_mate_name="USB_DN")




   .. py:method:: add_component(comp_name: str, comp_value: str, device_name: str, is_clock_driver: bool | str, is_high_speed: bool | str, is_ic: bool | str, is_oscillator: bool | str, x_loc: str | float, y_loc: str | float, cap_type: str | None = None) -> None

      Assign tags to a component.

      Parameters
      ----------
      comp_name : str
          Name of the component.
      comp_value : str
          Value of the component.
      device_name : str
          Name of the device.
      is_clock_driver : bool or str
          Whether the component is a clock driver.
      is_high_speed : bool or str
          Whether the component is high speed.
      is_ic : bool or str
          Whether the component is an IC.
      is_oscillator : bool or str
          Whether the component is an oscillator.
      x_loc : str or float
          X coordinate.
      y_loc : str or float
          Y coordinate.
      cap_type : str or None, optional
          Type of the capacitor. Options are ``"Decoupling"`` and ``"Stitching"``.
          The default is ``None``.

      Examples
      --------
      >>> settings = EMCRuleCheckerSettings()
      >>> settings.add_component(
      ...     comp_name="U1",
      ...     comp_value="FPGA",
      ...     device_name="XC7A35T",
      ...     is_clock_driver=False,
      ...     is_high_speed=True,
      ...     is_ic=True,
      ...     is_oscillator=False,
      ...     x_loc="10.5",
      ...     y_loc="20.3",
      ... )




