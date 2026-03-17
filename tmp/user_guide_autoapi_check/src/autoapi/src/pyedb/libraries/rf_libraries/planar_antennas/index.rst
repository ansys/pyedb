src.pyedb.libraries.rf_libraries.planar_antennas
================================================

.. py:module:: src.pyedb.libraries.rf_libraries.planar_antennas


Classes
-------

.. autoapisummary::

   src.pyedb.libraries.rf_libraries.planar_antennas.RectangularPatch
   src.pyedb.libraries.rf_libraries.planar_antennas.CircularPatch
   src.pyedb.libraries.rf_libraries.planar_antennas.TriangularPatch


Module Contents
---------------

.. py:class:: RectangularPatch(edb_cell=None, target_frequency: Union[str, float] = '2.4Ghz', length_feeding_line: Union[str, float] = 0, layer: str = 'TOP_METAL', bottom_layer: str = 'BOT_METAL', add_port: bool = True, permittivity: float = None)

   Rectangular microstrip patch antenna (optionally inset-fed).

   The class automatically determines the physical dimensions for a
   desired resonance frequency, creates the patch, ground plane and
   either an inset microstrip feed or a coaxial probe feed, and
   optionally sets up an HFSS simulation.

   Parameters
   ----------
   edb_cell : pyedb.Edb, optional
       EDB project/cell in which the antenna will be built.
   freq : str or float, default "2.4GHz"
       Target resonance frequency of the patch.  A string such as
       ``"2.4GHz"`` or a numeric value in Hz can be given.
   inset : str or float, default 0
       Inset depth for a 50 Ω microstrip feed.  A value of 0 selects
       a probe (via) feed instead.
   layer : str, default "TOP_METAL"
       Metallization layer on which the patch polygon is drawn.
   bottom_layer : str, default "BOT_METAL"
       Metallization layer on which the ground polygon is drawn.
   add_port : bool, default True
       If True, create a wave port (inset feed) or lumped port
       (probe feed) and add an HFSS setup with a frequency sweep.

   Attributes
   ----------
   substrate : Substrate
       Substrate definition (``er``, ``tand``, ``h``) used for all
       analytical calculations.

   Examples
   --------
   Build a 5.8 GHz patch on a 0.787 mm Rogers RO4350B substrate:

   >>> edb = pyedb.Edb()
   >>> patch = RectangularPatch(edb_cell=edb, freq="5.8GHz", inset="4.2mm", layer="TOP", bottom_layer="GND")
   >>> patch.substrate.er = 3.66
   >>> patch.substrate.tand = 0.0037
   >>> patch.substrate.h = 0.000787
   >>> patch.create()
   >>> edb.save_as("patch_5p8GHz.aedb")

   Probe-fed 2.4 GHz patch (no inset):

   >>> edb = pyedb.Edb()
   >>> RectangularPatch(edb, freq=2.4e9, inset=0).create()
   >>> edb.save_as("probe_patch_2p4GHz.aedb")


   .. py:attribute:: target_frequency


   .. py:attribute:: length_feeding_line


   .. py:attribute:: layer
      :value: 'TOP_METAL'



   .. py:attribute:: bottom_layer
      :value: 'BOT_METAL'



   .. py:attribute:: add_port
      :value: True



   .. py:attribute:: substrate


   .. py:property:: estimated_frequency
      :type: float


      Analytical resonance frequency (GHz) computed from the cavity model.

      Returns
      -------
      float
          Resonant frequency in Hz.



   .. py:property:: width
      :type: float


      Patch width (m) derived for the target frequency.



   .. py:property:: length
      :type: float


      Patch length (m) accounting for fringing fields.



   .. py:method:: create() -> bool

      Draw the patch, ground plane and feed geometry in EDB.

      Returns
      -------
      bool
          True when the geometry has been successfully created.



