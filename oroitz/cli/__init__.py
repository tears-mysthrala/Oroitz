# CLI entrypoints

from pathlib import Path
from typing import Optional

import click

from oroitz.core.executor import Executor
from oroitz.core.output import OutputExporter, OutputNormalizer
from oroitz.core.telemetry import setup_logging
from oroitz.core.workflow import registry, seed_workflows


@click.group()
@click.option("--log-level", default="INFO", help="Logging level", type=str)
def cli(log_level: str) -> None:
    """Oroitz - Cross-platform Volatility 3 wrapper"""
    setup_logging(log_level)
    seed_workflows()


@cli.command()
@click.argument("image_path", type=click.Path(exists=True, path_type=Path))
@click.option("--profile", default="windows", help="Memory image profile", type=str)
@click.option("--output", type=click.Path(path_type=Path), help="Output file path")
def quick_triage(image_path: Path, profile: str, output: Optional[Path]) -> None:
    """Run quick triage analysis on a memory image."""
    click.echo(f"Running quick triage on {image_path} with profile {profile}")

    # Get workflow
    workflow = registry.get("quick_triage")
    if not workflow:
        click.echo("Quick triage workflow not found", err=True)
        return

    # Check compatibility
    if not registry.validate_compatibility("quick_triage", profile):
        click.echo(f"Workflow not compatible with profile {profile}", err=True)
        return

    # Execute workflow
    executor = Executor()
    results = executor.execute_workflow(workflow, str(image_path), profile)

    # Normalize output
    normalizer = OutputNormalizer()
    normalized = normalizer.normalize_quick_triage(results)

    # Export if requested
    if output:
        exporter = OutputExporter()
        exporter.export_json(normalized, output)
        click.echo(f"Results exported to {output}")
    else:
        # Print summary
        click.echo(f"Processes found: {len(normalized.processes)}")
        click.echo(f"Network connections: {len(normalized.network_connections)}")
        click.echo(f"Malfind hits: {len(normalized.malfind_hits)}")


if __name__ == "__main__":
    cli()  # type: ignore
