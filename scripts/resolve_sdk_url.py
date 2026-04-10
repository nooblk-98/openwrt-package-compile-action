#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from typing import Iterable
from urllib.request import urlopen


def version_tuple(value: str) -> tuple[int, ...]:
    parts = []
    for part in value.split('.'):
        if part.isdigit():
            parts.append(int(part))
        else:
            parts.append(0)
    return tuple(parts)


def choose_best(candidates: Iterable[str]) -> str:
    items = list(candidates)
    if not items:
        raise ValueError("No SDK archive candidates found")

    def score(name: str) -> tuple[tuple[int, ...], str]:
        gcc = re.search(r"_gcc-([0-9.]+)_", name)
        gcc_ver = version_tuple(gcc.group(1)) if gcc else (0,)
        return (gcc_ver, name)

    return sorted(items, key=score)[-1]


def safe_cache_key(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]", "-", value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Resolve OpenWrt SDK URL for a release/target/subtarget")
    parser.add_argument("--sdk-version", required=True)
    parser.add_argument("--sdk-target", default="x86")
    parser.add_argument("--sdk-subtarget", default="64")
    parser.add_argument("--sdk-url-override", default="")
    parser.add_argument("--sdk-cache-key-override", default="")
    parser.add_argument("--github-output", default=os.environ.get("GITHUB_OUTPUT", ""))
    args = parser.parse_args()

    if args.sdk_url_override:
        sdk_url = args.sdk_url_override
    else:
        index_url = (
            f"https://archive.openwrt.org/releases/{args.sdk_version}/"
            f"targets/{args.sdk_target}/{args.sdk_subtarget}/"
        )
        try:
            with urlopen(index_url) as response:
                html = response.read().decode("utf-8", errors="replace")
        except Exception as exc:
            raise SystemExit(f"Failed to fetch SDK index {index_url}: {exc}") from exc

        pattern = re.compile(
            rf"openwrt-sdk-{re.escape(args.sdk_version)}-{re.escape(args.sdk_target)}-"
            rf"{re.escape(args.sdk_subtarget)}_[^\"/]*?\.tar\.zst"
        )
        sdk_url = index_url + choose_best(pattern.findall(html))

    if args.sdk_cache_key_override:
        sdk_cache_key = safe_cache_key(args.sdk_cache_key_override)
    else:
        sdk_cache_key = safe_cache_key(
            f"{args.sdk_version}-{args.sdk_target}-{args.sdk_subtarget}-v1"
        )

    print(f"sdk_url={sdk_url}")
    print(f"sdk_cache_key={sdk_cache_key}")

    if args.github_output:
        output_path = Path(args.github_output)
        with output_path.open("a", encoding="utf-8") as fh:
            fh.write(f"sdk_url={sdk_url}\n")
            fh.write(f"sdk_cache_key={sdk_cache_key}\n")


if __name__ == "__main__":
    main()
