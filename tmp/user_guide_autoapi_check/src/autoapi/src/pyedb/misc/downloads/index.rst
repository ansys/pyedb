src.pyedb.misc.downloads
========================

.. py:module:: src.pyedb.misc.downloads

.. autoapi-nested-parse::

   Download example datasets from https://github.com/pyansys/example-data



Attributes
----------

.. autoapisummary::

   src.pyedb.misc.downloads.pyedb_logger
   src.pyedb.misc.downloads.EXAMPLES_PATH


Functions
---------

.. autoapisummary::

   src.pyedb.misc.downloads.delete_downloads
   src.pyedb.misc.downloads.list_examples_files
   src.pyedb.misc.downloads.download_aedb
   src.pyedb.misc.downloads.download_edb_merge_utility
   src.pyedb.misc.downloads.download_via_wizard
   src.pyedb.misc.downloads.download_touchstone
   src.pyedb.misc.downloads.download_file
   src.pyedb.misc.downloads.unzip


Module Contents
---------------

.. py:data:: pyedb_logger

.. py:data:: EXAMPLES_PATH

.. py:function:: delete_downloads() -> None

   Delete all downloaded examples to free space or update the files.

   Examples
   --------
   >>> import pyedb.misc.downloads as downloads
   >>> downloads.delete_downloads()



.. py:function:: list_examples_files(folder) -> list

   List all files in a folder of the example-data repository.

   Parameters
   ----------
   folder : str
       The folder in the GitHub repository to list files from, e.g., "pyaedt/sbr/".

   Returns
   -------
   list
       A list of file paths in the specified folder.


.. py:function:: download_aedb(destination: str | None = None) -> str

   Download an example of AEDB File and return the def path.

   Examples files are downloaded to a persistent cache to avoid
   re-downloading the same file twice.

   Parameters
   ----------
   destination : str or None, optional
       Path for downloading files.
       The default is ``None``, which uses the user's temp folder.

   Returns
   -------
   str
       Path to the example file.

   Examples
   --------
   Download an example result file and return the path of the file.

   >>> import pyedb.misc.downloads
   >>> path = pyedb.misc.downloads.download_aedb()
   >>> path
   'C:/Users/user/AppData/local/temp/Galileo.aedb'



.. py:function:: download_edb_merge_utility(force_download: bool = False, destination: str | None = None) -> str

   Download an example of WPF Project which allows to merge 2 aedb files.

   Examples files are downloaded to a persistent cache to avoid
   re-downloading the same file twice.

   Parameters
   ----------
   force_download : bool, optional
       Force to delete cache and download files again.
       The default is ``False``.
   destination : str or None, optional
       Path for downloading files.
       The default is ``None``, which uses the user's temp folder.

   Returns
   -------
   str
       Path to the example file.

   Examples
   --------
   Download an example result file and return the path of the file.

   >>> import pyedb.misc.downloads
   >>> path = pyedb.misc.downloads.download_edb_merge_utility(force_download=True)
   >>> path
   'C:/Users/user/AppData/local/temp/PyAEDTExamples/wpf_edb_merge/merge_wizard.py'



.. py:function:: download_via_wizard(destination: str | None = None) -> str

   Download an example of Hfss Via Wizard and return the def path.

   Examples files are downloaded to a persistent cache to avoid
   re-downloading the same file twice.

   Parameters
   ----------
   destination : str or None, optional
       Path for downloading files.
       The default is ``None``, which uses the user's temp folder.

   Returns
   -------
   str
       Path to the example file.

   Examples
   --------
   Download an example result file and return the path of the file.

   >>> import pyedb.misc.downloads
   >>> path = pyedb.misc.downloads.download_via_wizard()
   >>> path
   'C:/Users/user/AppData/local/temp/PyAEDTExamples/viawizard_vacuum_FR4.aedt'


.. py:function:: download_touchstone(destination: str | None = None) -> str

   Download an example of touchstone File and return the def path.

   Examples files are downloaded to a persistent cache to avoid
   re-downloading the same file twice.

   Parameters
   ----------
   destination : str or None, optional
       Path for downloading files.
       The default is ``None``, which uses the user's temp folder.

   Returns
   -------
   str
       Path to the example file.

   Examples
   --------
   Download an example result file and return the path of the file.

   >>> import pyedb.misc.downloads
   >>> path = pyedb.misc.downloads.download_touchstone()
   >>> path
   'C:/Users/user/AppData/local/temp/PyAEDTExamples/SSN_ssn.s6p'



.. py:function:: download_file(directory: str, filename: str | None = None, destination: str | None = None) -> str

   Download file from directory.

   Files are downloaded to a destination. If filename is not specified, the full directory will be downloaded.

   Parameters
   ----------
   directory : str
       Directory name.
   filename : str or None, optional
       File name to download.
       The default is ``None``, which downloads all files inside directory.
   destination : str or None, optional
       Path where files will be downloaded.
       The default is ``None``, which uses the user's temp folder.

   Returns
   -------
   str
       Path to the example file.

   Examples
   --------
   Download an example result file and return the path of the file.

   >>> import pyedb.misc.downloads
   >>> path = pyedb.misc.downloads.download_file("pyaedt/edb/ansys_interposer", "dummy_interposer_hbm.map")
   >>> path
   'C:/Users/user/AppData/local/temp/PyAEDTExamples/pyaedt/edb/ansys_interposer/dummy_interposer_hbm.map'



.. py:function:: unzip(source_filename: str, dest_dir: str) -> None

   Extract all files from a zip archive.

   Parameters
   ----------
   source_filename : str
       Path to the zip file to extract.
   dest_dir : str
       Destination directory for extracted files.

   Examples
   --------
   >>> import pyedb.misc.downloads as downloads
   >>> downloads.unzip("example.zip", "/path/to/destination")



