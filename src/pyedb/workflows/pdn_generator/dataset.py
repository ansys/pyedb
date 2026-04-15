from __future__ import annotations
import csv
import json
from pathlib import Path
from typing import Iterable
from .config import PDNGeneratorConfig
from .placement import PDNGenerationPlan, plan_pdn_case
from .realization import generate_pdn_dataset_case
from .validation import summarize_generation_plan, validate_generation_plan
def plan_pdn_batch(
    config: PDNGeneratorConfig | None = None,
    seeds: Iterable[int] | None = None,
    *,
    seed_start: int = 1,
    seed_count: int = 10,
) -> list[PDNGenerationPlan]:
    """Create many deterministic plan-only PDN cases for dataset generation."""
    if seeds is None:
        seeds = range(seed_start, seed_start + seed_count)
    plans: list[PDNGenerationPlan] = []
    for seed in seeds:
        plan = plan_pdn_case(config=config, seed=seed)
        validate_generation_plan(plan)
        plans.append(plan)
    return plans
def plan_metadata_row(plan: PDNGenerationPlan) -> dict[str, object]:
    """Flatten a plan into a CSV-friendly metadata row."""
    summary = summarize_generation_plan(plan)
    return {
        "case_id": f"{plan.config.case_name_prefix}_{plan.seed:05d}",
        "dataset_name": plan.config.dataset_name,
        "label_schema_version": plan.config.label_schema_version,
        "seed": plan.seed,
        "stackup_preset": plan.config.stackup_preset,
        "mode": plan.config.mode,
        "source_topology": plan.config.source_topology,
        "board_width_m": plan.config.board_width_m,
        "board_height_m": plan.config.board_height_m,
        "rail_count": len(plan.rails),
        "load_count": len(plan.loads),
        "source_count": len(plan.sources),
        "island_count": len(plan.islands),
        "decap_count": len(plan.decaps),
        "hf_count": summary["role_counts"]["hf"],
        "mid_count": summary["role_counts"]["mid"],
        "bulk_count": summary["role_counts"]["bulk"],
        "ground_net": plan.config.ground_net_name,
        "power_nets": json.dumps([rail.name for rail in plan.rails]),
        "load_variants": json.dumps([rail.load_variant for rail in plan.rails]),
        "source_variants": json.dumps([rail.source_variant for rail in plan.rails]),
        "source_groups": json.dumps({rail.name: rail.source_group for rail in plan.rails}),
        "target_impedances_ohm": json.dumps({rail.name: rail.target_impedance_ohm for rail in plan.rails}),
        "rail_currents_a": json.dumps({rail.name: rail.load_current_a for rail in plan.rails}),
        "rail_capacitances_f": json.dumps({rail.name: rail.total_capacitance_f for rail in plan.rails}),
        "total_capacitance_f": sum(rail.total_capacitance_f for rail in plan.rails),
        "labels_json": json.dumps(summary, sort_keys=True),
    }
def export_plan_metadata(
    plans: Iterable[PDNGenerationPlan],
    *,
    csv_path: str | Path | None = None,
    json_path: str | Path | None = None,
    plans_directory: str | Path | None = None,
) -> dict[str, str]:
    """Export ML-friendly metadata manifests and optional per-case plan JSON files."""
    plans = list(plans)
    rows = [plan_metadata_row(plan) for plan in plans]
    outputs: dict[str, str] = {}
    if csv_path is not None:
        csv_path = Path(csv_path)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(rows[0].keys()) if rows else []
        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        outputs["csv"] = str(csv_path)
    if json_path is not None:
        json_path = Path(json_path)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "dataset_name": plans[0].config.dataset_name if plans else "pdn_dataset",
            "label_schema_version": plans[0].config.label_schema_version if plans else "pdn_labels.v1",
            "cases": [{"summary": summarize_generation_plan(plan), "plan": plan.to_dict()} for plan in plans],
        }
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        outputs["json"] = str(json_path)
    if plans_directory is not None:
        plans_directory = Path(plans_directory)
        plans_directory.mkdir(parents=True, exist_ok=True)
        for plan in plans:
            case_id = f"{plan.config.case_name_prefix}_{plan.seed:05d}.plan.json"
            (plans_directory / case_id).write_text(json.dumps(plan.to_dict(), indent=2), encoding="utf-8")
        outputs["plans_directory"] = str(plans_directory)
    return outputs
def generate_pdn_dataset_batch(
    output_directory: str | Path,
    config: PDNGeneratorConfig | None = None,
    seeds: Iterable[int] | None = None,
    *,
    seed_start: int = 1,
    seed_count: int = 10,
    realize_aedb: bool = False,
    version: str | None = None,
    grpc: bool | None = None,
) -> list[PDNGenerationPlan]:
    """Generate a batch of PDN cases plus metadata manifests for ML workflows."""
    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)
    plans = plan_pdn_batch(config=config, seeds=seeds, seed_start=seed_start, seed_count=seed_count)
    export_plan_metadata(
        plans,
        csv_path=output_directory / "metadata.csv",
        json_path=output_directory / "metadata.json",
        plans_directory=output_directory / "plans",
    )
    if realize_aedb:
        aedb_directory = output_directory / "aedb"
        aedb_directory.mkdir(parents=True, exist_ok=True)
        for plan in plans:
            generate_pdn_dataset_case(
                output_aedb_path=aedb_directory / f"{plan.config.case_name_prefix}_{plan.seed:05d}.aedb",
                config=plan.config,
                seed=plan.seed,
                version=version,
                grpc=grpc,
            )
    return plans
