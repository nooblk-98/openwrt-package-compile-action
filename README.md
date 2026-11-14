<div align="center">

# OpenWrt Package Builder

[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-OpenWrt%20Package%20Builder-2ea44f?logo=github)](https://github.com/marketplace/actions/openwrt-package-builder)
[![Release](https://img.shields.io/github/v/release/nooblk-98/openwrt-package-compile-action)](https://github.com/nooblk-98/openwrt-package-compile-action/releases)
![License: MIT](https://img.shields.io/badge/license-MIT-yellow)

Build OpenWrt `.ipk` and `.apk` packages in GitHub Actions with the official OpenWrt SDK.

[Quick start](#quick-start) • [Publish on release](#publish-packages-on-release) • [Inputs](#inputs) • [SDK versions](#sdk-versions) • [Tips](#tips)

</div>

---

Point the action at a package directory in your repository and it does the rest:

- Downloads the OpenWrt SDK for your version and target, and caches it between runs
- Updates the feeds and resolves your package's dependencies
- Compiles only your package
- Collects the `.ipk` / `.apk` files and uploads them as a workflow artifact

The package format follows the SDK: OpenWrt 25.x and newer produce `.apk`, older releases produce `.ipk`.

## Quick start

```yaml
- uses: actions/checkout@v4

- uses: nooblk-98/openwrt-package-compile-action@v1
  with:
    package-name: luci-app-example
    sdk-version: 24.10.5
```

The built package is uploaded as the `openwrt-package` artifact.

> [!TIP]
> If your package is in a subdirectory, set `package-dir`. Otherwise the action looks for a folder named after `package-name`, then falls back to the repository root.

## Publish packages on release

This workflow builds both formats whenever you publish a GitHub release and attaches the packages to it. Save it as `.github/workflows/release.yml`:

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
> Releases created with the default `GITHUB_TOKEN` do not trigger other workflows. Create releases from the GitHub UI, the `gh` CLI, or with a personal access token.

For a real-world example, see [luci-app-wban](https://github.com/nooblk-98/luci-app-wban/blob/main/.github/workflows/release.yml).

## Inputs

| Input | Default | Description |
|---|---|---|
| `package-name` | **required** | OpenWrt package name, for example `luci-app-example` |
| `sdk-version` | **required** | OpenWrt release, for example `24.10.5` |
| `package-dir` | `""` | Package directory in your repository |
| `sdk-target` | `x86` | SDK target, for example `ath79` or `ramips` |
| `sdk-subtarget` | `64` | SDK subtarget, for example `generic` or `mt7621` |
| `sdk-url-override` | `""` | Explicit SDK tarball URL (skips auto-detection) |
| `sdk-cache-key-override` | `""` | Explicit SDK cache key |
| `feeds-update` | `base packages luci` | Feeds to update |
| `feeds-install` | `comgt sms-tool` | Extra feed packages to install before building |
| `feeds-install-all-from` | `""` | Feeds to install every package from, for example `luci` |
| `artifact-name` | `openwrt-package` | Name of the uploaded artifact |
| `upload-artifact` | `true` | Set to `false` to skip the artifact upload |
| `retention-days` | `14` | Artifact retention in days |
| `make-jobs` | `""` | Parallel make jobs (defaults to `nproc`) |

### Outputs

| Output | Description |
|---|---|
| `artifact-dir` | Absolute path to the built package files on the runner |

## SDK versions

Any release listed at [downloads.openwrt.org/releases](https://downloads.openwrt.org/releases/) can be used as `sdk-version`.

| Version | Package format |
|---|---|
| `25.12.x` | `.apk` |
| `24.10.x` | `.ipk` |
| `23.05.x` | `.ipk` |

## Tips

- **Architecture-independent packages** (LuCI apps, scripts, `PKGARCH:=all`) only need one build per format. The default `x86/64` target is fine.
- **Compiled packages** need one build per target. Add `sdk-target` and `sdk-subtarget` to your matrix.
- **Missing dependencies?** Make sure the feed that provides them is listed in `feeds-update`.
- Works on both `ubuntu-24.04` and `ubuntu-latest` (26.04) runners.
