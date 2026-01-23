from pathlib import Path

from pydantic import BaseModel, Field
from typing import Optional
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

    def to_xml(self, root_name="c:Control",
               pretty=True) -> str:
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
