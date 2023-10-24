import pyaedt
from pyaedt import Edb, Hfss3dLayout

# Ansys release version
desktop_version = "2023.2"

#download and copy the layout file from examples
temp_folder = pyaedt.generate_unique_folder_name()
targetfile = pyaedt.downloads.download_file('edb/ANSYS-HSD_V1.aedb', destination=temp_folder)

# loading EDB
edbapp = Edb(edbpath=targetfile, edbversion=desktop_version)

simple_hfss_setup = edbapp.create_hfss_setup("MySimpleSetup")
simple_hfss_setup.set_solution_single_frequency(frequency="5GHz", max_num_passes=30, max_delta_s=0.05)
simple_hfss_setup.add_frequency_sweep(name="MySweep", frequency_sweep=[["linear scale", "0GHz", "10GHz", "0.01GHz"]])

multi_freq_setup = edbapp.create_hfss_setup("MyMultiFreqSetup")
multi_freq_setup.set_solution_multi_frequencies(frequencies=["5GHz", "7GHz", "10GHz"], max_num_passes=30, max_delta_s=0.02)
multi_freq_setup.add_frequency_sweep(name="MySweep", frequency_sweep=[["linear scale", "0GHz", "20GHz", "0.01GHz"]])

broad_band_sweep = edbapp.create_hfss_setup("MyBroadbandSetup")
broad_band_sweep.set_solution_broadband(low_frequency="5GHz", high_frequency="10GHz", max_num_passes=20, max_delta_s=0.01)
broad_band_sweep.add_frequency_sweep(name="MySweep", frequency_sweep=[["linear scale", "0GHz", "20GHz", "0.01GHz"]])

# adding frequency sweeps
multi_freq_sweep_setup = edbapp.create_hfss_setup("MyMultiFrequencySweepSetup")
multi_freq_sweep_setup.set_solution_single_frequency(frequency="5GHz", max_num_passes=30, max_delta_s=0.02)
multi_freq_sweep_setup.add_frequency_sweep(frequency_sweep=[["linear count", "0", "1kHz", 1],
                                                ["log scale", "1kHz", "0.1GHz", 10],
                                                ["linear scale", "0.1GHz", "10GHz", "0.1GHz"],
                                                ])

# save and close project
edbapp.save_edb()
edbapp.close_edb()
hfss = Hfss3dLayout(projectname=targetfile, specified_version=desktop_version)
hfss.release_desktop(close_desktop=False, close_projects=False)

