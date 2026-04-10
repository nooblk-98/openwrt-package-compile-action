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
- `sdk-version` (required): OpenWrt release version (example `24.10.5`)
- `sdk-target` (default: `x86`): OpenWrt target path segment
- `sdk-subtarget` (default: `64`): OpenWrt subtarget path segment
- `sdk-url-override` (default: empty): Optional explicit SDK URL
- `sdk-cache-key-override` (default: empty): Optional explicit cache key
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
            sdk_version: 24.10.5
          - label: APK
            sdk_version: 25.12.1

    steps:
      - uses: actions/checkout@v4

      - name: Build package
        uses: nooblk-98/openwrt-package-compile-action@v1
        with:
          package-name: luci-app-3ginfo-lite
          package-dir: luci-app-3ginfo-lite
          sdk-version: ${{ matrix.sdk_version }}
          sdk-target: x86
          sdk-subtarget: "64"
          artifact-name: luci-app-3ginfo-lite-${{ matrix.sdk_version }}
```

## Publish as public action

1. Push this repository to GitHub as public.
2. Create a tag (example `v1`).
3. Reference it from other repos as `nooblk-98/openwrt-package-compile-action@v1`.
4. For updates, move major tag to latest compatible release (example `v1`).

The file `.github/workflows/publish_marketplace.yml` is an example CI workflow that uses this action from the same repo.

## Notes

- Reference example:
  - `uses: nooblk-98/openwrt-package-compile-action@v1`
- Always use the latest release tag available in this repository (update the tag when a new version is released).
