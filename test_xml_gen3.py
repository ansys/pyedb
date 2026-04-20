import sys, re
sys.path.insert(0, 'src')
from pyedb.workflows.pdn_generator.generate_ipc2581_xml_only import XMLOnlyBoardGenerator

gen = XMLOnlyBoardGenerator(seed=42)
bcfg = gen.random_board_config(1, 'fpga_ddr', 'balanced')
xml_text = gen.build_board_xml(bcfg)
lines = xml_text.split('\n')

# Check Component packageRef in Step section (should NOT be empty)
comp_lines = [l for l in lines if '<Component ' in l and 'layerRef' in l]
empty = [l for l in comp_lines if 'packageRef=""' in l]
filled = [l for l in comp_lines if 'packageRef="' in l and 'packageRef=""' not in l]
print(f"Total Component elements in Step: {len(comp_lines)}")
print(f"  With proper packageRef: {len(filled)}")
print(f"  With empty packageRef:  {len(empty)}")
print(f"\nSample with proper packageRef:")
for l in filled[:3]: print(' ', l.strip())

# Check BOM RefDes (expected to have packageRef="")
refdes_lines = [l for l in lines if '<RefDes ' in l]
print(f"\nBOM RefDes count: {len(refdes_lines)} (all expected to have packageRef='')")

# Check Package elements
pkg_lines = [l for l in lines if '<Package ' in l and 'mountType=' in l]
print(f"\nPackage definitions: {len(pkg_lines)}")
for l in pkg_lines[:5]: print(' ', l.strip())

# Show a sample 2-pin pad set
sample = next((l for l in lines if 'geometry="Rectangle_0.5x0.5"' in l), None)
if sample:
    idx = lines.index(sample)
    print(f"\nSample 0402 pad Set:")
    for l in lines[idx:idx+6]: print(' ', l)
else:
    print("\nNo Rectangle_0.5x0.5 pad sets found!")

# Check Surface polygon (should NOT have closing segment back to 0,0 inside Surface)
in_surface = False
surface_polys = 0
closing_in_surface = 0
for l in lines:
    if '<Surface' in l: in_surface = True
    if '</Surface>' in l: in_surface = False; surface_polys += 1
    if in_surface and 'PolyStepSegment' in l and 'x="0" y="0"' in l:
        closing_in_surface += 1
print(f"\nSurfaces: {surface_polys}  Closing PolyStepSegments inside Surface: {closing_in_surface} (should be 0)")

