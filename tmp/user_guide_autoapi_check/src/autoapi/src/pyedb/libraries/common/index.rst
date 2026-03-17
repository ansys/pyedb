src.pyedb.libraries.common
==========================

.. py:module:: src.pyedb.libraries.common


Classes
-------

.. autoapisummary::

   src.pyedb.libraries.common.Substrate
   src.pyedb.libraries.common.Material
   src.pyedb.libraries.common.Conductor
   src.pyedb.libraries.common.Dielectric
   src.pyedb.libraries.common.Layer
   src.pyedb.libraries.common.MetalLayer
   src.pyedb.libraries.common.DielectricLayer
   src.pyedb.libraries.common.MicroStripTechnologyStackup


Module Contents
---------------

.. py:class:: Substrate

   Small helper that groups the four basic substrate parameters used
   throughout the library.

   Parameters
   ----------
   h : float, default 100 µm
       Substrate height in metres.
   er : float, default 4.4
       Relative permittivity.
   tan_d : float, default 0
       Loss tangent.
   name : str, default "SUB"
       Logical name used for layer creation.
   size : tuple[float, float], default (1 mm, 1 mm)
       (width, length) of the surrounding ground plane in metres.

   Examples
   --------
   >>> sub = Substrate(h=1.6e-3, er=4.4, tan_d=0.02, name="FR4", size=(10e-3, 15e-3))
   >>> sub.h
   0.0016


   .. py:attribute:: h
      :type:  float
      :value: 0.0001



   .. py:attribute:: er
      :type:  float
      :value: 4.4



   .. py:attribute:: tan_d
      :type:  float
      :value: 0



   .. py:attribute:: name
      :type:  str
      :value: 'SUB'



   .. py:attribute:: size
      :type:  Tuple[float, float]
      :value: (0.001, 0.001)



.. py:class:: Material(pedb, name)

   Generic material definition.

   When the material name is set, the object automatically registers
   itself in the provided PyEDB material database if the name is not
   already present.

   Parameters
   ----------
   pedb : ansys.edb.core.database.Database
       Active EDB session.
   name : str
       Material name (e.g. ``"Copper"``).

   Examples
   --------
   >>> m = Material(edb, "MyMaterial")
   >>> m.name
   'MyMaterial'
   >>> edb.materials["MyMaterial"]  # now exists in the database
   <Material object at ...>


   .. py:property:: name
      :type: str


      Material name.



.. py:class:: Conductor(pedb, name: str, conductivity: float = 58000000.0)

   Bases: :py:obj:`Material`


   Metallic conductor material with electrical conductivity.

   Parameters
   ----------
   pedb : ansys.edb.core.database.Database
       Active EDB session.
   name : str
       Material name.
   conductivity : float, optional
       Electrical conductivity in S/m.  Default is 5.8e7 (Copper).

   Examples
   --------
   >>> cu = Conductor(edb, "Copper", conductivity=5.8e7)
   >>> cu.conductivity
   58000000.0
   >>> cu.conductivity = 3.5e7  # update on-the-fly
   >>> edb.materials["Copper"].conductivity
   35000000.0


   .. py:property:: conductivity
      :type: float


      Electrical conductivity (S/m).



.. py:class:: Dielectric(pedb, name: str, permittivity: float = 11.9, loss_tg: float = 0.02)

   Bases: :py:obj:`Material`


   Dielectric material with relative permittivity and loss tangent.

   Parameters
   ----------
   pedb : ansys.edb.core.database.Database
       Active EDB session.
   name : str
       Material name.
   permittivity : float, optional
       Relative permittivity (εᵣ).  Default is 11.9 (Silicon).
   loss_tg : float, optional
       Loss tangent (tan δ).  Default is 0.02.

   Examples
   --------
   >>> sub = Dielectric(edb, "Silicon", permittivity=11.9, loss_tg=0.01)
   >>> sub.permittivity
   11.9
   >>> sub.loss_tg = 0.005
   >>> edb.materials["Silicon"].loss_tangent
   0.005


   .. py:property:: permittivity
      :type: float


      Relative permittivity (εᵣ).



   .. py:property:: loss_tg
      :type: float


      Loss tangent (tan δ).



.. py:class:: Layer(pedb, name: str, material: Union[Conductor, Dielectric] = None, thickness: float = 1e-06)

   Physical layer inside a stackup.

   Parameters
   ----------
   pedb : ansys.edb.core.database.Database
       Active EDB session.
   name : str
       Layer name.
   material : Conductor or Dielectric, optional
       Material instance assigned to the layer.
   thickness : float, optional
       Layer thickness in meters.  Default is 1 µm.

   Examples
   --------
   >>> diel = Dielectric(edb, "FR4")
   >>> lyr = Layer(edb, "Core", material=diel, thickness=100e-6)
   >>> lyr.thickness = 50e-6
   >>> edb.stackup.layers["Core"].thickness
   5e-05


   .. py:property:: name
      :type: str


      Layer name.



   .. py:property:: thickness
      :type: float


      Layer thickness (m).



   .. py:property:: material
      :type: Union[Conductor, Dielectric]


      Material assigned to this layer.



.. py:class:: MetalLayer(pedb, name, thickness=1e-06, material: str = 'Copper')

   Bases: :py:obj:`Layer`


   Convenience wrapper for metallic layers.

   Automatically creates a ``Conductor`` material.

   Parameters
   ----------
   pedb : ansys.edb.core.database.Database
       Active EDB session.
   name : str
       Layer name.
   thickness : float, optional
       Thickness in meters.  Default is 1 µm.
   material : str, optional
       Name of the conductor material.  Default is ``"Copper"``.

   Examples
   --------
   >>> top = MetalLayer(edb, "TOP", thickness=18e-6, material="Gold")
   >>> top.material.conductivity
   58000000.0


   .. py:attribute:: material

      Material assigned to this layer.



.. py:class:: DielectricLayer(pedb, name, thickness=1e-06, material: str = 'FR4')

   Bases: :py:obj:`Layer`


   Convenience wrapper for dielectric layers.

   Automatically creates a ``Dielectric`` material.

   Parameters
   ----------
   pedb : ansys.edb.core.database.Database
       Active EDB session.
   name : str
       Layer name.
   thickness : float, optional
       Thickness in meters.  Default is 1 µm.
   material : str, optional
       Name of the dielectric material.  Default is ``"FR4"``.

   Examples
   --------
   >>> core = DielectricLayer(edb, "Core", thickness=100e-6, material="FR4")
   >>> core.material.permittivity
   4.4


   .. py:attribute:: material

      Material assigned to this layer.



.. py:class:: MicroStripTechnologyStackup(pedb, botton_layer_name='BOT_METAL', substrate_layer_name='Substrate', top_layer_name='TOP_METAL')

   Pre-defined micro-strip stackup with bottom metal, substrate and top metal.

   Parameters
   ----------
   pedb : ansys.edb.core.database.Database
       Active EDB session.

   Attributes
   ----------
   bottom_metal : MetalLayer
       Bottom metal layer.
   substrate : DielectricLayer
       Substrate dielectric layer.
   top_metal : MetalLayer
       Top metal layer.

   Examples
   --------
   >>> stack = MicroStripTechnologyStackup(edb)
   >>> stack.top_metal.thickness = 5e-6
   >>> stack.substrate.material.permittivity = 9.8


   .. py:attribute:: bottom_metal


   .. py:attribute:: substrate


   .. py:attribute:: top_metal


