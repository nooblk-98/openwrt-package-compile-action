<div align="center">

# OpenWrt Package Builder

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-OpenWrt%20Package%20Builder-2ea44f?logo=github)](https://github.com/marketplace/actions/openwrt-package-builder)
[![Release](https://img.shields.io/github/v/release/nooblk-98/openwrt-package-compile-action)](https://github.com/nooblk-98/openwrt-package-compile-action/releases)
![License: MIT](https://img.shields.io/badge/license-MIT-yellow)

Build OpenWrt `.ipk` and `.apk` packages in GitHub Actions with the official OpenWrt SDK.

[Quick start](#quick-start) • [How it works](#how-it-works) • [Examples](#examples) • [Inputs](#inputs) • [SDK versions](#sdk-versions) • [Troubleshooting](#troubleshooting)

</div>

---

Point the action at a package directory in your repository. It downloads the matching OpenWrt SDK, compiles only your package, and hands you the `.ipk` / `.apk` files as a workflow artifact. No Docker image or self-hosted runner is needed.

- **Zero setup:** just give it a package name and an OpenWrt release.
- **Fast reruns:** the SDK is cached between workflow runs.
- **Any target:** build for `x86/64`, `ath79`, `ramips`, `mediatek` or any other target OpenWrt publishes an SDK for.
- **Both package formats:** OpenWrt 25.x and newer produce `.apk`, while older releases produce `.ipk`.

## Quick start

Add a workflow such as `.github/workflows/build.yml` to your package repository:

```yaml
name: Build package

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: nooblk-98/openwrt-package-compile-action@v1
        with:
          package-name: luci-app-example
          sdk-version: 24.10.5
```

When the run finishes, download the built package from the `openwrt-package` artifact on the run's summary page.

> [!TIP]
> The action looks for your package in a folder named after `package-name`, then falls back to the repository root. If it lives somewhere else, set `package-dir` (for example `package-dir: packages/luci-app-example`).

## How it works

1. **Resolve the SDK.** Finds the SDK tarball for `sdk-version`, `sdk-target` and `sdk-subtarget` on [archive.openwrt.org](https://archive.openwrt.org/releases/), picking the newest GCC build when there are several.
2. **Prepare the runner.** Installs the build dependencies. On Ubuntu 25.10+ runners it switches back to GNU coreutils, because the SDK rejects the default Rust coreutils.
3. **Restore or download the SDK.** Uses `actions/cache`, keyed by SDK file name.
4. **Update feeds.** Each feed in `feeds-update` is cloned fresh, so a stale cached feed never breaks the build. The packages in `feeds-install` and `feeds-install-all-from` are then installed.
5. **Build.** Copies your package into the SDK, enables only that package, and runs `make package/<name>/compile`.
6. **Collect.** Gathers the produced `.ipk` / `.apk` files and uploads them as an artifact.

## Examples

### Publish packages on release

Build both formats whenever you publish a GitHub release, and attach the files to it:

```yaml
name: Build and publish packages

on:
  release:
    types: [published]

permissions:
  contents: write

jobs:
  build:
    name: Build ${{ matrix.format }}
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - format: ipk
            sdk: 24.10.5
          - format: apk
            sdk: 25.12.1
    steps:
      - uses: actions/checkout@v4
      - uses: nooblk-98/openwrt-package-compile-action@v1
        with:
          package-name: luci-app-example
          sdk-version: ${{ matrix.sdk }}
          artifact-name: luci-app-example-${{ matrix.format }}

  publish:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          path: dist
          merge-multiple: true
      - uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ github.event.release.tag_name }}
          files: dist/*
          fail_on_unmatched_files: true
```

> [!NOTE]
> Releases created with the default `GITHUB_TOKEN` don't trigger other workflows. Create the release from the GitHub UI, the `gh` CLI, or with a personal access token.

For a real-world setup, see [luci-app-wban](https://github.com/nooblk-98/luci-app-wban/blob/main/.github/workflows/release.yml).

### Build a compiled package for several targets

Packages that contain native code need one build per target:

```yaml
strategy:
  matrix:
    include:
      - { target: x86,      subtarget: '64' }
      - { target: ath79,    subtarget: generic }
      - { target: ramips,   subtarget: mt7621 }
      - { target: mediatek, subtarget: filogic }
steps:
  - uses: actions/checkout@v4
  - uses: nooblk-98/openwrt-package-compile-action@v1
    with:
      package-name: my-daemon
      sdk-version: 24.10.5
      sdk-target: ${{ matrix.target }}
      sdk-subtarget: ${{ matrix.subtarget }}
      feeds-install: ""
      artifact-name: my-daemon-${{ matrix.target }}-${{ matrix.subtarget }}
```

### Use the built files in a later step

Skip the artifact upload and work with the files directly through the `artifact-dir` output:

```yaml
- uses: nooblk-98/openwrt-package-compile-action@v1
  id: build
  with:
    package-name: luci-app-example
    sdk-version: 24.10.5
    upload-artifact: false

- run: ls -l "${{ steps.build.outputs.artifact-dir }}"
```

## Inputs

| Input | Default | Description |
|---|---|---|
| `package-name` | **required** | OpenWrt package name, for example `luci-app-example`. |
| `sdk-version` | **required** | OpenWrt release, for example `24.10.5`. |
| `package-dir` | `""` | Package directory in your repository. If empty, the action uses `<package-name>/` when it exists, otherwise the repository root. |
| `sdk-target` | `x86` | SDK target, for example `ath79` or `ramips`. |
| `sdk-subtarget` | `64` | SDK subtarget, for example `generic` or `mt7621`. |
| `sdk-url-override` | `""` | Explicit SDK tarball URL, which skips auto-detection. Use it for snapshots or mirrors. |
| `sdk-cache-key-override` | `""` | Explicit SDK cache key. |
| `feeds-update` | `base packages luci` | Feeds to update. |
| `feeds-install` | `comgt sms-tool` | Extra feed packages to install before building. Set it to `""` if you don't need them. |
| `feeds-install-all-from` | `""` | Feeds to install every package from, for example `luci`. |
| `artifact-name` | `openwrt-package` | Name of the uploaded artifact. |
| `upload-artifact` | `true` | Set to `false` to skip the artifact upload. |
| `retention-days` | `14` | Artifact retention in days. |
| `make-jobs` | `""` | Number of parallel make jobs (defaults to `nproc`). |

### Outputs

| Output | Description |
|---|---|
| `artifact-dir` | Absolute path to the built package files on the runner. |

## SDK versions

Any release listed at [archive.openwrt.org/releases](https://archive.openwrt.org/releases/) works as `sdk-version`.

| Version | Package format |
|---|---|
| `25.12.x` | `.apk` |
| `24.10.x` | `.ipk` |
| `23.05.x` | `.ipk` |

The action runs on `ubuntu-24.04` and `ubuntu-latest` (26.04) runners.

> [!TIP]
> Architecture-independent packages (LuCI apps, shell scripts, `PKGARCH:=all`) only need one build per package format, and the default `x86/64` target is fine for them.

## Troubleshooting

- **`Failed to fetch SDK index`:** check that the version, target and subtarget exist on the archive. For snapshots or custom builds, use `sdk-url-override`.
- **Missing dependency:** add the feed that provides it to `feeds-update`, and add the package itself to `feeds-install`.
- **Build failure with little output:** when the parallel build fails, the action retries with `-j1 V=s`, so the end of the log shows the full compiler output.
- **`No .ipk or .apk package was produced`:** make sure `package-name` matches the `PKG_NAME` in your package's `Makefile`. The action lists the files in the SDK's `bin/packages/` directory to help you check.
