import sys
sys.path.insert(0, 'src')
from pyedb.workflows.pdn_generator.generate_ipc2581_xml_only import XMLOnlyBoardGenerator

gen = XMLOnlyBoardGenerator(seed=42)
bcfg = gen.random_board_config(1, 'fpga_ddr', 'balanced')
xml_text = gen.build_board_xml(bcfg)

# Write full XML for inspection
with open('debug_output.xml', 'w', encoding='utf-8') as f:
    f.write(xml_text)

lines = xml_text.split('\n')
print(f"Total lines: {len(lines)}")

# Find key sections and print surrounding context
def show_around(keyword, label, count=15, max_hits=2):
    hits = [i for i,l in enumerate(lines) if keyword in l]
    print(f"\n=== {label} ({len(hits)} hits) ===")
    for idx in hits[:max_hits]:
        for l in lines[max(0,idx-1):idx+count]:
            print(l)
        print("...")

show_around('<Package ', 'First Package definitions', 20, 1)
show_around('packageRef="FPGA', 'Component with packageRef', 5, 2)
show_around('<Surface', 'Surface (plane fill)', 18, 1)
show_around('geometry="Rectangle_0.5', 'Pad Set for 0402', 7, 1)
show_around('<LayerFeature', 'LayerFeature elements', 5, 3)

