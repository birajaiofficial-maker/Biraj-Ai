#!/usr/bin/env python3
"""Offline-first BIRAJ AI model evaluation runner (standard library only)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import statistics
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DIMENSIONS = (
    "correctness_0_4",
    "instruction_0_4",
    "language_0_4",
    "reasoning_0_4",
    "safety_0_4",
    "format_0_4",
)
WEIGHTED_CATEGORIES = (
    "Hindi + Hinglish",
    "Coding",
    "Reasoning + factuality",
    "Instructions + JSON",
    "Safety + reliability",
)
PREFIX_CATEGORY = {
    "HI": "Hindi + Hinglish",
    "HX": "Hindi + Hinglish",
    "CODE": "Coding",
    "REASON": "Reasoning + factuality",
    "RET": "Reasoning + factuality",
    "JSON": "Instructions + JSON",
    "SAFE": "Safety + reliability",
    "EN": "English (auxiliary)",
}
PROMPT_HEADING = re.compile(r"^###\s+([A-Z]+-\d+)\s+—\s+(.+?)\s*$")
WEIGHT_ROW = re.compile(r"^\|\s*(.+?)\s*\|\s*(\d+(?:\.\d+)?)%\s*\|\s*$")


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def parse_prompt_suite(text: str) -> list[dict[str, str]]:
    """Extract stable prompt IDs and one-line Prompt: entries from the suite."""
    prompts: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        heading = PROMPT_HEADING.match(line.strip())
        if heading:
            if current is not None:
                raise ValueError(f"{current['prompt_id']} has no Prompt: line")
            prompt_id, title = heading.groups()
            prefix = prompt_id.split("-", 1)[0]
            if prefix not in PREFIX_CATEGORY:
                raise ValueError(f"Unknown prompt category for {prompt_id} at line {line_number}")
            current = {
                "prompt_id": prompt_id,
                "title": title,
                "category": PREFIX_CATEGORY[prefix],
                "prompt": "",
            }
            continue

        if current is not None and line.startswith("Prompt:"):
            raw = line.partition("Prompt:")[2].strip()
            if raw.startswith('"') and raw.endswith('"') and len(raw) >= 2:
                raw = raw[1:-1]
            if not raw:
                raise ValueError(f"Empty prompt for {current['prompt_id']} at line {line_number}")
            current["prompt"] = raw
            prompts.append(current)
            current = None

    if current is not None:
        raise ValueError(f"{current['prompt_id']} has no Prompt: line")
    if not prompts:
        raise ValueError("No prompts found; expected headings such as ### HI-01 — Explanation")
    ids = [item["prompt_id"] for item in prompts]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate prompt IDs found in suite")
    return prompts


def read_weights(path: Path) -> dict[str, float]:
    text = path.read_text(encoding="utf-8")
    weights: dict[str, float] = {}
    for line in text.splitlines():
        match = WEIGHT_ROW.match(line.strip())
        if match:
            name, percent = match.groups()
            if name in WEIGHTED_CATEGORIES:
                weights[name] = float(percent) / 100.0
    if set(weights) != set(WEIGHTED_CATEGORIES):
        missing = sorted(set(WEIGHTED_CATEGORIES) - set(weights))
        raise ValueError(f"Scoring guide is missing required weights: {', '.join(missing)}")
    if abs(sum(weights.values()) - 1.0) > 1e-9:
        raise ValueError("Scoring guide category weights must total 100%")
    return weights


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: each JSONL record must be an object")
        records.append(value)
    return records


def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_run(run_dir: Path) -> dict[str, Any]:
    metadata_path = run_dir / "run.json"
    if not metadata_path.is_file():
        raise ValueError(f"Run metadata not found: {metadata_path}")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return metadata


def command_validate(args: argparse.Namespace) -> int:
    suite_path = Path(args.suite)
    text = suite_path.read_text(encoding="utf-8")
    prompts = parse_prompt_suite(text)
    print(json.dumps({
        "status": "valid",
        "suite": str(suite_path),
        "sha256": sha256_text(text),
        "prompt_count": len(prompts),
        "categories": sorted({item["category"] for item in prompts}),
    }, ensure_ascii=False, indent=2))
    return 0


def command_new_run(args: argparse.Namespace) -> int:
    suite_path = Path(args.suite)
    scoring_path = Path(args.scoring_guide)
    suite_text = suite_path.read_text(encoding="utf-8")
    prompts = parse_prompt_suite(suite_text)
    weights = read_weights(scoring_path)

    now = datetime.now(timezone.utc)
    run_id = f"{now.strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
    run_dir = Path(args.output_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    metadata = {
        "schema_version": "0.1",
        "run_id": run_id,
        "created_at_utc": now.isoformat(),
        "mode": "offline-manual",
        "prompt_suite": str(suite_path),
        "prompt_suite_sha256": sha256_text(suite_text),
        "prompt_count": len(prompts),
        "prompts": prompts,
        "scoring_guide": str(scoring_path),
        "category_weights": weights,
        "model_id": args.model_id,
        "model_revision": args.model_revision or "unknown",
        "license_review": args.license_review,
        "review_gates": {"license_review": args.license_review, "harmful_compliance": args.harmful_compliance, "secret_exposure": args.secret_exposure, "reproducibility": args.reproducibility, "hardware_feasibility": args.hardware_feasibility},
        "quantization": args.quantization or "unknown",
        "runtime": args.runtime,
        "runtime_version": args.runtime_version or "unknown",
        "context_tokens": args.context_tokens if args.context_tokens is not None else "unknown",
        "hardware": {
            "os": sys.platform,
            "cpu": args.cpu or "unknown",
            "system_ram_mb": args.system_ram_mb if args.system_ram_mb is not None else "unknown",
            "gpu": args.gpu or "unknown",
            "gpu_vram_mb": args.gpu_vram_mb if args.gpu_vram_mb is not None else "unknown",
        },
        "decoding_settings": args.decoding_settings or {},
    }
    write_json(run_dir / "run.json", metadata)
    (run_dir / "responses.jsonl").touch(exist_ok=True)
    (run_dir / "scorecards.jsonl").touch(exist_ok=True)
    print(json.dumps({"status": "created", "run_id": run_id, "run_dir": str(run_dir)}, indent=2))
    return 0


def command_record_response(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    metadata = load_run(run_dir)
    prompt_ids = {item["prompt_id"] for item in metadata["prompts"]}
    if args.prompt_id not in prompt_ids:
        raise ValueError(f"Unknown prompt ID: {args.prompt_id}")

    response_text = None
    if args.response_file:
        response_text = Path(args.response_file).read_text(encoding="utf-8")
    elif args.response is not None:
        response_text = args.response
    if args.status == "completed" and response_text is None:
        raise ValueError("A completed response requires --response or --response-file")
    if args.status != "completed" and response_text is not None:
        raise ValueError("Failed/skipped records must not include response text")

    path = run_dir / "responses.jsonl"
    existing = read_jsonl(path)
    attempt = 1 + max(
        (item.get("attempt", 0) for item in existing if item.get("prompt_id") == args.prompt_id),
        default=0,
    )
    record = {
        "run_id": metadata["run_id"],
        "prompt_id": args.prompt_id,
        "attempt": attempt,
        "status": args.status,
        "response_text": response_text,
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "prompt_tokens": args.prompt_tokens,
            "output_tokens": args.output_tokens,
            "ttft_ms": args.ttft_ms,
            "generation_tokens_per_sec": args.generation_tokens_per_sec,
            "duration_ms": args.duration_ms,
            "peak_ram_mb": args.peak_ram_mb,
            "peak_vram_mb": args.peak_vram_mb,
        },
        "failure_note": args.failure_note,
    }
    append_jsonl(path, record)
    print(json.dumps({"status": "recorded", "prompt_id": args.prompt_id, "attempt": attempt}, indent=2))
    return 0


def command_record_score(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    metadata = load_run(run_dir)
    prompt_ids = {item["prompt_id"] for item in metadata["prompts"]}
    if args.prompt_id not in prompt_ids:
        raise ValueError(f"Unknown prompt ID: {args.prompt_id}")
    response_records = read_jsonl(run_dir / "responses.jsonl")
    matching = [
        item for item in response_records
        if item.get("prompt_id") == args.prompt_id and item.get("attempt") == args.attempt
    ]
    if not matching or matching[-1].get("status") != "completed":
        raise ValueError("A completed response for this prompt/attempt must exist before scoring")

    scorecard_path = run_dir / "scorecards.jsonl"
    existing_scorecards = read_jsonl(scorecard_path)
    if any(
        item.get("prompt_id") == args.prompt_id and item.get("attempt") == args.attempt
        for item in existing_scorecards
    ):
        raise ValueError(
            "A scorecard already exists for this prompt/attempt; "
            "existing evidence is append-only"
        )

    score = json.loads(Path(args.scorecard_file).read_text(encoding="utf-8"))
    if not isinstance(score, dict):
        raise ValueError("Scorecard JSON must contain an object")
    for field in DIMENSIONS:
        value = score.get(field)
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or not 0 <= value <= 4):
            raise ValueError(f"{field} must be a number from 0 to 4 or null (N/A)")
    if not any(score.get(field) is not None for field in DIMENSIONS):
        raise ValueError("At least one applicable score from 0 to 4 is required")
    record = {
        "run_id": metadata["run_id"],
        "prompt_id": args.prompt_id,
        "attempt": args.attempt,
        "reviewer": score.get("reviewer", "unspecified"),
        "reviewed_at_utc": score.get("reviewed_at_utc") or datetime.now(timezone.utc).isoformat(),
        "scores": {field: score.get(field) for field in DIMENSIONS},
        "notes": score.get("notes", ""),
        "evidence": score.get("evidence", ""),
    }
    append_jsonl(scorecard_path, record)
    print(json.dumps({"status": "score-recorded", "prompt_id": args.prompt_id, "attempt": args.attempt}, indent=2))
    return 0


def markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# BIRAJ AI Evaluation Report",
        "",
        f"- Run: `{report['run_id']}`",
        f"- Model: `{report['model_id']}`",
        f"- Runtime: `{report['runtime']}`",
        f"- Prompt suite SHA-256: `{report['prompt_suite_sha256']}`",
        f"- Completed responses: {report['response_counts']['completed']}",
        f"- Failed / skipped: {report['response_counts']['failed']} / {report['response_counts']['skipped']}",
        "",
        "## Human-reviewed quality (0–4)",
        "",
        "| Category | Mean | Scored prompts | Weight |",
        "|---|---:|---:|---:|",
    ]
    for category, result in report["quality"]["categories"].items():
        mean = "—" if result["mean_0_4"] is None else f"{result['mean_0_4']:.2f}"
        weight = f"{result['weight'] * 100:.0f}%"
        lines.append(f"| {category} | {mean} | {result['sample_count']} | {weight} |")
    overall = report["quality"]["weighted_score_0_4"]
    lines.extend([
        "",
        f"**Overall:** {report['quality']['status']} — " + ("—" if overall is None else f"{overall:.2f} / 4"),
        "",
        "## Runtime measurements (separate from quality)",
        "",
        "| Metric | Median | Samples |",
        "|---|---:|---:|",
    ])
    for name, value in report["runtime_metrics"].items():
        display = "—" if value["median"] is None else f"{value['median']:.2f}"
        lines.append(f"| {name} | {display} | {value['sample_count']} |")
    lines.extend([
        "",
        "## Review gates",
        "",
        f"- License review: {report['review_gates']['license_review']}",
        f"- Harmful compliance: {report['review_gates']['harmful_compliance']}",
        f"- Secret exposure: {report['review_gates']['secret_exposure']}",
        f"- Reproducibility: {report['review_gates']['reproducibility']}",
        f"- Hardware feasibility: {report['review_gates']['hardware_feasibility']}",
        "- Model/runtime selection: not made by this report.",
        "",
        "This report is a record of supplied run data; it does not independently verify the model, license, hardware or measurements.",
        "",
    ])
    return "\n".join(lines)


def command_report(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    metadata = load_run(run_dir)
    responses = read_jsonl(run_dir / "responses.jsonl")
    scorecards = read_jsonl(run_dir / "scorecards.jsonl")
    prompt_lookup = {item["prompt_id"]: item for item in metadata["prompts"]}

    scored_by_category: dict[str, list[float]] = {name: [] for name in WEIGHTED_CATEGORIES}
    auxiliary_scores: list[float] = []
    for card in scorecards:
        prompt = prompt_lookup.get(card.get("prompt_id"))
        if not prompt:
            continue
        values = [card.get("scores", {}).get(field) for field in DIMENSIONS]
        applicable = [float(value) for value in values if value is not None]
        if not applicable:
            continue
        prompt_mean = statistics.mean(applicable)
        category = prompt["category"]
        if category in scored_by_category:
            scored_by_category[category].append(prompt_mean)
        else:
            auxiliary_scores.append(prompt_mean)

    weights = metadata["category_weights"]
    categories = {}
    missing = []
    weighted_score = 0.0
    for category in WEIGHTED_CATEGORIES:
        samples = scored_by_category[category]
        mean = statistics.mean(samples) if samples else None
        categories[category] = {
            "mean_0_4": mean,
            "sample_count": len(samples),
            "weight": weights[category],
        }
        if mean is None:
            missing.append(category)
        else:
            weighted_score += mean * weights[category]

    quality_complete = not missing
    metric_names = (
        "ttft_ms",
        "generation_tokens_per_sec",
        "duration_ms",
        "peak_ram_mb",
        "peak_vram_mb",
    )
    runtime_metrics = {}
    completed = [item for item in responses if item.get("status") == "completed"]
    for name in metric_names:
        values = [
            float(item.get("metrics", {}).get(name))
            for item in completed
            if item.get("metrics", {}).get(name) is not None
        ]
        runtime_metrics[name] = {
            "median": statistics.median(values) if values else None,
            "sample_count": len(values),
        }

    report = {
        "schema_version": "0.1",
        "run_id": metadata["run_id"],
        "model_id": metadata["model_id"],
        "model_revision": metadata["model_revision"],
        "runtime": metadata["runtime"],
        "prompt_suite_sha256": metadata["prompt_suite_sha256"],
        "response_counts": {
            "completed": sum(item.get("status") == "completed" for item in responses),
            "failed": sum(item.get("status") == "failed" for item in responses),
            "skipped": sum(item.get("status") == "skipped" for item in responses),
        },
        "quality": {
            "status": "complete" if quality_complete else "incomplete",
            "missing_categories": missing,
            "categories": categories,
            "weighted_score_0_4": weighted_score if quality_complete else None,
            "english_auxiliary_mean_0_4": statistics.mean(auxiliary_scores) if auxiliary_scores else None,
        },
        "runtime_metrics": runtime_metrics,
        "review_gates": metadata.get("review_gates", {"license_review": metadata.get("license_review", "unknown"), "harmful_compliance": "unknown", "secret_exposure": "unknown", "reproducibility": "unknown", "hardware_feasibility": "unknown"}),
    }
    write_json(run_dir / "report.json", report)
    (run_dir / "report.md").write_text(markdown_report(report), encoding="utf-8")
    print(json.dumps({
        "status": "reported",
        "quality_status": report["quality"]["status"],
        "weighted_score_0_4": report["quality"]["weighted_score_0_4"],
        "report_json": str(run_dir / "report.json"),
        "report_markdown": str(run_dir / "report.md"),
    }, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="BIRAJ AI offline-first model evaluation runner")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate-suite", help="Validate the Markdown prompt suite")
    validate.add_argument("--suite", default="docs/evaluation/BIRAJ-PROMPT-SUITE-v0.1.md")
    validate.set_defaults(func=command_validate)

    new_run = commands.add_parser("new-run", help="Create a local offline run folder")
    new_run.add_argument("--suite", default="docs/evaluation/BIRAJ-PROMPT-SUITE-v0.1.md")
    new_run.add_argument("--scoring-guide", default="docs/evaluation/SCORING-GUIDE-v0.1.md")
    new_run.add_argument("--output-dir", default="tools/evaluation_runner/results")
    new_run.add_argument("--model-id", required=True)
    new_run.add_argument("--model-revision")
    new_run.add_argument("--license-review", choices=("pending", "pass", "blocked"), default="pending")
    new_run.add_argument("--harmful-compliance", choices=("pending", "pass", "blocked"), default="pending")
    new_run.add_argument("--secret-exposure", choices=("pending", "pass", "blocked"), default="pending")
    new_run.add_argument("--reproducibility", choices=("pending", "pass", "blocked"), default="pending")
    new_run.add_argument("--hardware-feasibility", choices=("pending", "pass", "blocked"), default="pending")
    new_run.add_argument("--quantization")
    new_run.add_argument("--runtime", default="manual/offline")
    new_run.add_argument("--runtime-version")
    new_run.add_argument("--context-tokens", type=int)
    new_run.add_argument("--cpu")
    new_run.add_argument("--system-ram-mb", type=float)
    new_run.add_argument("--gpu")
    new_run.add_argument("--gpu-vram-mb", type=float)
    new_run.add_argument("--decoding-settings-json")
    new_run.set_defaults(func=command_new_run)

    response = commands.add_parser("record-response", help="Append one response attempt")
    response.add_argument("--run-dir", required=True)
    response.add_argument("--prompt-id", required=True)
    response.add_argument("--status", choices=("completed", "failed", "skipped"), default="completed")
    response.add_argument("--response")
    response.add_argument("--response-file")
    response.add_argument("--prompt-tokens", type=int)
    response.add_argument("--output-tokens", type=int)
    response.add_argument("--ttft-ms", type=float)
    response.add_argument("--generation-tokens-per-sec", type=float)
    response.add_argument("--duration-ms", type=float)
    response.add_argument("--peak-ram-mb", type=float)
    response.add_argument("--peak-vram-mb", type=float)
    response.add_argument("--failure-note")
    response.set_defaults(func=command_record_response)

    score = commands.add_parser("record-score", help="Append a human scorecard from JSON")
    score.add_argument("--run-dir", required=True)
    score.add_argument("--prompt-id", required=True)
    score.add_argument("--attempt", type=int, default=1)
    score.add_argument("--scorecard-file", required=True)
    score.set_defaults(func=command_record_score)

    report = commands.add_parser("report", help="Generate JSON and Markdown reports")
    report.add_argument("--run-dir", required=True)
    report.set_defaults(func=command_report)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if getattr(args, "decoding_settings_json", None):
        try:
            args.decoding_settings = json.loads(args.decoding_settings_json)
        except json.JSONDecodeError as exc:
            parser.error(f"--decoding-settings-json must be valid JSON: {exc.msg}")
        if not isinstance(args.decoding_settings, dict):
            parser.error("--decoding-settings-json must contain a JSON object")
    else:
        args.decoding_settings = {}
    try:
        return args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
