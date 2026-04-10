#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


def read_var(text: str, name: str) -> str:
    match = re.search(rf"^{name}:=([^\n\r]+)", text, flags=re.MULTILINE)
    if not match:
        raise ValueError(f"Could not read {name} from Makefile")
    return match.group(1).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description="Read OpenWrt package metadata from Makefile")
    parser.add_argument("--makefile", required=True, help="Path to package Makefile")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    args = parser.parse_args()

    makefile_path = Path(args.makefile)
    if not makefile_path.is_file():
        raise SystemExit(f"Makefile not found: {makefile_path}")

    text = makefile_path.read_text(encoding="utf-8")
    pkg_version = read_var(text, "PKG_VERSION")
    pkg_release = read_var(text, "PKG_RELEASE")

    version_with_release = f"{pkg_version}-{pkg_release}"
    release_tag = f"v{version_with_release}"

    print(f"pkg_version={version_with_release}")
    print(f"release_tag={release_tag}")

    if args.github_output:
        output_path = Path(args.github_output)
        with output_path.open("a", encoding="utf-8") as fh:
            fh.write(f"pkg_version={version_with_release}\n")
            fh.write(f"release_tag={release_tag}\n")


if __name__ == "__main__":
    main()
