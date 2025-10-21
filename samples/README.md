# Sample Memory Images

This directory contains information and pointers to public memory sample images used for testing and development.

Important: For privacy, legal, and repository-size reasons we do not commit large memory images into this repository. Instead we provide metadata and a small helper script to download samples to your local `samples/` directory.

Primary curated source:

- Memory sample aggregator: [pinesol93/MemoryForensicSamples](https://github.com/pinesol93/MemoryForensicSamples)

The canonical metadata is stored in `assets/samples.json`. To download the recommended samples listed there, run the helper script in `scripts/`.

Examples:

```bash
# List available samples
python scripts/fetch_samples.py --list

# Download the small samsclass memdump (interactive confirmation)
python scripts/fetch_samples.py --id samsclass-memdump

# Download all direct-downloadable samples non-interactively
python scripts/fetch_samples.py --all --yes
```

Please verify the licensing and terms of use for any sample you download. Do not add large memory images to the git history.
