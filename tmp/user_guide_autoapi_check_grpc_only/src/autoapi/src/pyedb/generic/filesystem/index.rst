src.pyedb.generic.filesystem
============================

.. py:module:: src.pyedb.generic.filesystem


Classes
-------

.. autoapisummary::

   src.pyedb.generic.filesystem.Scratch


Functions
---------

.. autoapisummary::

   src.pyedb.generic.filesystem.search_files
   src.pyedb.generic.filesystem.my_location
   src.pyedb.generic.filesystem.get_json_files


Module Contents
---------------

.. py:function:: search_files(dirname: str, pattern: str = '*') -> list[str]

   Search for files inside a directory given a specific pattern.

   Parameters
   ----------
   dirname : str
       Directory where the search will be performed.
   pattern : str, optional
       Pattern to match files against. The default is ``"*"``, which matches all files.

   Returns
   -------
   list


.. py:function:: my_location()

   Get the normalized path of the current file's directory.


.. py:class:: Scratch(local_path, permission=511, volatile=False)

   Class for managing a scratch directory.


   .. py:property:: path
      :type: str


      Get the path of the scratch directory.



   .. py:property:: is_empty
      :type: bool


      Check if the scratch directory is empty.



   .. py:method:: remove() -> None

      Remove the scratch directory and its contents.



   .. py:method:: copyfile(src_file: str, dst_filename: str | None = None) -> str

      Copy a file to the scratch directory.

      Parameters
      ----------
      src_file : str
          Source file with fullpath.
      dst_filename : str, optional
          Destination filename with the extension. The default is ``None``,
          in which case the destination file is given the same name as the
          source file.

      Returns
      -------
      dst_file : str
          Full path and file name of the copied file.



   .. py:method:: copyfolder(src_folder: str, destfolder: str | None = None) -> str

      Copy a folder to the scratch directory.

      Parameters
      ----------
      src_folder : str
          Source folder with fullpath.
      destfolder : str, optional
          Destination folder. The default is ``None``, in which case the destination folder
          is given the same name as the source folder.

      Returns
      -------
      destfolder : str
          Full path of the copied folder.



.. py:function:: get_json_files(start_folder)

   Get the absolute path to all JSON files in start_folder.

   Parameters
   ----------
   start_folder : str
       Path to the folder where the JSON files are located.

   Returns
   -------
   list
        List of paths to JSON files in start_folder.


