#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify release files directory is not empty")
    parser.add_argument("--dir", required=True, dest="release_dir")
    args = parser.parse_args()

    release_dir = Path(args.release_dir)
    if not release_dir.exists():
        raise SystemExit(f"Release directory does not exist: {release_dir}")

    files = sorted(p for p in release_dir.iterdir() if p.is_file())
    print(f"Release directory: {release_dir}")
    for item in files:
        print(item.name)

    if not files:
        raise SystemExit("No release files found")


if __name__ == "__main__":
    main()
