{
    "header": {
        "version": "2.1",
        "converter": "",
        "original_filename": "",
        "corner": "typ",
        "date": ""
    },
    "units": {
        "spacing": "um",
        "width": "um",
        "thickness": "um",
        "rpsq": "ohm/sq",
        "rho": "ohm*um",
        "etching": "um",
        "loading_effect": "um",
        "bottom_etching": "um",
        "temperature": "C",
        "tc1": "1/C",
        "tc2": "1/C/C"
    },
    "process": {
        "name": "",
        "global_temperature": "25",
        "shrink_factor": 1.0,
        "background_ER": 4.0
    },
    "substrate": {
        "name": "substrate",
        "thickness": 80,
        "dielectric_constant": 11.7,
        "rho": 100000.0
    },
    "backplane": {
        "name": "backplane",
        "thickness": 1.0,
        "rho": 0.001
    },
    "layers": [
        {
            "type": "dielectric",
            "name": "ox0a",
            "ER": 3.9,
            "thickness": 0.05
        },
        
        {
            "type": "dielectric",
            "name": "ox1a",
            "ER": 3.9,
            "thickness": 0.3
        },
        {
            "type": "dielectric",
            "name": "ox1b",
            "ER": 3.9,
            "thickness": 0.005
        },
        {
            "type": "dielectric",
            "name": "Poly_ox",
            "ER": 4.0,
            "thickness": 0.2
        },
        {
            "type": "dielectric",
            "name": "ox2a",
            "ER": 4.0,
            "thickness": 0.5
        },
        {
            "type": "conductor",
            "name": "Metal1",
            "thickness": 0.6,
            "wmin": 0.01,
            "smin": 0.01,
            "rpsq": 0.07,
            "crt1": 0.00299,
            "crt2": -6.44e-7
        }
 ]
}
