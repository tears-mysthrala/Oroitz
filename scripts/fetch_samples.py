#!/usr/bin/env python3
"""
Download sample memory images referenced in
`assets/samples.json` into the local `samples/` directory.

Usage:
    python scripts/fetch_samples.py --list
    python scripts/fetch_samples.py --id samsclass-memdump
    python scripts/fetch_samples.py --all --yes

This script tries to detect whether a link is a direct-download (non-HTML)
by issuing a HEAD request. Links that require interactive providers (Google
Drive, Mega) will be printed and skipped with instructions for manual
download.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict

SAMPLES_DIR = Path("samples")
ASSETS_FILE = Path("assets/samples.json")
DEFAULT_LARGE_THRESHOLD = 200 * 1024 * 1024  # 200 MB


def load_metadata() -> Dict[str, Any]:
    if not ASSETS_FILE.exists():
        print(f"Metadata file not found: {ASSETS_FILE}")
        sys.exit(1)
    with open(ASSETS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def is_direct_download(url: str) -> bool:
    """Return True if the URL looks like a direct downloadable file (non-HTML).

    This does a best-effort HEAD request; if the server doesn't support HEAD
    or returns a text/html content-type, we consider it non-direct.
    """
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as resp:
            ctype = resp.getheader("Content-Type", "")
            if ctype and "html" in ctype.lower():
                return False
            return True
    except Exception:
        # If HEAD fails, try GET but only check the headers; do not download
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=10) as resp:
                ctype = resp.getheader("Content-Type", "")
                if ctype and "html" in ctype.lower():
                    return False
                return True
        except Exception:
            return False


def download_url(
    url: str,
    dest: Path,
    non_interactive: bool = False,
    size_threshold: int = DEFAULT_LARGE_THRESHOLD,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)

    # Try HEAD to get content length
    size = None
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as resp:
            cl = resp.getheader("Content-Length")
            if cl:
                size = int(cl)
    except Exception:
        size = None

    if size and size > size_threshold and not non_interactive:
        print(f"Remote file is large ({size / (1024 * 1024):.1f} MB): {url}")
        if input("Proceed to download? [y/N]: ").strip().lower() not in ("y", "yes"):
            print("Skipping")
            return

    print(f"Downloading: {url} -> {dest}")

    # Stream download and compute sha256
    hashobj = hashlib.sha256()
    try:
        with urllib.request.urlopen(url) as resp, open(dest, "wb") as out:
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                out.write(chunk)
                hashobj.update(chunk)
    except Exception as e:
        if dest.exists():
            dest.unlink()
        print(f"Download failed: {e}")
        return

    print(f"Saved {dest} ({dest.stat().st_size} bytes), sha256={hashobj.hexdigest()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch sample memory images into samples/")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List available samples from metadata")
    group.add_argument("--id", type=str, help="Download a specific sample by id")
    group.add_argument(
        "--all", action="store_true", help="Attempt to download all direct-downloadable samples"
    )
    parser.add_argument(
        "--yes", action="store_true", help="Assume yes for all confirmations (non-interactive)"
    )
    args = parser.parse_args()

    meta = load_metadata()
    samples = {s["id"]: s for s in meta.get("recommended_samples", [])}

    if args.list:
        print("Available samples (metadata):")
        for s in samples.values():
            print(f"- {s['id']}: {s['name']} -> {s['download_url']}")
        print("\nSource aggregator:", meta.get("source_repo"))
        return

    if args.id:
        item = samples.get(args.id)
        if not item:
            print(f"Unknown sample id: {args.id}")
            sys.exit(2)
        url = item["download_url"]
        filename = item.get("recommended_filename") or Path(url).name
        if not is_direct_download(url):
            print(
                (
                    "The link for {id} is not a direct-download URL. "
                    "Please download manually: {url}"
                ).format(id=args.id, url=url)
            )
            return
        download_url(url, SAMPLES_DIR / filename, non_interactive=args.yes)
        return

    if args.all:
        for item in samples.values():
            url = item["download_url"]
            filename = item.get("recommended_filename") or Path(url).name
            if not is_direct_download(url):
                print(f"Skipping (not direct-download): {item['id']} -> {url}")
                continue
            download_url(url, SAMPLES_DIR / filename, non_interactive=args.yes)
        return


if __name__ == "__main__":
    main()
