class General:
    def __init__(self, pedb, general_dict):
        self._pedb = pedb
        self.s_parameter_library = (
            general_dict["s_parameter_library"] if "s_parameter_library" in general_dict else None
        )
        self.spice_model_library = (
            general_dict["spice_model_library"] if "spice_model_library" in general_dict else None
        )
