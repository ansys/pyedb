# Project Brief — PyEDB PDN-Only PCB Generator

## Goal
Build a PyEDB-based generator that automatically creates a valid, realistic PCB representing a PDN-only design focused on decoupling networks.

## Scope
The generator must create:
- layer stackup
- power/ground planes and feed traces
- discrete components
- decoupling capacitors

## Output
A new EDB/AEDB project containing:
- a board outline
- an even-layer stackup (default 4 or 6 layers)
- named nets: GND, VDD, VIN (optional)
- continuous GND plane
- one or more VDD copper areas or plane islands
- via structures connecting top-side decaps to internal planes
- physical capacitor components with realistic package/pad spacing
- a dummy load / sink landing pattern so decoupling placement is meaningful

## Design philosophy
- Prefer adjacent power/ground plane pairs.
- Minimize decap loop inductance.
- Place decaps close to the sink/load.
- Use short, wide copper between pad and via.
- Avoid arbitrary capacitor-value mixes; design around target impedance.
- Keep generator parameterized and reproducible.

## Parameters that must be configurable
- board size
- stackup preset (4L or 6L)
- copper thicknesses
- dielectric thicknesses
- VDD / GND net names
- load current estimate
- max ripple / target impedance
- decap library (package, value, ESR, ESL)
- number and placement pattern of capacitors
- via geometry preset