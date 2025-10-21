"""Simple benchmarking script for Oroitz quick_triage workflow.

This runs the quick_triage workflow against a sample image (samples/memdump.mem)
and writes a small JSON report under results/benchmark_report.json.

Designed for CI smoke benchmarking and quick local checks.
"""

import json
import time
from pathlib import Path

from oroitz.core.config import config
from oroitz.core.executor import Executor
from oroitz.core.workflow import registry, seed_workflows


def run_benchmark(image_path: Path, out_path: Path) -> None:
    seed_workflows()

    workflow = registry.get("quick_triage")
    if not workflow:
        raise SystemExit("quick_triage workflow not found")

    executor = Executor()

    start = time.time()
    results = executor.execute_workflow(workflow, str(image_path), config.default_profile)
    end = time.time()

    report = {
        "image": str(image_path),
        "profile": config.default_profile,
        "timestamp": int(start),
        "duration_seconds": end - start,
        "plugins": [],
    }

    for r in results:
        report["plugins"].append(
            {
                "plugin": r.plugin_name,
                "success": bool(r.success),
                "duration": float(r.duration),
                "attempts": int(r.attempts) if getattr(r, "attempts", None) is not None else 0,
                "used_mock": bool(getattr(r, "used_mock", False)),
            }
        )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"Benchmark finished in {report['duration_seconds']:.2f}s; report: {out_path}")


if __name__ == "__main__":
    sample = Path("samples/memdump.mem")
    out = Path("results/benchmark_report.json")
    if not sample.exists():
        print("Sample image not found; skipping benchmark")
    else:
        run_benchmark(sample, out)
