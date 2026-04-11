# OpenWrt Package Builder Action

Reusable GitHub Action to build OpenWrt packages using the OpenWrt SDK. Supports both `ipk` (stable) and `apk` (25.x+) output formats.

## What this action does

- Downloads and caches the OpenWrt SDK tarball
- Updates feeds (`packages`, `luci` by default)
- Stages your local package into the SDK
- Installs the package and resolves its declared dependencies
- Builds only the target package
- Collects generated `ipk` / `apk` files
- Uploads artifact (optional)

## Inputs

| Input | Required | Default | Description |
|---|---|---|---|
| `package-name` | yes | — | OpenWrt package name (e.g. `luci-app-netstat`) |
| `package-dir` | no | `""` | Path to package directory in your repo. Defaults to `package-name`, then repo root |
| `sdk-version` | yes | — | OpenWrt release version (e.g. `24.10.5`) |
| `sdk-target` | no | `x86` | SDK target (e.g. `ath79`, `ramips`) |
| `sdk-subtarget` | no | `64` | SDK subtarget (e.g. `generic`, `mt7621`) |
| `sdk-url-override` | no | `""` | Explicit SDK tarball URL (skips auto-resolve) |
| `sdk-cache-key-override` | no | `""` | Explicit cache key override |
| `feeds-update` | no | `packages luci` | Space-separated feeds to update |
| `feeds-install` | no | `comgt sms-tool` | Extra feed packages to install before build |
| `feeds-install-all-from` | no | `""` | Feeds to bulk-install all packages from (e.g. `luci`) |
| `artifact-name` | no | `openwrt-package` | Name of the uploaded artifact |
| `upload-artifact` | no | `true` | Set to `false` to skip artifact upload |
| `retention-days` | no | `14` | Artifact retention period in days |
| `make-jobs` | no | `""` | Parallel jobs for make (empty = `nproc`) |

## Outputs

| Output | Description |
|---|---|
| `artifact-dir` | Absolute path to collected package files on the runner |

---

## Complete example with auto release

This is the recommended workflow. Place it at `.github/workflows/build.yml` in your package repository.

- **Push** to `main` with changes to `Makefile` or `files/` → builds both IPK + APK and publishes a GitHub Release automatically
- **Manual run** (`workflow_dispatch`) → builds only, no release published

```yaml
name: Build OpenWrt Package

on:
  workflow_dispatch:
  push:
    branches:
      - main
    paths:
      - "Makefile"
      - "files/**"

permissions:
  contents: write

jobs:
  meta:
    name: Read Package Metadata
    runs-on: ubuntu-latest
    outputs:
      release_tag: ${{ steps.meta.outputs.release_tag }}
    steps:
      - uses: actions/checkout@v4
      - id: meta
        run: |
          PKG_VERSION=$(sed -n 's/^PKG_VERSION:=//p' Makefile | head -n1)
          PKG_RELEASE=$(sed -n 's/^PKG_RELEASE:=//p' Makefile | head -n1)
          echo "release_tag=v${PKG_VERSION}-${PKG_RELEASE}" >> "$GITHUB_OUTPUT"

  build:
    name: Build ${{ matrix.label }}
    runs-on: ubuntu-latest
    needs: meta
    strategy:
      fail-fast: false
      matrix:
        include:
          - label: IPK
            sdk_version: 24.10.5
          - label: APK
            sdk_version: 25.12.1
    steps:
      - uses: actions/checkout@v4
      - uses: nooblk-98/openwrt-package-compile-action@v1
        with:
          package-name: your-package-name
          sdk-version: ${{ matrix.sdk_version }}
          sdk-target: x86
          sdk-subtarget: "64"
          artifact-name: your-package-name-${{ matrix.sdk_version }}

  release:
    name: Publish Release
    runs-on: ubuntu-latest
    needs: [meta, build]
    if: always() && needs.build.result == 'success'
    steps:
      - uses: actions/download-artifact@v4
        with:
          path: ${{ runner.temp }}/release-files
          merge-multiple: true
      - uses: softprops/action-gh-release@v2
        with:
          tag_name: ${{ needs.meta.outputs.release_tag }}
          name: your-package-name ${{ needs.meta.outputs.release_tag }}
          files: ${{ runner.temp }}/release-files/*
          fail_on_unmatched_files: true
          overwrite: true
```

> Replace `your-package-name` with your actual package name.  
> The release tag is read automatically from `PKG_VERSION` and `PKG_RELEASE` in your `Makefile`.

---

## Package in a subdirectory

If your package files are inside a subdirectory (e.g. `my-package/Makefile`), add the `package-dir` input:

```yaml
      - uses: nooblk-98/openwrt-package-compile-action@v1
        with:
          package-name: my-package
          package-dir: my-package
          sdk-version: ${{ matrix.sdk_version }}
          artifact-name: my-package-${{ matrix.sdk_version }}
```

Also update the `meta` and `paths` trigger accordingly:

```yaml
    paths:
      - "my-package/Makefile"
      - "my-package/**"
```

And in the `meta` job:

```yaml
          PKG_VERSION=$(sed -n 's/^PKG_VERSION:=//p' my-package/Makefile | head -n1)
          PKG_RELEASE=$(sed -n 's/^PKG_RELEASE:=//p' my-package/Makefile | head -n1)
```

---

## Build only (no release)

For a simple build-only workflow with manual trigger:

```yaml
name: Build OpenWrt Package

on:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - label: IPK
            sdk_version: 24.10.5
          - label: APK
            sdk_version: 25.12.1
    steps:
      - uses: actions/checkout@v4
      - uses: nooblk-98/openwrt-package-compile-action@v1
        with:
          package-name: your-package-name
          sdk-version: ${{ matrix.sdk_version }}
          artifact-name: your-package-name-${{ matrix.sdk_version }}
```

---

## Available SDK versions

Any release available at `archive.openwrt.org/releases/` can be used as `sdk-version`:

| Version | Format | Notes |
|---|---|---|
| `24.10.5` | `ipk` | Latest stable |
| `25.12.1` | `apk` | Latest release |
| `23.05.6` | `ipk` | Previous stable |

---

## License

MIT
