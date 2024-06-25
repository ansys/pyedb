from pathlib import Path
from typing import Union

import pandas as pd


class Workflow:
    def __init__(self, pedb):
        self._pedb = pedb

    def export_bill_of_materials(self, file_path: Union[str, Path]):
        """Export bill of materials to a csv file.

        Parameters
        ----------
        file_path : Union[str, Path]
            Path to the csv file.

        Returns
        -------

        """
        file_path = str(file_path)
        data = self._pedb.configuration.get_data_from_db(components=True)
        comps = data["components"]
        temp = []
        for comp in comps:
            comp_attrs = {k: v for k, v in comp.items() if isinstance(v, Union[str, float, int])}
            temp.append(comp_attrs)

        df = pd.DataFrame(temp)
        return df.to_csv(file_path)
