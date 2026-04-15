# PDN Layout Rules for the Coding Agent

## Stackup Rules
1. Use an even number of layers.
2. Default to a 4-layer or 6-layer stackup.
3. Ensure at least one tightly coupled power/ground plane pair.
4. Prefer:
   - 4L: L1 signal/components, L2 GND, L3 VDD, L4 signal/components
   - 6L: L1 signal/components, L2 GND, L3 VDD, L4 signal/components, L5 GND, L6 signal/components
5. Keep GND continuous whenever possible.

## Plane Rules
1. Create a large continuous GND plane.
2. Create a VDD plane or island with direct access to the load region.
3. Do not place splits under critical current return paths.
4. Inset power islands from board edge unless edge behavior is a deliberate design feature.

## Decoupling Rules
1. Place the highest-frequency/local ceramic caps closest to the load pads.
2. Bulk capacitance should sit slightly farther from the sink than the smallest local caps.
3. Minimize pad-to-via distance.
4. Prefer one power via and one ground via per capacitor terminal region where space permits.
5. Use short/wide copper rather than long thin traces.
6. Do not scatter many arbitrary capacitor values; use a curated set derived from target impedance / anti-resonance considerations.

## Component Rules
1. Every capacitor is a physical 2-pin RLC component, not just abstract connectivity.
2. Each placed component must have:
   - refdes
   - part name
   - value
   - package / land pattern intent
   - net mapping: one pin to VDD, one pin to GND
3. Keep placement deterministic for reproducibility.

## Via Rules
1. Use realistic via drill / pad sizes for standard fabrication.
2. Put vias next to capacitor pads to reduce mounting inductance.
3. Keep current path compact from VDD plane -> cap -> GND plane.

## Generator Behavior Rules
1. Separate generator into:
   - config
   - stackup creation
   - nets
   - primitives
   - padstacks/vias
   - component placement
   - validation
2. All dimensions must be parameterized.
3. Use meters internally in Python when possible.
4. Provide a "draft" mode and a "realistic" mode.
5. Add assertions / sanity checks after each generation stage.