src.pyedb.siwave_core.product_properties
========================================

.. py:module:: src.pyedb.siwave_core.product_properties


Classes
-------

.. autoapisummary::

   src.pyedb.siwave_core.product_properties.SIwaveProperties
   src.pyedb.siwave_core.product_properties.AttribIndex


Module Contents
---------------

.. py:class:: SIwaveProperties

   .. py:attribute:: PIN_GROUP
      :value: 1



   .. py:attribute:: PART_NAME
      :value: 2



   .. py:attribute:: REF_DES_NAME
      :value: 3



   .. py:attribute:: PIN_NAME
      :value: 4



   .. py:attribute:: INTER_COMPONENT_PIN_GROUP
      :value: 5



   .. py:attribute:: DCIR_SIM_NAME
      :value: 100



   .. py:attribute:: DCIR_INIT_MESH_MAX_EDGE_LEN
      :value: 101



   .. py:attribute:: DCIR_MESH_BWS
      :value: 102



   .. py:attribute:: DCIR_MESH_VIAS
      :value: 103



   .. py:attribute:: DCIR_NUM_BW_FACETS
      :value: 104



   .. py:attribute:: DCIR_NUM_VIA_FACETS
      :value: 105



   .. py:attribute:: DCIR_ADAPTIVE_SOLVE
      :value: 106



   .. py:attribute:: DCIR_MIN_NUM_PASSES
      :value: 107



   .. py:attribute:: DCIR_MAX_NUM_PASSES
      :value: 108



   .. py:attribute:: DCIR_LOCAL_REFINEMENT
      :value: 109



   .. py:attribute:: DCIR_ENERGY_ERROR
      :value: 110



   .. py:attribute:: DCIR_REFINE_BWS
      :value: 111



   .. py:attribute:: DCIR_REFINE_VIAS
      :value: 112



   .. py:attribute:: DCIR_PLOT_JV
      :value: 113



   .. py:attribute:: DCIR_CKT_ELEM_CONTACT_R
      :value: 114



   .. py:attribute:: DCIR_ICEPAK_TEMP_FILE_PATH
      :value: 115



   .. py:attribute:: SOURCE_NEG_TERMINALS_TO_GROUND
      :value: 116



   .. py:attribute:: SOURCE_POS_TERMINALS_TO_GROUND
      :value: 117



   .. py:attribute:: DCIR_MIN_DC_PLANE_AREA_TO_MESH
      :value: 118



   .. py:attribute:: DCIR_MIN_DC_VOID_AREA_TO_MESH
      :value: 119



   .. py:attribute:: DCIR_COMPUTE_L
      :value: 120



   .. py:attribute:: NUM_CPUS_TO_USE
      :value: 200



   .. py:attribute:: USE_HPC_LICENSE
      :value: 201



   .. py:attribute:: HPC_LICENSE_VENDOR
      :value: 202



   .. py:attribute:: SYZ_COUPLING_COPLANE
      :value: 300



   .. py:attribute:: SYZ_COUPLING_INTRA_PLANE
      :value: 301



   .. py:attribute:: SYZ_COUPLING_SPLIT_PLANE
      :value: 302



   .. py:attribute:: SYZ_COUPLING_CAVITY
      :value: 303



   .. py:attribute:: SYZ_COUPLING_TRACE
      :value: 304



   .. py:attribute:: SYZ_COUPLING_XTALK_THRESH
      :value: 305



   .. py:attribute:: SY_ZMIN_VOID_MESH
      :value: 306



   .. py:attribute:: SYZ_MESH_REFINEMENT
      :value: 307



   .. py:attribute:: SYZ_TRACE_RETURN_CURRENT
      :value: 308



   .. py:attribute:: SYZ_INCLUDE_SOURCE_PARASITICS
      :value: 309



   .. py:attribute:: SYZ_USE_INF_GROUND_PLANE
      :value: 310



   .. py:attribute:: SYZ_INF_GROUND_PLANE_DIST
      :value: 311



   .. py:attribute:: SYZ_PERFORM_ERC
      :value: 312



   .. py:attribute:: SYZ_EXCLUDE_NON_FUNCTIONAL_PADS
      :value: 313



   .. py:attribute:: ICEPAK_SIM_NAME
      :value: 400



   .. py:attribute:: ICEPAK_DC_SIM_NAME
      :value: 401



   .. py:attribute:: ICEPAK_MESH_FIDELITY
      :value: 402



   .. py:attribute:: ICEPAK_CAB_ABOVE_PERCENT
      :value: 403



   .. py:attribute:: ICEPAK_CAB_BELOW_PERCENT
      :value: 404



   .. py:attribute:: ICEPAK_CAB_HORIZ_PERCENT
      :value: 405



   .. py:attribute:: ICEPAK_FLOW_STYLE
      :value: 406



   .. py:attribute:: ICEPAK_FLOW_SPEED
      :value: 407



   .. py:attribute:: ICEPAK_FLOW_DIR
      :value: 408



   .. py:attribute:: ICEPAK_FLOW_TEMP
      :value: 409



   .. py:attribute:: ICEPAK_COND_FLOW_SPEED_TOP
      :value: 410



   .. py:attribute:: ICEPAK_COND_FLOW_SPEED_BOTTOM
      :value: 411



   .. py:attribute:: ICEPAK_COND_FLOW_DIR_TOP
      :value: 412



   .. py:attribute:: ICEPAK_COND_FLOW_DIR_BOTTOM
      :value: 413



   .. py:attribute:: ICEPAK_COND_TEMP_TOP
      :value: 414



   .. py:attribute:: ICEPAK_COND_TEMP_BOTTOM
      :value: 415



   .. py:attribute:: ICEPAK_GRAV_X
      :value: 416



   .. py:attribute:: ICEPAK_GRAV_Y
      :value: 417



   .. py:attribute:: ICEPAK_GRAV_Z
      :value: 418



   .. py:attribute:: ICEPAK_AMBIENT_TEMP
      :value: 419



   .. py:attribute:: ICEPAK_COMPONENT_FILE
      :value: 420



   .. py:attribute:: ICEPAK_BRD_OUTLINE_FIDELITY_MM
      :value: 421



   .. py:attribute:: ICEPAK_USE_MINIMAL_COMP_DEFAULTS
      :value: 422



   .. py:attribute:: PSI_AC_SIM_NAME
      :value: 500



   .. py:attribute:: PSI_AC_SWEEP_STR
      :value: 501



   .. py:attribute:: PSI_SYZ_SIM_NAME
      :value: 502



   .. py:attribute:: PSI_SYZ_SWEEP_STR
      :value: 503



   .. py:attribute:: PSI_SYZ_INTERPOLATING
      :value: 504



   .. py:attribute:: PSI_SYZ_FAST_SWP
      :value: 505



   .. py:attribute:: PSI_SYZ_ADAPTIVE_SAMPLING
      :value: 506



   .. py:attribute:: PSI_SYZ_ENFORCE_DC
      :value: 507



   .. py:attribute:: PSI_SYZ_PORT_TYPE
      :value: 508



   .. py:attribute:: PSI_DISTRIBUTED
      :value: 509



   .. py:attribute:: PSI_NUM_CPUS
      :value: 510



   .. py:attribute:: PSI_USE_HPC
      :value: 511



   .. py:attribute:: PSI_HPC_LICENSE_TYPE
      :value: 512



   .. py:attribute:: PSI_SIM_SERVER_NAME
      :value: 513



   .. py:attribute:: PSI_SIM_SERVER_PORT
      :value: 514



   .. py:attribute:: PSI_SIMULATION_PREFERENCE
      :value: 515



   .. py:attribute:: PSI_MODEL_TYPE
      :value: 516



   .. py:attribute:: PSI_ENHANCED_BW_MODELING
      :value: 517



   .. py:attribute:: PSI_SURFACE_ROUGHNESS_MODEL
      :value: 518



   .. py:attribute:: PSI_RMS_ROUGHNESS
      :value: 519



   .. py:attribute:: PSI_TEMP_WORKING_DIR
      :value: 520



   .. py:attribute:: PSI_IGNORE_DUMMY_NETS
      :value: 521



   .. py:attribute:: PSI_PERFORM_ERC
      :value: 522



   .. py:attribute:: PSI_EXCLUDE_NONFUNCTIONAL_PADS
      :value: 523



   .. py:attribute:: PSI_AUTO_NET_SELECT
      :value: 524



   .. py:attribute:: PSI_IMPROVED_LOW_FREQ_RESIST
      :value: 525



   .. py:attribute:: PSI_SMALL_HOLE_SIZE
      :value: 526



   .. py:attribute:: PSI_SIGNAL_NET_ERROR_TOL
      :value: 527



   .. py:attribute:: PSI_CONDUCTOR_MODELING
      :value: 528



   .. py:attribute:: PSI_IMPROVED_METAL_LOSS
      :value: 529



   .. py:attribute:: PSI_IMPROVED_DIELECTRIC_FILL
      :value: 530



   .. py:attribute:: PSI_TOP_FILL_MATERIAL
      :value: 531



   .. py:attribute:: PSI_BOTTOM_FILL_MATERIAL
      :value: 532



   .. py:attribute:: PSI_PCB_MATERIAL
      :value: 533



   .. py:attribute:: PSI_INCLUDE_METAL_PLANE1
      :value: 534



   .. py:attribute:: PSI_INCLUDE_METAL_PLANE2
      :value: 535



   .. py:attribute:: PSI_FLOAT_METAL_PLANE1
      :value: 536



   .. py:attribute:: PSI_FLOAT_METAL_PLANE2
      :value: 537



   .. py:attribute:: PSI_H1
      :value: 538



   .. py:attribute:: PSI_H2
      :value: 539



   .. py:attribute:: CPA_SIM_NAME
      :value: 600



   .. py:attribute:: CPA_CHANNEL_SETUP
      :value: 601



   .. py:attribute:: CPA_ESD_R_MODEL
      :value: 602



   .. py:attribute:: CPA_USE_Q3D_SOLVER
      :value: 603



   .. py:attribute:: CPA_NET_PROCESSING_MODE
      :value: 604



   .. py:attribute:: CPA_NETS_TO_PROCESS
      :value: 605



   .. py:attribute:: CPA_CHANNEL_DIE_NAME
      :value: 610



   .. py:attribute:: CPA_CHANNEL_PIN_GROUPING_MODE
      :value: 611



   .. py:attribute:: CPA_CHANNEL_COMPONENT_EXPOSURE_CONFIG
      :value: 612



   .. py:attribute:: CPA_CHANNEL_VRM_SETUP
      :value: 613



   .. py:attribute:: CPA_REPORT_EXPORT_PATH
      :value: 614



   .. py:attribute:: CPA_RLCG_TABLE_EXPORT_PATH
      :value: 615



   .. py:attribute:: CPA_EXTRACTION_MODE
      :value: 616



   .. py:attribute:: CPA_CUSTOM_REFINEMENT
      :value: 617



   .. py:attribute:: CPA_EXTRACTION_FREQUENCY
      :value: 618



   .. py:attribute:: CPA_COMPUTE_CAPACITANCE
      :value: 619



   .. py:attribute:: CPA_COMPUTE_DC_PARAMS
      :value: 620



   .. py:attribute:: CPA_DC_PARAMS_COMPUTE_RL
      :value: 621



   .. py:attribute:: CPA_DC_PARAMS_COMPUTE_CG
      :value: 622



   .. py:attribute:: CPA_AC_PARAMS_COMPUTE_RL
      :value: 623



   .. py:attribute:: CPA_GROUND_PG_NETS_FOR_SI
      :value: 624



   .. py:attribute:: CPA_AUTO_DETECT_SMALL_HOLES
      :value: 625



   .. py:attribute:: CPA_SMALL_HOLE_DIAMETER
      :value: 626



   .. py:attribute:: CPA_MODEL_TYPE
      :value: 627



   .. py:attribute:: CPA_ADAPTIVE_REFINEMENT_CG_MAX_PASSES
      :value: 628



   .. py:attribute:: CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_ERROR
      :value: 629



   .. py:attribute:: CPA_ADAPTIVE_REFINEMENT_CG_PERCENT_REFINEMENT_PER_PASS
      :value: 630



   .. py:attribute:: CPA_ADAPTIVE_REFINEMENT_RL_MAX_PASSES
      :value: 631



   .. py:attribute:: CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_ERROR
      :value: 632



   .. py:attribute:: CPA_ADAPTIVE_REFINEMENT_RL_PERCENT_REFINEMENT_PER_PASS
      :value: 633



   .. py:attribute:: CPA_MIN_PLANE_AREA_TO_MESH
      :value: 634



   .. py:attribute:: CPA_MIN_VOID_AREA_TO_MESH
      :value: 635



   .. py:attribute:: CPA_VERTEX_SNAP_THRESHOLD
      :value: 636



   .. py:attribute:: CPA_TERMINAL_TYPE
      :value: 640



   .. py:attribute:: CPA_PLOC_CONFIG
      :value: 641



   .. py:attribute:: CPA_RETURN_PATH_NET_FOR_LOOP_PARAMS
      :value: 642



