SIwave manager
==============
`SIwave <https://www.ansys.com/products/electronics/ansys-siwave>`_ is a specialized tool
for power integrity, signal integrity, and EMI analysis of IC packages and PCB. This tool
solves power delivery systems and high-speed channels in electronic devices. It can be
accessed from PyEDB in Windows only. All setups can be implemented through EDB API.

.. image:: ../resources/siwave.png
  :width: 800
  :alt: EdbSiwave
  :target: https://www.ansys.com/products/electronics/ansys-siwave


.. currentmodule:: pyedb.siwave

.. autosummary::
   :toctree: _autosummary

   Siwave


.. code:: python

    from pyedb.siwave import Siwave

    # this call returns the Edb class initialized on 2024 R2
    siwave = Siwave("2024.2")
    siwave.open_project("pyproject.siw")
    siwave.export_element_data("mydata.txt")
    siwave.close_project()
    ...

.. currentmodule:: pyedb.siwave_core.icepak
   Icepak