.. py:class:: CircularPatch(edb_cell=None, target_frequency: Union[str, float] = '2.4GHz', length_feeding_line: Union[str, float] = 0, layer: str = 'TOP_METAL', bottom_layer: str = 'BOT_METAL', add_port: bool = True)

   Circular microstrip patch antenna (optionally probe-fed).

   The class automatically determines the physical dimensions for a
   desired resonance frequency, creates the patch, ground plane and
   either an inset microstrip feed or a coaxial probe feed, and
   optionally sets up an HFSS simulation.

   Parameters
   ----------
   edb_cell : pyedb.Edb, optional
       EDB project/cell in which the antenna will be built.
   freq : str or float, default "2.4GHz"
       Target resonance frequency of the patch.  A string such as
       ``"2.4GHz"`` or a numeric value in Hz can be given.
   probe_offset : str or float, default 0
       Radial offset of the 50 Ω coax probe from the patch center.
       A value of 0 places the probe at the center (not recommended
       for good matching).
   layer : str, default "TOP_METAL"
       Metallization layer on which the patch polygon is drawn.
   bottom_layer : str, default "BOT_METAL"
       Metallization layer on which the ground polygon is drawn.
   add_port : bool, default True
       If True, create a lumped port (probe feed) and add an HFSS
       setup with a frequency sweep.

   Attributes
   ----------
   substrate : Substrate
       Substrate definition (``er``, ``tand``, ``h``) used for all
       analytical calculations.

   Examples
   --------
   Build a 5.8 GHz circular patch on a 0.787 mm Rogers RO4350B substrate:

   >>> edb = pyedb.Edb()
   >>> patch = CircularPatch(edb_cell=edb, freq="5.8GHz", probe_offset="6.4mm", layer="TOP", bottom_layer="GND")
   >>> patch.substrate.er = 3.66
   >>> patch.substrate.tand = 0.0037
   >>> patch.substrate.h = 0.000787
   >>> patch.create()
   >>> edb.save_as("circ_patch_5p8GHz.aedb")

   Probe-fed 2.4 GHz patch with default 0 offset (center feed):

   >>> edb = pyedb.Edb()
   >>> CircularPatch(edb, freq=2.4e9).create()
   >>> edb.save_as("probe_circ_patch_2p4GHz.aedb")


   .. py:attribute:: target_frequency


   .. py:attribute:: length_feeding_line


   .. py:attribute:: layer
      :value: 'TOP_METAL'



   .. py:attribute:: bottom_layer
      :value: 'BOT_METAL'



   .. py:attribute:: substrate


   .. py:attribute:: add_port
      :value: True



   .. py:property:: estimated_frequency
      :type: float


      Improved analytical resonance frequency (Hz) of the dominant TM11 mode.

      Uses Balanis’ closed-form model for single-layer circular patches.
      Accuracy ≈ ±0.5 % compared with full-wave solvers for
      0.003 ≤ h/λd ≤ 0.05 and εr 2–12.

      Returns
      -------
      float
          Resonant frequency in Hz.



   .. py:property:: radius
      :type: float


      Patch physical radius (m) derived for the target frequency.



   .. py:method:: create() -> bool

      Draw the patch, ground plane and feed geometry in EDB.

      Returns
      -------
      bool
          True when the geometry has been successfully created.



.. py:class:: TriangularPatch(edb_cell=None, target_frequency: Union[str, float] = '2.4GHz', length_feeding_line: Union[str, float] = 0, layer: str = 'TOP_METAL', bottom_layer: str = 'BOT_METAL', add_port: bool = True)

   Equilateral-triangle microstrip patch antenna (optionally probe-fed).

   The class automatically determines the physical dimensions for a
   desired resonance frequency, creates the patch, ground plane and
   either an inset microstrip feed or a coaxial probe feed, and
   optionally sets up an HFSS simulation.

   Parameters
   ----------
   edb_cell : pyedb.Edb, optional
       EDB project/cell in which the antenna will be built.
   freq : str or float, default "2.4GHz"
       Target resonance frequency of the patch.  A string such as
       ``"2.4GHz"`` or a numeric value in Hz can be given.
   probe_offset : str or float, default 0
       Radial offset of the 50 Ω coax probe from the patch centroid.
       A value of 0 places the probe at the centroid (not recommended
       for good matching).
   layer : str, default "TOP_METAL"
       Metallization layer on which the patch polygon is drawn.
   bottom_layer : str, default "BOT_METAL"
       Metallization layer on which the ground polygon is drawn.
   add_port : bool, default True
       If True, create a lumped port (probe feed) and add an HFSS
       setup with a frequency sweep.

   Attributes
   ----------
   substrate : Substrate
       Substrate definition (``er``, ``tand``, ``h``) used for all
       analytical calculations.

   Examples
   --------
   Build a 5.8 GHz triangular patch on a 0.787 mm Rogers RO4350B substrate:

   >>> edb = pyedb.Edb()
   >>> patch = TriangularPatch(edb_cell=edb, freq="5.8GHz", probe_offset="5.6mm", layer="TOP", bottom_layer="GND")
   >>> patch.substrate.er = 3.66
   >>> patch.substrate.tand = 0.0037
   >>> patch.substrate.h = 0.000787
   >>> patch.create()
   >>> edb.save_as("tri_patch_5p8GHz.aedb")

   Probe-fed 2.4 GHz patch with default 0 offset (center feed):

   >>> edb = pyedb.Edb()
   >>> TriangularPatch(edb, freq=2.4e9).create()
   >>> edb.save_as("probe_tri_patch_2p4GHz.aedb")


   .. py:attribute:: target_frequency


   .. py:attribute:: length_feeding_line


   .. py:attribute:: layer
      :value: 'TOP_METAL'



   .. py:attribute:: bottom_layer
      :value: 'BOT_METAL'



   .. py:attribute:: substrate


   .. py:attribute:: add_port
      :value: True



   .. py:property:: estimated_frequency
      :type: float


      Improved analytical resonance frequency (Hz) of the dominant TM10 mode.

      Uses a closed-form model for equilateral-triangle patches.
      Accuracy ≈ ±1 % compared with full-wave solvers for
      0.003 ≤ h/λd ≤ 0.05 and εr 2–12.

      Returns
      -------
      float
          Resonant frequency in Hz.



   .. py:property:: side
      :type: float


      Patch physical side length (m) for the target frequency.

      Uses a **full-cavity model** with dynamic fringing and dispersion
      corrections that keeps the error < 0.25 % for
      0.003 ≤ h/λd ≤ 0.06 and 2 ≤ εr ≤ 12.



   .. py:method:: create() -> bool

      Draw the patch, ground plane and feed geometry in EDB.

      Returns
      -------
      bool
          True when the geometry has been successfully created.



