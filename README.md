# Roains-Nethunter-Sapphire

A NetHunter-oriented custom kernel project for the Xiaomi Redmi Note 13 4G family.

## Target

- **Project:** Roains-Nethunter-Sapphire
- **Kernel display name:** `Nethunter-Roains-Sapphire`
- **Devices:** Sapphire / Sapphiren (`sapphire`, `sapphiren`)
- **SoC:** Qualcomm SM6225 / Snapdragon 685
- **Architecture:** arm64
- **Kernel line:** Linux 5.15
- **Compatibility goal:** Android 13–17 ROMs that retain a compatible Sapphire vendor ABI

Android version alone does not establish kernel compatibility. Each ROM must be checked for its boot layout, vendor modules, exported symbol CRCs, device tree and userspace integration. A ROM not tested against the ABI baseline must not be described as supported.

## Kernel source and baseline

The build branch pins the Zepharo R9-matching source revision:

- Repository: `topnotchfreaks/kernel_msm-5.15`
- Commit: `c3405fe3912bf981aa5129a74410104140a25a93`
- Expected kernel line: `5.15.211`
- Android Common Kernel manifest: `common-android13-5.15-lts`
- Clang: `r450784e`
- LTO: Full LTO, matching the R9 baseline

The baseline configuration is extracted from the original R9 stock `boot.img`. R10 kernel images, configs, source changes and build artifacts are not used as the build base.

The project keeps its existing GitHub repository. The current development build is isolated on branch `build/r9-nethunter`.

## ABI and vendor-module policy

The ROM's vendor modules are not rebuilt or blindly replaced.

The original R9 vendor ramdisk module ABI is recorded in `abi/r9-vendor-abi.tsv.gz.b64`. The build checks the candidate `Module.symvers`, `module_layout` CRC, retained `cfg80211` exports, QCA vendor WLAN imports and the new `mac80211.ko` imports.

Important design choices:

- `CONFIG_MODVERSIONS=y` is preserved.
- `cfg80211` and `mac80211` are built as modules, not built into the kernel.
- The ROM's existing Qualcomm `cfg80211.ko` and QCA WLAN stack are retained.
- The NetHunter patch is limited to mac80211 TX injection handling.
- cfg80211 channel-policy changes and in-tree RTL8187/ZD1211RW driver changes are deliberately excluded.
- External USB Wi-Fi adapter drivers are not built by this workflow; the user builds those separately.

A build must fail if the verified ABI checks detect incompatible CRCs. A successful compile alone is not sufficient.

## Feature configuration

The build starts from the extracted R9 configuration and changes only missing or required options.

Feature groups include:

- NetHunter mac80211 frame injection support.
- Wireless framework support for separately built external adapters.
- PID, user, IPC and network namespaces; cgroups and container foundations.
- USB gadget/HID and RNDIS support.
- CAN interfaces.
- NFS client/server support.
- SDR and RTL-SDR/DVB foundations.
- Existing Bluetooth, networking, filesystem and device features retained from the baseline.

The final generated `.config` is checked and uploaded as a diagnostic artifact. Features are not advertised as working merely because a config option is enabled; hardware and userspace testing is still required.

Docker/container functionality also depends on Android userspace, cgroups, SELinux policy, storage drivers and runtime configuration.

## Build output

The GitHub Actions workflow builds:

- Raw arm64 kernel `Image`.
- New feature modules, including patched `mac80211.ko`.
- `Module.symvers` and final kernel configuration for ABI review.
- A compact flashable ZIP named:

`Roains-Nethunter-Sapphire-5.15.211.zip`

The ZIP contains the kernel, selected new modules and a project-specific recovery installer. The installer is custom and **does not use AnyKernel/AnyKernel3**.

The installer is designed to:

1. Check for Sapphire/Sapphiren.
2. Back up the active boot image and module metadata.
3. Repack the current ROM's boot image while preserving its other boot components.
4. Add the new modules without blindly replacing the ROM's Qualcomm vendor Wi-Fi stack.
5. Update module dependency/load metadata.
6. Abort if required partitions or module directories cannot be accessed safely.

The installer has not been declared production-ready until it passes recovery testing on the actual device.

## Compatibility policy

Android 13–17 is the project target, not a blanket guarantee for every ROM.

A ROM is eligible only after confirming:

- Sapphire/Sapphiren device identity.
- Compatible 5.15 GKI/KMI and vendor symbol CRCs.
- Required vendor modules and dependencies.
- Boot image header and partition layout.
- Device tree and DTBO expectations.
- Successful boot and runtime tests.

The same kernel binary may work across multiple ROMs when their vendor ABI and hardware interfaces are compatible. Separate builds or installer variants are only needed when evidence shows a real difference.

## Safety and status

- Do not flash an artifact that has not passed the ABI gate.
- Keep a known-good boot backup and recovery route.
- Do not flash on another device family.
- Do not assume monitor mode, packet injection, USB HID, SDR, CAN, NFS or Docker works until tested on hardware.
- No KernelSU or SukiSU binaries are built into this kernel.
- No R10 artifacts are used as the build base.

This is an active development project. Build success, module compatibility, installation success and real-device functionality are separate validation milestones.
