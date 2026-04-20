import sys, re
sys.path.insert(0, 'src')
from pyedb.workflows.pdn_generator.generate_ipc2581_xml_only import XMLOnlyBoardGenerator
import xml.etree.ElementTree as ET

gen = XMLOnlyBoardGenerator(seed=42)

for arch in ['fpga_ddr', 'mcu_pmic', 'mixed_signal', 'storage_controller']:
    bcfg = gen.random_board_config(1, arch, 'balanced')
    xml_text = gen.build_board_xml(bcfg)
    ET.fromstring(xml_text)   # must not raise

    lines = xml_text.split('\n')

    # Surface polygon closing segment check
    in_surf, close_ok, surf_total = False, 0, 0
    for l in lines:
        if '<Surface' in l:   in_surf = True
        if '</Surface>' in l: in_surf = False; surf_total += 1
        if in_surf and 'PolyStepSegment' in l and 'x="0" y="0"' in l:
            close_ok += 1

    # Package Outline closing segment check
    in_outline, outline_close = False, 0
    for l in lines:
        if '<Outline' in l:    in_outline = True
        if '</Outline>' in l:  in_outline = False
        if in_outline and 'PolyStepSegment' in l:
            # Count the ones that close back to the PolyBegin corner
            # (we just count any closing segment — it should be x="-hw" y="-hh")
            outline_close += 1

    pkg_count  = xml_text.count('<Package ')
    pad_sets   = len(re.findall(r'<Set[^>]+geometry="Rectangle_', xml_text))
    empty_ref  = sum(1 for l in lines if '<Component ' in l and 'layerRef' in l and 'packageRef=""' in l)

    print(f"{arch}:")
    print(f"  Surfaces={surf_total}  Surfaces-with-close={close_ok}  (should equal surf_total)")
    print(f"  Packages={pkg_count}  PadSets={pad_sets}  EmptyPackageRef={empty_ref} (must be 0)")
    print()

print("ALL DONE")

