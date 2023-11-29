Getting layout size
===================
This section describes how to retrieve the layout size by getting the bounding box:

.. autosummary::
   :toctree: _autosummary

.. code:: python



    from pyedb.legacy.edb import EdbLegacy
    from pyedb.generic.general_methods import generate_unique_folder_name
    import pyedb.misc.downloads as downloads

    temp_folder = generate_unique_folder_name()
    targetfile = downloads.download_file('edb/ANSYS-HSD_V1.aedb', destination=temp_folder)
    edbapp = EdbLegacy(edbpath=targetfile, edbversion="2023.2")

    edbapp.get_bounding_box()

.. image:: ../Resources/layout_bbox.png
    :width: 800
    :alt: Layout bounding box
