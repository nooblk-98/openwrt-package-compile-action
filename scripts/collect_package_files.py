#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def collect_candidates(sdk_dir: Path, pkg_name: str, extensions: list[str]) -> list[Path]:
    packages_dir = sdk_dir / "bin" / "packages"
    if not packages_dir.exists():
        return []

    patterns = []
    for ext in extensions:
        patterns.append(f"{pkg_name}_*.{ext}")
        patterns.append(f"{pkg_name}-*.{ext}")

    matches: list[Path] = []
    for file_path in packages_dir.rglob("*"):
        if not file_path.is_file():
            continue
        for pattern in patterns:
            if file_path.match(pattern):
                matches.append(file_path)
                break

    return matches


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect built OpenWrt package files")
    parser.add_argument("--sdk-dir", required=True)
    parser.add_argument("--pkg-name", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--extensions", nargs="+", required=True)
    parser.add_argument("--required-ext", required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    sdk_dir = Path(args.sdk_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = collect_candidates(sdk_dir, args.pkg_name, args.extensions)
    for src in files:
        shutil.copy2(src, output_dir / src.name)

    required = list(output_dir.glob(f"*.{args.required_ext}"))
    if not required:
        print(f"No .{args.required_ext} package was produced for {args.label}")
        print("Debug: available files from SDK output path")
        packages_dir = sdk_dir / "bin" / "packages"
        if packages_dir.exists():
            for idx, path in enumerate(sorted(p for p in packages_dir.rglob("*") if p.is_file()), start=1):
                if idx > 200:
                    break
                print(path)
        raise SystemExit(1)

    print(f"Collected files in {output_dir}:")
    for path in sorted(output_dir.glob("*")):
        if path.is_file():
            print(path.name)


if __name__ == "__main__":
    main()