.. py:class:: AttribIndex

   .. py:attribute:: FROM_GROUP_NAME
      :value: 0



   .. py:attribute:: FROM_NET_NAME
      :value: 1



   .. py:attribute:: FROM_PIN_NAME
      :value: 2



   .. py:attribute:: FROM_PINS_ON_NET_NAME
      :value: 3



   .. py:attribute:: FROM_REFDES_NAME
      :value: 4



   .. py:attribute:: TO_GROUP_NAME
      :value: 5



   .. py:attribute:: TO_NET_NAME
      :value: 6



   .. py:attribute:: TO_PIN_NAME
      :value: 7



   .. py:attribute:: TO_PINS_ON_NET_NAME
      :value: 8



   .. py:attribute:: TO_REFDES_NAME
      :value: 9



   .. py:attribute:: TO_SOURCE_TYPE
      :value: 10



   .. py:attribute:: TO_SOURCE_MAG
      :value: 11



   .. py:attribute:: TO_RLC_TYPE
      :value: 12



   .. py:attribute:: TO_RLC_MAG
      :value: 13



   .. py:attribute:: REF_DES_NAME
      :value: 14



   .. py:attribute:: PIN_NAME
      :value: 15



   .. py:attribute:: PINS_ON_NET_NAME
      :value: 16



   .. py:attribute:: TERM_TYPE
      :value: 17



   .. py:attribute:: PIN_REGEX
      :value: 18



   .. py:attribute:: PART_REGEX
      :value: 19



   .. py:attribute:: REFDES_REGEX
      :value: 20



   .. py:attribute:: NET_REGEX
      :value: 21



   .. py:attribute:: FROM_PIN_ON_NET_NAME
      :value: 22



   .. py:attribute:: TO_PIN_ON_NET_NAME
      :value: 23



   .. py:attribute:: LAYER_NAME
      :value: 24



   .. py:attribute:: X_POS
      :value: 25



   .. py:attribute:: Y_POS
      :value: 26



   .. py:attribute:: NUM_ATTRIBS
      :value: 27



