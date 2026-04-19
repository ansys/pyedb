# PDN Generator Workflow

This folder contains a self-contained workflow for generating seeded, realistic PDN-only layouts focused on decoupling capacitor networks for machine-learning dataset creation.

## What it does

- builds a 4-layer or 6-layer stackup
- creates a board outline, continuous GND planes, and one or more power islands
- supports multiple rails such as `VDD_CORE`, `VDD_IO`, and `VDD_AUX`
- supports dedicated, pair-shared, or fully shared source-entry topologies
- varies load/source topology through configurable endpoint variants
- embeds a per-case label schema version in every exported manifest
- refines the decap mix from target impedance, current, ripple, and variant context
- places realistic 2-pin decoupling capacitors from a curated library
- adds short pad-to-via fanout connections using PyEDB
- exports CSV/JSON metadata suitable for ML labels
- supports plan-only batch generation over many seeds
- keeps generation deterministic through explicit seeds

## Public API

```python
from pyedb.workflows.pdn_generator import (
    PDNGeneratorConfig,
    RailSpec,
    SourceTopologyName,
    export_plan_metadata,
    generate_pdn_dataset_batch,
    generate_pdn_dataset_case,
    plan_pdn_batch,
    plan_pdn_case,
    refine_decap_mix,
    summarize_generation_plan,
    validate_generation_plan,
)
```

## Typical usage

### 1. Single-case plan only

```python
from pyedb.workflows.pdn_generator import PDNGeneratorConfig, plan_pdn_case, validate_generation_plan

config = PDNGeneratorConfig(stackup_preset="6L", mode="realistic", load_current_a=12.0)
plan = plan_pdn_case(config=config, seed=23)
validate_generation_plan(plan)
print(plan.to_dict()["counts"])
```

### 2. Multi-rail plan with variants

```python
from pyedb.workflows.pdn_generator import PDNGeneratorConfig, RailSpec, plan_pdn_case

config = PDNGeneratorConfig(
    dataset_name="multi_rail_demo",
    label_schema_version="pdn_labels.v2",
    source_topology="shared_pairs",
    rails=[
        RailSpec(name="VDD_CORE", current_a=4.0, max_ripple_v=0.020, load_variant="fpga_cluster", source_variant="vrm_patch"),
        RailSpec(name="VDD_IO", current_a=1.5, max_ripple_v=0.030, load_variant="connector_load", source_variant="connector"),
        RailSpec(name="VDD_AUX", current_a=0.8, max_ripple_v=0.040, load_variant="small_ic", source_variant="remote_source"),
    ],
)
plan = plan_pdn_case(config=config, seed=7)
print([rail.name for rail in plan.rails])
print([source.source_group for source in plan.sources])
print(plan.to_dict()["counts"])
```

### 3. Batch dataset generation with CSV/JSON labels

```python
from pathlib import Path
from pyedb.workflows.pdn_generator import PDNGeneratorConfig, RailSpec, generate_pdn_dataset_batch

config = PDNGeneratorConfig(
    dataset_name="pdn_ml_dataset",
    rails=[
        RailSpec(name="VDD_CORE", current_a=4.0, max_ripple_v=0.020, load_variant="fpga_cluster", source_variant="vrm_patch"),
        RailSpec(name="VDD_IO", current_a=1.5, max_ripple_v=0.030, load_variant="connector_load", source_variant="connector"),
    ],
)
generate_pdn_dataset_batch(Path(r"C:\temp\pdn_batch"), config=config, seed_start=1, seed_count=20)
```

### 4. Realize one AEDB

```python
from pathlib import Path
from pyedb.workflows.pdn_generator import PDNGeneratorConfig, RailSpec, generate_pdn_dataset_case

config = PDNGeneratorConfig(
    rails=[RailSpec(name="VDD_CORE", current_a=4.0, max_ripple_v=0.020, load_variant="fpga_cluster", source_variant="vrm_patch")]
)
plan = generate_pdn_dataset_case(Path(r"C:\temp\pdn_case_001.aedb"), config=config, seed=7, version="2026.1")
print(plan.seed)
```

## Quick command-line runs

```powershell
python -m pyedb.workflows.pdn_generator.runner --seed 7 --json-out C:\temp\pdn_case_007.plan.json
python -m pyedb.workflows.pdn_generator.runner --seed 11 --stackup 6L --aedb-out C:\temp\pdn_case_011.aedb --version 2026.1
python -m pyedb.workflows.pdn_generator.runner --dataset-name pdn_batch --seed-start 1 --seed-count 25 --rail-count 3 --output-dir C:\temp\pdn_batch
python -m pyedb.workflows.pdn_generator.runner --dataset-name pdn_shared --label-schema-version pdn_labels.v2 --source-topology shared_pairs --seed-start 1 --seed-count 10 --rail-count 4 --output-dir C:\temp\pdn_shared
```

## Metadata outputs

Batch generation can emit:

- `metadata.csv`: flattened per-case labels for ML pipelines
- `metadata.json`: rich manifest containing summaries and full plan payloads
- `plans/*.plan.json`: one JSON file per generated case

Typical labels include:

- label schema version
- seed
- board size
- stackup preset
- rail count
- source topology and source groups
- load/source variants
- target impedance per rail
- rail current per rail
- total capacitance
- hf/mid/bulk decap counts

## Notes

- All geometry is generated in meters internally.
- The generator is intentionally constrained to a curated capacitor family set instead of arbitrary random RLC values.
- Target-impedance-driven refinement adjusts the decap mix per rail rather than using a fixed global decap recipe.
- Shared-source topologies cluster multiple rails around a common source entry while preserving separate rail branches and labels.
- If a case cannot be placed because the board is too small or the capacitor count is too high, the planner raises a clear error instead of silently generating unrealistic geometry.
- `realization.py` uses `from pyedb import Edb` with `grpc=True` (the default for this workflow) as required by the local API contract.
