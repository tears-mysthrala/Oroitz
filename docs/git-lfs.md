# Git LFS for Sample Files

This repository uses Git LFS (Large File Storage) to manage large forensic sample files without bloating the main repository.

## Setup

1. Install Git LFS:
   ```bash
   git lfs install
   ```

2. Track sample files:
   ```bash
   git lfs track "samples/*.7z"
   git lfs track "samples/*.mem"
   git add .gitattributes
   git commit -m "Track large samples with LFS"
   ```

3. Push to remote (ensure LFS is enabled on the repository):
   ```bash
   git push origin main
   ```

## Migration

If you have existing large files in history, use `git lfs migrate` to move them to LFS:

```bash
git lfs migrate import --include="samples/*.7z,samples/*.mem" --yes
git push origin main
```

## Usage

- Add large samples as usual: `git add samples/large-file.7z`
- LFS will handle storage and retrieval automatically.
- For CI, ensure workflows can access LFS-tracked files (GitHub Actions supports LFS).

## Notes

- LFS requires the remote repository to have LFS enabled.
- Files are stored in LFS storage, pointers in Git.
- Avoid committing untracked large files; use LFS or releases instead.