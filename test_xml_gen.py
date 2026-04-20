import sys
sys.path.insert(0, 'src')
from pyedb.workflows.pdn_generator.generate_ipc2581_xml_only import XMLOnlyBoardGenerator
import re, xml.etree.ElementTree as ET

gen = XMLOnlyBoardGenerator(seed=42)
for arch in ['fpga_ddr', 'storage_controller', 'mcu_pmic', 'mixed_signal']:
    bcfg = gen.random_board_config(1, arch, 'balanced')
    xml_text = gen.build_board_xml(bcfg)
    ET.fromstring(xml_text)  # validate well-formedness
    ids = re.findall(r'EntryStandard[^>]+id="([^"]+)"', xml_text)
    dups = [x for x in ids if ids.count(x) > 1]
    pad_count = xml_text.count('<RectCenter')
    body_count = xml_text.count('<Polyline')
    surf_count = xml_text.count('<Surface')
    print(f"{arch}: OK  pads={pad_count}  polylines={body_count}  surfaces={surf_count}  dict_ids={ids}  dups={dups}")
print("ALL DONE")

