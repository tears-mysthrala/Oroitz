"""Simple benchmarking script for Oroitz quick_triage workflow.

This runs the quick_triage workflow against a sample image and writes a
small JSON report under results/benchmark_report.json.

The script will look for a sample image in a set of known candidate
locations (e.g. `samples/memdump.mem`, `samples/windows-sample-memory.dmp`,
`samples/linux-sample-memory.bin`) and will also accept an explicit
`--sample` path to override the automatic discovery.

Designed for CI smoke benchmarking and quick local checks.
"""

import argparse
import json
import time
from pathlib import Path
from typing import Optional

try:
    from oroitz.core.config import config
    from oroitz.core.executor import Executor
    from oroitz.core.workflow import registry, seed_workflows
except Exception:
    # Allow running the benchmark directly from a developer checkout where the
    # package isn't installed into the active interpreter. This inserts the
    # repository root on sys.path so `import oroitz` works without `poetry install`.
    import sys
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from oroitz.core.config import config
    from oroitz.core.executor import Executor
    from oroitz.core.workflow import registry, seed_workflows


def find_sample(candidates: Optional[list[Path]] = None) -> Optional[Path]:
    """Return the first existing sample image from the candidate list.

    The default list includes `samples/memdump.mem`, then repo-root sample
    filenames that may already exist in this repository.
    """
    if candidates is None:
        candidates = [
            Path("samples/memdump.mem"),
            Path("samples/memdump.dmp"),
            Path("samples/windows-sample-memory.dmp"),
            Path("samples/linux-sample-memory.bin"),
        ]

    for p in candidates:
        if p.exists():
            return p
    return None


def run_benchmark(image_path: Path, out_path: Path) -> None:
    seed_workflows()

    workflow = registry.get("quick_triage")
    if not workflow:
        raise SystemExit("quick_triage workflow not found")

    executor = Executor()

    # Get image size for reporting
    image_size_bytes = image_path.stat().st_size
    image_size_gb = image_size_bytes / (1024**3)

    # Track memory usage if psutil is available
    memory_info = {}
    try:
        import psutil

        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024**2)  # MB
        memory_info["initial_memory_mb"] = initial_memory
    except ImportError:
        print("psutil not available, skipping memory monitoring")

    start = time.time()
    results = executor.execute_workflow(workflow, str(image_path), config.default_profile)
    end = time.time()

    # Get final memory usage
    if "initial_memory_mb" in memory_info:
        try:
            final_memory = process.memory_info().rss / (1024**2)  # MB
            memory_info["final_memory_mb"] = final_memory
            memory_info["memory_delta_mb"] = final_memory - memory_info["initial_memory_mb"]
            memory_info["peak_memory_mb"] = max(initial_memory, final_memory)  # Approximation
        except Exception:
            pass

    report = {
        "image": str(image_path),
        "image_size_bytes": image_size_bytes,
        "image_size_gb": image_size_gb,
        "profile": config.default_profile,
        "timestamp": int(start),
        "duration_seconds": end - start,
        "memory_info": memory_info,
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
    if memory_info:
        print(f"Memory usage: {memory_info.get('memory_delta_mb', 'N/A'):.1f} MB delta")


def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run quick_triage benchmark")
    p.add_argument(
        "--sample",
        type=str,
        help="Path to memory image to use for benchmark (overrides auto-discovery)",
    )
    p.add_argument(
        "--output",
        type=str,
        default="results/benchmark_report.json",
        help="Output JSON report path",
    )
    return p


if __name__ == "__main__":
    parser = _build_arg_parser()
    args = parser.parse_args()

    out = Path(args.output)

    sample = Path(args.sample) if args.sample else find_sample()

    if not sample or not sample.exists():
        print("Sample image not found; skipping benchmark")
    else:
        run_benchmark(sample, out)
