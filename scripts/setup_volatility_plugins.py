"""Utility to fetch Volatility 3 community plugins for Oroitz.

This script downloads the community plugin bundle (community3) and places it
in a local directory, optionally updating an environment file so Oroitz can
discover the plugins automatically at runtime.
"""

from __future__ import annotations

import argparse
import io
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Iterable


COMMUNITY_ZIP_URL = (
    "https://github.com/volatilityfoundation/community3/archive/refs/heads/master.zip"
)
DEFAULT_DEST = Path("vendor") / "volatility_plugins"


def download(url: str) -> bytes:
    with urllib.request.urlopen(url) as response:  # type: ignore[call-arg]
        if response.status != 200:
            raise RuntimeError(f"Unexpected HTTP status {response.status} while downloading")
        return response.read()


def extract_plugins(archive_bytes: bytes, dest: Path, *, force: bool = False) -> Path:
    dest.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as zip_file:
            zip_file.extractall(tmp_path)

        # community3 archive has a single top-level directory
        extracted_roots = list(tmp_path.iterdir())
        if not extracted_roots:
            raise RuntimeError("Downloaded archive is empty")

        source_root = extracted_roots[0]
        target_root = dest / "community3"

        if target_root.exists():
            if force:
                shutil.rmtree(target_root)
            else:
                # Leave existing plugins in place
                return target_root

        shutil.move(str(source_root), target_root)
        return target_root


def ensure_env_entry(env_path: Path, key: str, values: Iterable[str]) -> None:
    env_path.parent.mkdir(parents=True, exist_ok=True)
    if env_path.exists():
        content = env_path.read_text(encoding="utf-8").splitlines()
    else:
        content = []

    value = os.pathsep.join(values)
    key_prefix = f"{key}="
    updated = False
    for index, line in enumerate(content):
        if line.startswith(key_prefix):
            content[index] = f"{key}={value}"
            updated = True
            break

    if not updated:
        content.append(f"{key}={value}")

    env_path.write_text("\n".join(content) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch Volatility 3 community plugins")
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help="Destination directory for plugins (default: vendor/volatility_plugins)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download plugins even if destination already exists",
    )
    parser.add_argument(
        "--update-env",
        action="store_true",
        help="Update/create an .env entry with the plugin directory",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        default=Path(".env"),
        help="Path to .env file to update (default: ./.env)",
    )
    parser.add_argument(
        "--env-key",
        type=str,
        default="OROITZ_PLUGIN_DIRS",
        help="Environment variable key to set when using --update-env",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    dest = args.dest.expanduser().resolve()

    try:
        print("Downloading Volatility community plugins...")
        archive_bytes = download(COMMUNITY_ZIP_URL)
        target_dir = extract_plugins(archive_bytes, dest, force=args.force)
        print(f"Plugins installed in: {target_dir}")

        if args.update_env:
            ensure_env_entry(args.env_file, args.env_key, [str(target_dir)])
            print(f"Updated {args.env_file} with {args.env_key}={target_dir}")

        print(
            "Set environment variable OROITZ_PLUGIN_DIRS or use the updated .env file to enable\n"
            "hash extraction plugins (hashdump/cachedump)."
        )
    except urllib.error.URLError as error:
        print(
            f"WARNING: Could not download community plugins ({error}).\n"
            "Install them manually or re-run this script when connectivity is available.",
            file=sys.stderr,
        )
    except Exception as exc:  # pylint: disable=broad-except
        print(f"WARNING: Failed to set up community plugins: {exc}", file=sys.stderr)

    # Always return 0 so build scripts continue even if download fails
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

