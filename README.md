# OpenWrt Package Builder Action

Reusable public GitHub Action to build OpenWrt packages with the OpenWrt SDK.

## What this action does

- Downloads and caches an OpenWrt SDK tarball
- Updates/install feeds
- Stages your local package into SDK `package/<name>`
- Builds only the target package
- Collects generated `ipk`/`apk` files
- Uploads artifact (optional)

## Inputs

- `package-name` (required): OpenWrt package name
- `package-dir` (required): Path to package directory in caller repo
- `sdk-url` (required): OpenWrt SDK archive URL
- `sdk-cache-key` (required): Cache key suffix (example `24.10.5-x86-64-ipk-v1`)
- `output-extensions` (default: `ipk`): Space-separated extensions to collect
- `required-extension` (default: `ipk`): Required extension; action fails if missing
- `feeds-update` (default: `packages luci`): Space-separated feeds to update
- `feeds-install-all-from` (default: `luci`): Feeds to install all packages from
- `feeds-install` (default: `comgt sms-tool`): Specific feed packages to install
- `artifact-name` (default: `openwrt-package`): Upload artifact name
- `upload-artifact` (default: `true`): Upload output with `actions/upload-artifact`
- `retention-days` (default: `14`): Artifact retention days
- `make-jobs` (default: empty): Make job count; empty uses `nproc`

## Output

- `artifact-dir`: absolute path to collected files on the runner

## Usage

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
            sdk_cache_key: 24.10.5-x86-64-ipk-v1
            sdk_url: https://archive.openwrt.org/releases/24.10.5/targets/x86/64/openwrt-sdk-24.10.5-x86-64_gcc-13.3.0_musl.Linux-x86_64.tar.zst
            output_extensions: ipk
            required_extension: ipk

    steps:
      - uses: actions/checkout@v4

      - name: Build package
        uses: YOUR_ORG/openwrt-package-compile-action@v1
        with:
          package-name: luci-app-3ginfo-lite
          package-dir: luci-app-3ginfo-lite
          sdk-url: ${{ matrix.sdk_url }}
          sdk-cache-key: ${{ matrix.sdk_cache_key }}
          output-extensions: ${{ matrix.output_extensions }}
          required-extension: ${{ matrix.required_extension }}
          artifact-name: luci-app-3ginfo-lite-${{ matrix.required_extension }}
```

## Publish as public action

1. Push this repository to GitHub as public.
2. Create a tag (example `v1`).
3. Reference it from other repos as `OWNER/REPO@v1`.
4. For updates, move major tag to latest compatible release (example `v1`).

The file `.github/workflows/publish_marketplace.yml` is an example CI workflow that uses this action from the same repo.
