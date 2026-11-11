"""Refresh or verify repository artifact hashes and inventories without touching inputs.

Paths are relative to NSCache_Experiment_DB, including ../README.md and the ZIP.
The hash manifest omits its own digest; the directory inventory includes itself
and the manifest. Git's ignored build/runtime/cache files are excluded.
"""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(repo, *args):
    return subprocess.check_output(['git', '-C', str(repo), *args]).decode().split('\0')


def snapshot(root=ROOT, check=False, base='origin/main'):
    repo = root.parent
    manifest = root / 'provenance/artifact_SHA256SUMS.txt'
    inventory = root / 'provenance/directory_inventory.txt'
    changes = root / 'reports/changed_files.txt'
    names = {n for n in git(repo, 'ls-files', '--cached', '--others', '--exclude-standard', '-z') if n}
    names.update(str(p.relative_to(repo)) for p in (manifest, inventory, changes))
    files = sorted(repo / n for n in names if (repo / n).is_file())
    # Metadata output paths must also be present on the initial invocation.
    files = sorted(set(files + [manifest, inventory, changes]))
    if any(p.is_symlink() or not p.resolve().is_relative_to(repo.resolve()) for p in files):
        raise ValueError('artifact path is a symlink or escapes repository')
    rel = lambda p: Path(os.path.relpath(p, root)).as_posix()
    inventory_text = ''.join(rel(p) + '\n' for p in sorted(files, key=rel))
    changed = {n for n in git(repo, 'diff', '--name-only', '-z', base, '--') if n}
    changed.update(n for n in git(repo, 'ls-files', '--others', '--exclude-standard', '-z') if n)
    changed.update(str(p.relative_to(repo)) for p in (manifest, inventory, changes))
    changed_text = ''.join(n + '\n' for n in sorted(changed))
    if check:
        if inventory.read_text() != inventory_text or changes.read_text() != changed_text:
            raise ValueError('file inventory or changed-file list is stale')
    else:
        inventory.write_text(inventory_text)
        changes.write_text(changed_text)
    manifest_text = ''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel(p)}\n'
        for p in sorted(files, key=rel) if p != manifest)
    if check:
        if manifest.read_text() != manifest_text:
            raise ValueError('SHA-256 manifest is stale or an artifact changed')
    else:
        manifest.write_text(manifest_text)
    return len(files), len(files) - 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='verify without writing')
    parser.add_argument('--base', default='origin/main', help='base for reports/changed_files.txt')
    args = parser.parse_args()
    try:
        files, hashes = snapshot(check=args.check, base=args.base)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        parser.exit(1, f'Manifest verification failed: {exc}\n')
    print(f'{"Verified" if args.check else "Updated"}: {files} inventory entries, {hashes} SHA-256 entries')
