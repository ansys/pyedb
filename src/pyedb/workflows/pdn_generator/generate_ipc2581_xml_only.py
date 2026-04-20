"""
generate_ipc2581_xml_only.py
Synthetic IPC-2581 board generator focused on realistic PDN (Power Delivery Network) designs.
Each generated board has:
  - multiple power rails with dedicated VRMs
  - bulk capacitors (electrolytic + MLCC) near VRM outputs
  - local MLCC decoupling rings around every IC power pin cluster
  - ferrite beads and feedback resistors on each rail
  - proper trace widths (power: 0.3-0.5 mm, signal: 0.1-0.15 mm)
  - vias between layers for inter-layer power distribution
  - ground planes on dedicated layers
"""
from __future__ import annotations
import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET

try:
    import yaml  # type: ignore
except Exception:
    yaml = None

IPC2581_NS = 'http://webstds.ipc.org/2581'
ET.register_namespace('', IPC2581_NS)

# ---------------------------------------------------------------------------
# Package physical sizes  (width_mm, height_mm)
# ---------------------------------------------------------------------------
PACKAGE_BODY: Dict[str, Tuple[float, float]] = {
    'FPGA_BGA256':   (17.0, 17.0),
    'DDR_BGA96':     (10.5, 10.5),
    'MCU_QFP100':    (14.0, 14.0),
    'BUCK_QFN48':    (7.0,  7.0),
    'LDO_SOT223':    (3.5,  3.7),
    'LDO_DFN8':      (3.0,  3.0),
    'PMIC_QFN32':    (5.0,  5.0),
    'NAND_TSOP48':   (18.0, 7.2),
    'FLASH_SOIC8':   (5.0,  4.0),
    'SATA_CONN':     (20.0, 6.5),
    'ETH_MAGJACK':   (22.0, 16.0),
    'CAP_0402':      (1.0,  0.5),
    'CAP_0603':      (1.6,  0.8),
    'CAP_1210':      (3.2,  2.5),
    'CAP_TANT_D':    (7.3,  4.3),
    'RES_0402':      (1.0,  0.5),
    'RES_0603':      (1.6,  0.8),
    'FERRITE_0603':  (1.6,  0.8),
    'FERRITE_1806':  (4.5,  1.6),
    'INDUCTOR_1212': (3.2,  3.2),
    'INDUCTOR_2020': (5.0,  5.0),
}

HIGH_SPEED_CLASSES = {
    'DDR_DATA_CLASS', 'DDR_DIFF_CLASS', 'SATA_DIFF_CLASS',
    'ETH_DIFF_CLASS', 'ADC_CLK_CLASS',
}

# ---------------------------------------------------------------------------
# SMD pad geometry for 2-pin discrete components
# (pad_width_mm, pad_height_mm, pin_pitch_mm)
# ---------------------------------------------------------------------------
PAD_2PIN: Dict[str, Tuple[float, float, float]] = {
    'CAP_0402':      (0.50, 0.50, 1.00),
    'CAP_0603':      (0.70, 0.90, 1.60),
    'CAP_1210':      (1.50, 2.80, 2.50),
    'CAP_TANT_D':    (2.50, 4.00, 5.50),
    'RES_0402':      (0.50, 0.50, 1.00),
    'RES_0603':      (0.70, 0.90, 1.60),
    'FERRITE_0603':  (0.70, 0.90, 1.60),
    'FERRITE_1806':  (1.40, 1.80, 4.00),
    'INDUCTOR_1212': (1.00, 1.20, 2.20),
    'INDUCTOR_2020': (1.50, 2.00, 3.50),
}

# IC / connector body outline scale (fraction of body dimensions)
IC_BODY_SCALE = 0.9   # rendered outline is 90 % of body size

LAYER_COLORS: Dict[str, Tuple[int, int, int]] = {
    'TOP':    (196, 171, 30),   'BOTTOM': (183, 191, 145),
    'L2_GND': (152, 143, 192),  'L3_SIG': (141, 225, 218),
    'L4_PWR': (232, 149, 131),  'L5_GND': (131, 174, 142),
    'L5_SIG': (200, 180, 100),  'L6_GND': (140, 160, 220),
    'L6_SIG': (200, 180, 100),  'L7_SIG': (160, 200, 180),
    'L7_PWR': (180, 130, 200),  'L8_GND': (140, 160, 220),
    'L9_SIG': (220, 160, 140),  'L3_PWR': (232, 149, 131),
}
UNNAMED_RGB = (127, 127, 127)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_cfg(path: str) -> Dict:
    p = Path(path)
    text = p.read_text(encoding='utf-8')
    if p.suffix.lower() == '.json':
        return json.loads(text)
    if p.suffix.lower() in {'.yaml', '.yml'}:
        if yaml is None:
            raise RuntimeError('PyYAML not available.')
        return yaml.safe_load(text)
    try:
        return json.loads(text)
    except Exception:
        if yaml is None:
            raise
        return yaml.safe_load(text)


def normalize_dist(d: Dict[str, float]) -> Dict[str, float]:
    s = sum(max(v, 0.0) for v in d.values())
    if s <= 0:
        n = max(1, len(d))
        return {k: 1.0 / n for k in d}
    return {k: max(v, 0.0) / s for k, v in d.items()}


def pick_weighted(rng: random.Random, d: Dict[str, float]) -> str:
    norm = normalize_dist(d)
    r = rng.random()
    acc = 0.0
    for k, p in norm.items():
        acc += p
        if r <= acc:
            return k
    return list(norm)[-1]


def bga_perimeter_pos(cx: float, cy: float,
                      bga_w: float, bga_h: float,
                      n: int, pitch: float = 1.5, margin: float = 1.3,
                      n_rows: int = 2, row_pitch: float = 1.5
                      ) -> List[Tuple[float, float]]:
    """Place caps in rectangular rows just outside a BGA perimeter (no circles).

    Caps are distributed across all four sides in order: south, north, west, east.
    Multiple rows are populated inward-to-outward.  Matches real FPGA PDN practice
    where MLCCs sit immediately outside the keepout with minimum mounted inductance.
    """
    positions: List[Tuple[float, float]] = []
    half_w = bga_w / 2.0
    half_h = bga_h / 2.0
    for row in range(n_rows):
        row_off_w = half_w + margin + row * row_pitch
        row_off_h = half_h + margin + row * row_pitch
        # south row – primary power entry edge
        n_side_h = max(1, int(round(bga_w / pitch)))
        start_x = cx - (n_side_h - 1) * pitch / 2.0
        for i in range(n_side_h):
            positions.append((start_x + i * pitch, cy - row_off_h))
        # north row
        for i in range(n_side_h):
            positions.append((start_x + i * pitch, cy + row_off_h))
        # west column
        n_side_v = max(1, int(round(bga_h / pitch)))
        start_y = cy - (n_side_v - 1) * pitch / 2.0
        for j in range(n_side_v):
            positions.append((cx - row_off_w, start_y + j * pitch))
        # east column
        for j in range(n_side_v):
            positions.append((cx + row_off_w, start_y + j * pitch))
    return positions[:max(1, n)]


def grid_pos(ox: float, oy: float, cols: int, rows: int,
             px: float, py: float) -> List[Tuple[float, float]]:
    return [(ox + c*px, oy + r*py) for r in range(rows) for c in range(cols)]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Comp:
    refdes: str
    part: str
    pkg: str
    x: float
    y: float
    layer: str
    pin_count: int
    value: str


