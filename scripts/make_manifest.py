#!/usr/bin/env python3
"""Write or verify MANIFEST.sha256: one SHA-256 checksum per project file.

  python scripts/make_manifest.py           write MANIFEST.sha256 (run after the final evidence run)
  python scripts/make_manifest.py --check   verify every listed file; exit 1 on any difference

Same format as `sha256sum`, so `sha256sum -c MANIFEST.sha256` also works on Linux.
Excluded: secrets (.env), local environments and caches, IDE folders, the manifest itself.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"
SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".idea", ".vscode"}
SKIP_FILES = {".env", "MANIFEST.sha256", ".DS_Store"}
SKIP_SUFFIXES = {".pyc", ".mp4", ".mkv"}


def project_files():
    for path in sorted(ROOT.rglob("*")):
        rel = path.relative_to(ROOT)
        if not path.is_file() or any(part in SKIP_DIRS for part in rel.parts):
            continue
        if path.name in SKIP_FILES or path.suffix in SKIP_SUFFIXES:
            continue
        yield rel.as_posix()


def sha256(rel: str) -> str:
    h = hashlib.sha256()
    with open(ROOT / rel, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def write():
    lines = [f"{sha256(rel)}  {rel}" for rel in project_files()]
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {MANIFEST.name}: {len(lines)} files.")


def check() -> int:
    if not MANIFEST.exists():
        print("MANIFEST.sha256 not found. Create it with: python scripts/make_manifest.py")
        return 1
    listed = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if line.strip():
            digest, rel = line.split("  ", 1)
            listed[rel] = digest
    problems = []
    for rel, digest in listed.items():
        if not (ROOT / rel).is_file():
            problems.append(f"MISSING  {rel}")
        elif sha256(rel) != digest:
            problems.append(f"CHANGED  {rel}")
    problems += [f"NEW      {rel}" for rel in project_files() if rel not in listed]
    for p in problems:
        print(p)
    print(f"{len(listed) - sum(p.startswith(('MISSING', 'CHANGED')) for p in problems)}/{len(listed)} "
          f"files match" + ("" if not problems else f", {len(problems)} difference(s)"))
    return 1 if problems else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--check", action="store_true")
    sys.exit(check() if p.parse_args().check else write())
