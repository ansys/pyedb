src.pyedb.generic.process
=========================

.. py:module:: src.pyedb.generic.process


Classes
-------

.. autoapisummary::

   src.pyedb.generic.process.SiwaveSolve


Module Contents
---------------

.. py:class:: SiwaveSolve(pedb)

   Bases: :py:obj:`object`


   .. py:method:: solve_siwave(edbpath, analysis_type)

      Solve an SIWave setup. Only non-graphical batch mode is supported.

      .. warning::
          Do not execute this function with untrusted function argument, environment
          variables or pyedb global settings.
          See the :ref:`security guide<ref_security_consideration>` for details.

      Parameters
      ----------
      analysis_type: str
          Type of SIWave analysis to perform. Available types are "SYZ", "DCIR", "CPA", "TimeCrosstalk",
          "FreqCrosstalk", "Impedance".
      edbpath: str
          Full path to the .aedb folder, siw or siwz file to be solved.
      siwave_ng: str, optinial
          Path to the siwave_ng. Default is the SIWave installation path.



   .. py:method:: solve(num_of_cores=4)

      Solve using siwave_ng.exe

      .. warning::
          Do not execute this function with untrusted function argument, environment
          variables or pyedb global settings.
          See the :ref:`security guide<ref_security_consideration>` for details.




   .. py:method:: export_3d_cad(format_3d='Q3D', output_folder=None, net_list=None, num_cores=4, aedt_file_name=None, hidden=False)

      Export edb to Q3D or HFSS

      .. warning::
          Do not execute this function with untrusted function argument, environment
          variables or pyedb global settings.
          See the :ref:`security guide<ref_security_consideration>` for details.

      Parameters
      ----------
      format_3d : str, default ``Q3D``
      output_folder : str
          Output file folder. If `` then the aedb parent folder is used
      net_list : list, default ``None``
          Define Nets to Export. if None, all nets will be exported
      num_cores : int, optional
          Define number of cores to use during export
      aedt_file_name : str, optional
          Output  aedt file name (without .aedt extension). If `` then default naming is used
      Returns
      -------
      str
          path to aedt file



   .. py:method:: export_dc_report(siwave_project, solution_name, output_folder=None, html_report=True, vias=True, voltage_probes=True, current_sources=True, voltage_sources=True, power_tree=True, loop_res=True, hidden=True)

      Close EDB and solve it with Siwave.

      .. warning::
          Do not execute this function with untrusted function argument, environment
          variables or pyedb global settings.
          See the :ref:`security guide<ref_security_consideration>` for details.

      Parameters
      ----------
      siwave_project : str
          Siwave full project name.
      solution_name : str
          Siwave DC Analysis name.
      output_folder : str, optional
          Ouptu folder where files will be downloaded.
      html_report : bool, optional
          Either if generate or not html report. Default is `True`.
      vias : bool, optional
          Either if generate or not vias report. Default is `True`.
      voltage_probes : bool, optional
          Either if generate or not voltage probe report. Default is `True`.
      current_sources : bool, optional
          Either if generate or not current source report. Default is `True`.
      voltage_sources : bool, optional
          Either if generate or not voltage source report. Default is `True`.
      power_tree : bool, optional
          Either if generate or not power tree image. Default is `True`.
      loop_res : bool, optional
          Either if generate or not loop resistance report. Default is `True`.

      Returns
      -------
      list
          list of files generated.