@dataclass
class Net:
    name: str
    class_name: Optional[str]
    pins: List[Tuple[str, str]]
    current_a: float = 0.0

    @property
    def trace_width(self) -> float:
        if self.current_a >= 10: return 0.5
        if self.current_a >= 6:  return 0.4
        if self.current_a >= 3:  return 0.3
        if self.current_a >= 1:  return 0.25
        if self.class_name in HIGH_SPEED_CLASSES: return 0.1
        return 0.15


@dataclass
class BoardConfig:
    name: str
    archetype: str
    width_mm: float
    height_mm: float
    layer_count: int
    board_thickness_mm: float
    seed: int
    variant: str = 'balanced'


# ---------------------------------------------------------------------------
# PDN builder
# ---------------------------------------------------------------------------

class PDNBuilder:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self._idx: Dict[str, int] = {}

    def _next(self, pfx: str) -> str:
        self._idx[pfx] = self._idx.get(pfx, 0) + 1
        return f'{pfx}{self._idx[pfx]}'

    # ── component factories ───────────────────────────────────────────

    def buck(self, rd: str, x: float, y: float) -> Comp:
        return Comp(rd, f'SYNTH_BUCK_{rd}', 'BUCK_QFN48', x, y, 'TOP', 48, 'IC')

    def ldo(self, rd: str, x: float, y: float) -> Comp:
        return Comp(rd, f'SYNTH_LDO_{rd}', 'LDO_DFN8', x, y, 'TOP', 8, 'IC')

    def inductor(self, x: float, y: float) -> Comp:
        rd = self._next('L')
        return Comp(rd, f'SYNTH_IND_{rd}', 'INDUCTOR_1212', x, y, 'TOP', 2, 'passive')

    def bulk(self, x: float, y: float, val: str = '100uF') -> Comp:
        rd = self._next('C')
        pkg = 'CAP_TANT_D' if float(val.replace('uF','')) >= 47 else 'CAP_1210'
        return Comp(rd, f'SYNTH_CAP_{val}', pkg, x, y, 'TOP', 2, val)

    def mlcc(self, x: float, y: float, val: str = '100nF') -> Comp:
        rd = self._next('C')
        return Comp(rd, f'SYNTH_MLCC_{val}', 'CAP_0402', x, y, 'TOP', 2, val)

    def ferrite(self, x: float, y: float) -> Comp:
        rd = self._next('FB')
        return Comp(rd, f'SYNTH_FB_{rd}', 'FERRITE_0603', x, y, 'TOP', 2, 'FB')

    def res(self, x: float, y: float, val: str = '10K') -> Comp:
        rd = self._next('R')
        return Comp(rd, f'SYNTH_RES_{val}', 'RES_0402', x, y, 'TOP', 2, val)

    # ── rail builder ─────────────────────────────────────────────────

    def rail(self,
             comps: List[Comp], nets: List[Net],
             name: str, current_a: float,
             vrm: Comp, vrm_pin: str,
             ic_pins: List[Tuple[str, str]],
             bulk_xy: List[Tuple[float, float]],
             mlcc_xy: List[Tuple[float, float]],
             bulk_val: str = '100uF',
             mlcc_val: str = '100nF',
             add_inductor: bool = False,
             add_ferrite: bool = False) -> None:
        """Wire one complete PDN rail: VRM → inductor? → bulk → ferrite? → MLCC → IC."""
        rail_pins: List[Tuple[str, str]] = [(vrm.refdes, vrm_pin)]

        if add_inductor:
            L = self.inductor(vrm.x + 4.5, vrm.y)
            comps.append(L)
            rail_pins += [(L.refdes, '1'), (L.refdes, '2')]

        bulk_comps = []
        for bx, by in bulk_xy:
            C = self.bulk(bx, by, bulk_val)
            comps.append(C); bulk_comps.append(C)
            rail_pins.append((C.refdes, '1'))

        if add_ferrite and mlcc_xy:
            cx = sum(x for x, _ in mlcc_xy) / len(mlcc_xy)
            cy = sum(y for _, y in mlcc_xy) / len(mlcc_xy)
            FB = self.ferrite(cx - 3.5, cy)
            comps.append(FB)
            rail_pins += [(FB.refdes, '1'), (FB.refdes, '2')]

        for mx, my in mlcc_xy:
            C = self.mlcc(mx, my, mlcc_val)
            comps.append(C)
            rail_pins.append((C.refdes, '1'))

        rail_pins.extend(ic_pins)
        nets.append(Net(name, None, rail_pins, current_a))

        # Feedback divider
        R1 = self.res(vrm.x - 3.5, vrm.y,       '47.5K')
        R2 = self.res(vrm.x - 3.5, vrm.y - 1.8, '10K')
        comps += [R1, R2]
        nets.append(Net(f'{name}_FB', None,
                        [(vrm.refdes, str(vrm.pin_count - 1)),
                         (R1.refdes, '1'), (R1.refdes, '2'), (R2.refdes, '1')],
                        0.001))

    # ── GND net ──────────────────────────────────────────────────────

    def gnd(self, comps: List[Comp], nets: List[Net],
            extra_pins: List[Tuple[str, str]]) -> None:
        gnd_pins = [(c.refdes, '2') for c in comps
                    if any(k in c.part for k in ('CAP', 'MLCC', 'FB', 'IND'))]
        gnd_pins += [(c.refdes, '1') for c in comps
                     if any(k in c.part for k in ('BUCK', 'LDO'))]
        gnd_pins.extend(extra_pins)
        if gnd_pins:
            nets.append(Net('GND', None, gnd_pins, 0.0))

    # ── archetypes ───────────────────────────────────────────────────

    def build_fpga_ddr(self, cfg: BoardConfig, vp: Dict) -> Tuple[List[Comp], List[Net]]:
        rng = self.rng; p = vp; w, h = cfg.width_mm, cfg.height_mm
        comps: List[Comp] = []; nets: List[Net] = []

        # ICs
        fpga = Comp('U1', 'SYNTH_FPGA_XC7K325T', 'FPGA_BGA256', w*0.42, h*0.50, 'TOP', 256, 'IC')
        comps.append(fpga)
        ddr_n = max(1, int(round(rng.choice([1,2,2]) * p['complexity_mul'])))
        ddrs = [Comp(f'U{2+i}', 'SYNTH_DDR4_MT40A512M16', 'DDR_BGA96',
                     w*0.76, h*(0.28+i*0.22), 'TOP', 96, 'IC') for i in range(ddr_n)]
        comps.extend(ddrs)
        nand_n = max(2, int(round(rng.choice([2,4]) * p['complexity_mul'])))
        nands = [Comp(f'U{20+i}', 'SYNTH_NAND_MT29F', 'NAND_TSOP48',
                      w*0.12, h*(0.14+i*0.09), 'TOP', 48, 'IC') for i in range(nand_n)]
        comps.extend(nands)

        # VRMs
        vrm_vint = self.buck('U_VINT', w*0.20, h*0.18); comps.append(vrm_vint)
        vrm_vaux = self.ldo( 'U_VAUX', w*0.12, h*0.82); comps.append(vrm_vaux)
        vrm_vcco = self.buck('U_VCCO', w*0.32, h*0.12); comps.append(vrm_vcco)
        vrm_vddq = self.buck('U_VDDQ', w*0.76, h*0.82); comps.append(vrm_vddq)
        vrm_vtt  = self.ldo( 'U_VTT',  w*0.88, h*0.82); comps.append(vrm_vtt)
        vrm_3v3  = self.ldo( 'U_3V3',  w*0.06, h*0.50); comps.append(vrm_3v3)

        # VCCINT 0.95V 15A  — dense perimeter grid on all four FPGA BGA sides
        self.rail(comps, nets, 'VCCINT', 15.0, vrm_vint, '5',
                  [(fpga.refdes, str(i)) for i in range(1, 17)],
                  grid_pos(w*0.20, h*0.28, 2, 2, 4.5, 4.5),
                  bga_perimeter_pos(fpga.x, fpga.y, 17.0, 17.0,
                                    int(round(32*p['pdn_mul'])), pitch=1.5, margin=1.2, n_rows=2),
                  '100uF', '100nF', add_inductor=True)

        # VCCAUX 1.8V 3A  — single perimeter row, sparser
        self.rail(comps, nets, 'VCCAUX', 3.0, vrm_vaux, '5',
                  [(fpga.refdes, str(i)) for i in range(17, 25)],
                  [(fpga.x-18, fpga.y+8), (fpga.x-18, fpga.y+3)],
                  bga_perimeter_pos(fpga.x, fpga.y, 17.0, 17.0,
                                    int(round(16*p['pdn_mul'])), pitch=2.0, margin=2.8, n_rows=1),
                  '47uF', '100nF', add_ferrite=True)

        # VCCO 2.5V 5A  — south perimeter row only (I/O bank edge)
        self.rail(comps, nets, 'VCCO_BANK0', 5.0, vrm_vcco, '5',
                  [(fpga.refdes, str(i)) for i in range(25, 37)],
                  grid_pos(w*0.32, h*0.22, 3, 1, 4.0, 0),
                  bga_perimeter_pos(fpga.x, fpga.y, 17.0, 17.0,
                                    int(round(20*p['pdn_mul'])), pitch=1.5, margin=4.5, n_rows=1),
                  '22uF', '100nF')

        # VDDQ 1.35V 8A (DDR)  — west side of each DDR chip (facing FPGA = shortest loop)
        ddr_vddq_pins = [(d.refdes, str(i)) for d in ddrs for i in range(1, 9)]
        local_vddq: List[Tuple[float,float]] = []
        for d in ddrs:
            local_vddq += bga_perimeter_pos(d.x, d.y, 10.5, 10.5,
                                            int(round(12*p['pdn_mul'])), pitch=1.5, margin=1.2, n_rows=1)
        self.rail(comps, nets, 'VDDQ', 8.0, vrm_vddq, '5',
                  ddr_vddq_pins,
                  grid_pos(w*0.76, h*0.72, 2, 2, 4.5, 4.0),
                  local_vddq, '47uF', '100nF', add_inductor=True)

        # VTT 0.675V 3A  — north perimeter of each DDR (termination side)
        ddr_vtt_pins = [(d.refdes, str(i)) for d in ddrs for i in range(9, 13)]
        local_vtt: List[Tuple[float,float]] = []
        for d in ddrs:
            local_vtt += bga_perimeter_pos(d.x, d.y, 10.5, 10.5,
                                           8, pitch=1.5, margin=2.8, n_rows=1)
        self.rail(comps, nets, 'VTT', 3.0, vrm_vtt, '5',
                  ddr_vtt_pins,
                  [(w*0.88, h*0.72), (w*0.93, h*0.72)],
                  local_vtt, '10uF', '10nF', add_ferrite=True)

        # VCC_3V3 2.0A  — outer perimeter row (housekeeping rail, Tier 4)
        nand_3v3_pins = [(n.refdes, '48') for n in nands]
        self.rail(comps, nets, 'VCC_3V3', 2.0, vrm_3v3, '5',
                  [(fpga.refdes, str(i)) for i in range(37, 45)] + nand_3v3_pins,
                  [(w*0.06, h*0.38), (w*0.06, h*0.30)],
                  bga_perimeter_pos(fpga.x, fpga.y, 17.0, 17.0,
                                    int(round(12*p['pdn_mul'])), pitch=2.5, margin=6.0, n_rows=1),
                  '22uF', '100nF')

        # GND
        gnd_extra = [(fpga.refdes, str(i)) for i in range(45, 65)]
        gnd_extra += [(d.refdes, str(i)) for d in ddrs for i in range(13, 21)]
        self.gnd(comps, nets, gnd_extra)

        # High-speed DDR nets
        for i, d in enumerate(ddrs):
            for b in range(8):
                nets.append(Net(f'DDR{i}_DQ{b}', 'DDR_DATA_CLASS',
                                [(fpga.refdes, str(100+i*16+b)), (d.refdes, str(30+b))], 0.01))
            nets.append(Net(f'DDR{i}_CK_P', 'DDR_DIFF_CLASS',
                            [(fpga.refdes, str(140+i*2)), (d.refdes, '50')], 0.005))
            nets.append(Net(f'DDR{i}_CK_N', 'DDR_DIFF_CLASS',
                            [(fpga.refdes, str(141+i*2)), (d.refdes, '51')], 0.005))
        for i, n in enumerate(nands):
            nets.append(Net(f'NAND{i}_IO0', None,
                            [(fpga.refdes, str(200+i*4)), (n.refdes, '10')], 0.01))

        # SATA connector
        J1 = Comp('J1', 'SYNTH_SATA_CONN', 'SATA_CONN', w*0.97, h*0.50, 'TOP', 22, 'IO')
        comps.append(J1)
        for sig, p1, p2 in [('SATA_TX_P','200','1'),('SATA_TX_N','201','2'),
                             ('SATA_RX_P','202','3'),('SATA_RX_N','203','4')]:
            nets.append(Net(sig, 'SATA_DIFF_CLASS', [(fpga.refdes, p1), (J1.refdes, p2)], 0.02))

        return comps, nets

    def build_storage_controller(self, cfg: BoardConfig, vp: Dict) -> Tuple[List[Comp], List[Net]]:
        rng = self.rng; p = vp; w, h = cfg.width_mm, cfg.height_mm
        comps: List[Comp] = []; nets: List[Net] = []

        ctrl = Comp('U1','SYNTH_CTRL_BGA256','FPGA_BGA256', w*0.40, h*0.50,'TOP',256,'IC')
        dram = Comp('U2','SYNTH_DRAM_BGA96', 'DDR_BGA96',  w*0.66, h*0.42,'TOP',96,'IC')
        comps += [ctrl, dram]
        nand_n = max(4, int(round(rng.choice([4,8]) * p['complexity_mul'])))
        nands  = [Comp(f'U{10+i}','SYNTH_NAND_MT29','NAND_TSOP48',
                       w*0.12, h*(0.12+i*0.08),'TOP',48,'IC') for i in range(nand_n)]
        comps.extend(nands)
        flash = Comp('U3','SYNTH_NOR_FLASH','FLASH_SOIC8', w*0.18, h*0.18,'TOP',8,'IC')
        comps.append(flash)

        vrm_core = self.buck('U_VCORE', w*0.20, h*0.20); comps.append(vrm_core)
        vrm_io   = self.ldo( 'U_VIO',   w*0.08, h*0.70); comps.append(vrm_io)
        vrm_nand = self.ldo( 'U_VNAND', w*0.08, h*0.35); comps.append(vrm_nand)
        vrm_ddr  = self.buck('U_VDDR',  w*0.66, h*0.78); comps.append(vrm_ddr)

        self.rail(comps, nets, 'VCC_CORE', 12.0, vrm_core, '5',
                  [(ctrl.refdes, str(i)) for i in range(1,20)],
                  grid_pos(w*0.22, h*0.30, 2, 2, 4.5, 4.0),
                  bga_perimeter_pos(ctrl.x, ctrl.y, 17.0, 17.0,
                                    int(round(28*p['pdn_mul'])), pitch=1.5, margin=1.2, n_rows=2),
                  '100uF', '100nF', add_inductor=True)

        self.rail(comps, nets, 'VCC_IO', 4.0, vrm_io, '5',
                  [(ctrl.refdes, str(i)) for i in range(20,32)],
                  [(w*0.08, h*0.60), (w*0.08, h*0.55)],
                  bga_perimeter_pos(ctrl.x, ctrl.y, 17.0, 17.0,
                                    int(round(16*p['pdn_mul'])), pitch=2.0, margin=2.8, n_rows=1),
                  '22uF', '100nF', add_ferrite=True)

        nand_pins = [(n.refdes, p2) for n in nands for p2 in ['48','24']]
        local_nand = [(n.x+dx, n.y+dy) for n in nands
                      for dx,dy in [(1.5,2),(-1.5,2),(1.5,-2),(-1.5,-2)]]
        self.rail(comps, nets, 'VNAND', 3.0, vrm_nand, '5',
                  nand_pins, [(w*0.08, h*0.28), (w*0.08, h*0.22)],
                  local_nand, '10uF', '100nF')

        self.rail(comps, nets, 'VDDR', 6.0, vrm_ddr, '5',
                  [(dram.refdes, str(i)) for i in range(1,9)],
                  grid_pos(w*0.66, h*0.68, 2, 2, 4.0, 3.5),
                  bga_perimeter_pos(dram.x, dram.y, 10.5, 10.5,
                                    int(round(14*p['pdn_mul'])), pitch=1.5, margin=1.2, n_rows=1),
                  '47uF', '100nF', add_inductor=True)

        gnd_extra  = [(ctrl.refdes, str(i)) for i in range(32,48)]
        gnd_extra += [(dram.refdes, str(i)) for i in range(9,17)]
        self.gnd(comps, nets, gnd_extra)

        J1 = Comp('J1','SYNTH_SATA','SATA_CONN', w*0.97, h*0.50,'TOP',22,'IO')
        comps.append(J1)
        for sig,p1,p2 in [('SATA_TX_P','100','1'),('SATA_TX_N','101','2'),
                           ('SATA_RX_P','102','3'),('SATA_RX_N','103','4')]:
            nets.append(Net(sig,'SATA_DIFF_CLASS',[(ctrl.refdes,p1),(J1.refdes,p2)],0.02))
        return comps, nets

    def build_mcu_pmic(self, cfg: BoardConfig, vp: Dict) -> Tuple[List[Comp], List[Net]]:
        rng = self.rng; p = vp; w, h = cfg.width_mm, cfg.height_mm
        comps: List[Comp] = []; nets: List[Net] = []

        mcu   = Comp('U1','SYNTH_MCU_STM32H7','MCU_QFP100', w*0.45,h*0.50,'TOP',100,'IC')
        pmic  = Comp('U2','SYNTH_PMIC_LP8758', 'PMIC_QFN32', w*0.22,h*0.72,'TOP',32,'IC')
        flash = Comp('U3','SYNTH_QSPI_FLASH',  'FLASH_SOIC8',w*0.22,h*0.25,'TOP',8,'IC')
        J1    = Comp('J1','SYNTH_ETH_MAGJACK', 'ETH_MAGJACK',w*0.88,h*0.50,'TOP',12,'IO')
        comps += [mcu, pmic, flash, J1]

        vrm_core = pmic; vrm_3v3 = pmic  # PMIC provides all rails

        self.rail(comps, nets, 'VDD_MCU_CORE', 1.0, pmic, '10',
                  [(mcu.refdes, str(i)) for i in range(1,9)],
                  [(w*0.30, h*0.62), (w*0.30, h*0.57)],
                  bga_perimeter_pos(mcu.x, mcu.y, 14.0, 14.0,
                                    int(round(16*p['pdn_mul'])), pitch=1.5, margin=1.2, n_rows=1),
                  '22uF', '100nF')

        self.rail(comps, nets, 'VDD_3V3', 0.8, pmic, '12',
                  [(mcu.refdes, str(i)) for i in range(9,17)] + [(flash.refdes,'8')],
                  [(w*0.22, h*0.62), (w*0.22, h*0.57)],
                  bga_perimeter_pos(mcu.x, mcu.y, 14.0, 14.0,
                                    int(round(12*p['pdn_mul'])), pitch=2.0, margin=2.5, n_rows=1),
                  '10uF', '100nF', add_ferrite=True)

        self.rail(comps, nets, 'VDD_1V8', 0.3, pmic, '14',
                  [(mcu.refdes, str(i)) for i in range(17,23)],
                  [(w*0.14, h*0.62)],
                  bga_perimeter_pos(mcu.x, mcu.y, 14.0, 14.0,
                                    int(round(10*p['pdn_mul'])), pitch=2.5, margin=4.0, n_rows=1),
                  '4.7uF', '100nF')

        self.gnd(comps, nets, [(pmic.refdes,'1'),(mcu.refdes,'25'),
                               (mcu.refdes,'26'),(flash.refdes,'4')])

        for sig,p1,p2 in [('ETH_TX_P','50','1'),('ETH_TX_N','51','2'),
                           ('ETH_RX_P','52','3'),('ETH_RX_N','53','4')]:
            nets.append(Net(sig,'ETH_DIFF_CLASS',[(mcu.refdes,p1),(J1.refdes,p2)],0.02))
        return comps, nets

    def build_mixed_signal(self, cfg: BoardConfig, vp: Dict) -> Tuple[List[Comp], List[Net]]:
        rng = self.rng; p = vp; w, h = cfg.width_mm, cfg.height_mm
        comps: List[Comp] = []; nets: List[Net] = []

        mcu   = Comp('U1','SYNTH_MCU_MSP432','MCU_QFP100', w*0.42,h*0.55,'TOP',100,'IC')
        pmic  = Comp('U2','SYNTH_PMIC_TPS65', 'PMIC_QFN32', w*0.18,h*0.78,'TOP',32,'IC')
        adc   = Comp('U3','SYNTH_ADC_ADS131', 'PMIC_QFN32', w*0.70,h*0.32,'TOP',32,'IC')
        flash = Comp('U4','SYNTH_FLASH_W25Q', 'FLASH_SOIC8',w*0.18,h*0.22,'TOP',8,'IC')
        comps += [mcu, pmic, adc, flash]

        self.rail(comps, nets, 'VDD_MCU', 0.6, pmic, '10',
                  [(mcu.refdes, str(i)) for i in range(1,10)],
                  [(w*0.28, h*0.70),(w*0.28, h*0.64)],
                  bga_perimeter_pos(mcu.x, mcu.y, 14.0, 14.0,
                                    int(round(16*p['pdn_mul'])), pitch=1.5, margin=1.2, n_rows=1),
                  '22uF', '100nF')

        self.rail(comps, nets, 'AVDD_ADC', 0.2, pmic, '12',
                  [(adc.refdes, str(i)) for i in range(1,7)],
                  [(w*0.62, h*0.22),(w*0.68, h*0.22)],
                  bga_perimeter_pos(adc.x, adc.y, 5.0, 5.0,
                                    int(round(10*p['pdn_mul'])), pitch=1.5, margin=1.2, n_rows=1),
                  '10uF', '100nF', add_ferrite=True)

        self.rail(comps, nets, 'DVDD_ADC', 0.1, pmic, '14',
                  [(adc.refdes, str(i)) for i in range(7,11)],
                  [],
                  bga_perimeter_pos(adc.x, adc.y, 5.0, 5.0,
                                    int(round(8*p['pdn_mul'])), pitch=2.0, margin=2.5, n_rows=1),
                  '4.7uF', '100nF')

        self.rail(comps, nets, 'VDD_3V3', 0.4, pmic, '8',
                  [(flash.refdes,'8'),(mcu.refdes,'10')],
                  [(w*0.12, h*0.68)],
                  bga_perimeter_pos(mcu.x, mcu.y, 14.0, 14.0,
                                    int(round(10*p['pdn_mul'])), pitch=2.5, margin=4.0, n_rows=1),
                  '10uF', '100nF')

        self.gnd(comps, nets, [(pmic.refdes,'1'),(mcu.refdes,'20'),
                               (adc.refdes,'16'),(flash.refdes,'4')])

        nets.append(Net('ADC_CLK','ADC_CLK_CLASS',
                        [(mcu.refdes,'40'),(adc.refdes,'20')], 0.005))
        nets.append(Net('ADC_SDO', None,
                        [(mcu.refdes,'41'),(adc.refdes,'21')], 0.005))
        return comps, nets


