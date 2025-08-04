from pathlib import Path

from pyedb.extensions.via_design_backend import ViaDesignBackend

import toml


def test_custom():
    # This needs to be updated to match your file location
    create_design_path = Path("use/pyaedt/project/resources/via_design_pcb_rf.toml")
    assert create_design_path.exists()

    dict_config = toml.load(create_design_path)
    stacked_vias = dict_config.pop("stacked_vias")
    for param_name, param_value in dict_config["signals"].items():
        stacked_vias_name = param_value["stacked_vias"]
        dict_config["signals"][param_name]["stacked_vias"] = stacked_vias[stacked_vias_name]
    for param_name, param_value in dict_config["differential_signals"].items():
        stacked_vias_name = param_value["stacked_vias"]
        dict_config["differential_signals"][param_name]["stacked_vias"] = stacked_vias[stacked_vias_name]

    # The following code line should fail
    backend = ViaDesignBackend(dict_config)
    print("Created via design backend.")