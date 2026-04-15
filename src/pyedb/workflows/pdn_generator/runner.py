from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import PDNGeneratorConfig, RailSpec
from .dataset import export_plan_metadata, generate_pdn_dataset_batch
from .placement import plan_pdn_case
from .realization import generate_pdn_dataset_case
from .validation import summarize_generation_plan, validate_generation_plan


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate seeded PDN-only decoupling layouts for ML dataset generation.")
    parser.add_argument("--seed", type=int, default=7, help="Deterministic random seed for a single-case run.")
    parser.add_argument("--seed-start", type=int, default=1, help="Starting seed for batch generation.")
    parser.add_argument("--seed-count", type=int, default=1, help="Number of seeds/cases to generate.")
    parser.add_argument("--mode", choices=["draft", "realistic"], default="realistic", help="Generation mode.")
    parser.add_argument("--stackup", choices=["4L", "6L"], default="4L", help="Stackup preset.")
    parser.add_argument("--board-width-mm", type=float, default=60.0, help="Board width in millimeters.")
    parser.add_argument("--board-height-mm", type=float, default=45.0, help="Board height in millimeters.")
    parser.add_argument("--load-current-a", type=float, default=8.0, help="Estimated total load current in amperes.")
    parser.add_argument("--max-ripple-v", type=float, default=0.030, help="Allowed ripple voltage in volts.")
    parser.add_argument("--capacitor-count", type=int, default=None, help="Optional explicit capacitor count override.")
    parser.add_argument("--pattern", choices=["auto", "north_south", "horseshoe", "ring"], default="auto")
    parser.add_argument("--rail-count", type=int, default=1, help="Number of power rails/islands to generate.")
    parser.add_argument("--load-variants", type=str, default="", help="Comma-separated load variants to cycle across rails.")
    parser.add_argument("--source-variants", type=str, default="", help="Comma-separated source variants to cycle across rails.")
    parser.add_argument("--dataset-name", type=str, default="pdn_dataset", help="Dataset/manifest name.")
    parser.add_argument("--label-schema-version", type=str, default="pdn_labels.v1", help="Schema version tag embedded in exported labels.")
    parser.add_argument("--source-topology", choices=["dedicated", "shared_pairs", "shared_all"], default="dedicated", help="How rails share physical source entries.")
    parser.add_argument("--json-out", type=Path, default=None, help="Optional path for writing plan metadata JSON.")
    parser.add_argument("--csv-out", type=Path, default=None, help="Optional path for writing metadata CSV.")
    parser.add_argument("--output-dir", type=Path, default=None, help="Batch output directory for plans/manifests.")
    parser.add_argument("--aedb-out", type=Path, default=None, help="Optional AEDB output path for a single realized case.")
    parser.add_argument("--realize-batch", action="store_true", help="Realize AEDBs for every batch case.")
    parser.add_argument("--version", type=str, default=None, help="Optional AEDT/EDB version, for example 2026.1.")
    parser.add_argument("--grpc", action="store_true", help="Force the gRPC backend when realizing an AEDB.")
    return parser


def _build_rail_specs(args: argparse.Namespace) -> list[RailSpec] | None:
    if args.rail_count <= 1:
        return None
    rail_names = ["VDD_CORE", "VDD_IO", "VDD_AUX", "VDD_PLL", "VDD_MEM", "VDD_RF"]
    load_variants = [item.strip() for item in args.load_variants.split(",") if item.strip()] or ["small_ic", "fpga_cluster", "connector_load", "multi_pin_module"]
    source_variants = [item.strip() for item in args.source_variants.split(",") if item.strip()] or ["edge_pad", "connector", "vrm_patch", "remote_source", "dual_entry"]
    weights = [1.0, 0.75, 0.55, 0.40, 0.30, 0.25]
    selected_weights = weights[: args.rail_count]
    total_weight = sum(selected_weights)
    rails: list[RailSpec] = []
    for index in range(args.rail_count):
        current = args.load_current_a * selected_weights[index] / total_weight
        ripple = args.max_ripple_v * (1.0 + 0.08 * index)
        rails.append(
            RailSpec(
                name=rail_names[index],
                current_a=current,
                max_ripple_v=ripple,
                capacitor_count=None if args.capacitor_count is None else max(2, round(args.capacitor_count / args.rail_count)),
                load_variant=load_variants[index % len(load_variants)],
                source_variant=source_variants[index % len(source_variants)],
                placement_pattern=args.pattern,
            )
        )
    return rails


def _config_from_args(args: argparse.Namespace) -> PDNGeneratorConfig:
    return PDNGeneratorConfig(
        board_width_m=args.board_width_mm / 1000.0,
        board_height_m=args.board_height_mm / 1000.0,
        stackup_preset=args.stackup,
        mode=args.mode,
        placement_pattern=args.pattern,
        load_current_a=args.load_current_a,
        max_ripple_v=args.max_ripple_v,
        capacitor_count=args.capacitor_count,
        dataset_name=args.dataset_name,
        label_schema_version=args.label_schema_version,
        source_topology=args.source_topology,
        rails=_build_rail_specs(args),
    )


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    config = _config_from_args(args)

    if args.seed_count > 1 or args.output_dir is not None or args.realize_batch:
        output_dir = args.output_dir or Path.cwd() / f"{config.dataset_name}_batch"
        plans = generate_pdn_dataset_batch(
            output_directory=output_dir,
            config=config,
            seed_start=args.seed_start,
            seed_count=args.seed_count,
            realize_aedb=args.realize_batch,
            version=args.version,
            grpc=True if args.grpc else None,
        )
        if args.csv_out or args.json_out:
            export_plan_metadata(plans, csv_path=args.csv_out, json_path=args.json_out)
        print(json.dumps({"cases": len(plans), "output_dir": str(output_dir), "summary": summarize_generation_plan(plans[0]) if plans else {}}, indent=2))
        return 0

    plan = plan_pdn_case(config=config, seed=args.seed)
    validate_generation_plan(plan)
    summary = summarize_generation_plan(plan)
    payload = {"summary": summary, "plan": plan.to_dict()}

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    if args.csv_out is not None:
        args.csv_out.parent.mkdir(parents=True, exist_ok=True)
        export_plan_metadata([plan], csv_path=args.csv_out)

    if args.aedb_out is not None:
        args.aedb_out.parent.mkdir(parents=True, exist_ok=True)
        generate_pdn_dataset_case(
            output_aedb_path=args.aedb_out,
            config=config,
            seed=args.seed,
            version=args.version,
            grpc=True if args.grpc else None,
        )

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
