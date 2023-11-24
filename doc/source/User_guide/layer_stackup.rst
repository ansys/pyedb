Checking and editing layer stackup
==================================
This section describes how to edit layer stackup:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.legacy.edb_core.edb import EdbLegacy

    # Ansys release version
    desktop_version = "2024.1"

    temp_folder = r"C:\Temp\stackup_example"
    source_file = pyedb.layout_examples.ANSYS-HSD_V1.aedb
    pyedb.misc.utilities.file_tools.copy_folder(source_file, temp_folder)

    # loading EDB
    targe_tfile = os.path.join(temp_folder, source_file)
    edbapp = EdbLegacy(edbpath=target_file, edbversion=desktop_version)

    # ploting layer stackup in matplotlib
    edbapp.stackup.plot()

. image:: ../Resources/stackup.png
:width: 800
:alt: Layer stackup plot

.. code:: python



    # retrieving signal layers name
    signal_layers = list(edbapp.stackup.signal_layers.keys())

    # selecting top layer
    top_layer = edbapp.stackup.signal_layers[signal_layers[0]]

    # Stackup total thickness
    layout_stats = edbapp.get_statistics()
    layout_stats.stackup_thickness

    # setting all signal layers thickness to 20um
    for layer_name, layer in edbapp.stackup.signal_layers.items():
        layer.thickness = "20um"

    edbapp.materials.add_material(name="MyMaterial", permittivity=4.35, dielectric_loss_tangent=2e-4)
    edbapp.materials.add_material(name="MyMetal", conductivity=1e7)
    for layer in list(edbapp.stackup.dielectric_layers.values()):
        layer.material = "MyMaterial"
    for layer in list(edbapp.stackup.signal_layers.values()):
        layer.material = "MyMetal"
    edbapp.materials.add_material(name="SolderMask", permittivity=3.8, dielectric_loss_tangent=1e-3)
    edbapp.stackup.add_layer(layer_name="Solder_mask", base_layer="1_Top", thickness="200um", material="SolderMask")




