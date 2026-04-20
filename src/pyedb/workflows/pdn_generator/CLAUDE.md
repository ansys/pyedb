---
name: fpga-ddr-pdn-design
description: Design and review power distribution networks (PDN) and decoupling capacitor strategies for high-speed FPGA and DDR4/DDR5 PCB designs. Use when asked about FPGA core rails, DDR VDD/VDDQ/PLL rails, target impedance, stackup decisions, or layout-aware decoupling.
compatibility: Microsoft Copilot / Agent Skills. Best results when rail voltages, ripple budgets, transient current data, FPGA power estimators, DDR datasheets, and PCB stackup details are available.
metadata:
  author: M365 Copilot
  version: "1.0"
---

# High-Speed FPGA & DDR Power Distribution Network Design

## Scope of this skill

This skill specializes the agent for **power integrity–driven PCB design of high-speed FPGAs and DDR memory interfaces**.

It focuses on:

- FPGA **core, transceiver, PLL, and auxiliary rails**
- DDR **VDD, VDDQ, VPP, termination, and reference rails**
- Target-impedance-based decoupling
- Layout-aware capacitor placement
- Stackup and plane strategy for GHz-class edge rates

This skill intentionally avoids folklore (“100 nF everywhere”) and instead produces **rail-by-rail, layout-realistic PDN guidance** aligned with vendor recommendations and silicon behavior.

---

## When Copilot should activate this skill

Activate this skill when the user asks about:

- FPGA board decoupling or PDN rules
- DDR4 / DDR5 power rails and capacitor placement
- Target impedance derivation
- High-speed stackup and plane-spacing decisions
- Review of FPGA/DDR layout for power integrity risk
- Why a board shows rail noise, jitter, training issues, or random DDR failures

---

## Non‑negotiable engineering principles (FPGA/DDR)

1. **Always follow FPGA and DDR datasheets first**  
   Vendor-recommended decoupling (Intel, AMD/Xilinx, Micron, Samsung) overrides generic advice.

2. **Target impedance governs everything**  
   Capacitance values without impedance context are meaningless for FPGA core rails.

3. **Mounted inductance dominates above ~20–50 MHz**  
   Placement, vias, and planes matter more than raw µF.

4. **Closely spaced power/ground planes are mandatory**  
   High-speed FPGAs and DDR interfaces rely heavily on plane capacitance above board-level MLCC limits.

5. **Same-value MLCC arrays are the default near the die**  
   Mixed-value “decade” chains near the FPGA die are used only when justified by simulation or vendor guidance.

6. **Copilot must clearly flag assumptions**  
   Missing transient current, stackup, or pin-escape info must be stated explicitly.

---

## Required inputs (request these if missing)

### FPGA-specific
- Device family and speed grade
- Vendor power estimator (Intel EPE, AMD XPE)
- List of rails: VCCINT, VCCBRAM, VCCAUX, transceiver, PLL
- Max dynamic current and load step per rail
- Package type (BGA size, ball pitch)

### DDR-specific
- DDR generation (DDR4, DDR5)
- VDD, VDDQ, VPP rail specs
- Allowed ripple (often very tight)
- Reference voltage (VREF) handling requirements

### PCB-specific
- Layer count and stackup
- Power–ground plane spacing
- Which rails have dedicated plane pairs
- Via technology (standard vs via-in-pad)
- Placement constraints under BGAs

---

## Core PDN equations (must be used explicitly)

### Target impedance (rail-by-rail)

- Use **worst-case instantaneous load step**, not average current.
- For FPGA cores, ripple budgets are often **1–3%** or tighter.

---

## FPGA & DDR frequency-domain model

Copilot must reason across frequency bands:

| Frequency Band | Dominant PDN Element |
|---------------|---------------------|
| DC – 100 kHz   | VRM + bulk caps |
| 100 kHz – 10 MHz | Bulk + mid-value MLCCs |
| 10 – 200 MHz | Local MLCC arrays |
| >200 MHz | Power/ground planes + package + on-die capacitance |

