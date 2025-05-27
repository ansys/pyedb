from dataclasses import dataclass


@dataclass
class CfgTerminal:
    pin: str
    net: str


class CfgPort:
    name: str
    reference_designator: str
    type: str
    positive_terminal: CfgTerminal

    {
        "ports": [
            {
                "name": "CIRCUIT_C375_1_2",
                "reference_designator": "C375",
                "type": "circuit",
                "positive_terminal": {"pin": "1"},
                "negative_terminal": {"pin": "2"},
            },
            {
                "name": "CIRCUIT_X1_B8_GND",
                "reference_designator": "X1",
                "type": "circuit",
                "positive_terminal": {"pin": "B8"},
                "negative_terminal": {"net": "GND"},
            },
            {
                "name": "CIRCUIT_X1_B9_GND",
                "reference_designator": "X1",
                "type": "circuit",
                "positive_terminal": {"net": "PCIe_Gen4_TX2_N"},
                "negative_terminal": {"net": "GND"},
            },
            {
                "name": "CIRCUIT_U7_VDD_DDR_GND",
                "reference_designator": "U7",
                "type": "circuit",
                "positive_terminal": {"net": "VDD_DDR"},
                "negative_terminal": {"net": "GND"},
            },
        ]
    }
