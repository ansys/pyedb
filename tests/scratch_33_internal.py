import time

from pyedb import Edb
import os

aedbpath = r'c:\ansysdev\models\customers\Ericsson'
aedbcutout = r'c:\ansysdev\models\customers\Ericsson'
aedbfilein = 'inx1033721_r1a_20240531_00_pa38.aedb'
aedbfileout = 'inx1033721_r1a_pa38_cut_grpc_internal.aedb'
aedbinput = os.path.join(aedbpath, aedbfilein)
aedboutput = os.path.join(aedbcutout, aedbfileout)



edbapp = Edb(aedbinput, edbversion="2025.2",grpc=True)
edbapp.save_edb_as(aedboutput)


reference_nets = ["PGND",
                  ]

signal_nets = ["UNNAMED_3_CAPUNPOL5_I23_A<0>SPXO",
              "UNNAMED_3_CAPUNPOL5_I15_YSPXO",
              "AMP_SEL1",
              "UNNAMED_1_CAPUNPOL5ADW_I96_A_2",
              "UNNAMED_1_CAPUNPOL5ADW_I96_AB1",
              "UNNAMED_1_CAPUNPOL5ADW_I96_A",
              "UNNAMED_1_CAPUNPOL5ADW_I32_A_3",
              "UNNAMED_1_CAPUNPOL5ADW_I32_AB1",
              "UNNAMED_1_CAPUNPOL5ADW_I32_A",
              "DC_MBM_AUX_3V3",
              "UNNAMED_1_CAPUNPOL5ADW_I96_A_1",
              "UNNAMED_1_CAPUNPOL5ADW_I68_AB1",
              "UNNAMED_1_CAPUNPOL5ADW_I32_A_2",
              "UNNAMED_1_RESFIXED_I39_Y_2",
              "UNNAMED_1_RESFIXED_I39_A_2",
              "UNNAMED_1_CAPUNPOL5ADW_I45_Y",
              "UNNAMED_1_CAPUNPOL5ADW_I33_Y",
              "SW_NODE_MBM_AUX_3V3"
               ]

cutout_settings_type = "Conforming"
cutout_settings_Expansion = 0.01
cutout_settings_roundcorners = False
simulation_type = "1"
preserve_spice_component_bool = True
if simulation_type == "1" or simulation_type == "0":
    deactivate_only_bool = False
else:
    deactivate_only_bool = True
start = time.time()
if not edbapp.cutout(
            signal_list=signal_nets,
            reference_list=reference_nets,
            extent_type=cutout_settings_type,
            expansion_size=cutout_settings_Expansion ,
            use_round_corner=cutout_settings_roundcorners,
            open_cutout_at_end=False,
            number_of_threads=6,
            remove_single_pin_components=False,
            use_pyaedt_extent_computing=True,
            preserve_components_with_model=preserve_spice_component_bool,
            check_terminals=True,
            include_pingroups=True,
            include_voids_in_extents=True,
            use_pyaedt_cutout=False,
        ):
    success = False
    raise ValueError("Cutout failed.")

end = time.time()-start
edbapp.logger.info(f"Cutout time: {end} seconds")
edbapp.logger.info("Saving edb...")
edbapp.save_edb()
edbapp.logger.info("Closing edb...")
edbapp.close_edb()