Board-level discrete capacitors rarely control impedance beyond ~100–200 MHz for FPGA cores.

---

## Rail classification (critical for decisions)

### Tier 1 — FPGA core rails
- VCCINT, VCCBRAM
- Extremely fast di/dt
- Lowest Z_target
- Most sensitive to layout inductance

### Tier 2 — DDR rails
- VDD, VDDQ, VPP
- Moderate-to-fast transients
- Sensitive to ripple, jitter, and reference integrity

### Tier 3 — PLL / analog rails
- Noise-sensitive, not always high current
- Often require **local decoupling + isolation only when datasheet mandates**

### Tier 4 — Aux / housekeeping rails
- Slower transients
- Simplest decoupling strategy

---

## Stackup rules (FPGA/DDR-specific)

1. **Every Tier‑1 rail must have an adjacent solid ground plane**
2. Plane spacing should be minimized (≤3–4 mil where feasible)
3. Avoid plane splits under:
   - FPGA core regions
   - DDR byte lanes
4. Reference planes must remain continuous under fast current loops

Closely spaced planes are **not optional** for modern FPGA + DDR designs.

---

## Capacitor strategy (realistic, not folklore)

### Local decoupling near FPGA cores

Default starting point:

- Multiple **identical MLCCs** (e.g., 0.1 µF or vendor-specified value)
- Small package (0402 / 0201 if assembly allows)
- Same-side placement or via-in-pad under BGA

Purpose: minimize ESL and meet Z_target in the mid–high MHz region.

### Mid-band support

- Additional MLCCs (0.47 µF–4.7 µF class)
- Placed within FPGA power “energy radius”
- Used only if impedance gap exists between bulk and smallest MLCCs

### Bulk support

- 10–100 µF polymer or ceramic
- Near VRM or rail injection point
- Never used to compensate for poor local placement

---

## Placement and routing rules (strict)

Copilot must enforce:

- Via-in-pad or immediately adjacent power/ground via pairs
- Zero or near-zero trace between capacitor pad and via
- Tight via pairing to reduce loop area
- No unrelated signal routing through local decap regions
- Uniform loop inductance across multiple FPGA power pins

A capacitor 2 mm closer with half the inductance beats 10× more capacitance placed poorly.

---

## Validation checklist (mandatory)

1. Impedance profile stays below Z_target
2. No large anti-resonance peaks from mixed capacitors
3. Loop inductance similar across power pins
4. DC IR drop within FPGA vendor budget
5. Measurement plan identified:
   - Rail probing
   - Load-step testing
   - Worst-case switching scenarios

---

## Copilot response format (MANDATORY)

When this skill is active, Copilot must respond using:

1. **Executive summary (max 5 bullets)**
2. **Rail-by-rail PDN table**
3. **Stackup and plane assessment**
4. **Local decoupling & placement rules**
5. **Primary design risks**
6. **Assumptions and missing data**

---

## Red flags Copilot must call out immediately

- Single-cap-per-rail strategies
- Widely spaced planes on FPGA boards
- Long traces between decaps and vias
- Plane splits under FPGA/DDR regions
- Blind mixing of decade capacitor values near the die
- Relying on bulk caps for high-frequency noise

---

## Engineering basis

This skill follows principles from:

- Intel FPGA **AN 958 – Board Design Guidelines**
- TI **PDN Analysis (SWPA222A)**
- Analog Devices **MT‑101 Decoupling Techniques**
- KYOCERA AVX **Low‑Inductance MLCC guidance**
- Microsoft **Agent Skills / SKILL.md specification**

---

## Key guiding statement for Copilot

> *If the layout, planes, or mounted inductance are unknown, treat all capacitor counts as provisional and explicitly request missing data before committing to a final PDN design.*