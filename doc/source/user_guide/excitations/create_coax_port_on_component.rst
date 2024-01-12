Create coaxial port on component
================================
This section shows a simple example to create HFSS coaxial port on a component.

.. autosummary::
   :toctree: _autosummary

.. code:: python


    from pyedb.legacy.edb import EdbLegacy
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    # Ansys release version
    ansys_version = "2023.2"

    # download and copy the layout file from examples
    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file("edb/ANSYS-HSD_V1.aedb", destination=temp_folder)

    # loading EDB
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    edbapp.hfss.create_coax_port_on_component("U1", ["DDR4_DQS0_P", "DDR4_DQS0_N"])

- In this example coaxial port on Nets DDR4_DSQ0_P and DDR4_DSQ0_N from componennt U1 are created.

.. .. image:: ../../Resources/create_port_on_component_simple.png
..   :width: 800
..   :alt: Create port on component