# ---------------------------------------------------------------------------
# XML generator
# ---------------------------------------------------------------------------

class XMLOnlyBoardGenerator:
    def __init__(self, seed: int = 1):
        self.rng = random.Random(seed)

    def random_board_config(self, index: int, archetype: Optional[str] = None,
                            variant: str = 'balanced') -> BoardConfig:
        arch = archetype or self.rng.choice(
            ['fpga_ddr','storage_controller','mcu_pmic','mixed_signal'])
        if arch == 'fpga_ddr':
            layers = self.rng.choice([8,10]); th = self.rng.choice([1.6,1.8])
            w,h = self.rng.uniform(100,140), self.rng.uniform(80,110)
        elif arch == 'storage_controller':
            layers = self.rng.choice([6,8]);  th = self.rng.choice([1.2,1.6])
            w,h = self.rng.uniform(80,120),   self.rng.uniform(60,100)
        elif arch == 'mcu_pmic':
            layers = self.rng.choice([4,6]);  th = self.rng.choice([1.0,1.2,1.6])
            w,h = self.rng.uniform(60,100),   self.rng.uniform(50,85)
        else:
            layers = self.rng.choice([4,6,8]);th = self.rng.choice([1.0,1.2,1.6])
            w,h = self.rng.uniform(70,110),   self.rng.uniform(55,90)
        return BoardConfig(f'{arch}_{index:04d}', arch, round(w,3), round(h,3),
                           layers, th, self.rng.randrange(1, 10_000_000), variant)

    def _layer_names(self, n: int) -> List[str]:
        if n == 4:  return ['TOP','L2_GND','L3_PWR','BOTTOM']
        if n == 6:  return ['TOP','L2_GND','L3_SIG','L4_PWR','L5_GND','BOTTOM']
        if n == 8:  return ['TOP','L2_GND','L3_SIG','L4_PWR','L5_SIG','L6_GND','L7_SIG','BOTTOM']
        return ['TOP','L2_GND','L3_SIG','L4_PWR','L5_GND','L6_SIG','L7_PWR','L8_GND','L9_SIG','BOTTOM']

    def _variant_params(self, variant: str) -> Dict:
        return {
            'canonical':        {'complexity_mul':0.75,'pdn_mul':1.15,'edge_case':False},
            'balanced':         {'complexity_mul':1.00,'pdn_mul':1.00,'edge_case':False},
            'challenging':      {'complexity_mul':1.25,'pdn_mul':0.90,'edge_case':False},
            'edge_case_variant':{'complexity_mul':1.10,'pdn_mul':0.70,'edge_case':True},
        }[variant]

    # ── IC pin layout helpers ─────────────────────────────────────────────

    def _ic_pin_positions(self, pkg: str, n_pins: int,
                          bw: float, bh: float) -> List[Tuple[float, float]]:
        """Return list of (x, y) pin centre positions relative to component origin."""
        hw = bw / 2.0; hh = bh / 2.0
        if pkg in ('FPGA_BGA256', 'DDR_BGA96'):
            # BGA: square grid
            cols = int(math.ceil(math.sqrt(n_pins)))
            rows = int(math.ceil(n_pins / cols))
            pitch = min(bw, bh) / (max(cols, rows) + 1)
            pos: List[Tuple[float, float]] = []
            for r in range(rows):
                for c in range(cols):
                    pos.append((-hw + pitch * (c + 1), -hh + pitch * (r + 1)))
            return pos[:n_pins]
        elif pkg in ('MCU_QFP100', 'BUCK_QFN48', 'PMIC_QFN32', 'LDO_DFN8', 'LDO_SOT223'):
            # QFP/QFN: pins distributed around perimeter
            per_side = max(1, n_pins // 4)
            ph_x = bw / (per_side + 1); ph_y = bh / (per_side + 1)
            pos = []
            for i in range(per_side):   pos.append((-hw + ph_x * (i+1), -hh))     # bottom
            for i in range(per_side):   pos.append((hw,  -hh + ph_y * (i+1)))      # right
            for i in range(per_side):   pos.append((hw - ph_x * (i+1), hh))        # top
            for i in range(per_side):   pos.append((-hw, hh - ph_y * (i+1)))       # left
            return pos[:n_pins]
        else:
            # SOIC / TSOP / connector: two columns
            per_col = max(1, n_pins // 2)
            pitch = bh / (per_col + 1)
            pos = []
            for i in range(per_col):
                y = -hh + pitch * (i + 1)
                pos.append((-hw * 0.65, y))   # left column
                pos.append(( hw * 0.65, y))   # right column
            return pos[:n_pins]

    def _gen_package_xml(self, pkg_keys: List[str], X: str) -> List[str]:
        """Return XML lines for all Package definitions inside CadData."""
        out: List[str] = []
        # IC pin counts by package key
        IC_PINS: Dict[str, int] = {
            'FPGA_BGA256': 256, 'DDR_BGA96': 96,  'MCU_QFP100': 100,
            'BUCK_QFN48':   48, 'LDO_SOT223':  4,  'LDO_DFN8':     8,
            'PMIC_QFN32':   32, 'NAND_TSOP48': 48,  'FLASH_SOIC8':  8,
            'SATA_CONN':    22, 'ETH_MAGJACK': 12,
        }
        for pk in sorted(pkg_keys):
            bw, bh = PACKAGE_BODY.get(pk, (2.0, 2.0))
            hw = bw / 2.0; hh = bh / 2.0
            if pk in PAD_2PIN:
                pw, ph, pitch = PAD_2PIN[pk]
                pid = f'Rectangle_{pw:g}x{ph:g}'
                out.append(f'      <Package {X} mountType="SMT" name="{pk}" pinCount="2" type="ELECTRICAL">')
                out.append(f'        <Outline {X}>')
                out.append(f'          <Polygon {X}>')
                out.append(f'            <PolyBegin {X} x="{-hw:.4f}" y="{-hh:.4f}"/>')
                out.append(f'            <PolyStepSegment {X} x="{hw:.4f}" y="{-hh:.4f}"/>')
                out.append(f'            <PolyStepSegment {X} x="{hw:.4f}" y="{hh:.4f}"/>')
                out.append(f'            <PolyStepSegment {X} x="{-hw:.4f}" y="{hh:.4f}"/>')
                out.append(f'            <PolyStepSegment {X} x="{-hw:.4f}" y="{-hh:.4f}"/>')
                out.append(f'          </Polygon>')
                out.append(f'        </Outline>')
                out.append(f'        <Pin {X} number="1" side="TOP" type="SMT">')
                out.append(f'          <Location {X} x="{-pitch/2:.4f}" y="0"/>')
                out.append(f'          <StandardPrimitiveRef {X} id="{pid}"/>')
                out.append(f'        </Pin>')
                out.append(f'        <Pin {X} number="2" side="TOP" type="SMT">')
                out.append(f'          <Location {X} x="{pitch/2:.4f}" y="0"/>')
                out.append(f'          <StandardPrimitiveRef {X} id="{pid}"/>')
                out.append(f'        </Pin>')
                out.append(f'      </Package>')
            else:
                n_pins = IC_PINS.get(pk, 4)
                # small pad for IC pins: 6% of body dimension, min 0.1 mm
                ic_pw = max(0.1, round(bw * 0.06, 3))
                ic_ph = max(0.1, round(bh * 0.06, 3))
                ic_pid = f'Rectangle_{ic_pw:g}x{ic_ph:g}'
                out.append(f'      <Package {X} mountType="SMT" name="{pk}" pinCount="{n_pins}" type="ELECTRICAL">')
                out.append(f'        <Outline {X}>')
                out.append(f'          <Polygon {X}>')
                out.append(f'            <PolyBegin {X} x="{-hw:.4f}" y="{-hh:.4f}"/>')
                out.append(f'            <PolyStepSegment {X} x="{hw:.4f}" y="{-hh:.4f}"/>')
                out.append(f'            <PolyStepSegment {X} x="{hw:.4f}" y="{hh:.4f}"/>')
                out.append(f'            <PolyStepSegment {X} x="{-hw:.4f}" y="{hh:.4f}"/>')
                out.append(f'            <PolyStepSegment {X} x="{-hw:.4f}" y="{-hh:.4f}"/>')
                out.append(f'          </Polygon>')
                out.append(f'        </Outline>')
                pin_pos = self._ic_pin_positions(pk, n_pins, bw, bh)
                for idx, (px, py) in enumerate(pin_pos):
                    out.append(f'        <Pin {X} number="{idx+1}" side="TOP" type="SMT">')
                    out.append(f'          <Location {X} x="{px:.4f}" y="{py:.4f}"/>')
                    out.append(f'          <StandardPrimitiveRef {X} id="{ic_pid}"/>')
                    out.append(f'        </Pin>')
                out.append(f'      </Package>')
        return out

    def _full_layer_stack(self, signal_layers: List[str]) -> List[Dict]:
        DIEL = [0.0, 0.1143, 0.2032, 1.143, 0.1143, 0.1016, 0.1143, 0.1016, 0.0, 0.0]
        stack = []
        for idx, sig in enumerate(signal_layers):
            dt = DIEL[idx] if idx < len(DIEL) else 0.1143
            side = 'TOP' if sig=='TOP' else ('BOTTOM' if sig=='BOTTOM' else 'INTERNAL')
            stack.append({'name': f'UNNAMED_{idx*2:03d}','fn':'DIELCORE','side':side,'thickness':dt})
            stack.append({'name': sig,'fn':'MIXED_MATERIAL','side':side,'thickness':0.03048})
        last = len(signal_layers)
        stack.append({'name':f'UNNAMED_{last*2:03d}','fn':'DIELCORE','side':'BOTTOM','thickness':0.0})
        return stack

    def _route_nets(self, nets: List[Net], comps: List[Comp],
                    signal_layers: List[str], rng: random.Random) -> Tuple[List[Dict], List[Dict]]:
        comp_map = {c.refdes: c for c in comps}
        inner_sig = next((l for l in signal_layers if 'SIG' in l), 'TOP')
        pwr_layer = next((l for l in signal_layers if 'PWR' in l), 'TOP')
        routes: List[Dict] = []
        vias: List[Dict] = []
        via_n = [0]

        def add_via(x: float, y: float, net_name: str, fl: str, tl: str) -> None:
            via_n[0] += 1
            vias.append({'name':f'V{via_n[0]}','x':x,'y':y,'net':net_name,
                         'from':fl,'to':tl,'drill_d':0.3,'pad_d':0.6})

        for net in nets:
            if len(net.pins) < 2:
                continue
            tw = net.trace_width
            is_pwr = net.current_a >= 1.0
            is_hs  = net.class_name in HIGH_SPEED_CLASSES

            # GND: short stubs to ground plane via
            if net.name == 'GND':
                gnd_layer = next((l for l in signal_layers if 'GND' in l), 'TOP')
                for rd, _ in net.pins[:min(12, len(net.pins))]:
                    c = comp_map.get(rd)
                    if c is None: continue
                    vx = c.x + rng.uniform(-0.4, 0.4)
                    vy = c.y + rng.uniform(-0.4, 0.4)
                    routes.append({'net':'GND','layer':'TOP','width':0.2,
                                   'points':[(c.x,c.y),(vx,vy)]})
                    add_via(vx, vy, 'GND', 'TOP', gnd_layer)
                continue

            src_rd, _ = net.pins[0]
            src = comp_map.get(src_rd)
            if src is None: continue

            for dst_rd, _ in net.pins[1:]:
                dst = comp_map.get(dst_rd)
                if dst is None: continue
                bs = PACKAGE_BODY.get(src.pkg, (2.0,2.0))
                bd = PACKAGE_BODY.get(dst.pkg, (2.0,2.0))
                sx = src.x + (bs[0]/2 + tw*3 if dst.x >= src.x else -(bs[0]/2 + tw*3))
                sy = src.y
                dx = dst.x + (-(bd[0]/2 + tw*3) if dst.x >= src.x else (bd[0]/2 + tw*3))
                dy = dst.y

                if is_hs:
                    pts = [(src.x,src.y),(sx,sy),(sx,(sy+dy)/2),(dx,(sy+dy)/2),(dx,dy),(dst.x,dst.y)]
                    route_layer = inner_sig
                elif is_pwr:
                    mid_x = (sx+dx)/2
                    pts = [(src.x,src.y),(sx,sy),(mid_x,sy),(mid_x,dy),(dx,dy),(dst.x,dst.y)]
                    route_layer = pwr_layer
                    if route_layer != 'TOP':
                        add_via(sx, sy, net.name, 'TOP', route_layer)
                        add_via(dx, dy, net.name, route_layer, 'TOP')
                else:
                    jog = rng.uniform(-2.0, 2.0)
                    mid_x = (sx+dx)/2 + jog
                    pts = [(src.x,src.y),(sx,sy),(mid_x,sy),(mid_x,dy),(dx,dy),(dst.x,dst.y)]
                    route_layer = 'TOP'

                routes.append({'net':net.name,'layer':route_layer,'width':tw,'points':pts})

        return routes, vias

    def build_board_xml(self, cfg: BoardConfig) -> str:
        rng = random.Random(cfg.seed)
        signal_layers = self._layer_names(cfg.layer_count)
        vp = self._variant_params(cfg.variant)

        pdn = PDNBuilder(rng)
        build_fn = {
            'fpga_ddr':           pdn.build_fpga_ddr,
            'storage_controller': pdn.build_storage_controller,
            'mcu_pmic':           pdn.build_mcu_pmic,
            'mixed_signal':       pdn.build_mixed_signal,
        }
        comps_obj, nets_obj = build_fn[cfg.archetype](cfg, vp)

        # Flat dicts for XML rendering
        comps = [{'refdes':c.refdes,'part':c.part,'package_key':c.pkg,
                  'x':c.x,'y':c.y,'layer':c.layer,'pin_count':c.pin_count,'value':c.value}
                 for c in comps_obj]

        # Build component-pin → net lookup (for pad rendering)
        pin_net: Dict[Tuple[str,str], str] = {}
        for net in nets_obj:
            for rd, pn in net.pins:
                pin_net[(rd, pn)] = net.name

        graph_routes, vias = self._route_nets(nets_obj, comps_obj, signal_layers, rng)

        full_stack = self._full_layer_stack(signal_layers)
        all_layer_names = [e['name'] for e in full_stack] + ['DRILL_TOP-BOTTOM']
        used_widths = sorted(set(r['width'] for r in graph_routes)) or [0.1,0.15,0.25,0.35,0.5]
        w, h = cfg.width_mm, cfg.height_mm

        # Which nets fill GND / PWR planes?
        plane_nets: Dict[str, str] = {}
        for layer in signal_layers:
            if 'GND' in layer:
                plane_nets[layer] = 'GND'
            elif 'PWR' in layer:
                # pick the highest-current net for the PWR plane; fallback to any power net
                heavy = max((n for n in nets_obj if n.current_a >= 1.0),
                            key=lambda n: n.current_a, default=None)
                if heavy is None:
                    heavy = next((n for n in nets_obj
                                  if not n.name.endswith('_FB') and n.name != 'GND'), None)
                if heavy:
                    plane_nets[layer] = heavy.name

        X  = 'xmlns=""'
        NL = '\n'
        out: List[str] = []

        # root
        out.append('<?xml version="1.0" encoding="UTF-8" standalone="no" ?>')
        out.append('<IPC-2581 xmlns="http://webstds.ipc.org/2581" revision="4.0.0" '
                   'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')

        # Content
        out.append(f'  <Content {X}>')
        out.append(f'    <StepRef {X} name="{cfg.name}"/>')
        for ln in all_layer_names:
            out.append(f'    <LayerRef {X} name="{ln}"/>')
        out.append(f'    <BomRef {X} name="BOM"/>')

        out.append(f'    <DictionaryColor {X}>')
        for e in full_stack:
            r_, g_, b_ = LAYER_COLORS.get(e['name'], UNNAMED_RGB)
            out.append(f'      <EntryColor {X} id="{e["name"]}">')
            out.append(f'        <Color {X} b="{b_}" g="{g_}" r="{r_}"/>')
            out.append(f'      </EntryColor>')
        out.append(f'    </DictionaryColor>')

        out.append(f'    <DictionaryLineDesc {X} units="MILLIMETER">')
        out.append(f'      <EntryLineDesc {X} id="ROUND_0">')
        out.append(f'        <LineDesc {X} lineEnd="NONE" lineWidth="0"/>')
        out.append(f'      </EntryLineDesc>')
        for wval in used_widths:
            wid = f'{wval:g}'
            out.append(f'      <EntryLineDesc {X} id="ROUND_{wid}">')
            out.append(f'        <LineDesc {X} lineEnd="ROUND" lineWidth="{wid}"/>')
            out.append(f'      </EntryLineDesc>')
        out.append(f'    </DictionaryLineDesc>')

        pkg_keys = sorted(set(c['package_key'] for c in comps))
        via_geom = 'VIA_30_60'

        # ── Deduplicated pad geometry entries for DictionaryStandard ─────────
        # 2-pin discretes: real pad dimensions; ICs: 6 % of body (min 0.1 mm)
        IC_PINS: Dict[str, int] = {
            'FPGA_BGA256': 256, 'DDR_BGA96': 96,  'MCU_QFP100': 100,
            'BUCK_QFN48':   48, 'LDO_SOT223':  4,  'LDO_DFN8':     8,
            'PMIC_QFN32':   32, 'NAND_TSOP48': 48,  'FLASH_SOIC8':  8,
            'SATA_CONN':    22, 'ETH_MAGJACK': 12,
        }
        pad_entries: Dict[str, Tuple[float, float]] = {}  # id -> (w, h)
        for pk in pkg_keys:
            if pk in PAD_2PIN:
                pw, ph, _ = PAD_2PIN[pk]
            else:
                bw_b, bh_b = PACKAGE_BODY.get(pk, (2.0, 1.0))
                pw = max(0.1, round(bw_b * 0.06, 3))
                ph = max(0.1, round(bh_b * 0.06, 3))
            pad_entries[f'Rectangle_{pw:g}x{ph:g}'] = (pw, ph)

        out.append(f'    <DictionaryStandard {X} units="MILLIMETER">')
        for pid, (pw, ph) in sorted(pad_entries.items()):
            out.append(f'      <EntryStandard {X} id="{pid}">')
            out.append(f'        <RectCenter {X} height="{ph:g}" width="{pw:g}"/>')
            out.append(f'      </EntryStandard>')
        out.append(f'      <EntryStandard {X} id="{via_geom}">')
        out.append(f'        <Circle {X} diameter="0.6"/>')
        out.append(f'      </EntryStandard>')
        out.append(f'    </DictionaryStandard>')
        out.append(f'  </Content>')

        out.append(f'  <HistoryRecord {X} lastChange="2026-04-19T16:35:00" '
                   f'number="2.0" origination="2026-04-19T16:35:00" '
                   f'software="generate_ipc2581_xml_only.py"/>')

        # BOM
        out.append(f'  <Bom {X} name="BOM_{cfg.name}">')
        by_part: Dict = {}
        for c in comps:
            by_part.setdefault(c['part'], []).append(c)
        for part in sorted(by_part):
            items = by_part[part]
            out.append(f'    <BomItem {X} OEMDesignNumberRef="{part}" '
                       f'category="ELECTRICAL" pinCount="{items[0]["pin_count"]}" '
                       f'quantity="{len(items)}">')
            for i in items:
                out.append(f'      <RefDes {X} layerRef="{i["layer"]}" '
                           f'name="{i["refdes"]}" packageRef="" populate="true"/>')
            out.append(f'      <Characteristics {X} category="ELECTRICAL">')
            out.append(f'        <Textual {X} definitionSource="synthetic" '
                       f'textualCharacteristicName="Value" '
                       f'textualCharacteristicValue="{items[0]["value"]}"/>')
            out.append(f'      </Characteristics>')
            out.append(f'    </BomItem>')
        out.append(f'  </Bom>')

        # ECAD
        out.append(f'  <Ecad {X} name="{cfg.name}">')
        out.append(f'    <CadData {X}>')
        for e in full_stack:
            out.append(f'      <Layer {X} layerFunction="{e["fn"]}" '
                       f'name="{e["name"]}" polarity="POSITIVE" side="{e["side"]}"/>')
        out.append(f'      <Layer {X} layerFunction="DRILL" '
                   f'name="DRILL_TOP-BOTTOM" polarity="POSITIVE" side="NONE">')
        out.append(f'      </Layer>')

        total_th = cfg.board_thickness_mm
        out.append(f'      <Stackup {X} name="Stackup" overallThickness="{total_th}" '
                   f'tolMinus="0" tolPlus="0" whereMeasured="OTHER">')
        out.append(f'        <StackupGroup {X} name="StackupGroup" '
                   f'thickness="{total_th}" tolMinus="0" tolPlus="0">')
        for e in full_stack:
            out.append(f'          <StackupLayer {X} layerOrGroupRef="{e["name"]}" '
                       f'thickness="{e["thickness"]}" tolMinus="0" tolPlus="0"/>')
        out.append(f'        </StackupGroup>')
        out.append(f'      </Stackup>')

        # ── Package footprint definitions ─────────────────────────────────────
        for line in self._gen_package_xml(pkg_keys, X):
            out.append(line)

        out.append(f'      <Step {X} name="{cfg.name}">')
        out.append(f'        <Datum {X} x="0" y="0"/>')
        out.append(f'        <Profile {X}>')
        out.append(f'          <Polygon {X}>')
        out.append(f'            <PolyBegin {X} x="0" y="0"/>')
        out.append(f'            <PolyStepSegment {X} x="{w}" y="0"/>')
        out.append(f'            <PolyStepSegment {X} x="{w}" y="{h}"/>')
        out.append(f'            <PolyStepSegment {X} x="0" y="{h}"/>')
        out.append(f'            <PolyStepSegment {X} x="0" y="0"/>')
        out.append(f'          </Polygon>')
        out.append(f'        </Profile>')

        for c in comps:
            out.append(f'        <Component {X} layerRef="{c["layer"]}" '
                       f'mountType="SMT" packageRef="{c["package_key"]}" part="{c["part"]}" '
                       f'refDes="{c["refdes"]}">')
            out.append(f'          <Location {X} x="{c["x"]:.4f}" y="{c["y"]:.4f}"/>')
            out.append(f'        </Component>')

        for layer in signal_layers:
            out.append(f'        <LayerFeature {X} layerRef="{layer}">')
            out.append(f'          <Set {X}>')
            out.append(f'            <ColorRef {X} id="{layer}"/>')
            out.append(f'          </Set>')

            if layer in plane_nets:
                pnet = plane_nets[layer]
                out.append(f'          <Set {X} net="{pnet}">')
                out.append(f'            <Features {X}>')
                out.append(f'              <Location {X} x="0" y="0"/>')
                out.append(f'              <Surface {X}>')
                out.append(f'                <Polygon {X}>')
                out.append(f'                  <PolyBegin {X} x="0" y="0"/>')
                out.append(f'                  <PolyStepSegment {X} x="{w}" y="0"/>')
                out.append(f'                  <PolyStepSegment {X} x="{w}" y="{h}"/>')
                out.append(f'                  <PolyStepSegment {X} x="0" y="{h}"/>')
                out.append(f'                  <PolyStepSegment {X} x="0" y="0"/>')
                out.append(f'                </Polygon>')
                out.append(f'              </Surface>')
                out.append(f'            </Features>')
                out.append(f'          </Set>')

            for r in graph_routes:
                if r['layer'] != layer: continue
                wid = f'{r["width"]:g}'
                out.append(f'          <Set {X} net="{r["net"]}">')
                out.append(f'            <Features {X}>')
                out.append(f'              <Location {X} x="0" y="0"/>')
                out.append(f'              <Polyline {X}>')
                for pidx,(px,py) in enumerate(r['points']):
                    tag2 = 'PolyBegin' if pidx == 0 else 'PolyStepSegment'
                    out.append(f'                <{tag2} {X} x="{px:.4f}" y="{py:.4f}"/>')
                out.append(f'                <LineDescRef {X} id="ROUND_{wid}"/>')
                out.append(f'              </Polyline>')
                out.append(f'            </Features>')
                out.append(f'          </Set>')

            for v in vias:
                if v['from'] != layer and v['to'] != layer: continue
                out.append(f'          <Set {X} geometry="{via_geom}" net="{v["net"]}">')
                out.append(f'            <Features {X}>')
                out.append(f'              <Location {X} x="{v["x"]:.4f}" y="{v["y"]:.4f}"/>')
                out.append(f'              <UserPrim {X}>')
                out.append(f'                <Circle {X} diameter="{v["pad_d"]}"/>')
                out.append(f'              </UserPrim>')
                out.append(f'            </Features>')
                out.append(f'          </Set>')

            # ── Component copper pads on TOP layer ───────────────────────
            # Pad shape is declared by geometry= (DictionaryStandard reference);
            # Features only needs the Location — no inline RectCenter.
            if layer == 'TOP':
                for c in comps:
                    pk = c['package_key']
                    cx, cy = c['x'], c['y']
                    rd = c['refdes']
                    if pk in PAD_2PIN:
                        pw, ph, pitch = PAD_2PIN[pk]
                        pid = f'Rectangle_{pw:g}x{ph:g}'
                        for pin_n, px_pad in (('1', cx - pitch / 2.0),
                                              ('2', cx + pitch / 2.0)):
                            net_name = pin_net.get((rd, pin_n), '')
                            net_attr = f' net="{net_name}"' if net_name else ''
                            out.append(f'          <Set {X} geometry="{pid}"{net_attr}>')
                            out.append(f'            <Features {X}>')
                            out.append(f'              <Location {X} x="{px_pad:.4f}" y="{cy:.4f}"/>')
                            out.append(f'            </Features>')
                            out.append(f'          </Set>')
                    else:
                        # Multi-pin IC: emit one pad Set per pin using Package pin positions
                        bw_b, bh_b = PACKAGE_BODY.get(pk, (2.0, 2.0))
                        ic_pw = max(0.1, round(bw_b * 0.06, 3))
                        ic_ph = max(0.1, round(bh_b * 0.06, 3))
                        ic_pid = f'Rectangle_{ic_pw:g}x{ic_ph:g}'
                        n_pins = IC_PINS.get(pk, 4)
                        pin_pos = self._ic_pin_positions(pk, n_pins, bw_b, bh_b)
                        for pin_idx, (ppx, ppy) in enumerate(pin_pos):
                            pin_n = str(pin_idx + 1)
                            net_name = pin_net.get((rd, pin_n), '')
                            net_attr = f' net="{net_name}"' if net_name else ''
                            out.append(f'          <Set {X} geometry="{ic_pid}"{net_attr}>')
                            out.append(f'            <Features {X}>')
                            out.append(f'              <Location {X} x="{cx+ppx:.4f}" y="{cy+ppy:.4f}"/>')
                            out.append(f'            </Features>')
                            out.append(f'          </Set>')

            out.append(f'        </LayerFeature>')

        # DRILL layer
        if vias:
            out.append(f'        <LayerFeature {X} layerRef="DRILL_TOP-BOTTOM">')
            for v in vias:
                out.append(f'          <Set {X} geometry="{via_geom}" net="{v["net"]}">')
                out.append(f'            <Hole {X} diameter="{v["drill_d"]}" minusTol="0" '
                           f'name="{v["name"]}" platingStatus="VIA" plusTol="0" '
                           f'x="{v["x"]:.4f}" y="{v["y"]:.4f}"/>')
                out.append(f'          </Set>')
            out.append(f'        </LayerFeature>')

        out += ['      </Step>', '    </CadData>', '  </Ecad>', '</IPC-2581>']
        return NL.join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description='Generate IPC-2581 XML boards with realistic PDN designs')
    parser.add_argument('--config', required=True, help='YAML or JSON config path')
    args = parser.parse_args()
    cfg = load_cfg(args.config)

    out_dir   = Path(cfg.get('out_dir', 'xml_only_dataset'))
    boards    = int(cfg.get('boards', 1))
    seed      = int(cfg.get('seed', 1234))
    arch_dist = cfg.get('archetype_distribution',
                        {'fpga_ddr':0.35,'storage_controller':0.25,
                         'mcu_pmic':0.25,'mixed_signal':0.15})
    var_dist  = cfg.get('variant_distribution',
                        {'canonical':0.3,'balanced':0.45,
                         'challenging':0.2,'edge_case_variant':0.05})

    xml_dir = out_dir / 'xml'
    xml_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    master_rng = random.Random(seed)
    gen = XMLOnlyBoardGenerator(seed)

    for i in range(1, boards + 1):
        archetype = pick_weighted(master_rng, arch_dist)
        variant   = pick_weighted(master_rng, var_dist)
        bcfg = gen.random_board_config(i, archetype, variant)
        xml_text = gen.build_board_xml(bcfg)
        xml_path = xml_dir / f'{bcfg.name}.xml'
        xml_path.write_text(xml_text, encoding='utf-8')
        ET.parse(str(xml_path))   # validate well-formedness
        sz = xml_path.stat().st_size
        manifest.append({'board_name': bcfg.name, 'archetype': bcfg.archetype,
                         'variant': bcfg.variant, 'xml': str(xml_path.relative_to(out_dir))})
        print(f'  [{i}/{boards}] {bcfg.name}  ({sz//1024} KB)', flush=True)

    (out_dir / 'xml_manifest.json').write_text(
        json.dumps(manifest, indent=2), encoding='utf-8')
    print(json.dumps({'out_dir': str(out_dir), 'boards': boards,
                      'xml_files': len(manifest)}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

