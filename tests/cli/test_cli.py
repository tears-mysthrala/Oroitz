"""Tests for CLI module."""

import tempfile
from pathlib import Path

from click.testing import CliRunner

from oroitz.cli import cli


def test_cli_quick_triage():
    """Test CLI quick_triage command."""
    runner = CliRunner()

    # Create a fake image file
    with tempfile.NamedTemporaryFile(suffix=".dmp", delete=False) as tmp:
        fake_image = Path(tmp.name)

    try:
        # Run quick_triage command
        result = runner.invoke(cli, [
            "quick-triage",
            str(fake_image),
            "--profile", "Win10x64_19041"
        ])

        # Should succeed (mock data)
        assert result.exit_code == 0
        assert "Running quick triage" in result.output
        assert "Processes found:" in result.output
        assert "Network connections:" in result.output
        assert "Malfind hits:" in result.output

    finally:
        fake_image.unlink()


def test_cli_quick_triage_with_output():
    """Test CLI quick_triage with JSON output."""
    runner = CliRunner()

    # Create a fake image file and output file
    with tempfile.NamedTemporaryFile(suffix=".dmp", delete=False) as tmp:
        fake_image = Path(tmp.name)
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        output_file = Path(tmp.name)

    try:
        # Run quick_triage command with output
        result = runner.invoke(cli, [
            "quick-triage",
            str(fake_image),
            "--profile", "Win10x64_19041",
            "--output", str(output_file)
        ])

        # Should succeed
        assert result.exit_code == 0
        assert "Results exported to" in result.output

        # Check output file exists and has content
        assert output_file.exists()
        content = output_file.read_text()
        assert "processes" in content
        assert "network_connections" in content
        assert "malfind_hits" in content

    finally:
        fake_image.unlink()
        output_file.unlink(missing_ok=True)


def test_cli_quick_triage_invalid_image():
    """Test CLI quick_triage with non-existent image."""
    runner = CliRunner()

    # Run with non-existent image
    result = runner.invoke(cli, [
        "quick-triage",
        "/nonexistent/image.dmp",
        "--profile", "Win10x64_19041"
    ])

    # Should fail due to missing file
    assert result.exit_code != 0
