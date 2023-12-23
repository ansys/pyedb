from distutils.dir_util import copy_tree


class file_tools:
    def __init__(self):
        pass

    @staticmethod
    def copy_folder(source_folder, destination_folder):
        """

        Parameters
        ----------
        source_folder : str
            source folder

        destination_folder : str
            destination folder.


        Returns
        -------

        """

        copy_tree(source_folder, destination_folder)
        return True
