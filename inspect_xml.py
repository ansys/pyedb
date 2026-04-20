import sys
sys.path.insert(0, 'src')
from pyedb.workflows.pdn_generator.generate_ipc2581_xml_only import XMLOnlyBoardGenerator

gen = XMLOnlyBoardGenerator(seed=42)
bcfg = gen.random_board_config(1, 'fpga_ddr', 'balanced')
xml_text = gen.build_board_xml(bcfg)

lines = xml_text.split('\n')

# Show Component sections (first 3)
print("=== Component elements ===")
comp_lines = [i for i,l in enumerate(lines) if '<Component' in l]
for idx in comp_lines[:3]:
    for l in lines[idx:idx+5]:
        print(l)
    print()

# Show first pad Set in TOP layer
print("\n=== First pad Set in TOP LayerFeature ===")
top_lf = next(i for i,l in enumerate(lines) if 'LayerFeature' in l and 'layerRef="TOP"' in l)
# find first geometry= Set after the TOP layerfeature
for i in range(top_lf, min(top_lf+3000, len(lines))):
    if 'geometry="Rectangle_' in lines[i]:
        for l in lines[i:i+8]:
            print(l)
        break

# Show power plane Surface in L4_PWR
print("\n=== L4_PWR plane Surface ===")
pwr_lf = next(i for i,l in enumerate(lines) if 'LayerFeature' in l and 'L4_PWR' in l)
for l in lines[pwr_lf:pwr_lf+20]:
    print(l)

