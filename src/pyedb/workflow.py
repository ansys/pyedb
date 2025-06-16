# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
