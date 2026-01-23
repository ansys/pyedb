# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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
from typing import Optional

from pydantic import BaseModel, Field
import xmltodict

from pyedb.xml_parser.xml_stackup import XmlStackup


# ---------- Nets ----------
class XmlNet(BaseModel):
    name: str = Field(alias="@Name")
    pins_become_ports: Optional[bool] = Field(None, alias="@PinsBecomePorts")

    model_config = dict(populate_by_name=True)


# ---------- Import Options ----------
class XmlImportOptions(BaseModel):
    enable_default_component_values: Optional[bool] = Field(None, alias="EnableDefaultComponentValues")
    flatten: Optional[bool] = Field(None, alias="Flatten")

    model_config = dict(populate_by_name=True)


# ---------- Control root ----------
class XmlParser(BaseModel):
    stackup: Optional[XmlStackup] = Field(default=None, alias="Stackup")
    import_options: Optional[XmlImportOptions] = Field(default=None, alias="ImportOptions")
    nets: Optional[dict] = Field(default=None, alias="Nets")
    schema_version: Optional[str] = Field(default=None, alias="schemaVersion")

    model_config = dict(populate_by_name=True)

    def add_stackup(self):
        self.stackup = XmlStackup()
        return self.stackup

    @classmethod
    def load_xml_file(cls, path: str | Path) -> "XmlParser":
        with open(path, "r", encoding="utf-8") as f:
            xml_data = f.read()

        data_dict = xmltodict.parse(xml_data)

        control_dict = list(data_dict.values())[0]

        return cls.model_validate(control_dict)

    def to_xml(self, root_name="c:Control", pretty=True) -> str:
        root = self.model_dump(by_alias=True, exclude_none=True)

        # Ensure the desired root tag attributes exist
        root["@xmlns:c"] = "http://www.ansys.com/control"
        root.setdefault("@schemaVersion", "1.0")
        stackup = root.get("Stackup")
        stackup.setdefault("@schemaVersion", "1.0")

        d = {root_name: root}
        return xmltodict.unparse(d, pretty=pretty)

    def to_xml_file(self, file_path: str | Path):
        xml_out = self.to_xml()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(xml_out)
        return str(file_path)

    def to_dict(self):
        return {"stackup": self.stackup.to_dict()}
