import sys, re
sys.path.insert(0, 'src')
from pyedb.workflows.pdn_generator.generate_ipc2581_xml_only import XMLOnlyBoardGenerator
import xml.etree.ElementTree as ET

gen = XMLOnlyBoardGenerator(seed=42)
for arch in ['fpga_ddr', 'storage_controller', 'mcu_pmic', 'mixed_signal']:
    bcfg = gen.random_board_config(1, arch, 'balanced')
    xml_text = gen.build_board_xml(bcfg)
    ET.fromstring(xml_text)  # validate well-formedness

    # Check key elements
    pkg_count   = xml_text.count('<Package ')
    pin_count   = xml_text.count('<Pin ')
    pad_sets    = len(re.findall(r'<Set[^>]+geometry="Rectangle_[^"]*"', xml_text))
    inline_rect = xml_text.count('<RectCenter') - xml_text.count('EntryStandard')
    surfaces    = xml_text.count('<Surface')
    closing_seg = xml_text.count('<PolyStepSegment') - xml_text.count('<PolyBegin')
    # packageRef check
    empty_pkgref = xml_text.count('packageRef=""')

    ids = re.findall(r'<EntryStandard[^>]+id="([^"]+)"', xml_text)
    dups = [x for x in ids if ids.count(x) > 1]

    print(f"{arch}:")
    print(f"  Packages={pkg_count}  Pins={pin_count}  PadSets={pad_sets}")
    print(f"  InlineRectCenter={inline_rect} (should be 0)")
    print(f"  Surfaces={surfaces}  EmptyPackageRef={empty_pkgref} (should be 0)")
    print(f"  DictStdDups={dups}")
    print()

print("ALL DONE")

