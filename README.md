# Roains-Nethunter-Sapphire

A NetHunter-oriented kernel project for the Xiaomi Redmi Note 13 4G family, targeting the **Sapphire** device (Qualcomm SM6225 / Snapdragon 685, arm64).

This repository follows the pinned Zepharo R9 kernel source revision documented below.

## Project identity and target

- **Project:** Roains-Nethunter-Sapphire
- **Kernel display name:** `Nethunter-Roains-Sapphire`
- **Target codename:** `sapphire`
- **Sapphiren:** installer accepts the codename string, but this hardware variant has not been validated; treat it as unsupported until tested.
- **SoC:** Qualcomm SM6225 (Snapdragon 685)
- **Architecture:** arm64
- **Kernel source version:** Linux 5.15.211
- **Canonical repository branch:** `main` (R9 line)
- **R9 development branch:** `build/r9-nethunter` (kept as the working branch during transition)

Android version alone does not establish compatibility. A ROM must have a compatible vendor ABI, boot image layout, device tree and module integration.

## Source and build configuration

The workflow fetches the kernel source at an immutable commit:

- **Source repository:** [topnotchfreaks/kernel_msm-5.15](https://github.com/topnotchfreaks/kernel_msm-5.15)
- **Pinned commit:** `c3405fe3912bf981aa5129a74410104140a25a93`
- **Expected kernel version:** `5.15.211`

The workflow also uses the Android Common Kernel build system from the `common-android13-5.15-lts` manifest and pins Android Clang to `r450784e`.

The starting point is the archived R9 configuration in `config/r9-kernel.config.gz.b64`. The build changes the LTO mode from the baseline's Full LTO to **ThinLTO** to reduce CI peak memory use. CFI and Shadow Call Stack are retained and checked in the generated configuration. The build uses two parallel jobs.

The kernel local version is set to `-Nethunter-Roains-Sapphire`; automatic local version suffixing is disabled.

## ABI compatibility

The R9 ABI baseline probe passed with an exact `module_layout` CRC match:

- Expected R9 CRC: `0x0222dd63`
- Observed baseline CRC: `0x0222dd63`

This validates the baseline comparison only; it is not a final kernel build or proof that every vendor module is compatible.

The full build has a separate ABI gate. It checks the candidate `Module.symvers`, the `module_layout` CRC, recorded R9 vendor imports, Qualcomm vendor WLAN imports, retained `cfg80211` exports and imports required by the newly built `mac80211.ko`. A successful compile by itself is insufficient. The workflow must stop before packaging if this ABI audit reports errors.

The ROM-provided Qualcomm vendor Wi-Fi stack is preserved. The project does not blindly replace the ROM's `cfg80211.ko` or Qualcomm WLAN modules.

## Configured kernel capabilities

The R9 configuration and feature script enable or request the following capabilities. The workflow verifies a core subset in the final generated `.config`; optional modules are packaged only when they are actually produced.

### Containers and networking

- PID, user, IPC, network and UTS namespaces.
- Cgroups, memory accounting, freezer, CPU sets, CPU accounting, process/device cgroups.
- BPF syscall and seccomp / seccomp filter.
- TUN and VETH.
- OverlayFS, FUSE, loop devices, device mapper and dm-crypt.
- Netfilter, conntrack, IPv4 NAT and IPv6 NAT.

These are kernel prerequisites, not a ready-made Docker environment. Android userspace, SELinux policy, cgroup mounts, storage and runtime configuration are also required.

### Wireless and NetHunter

- `CONFIG_CFG80211=m` and `CONFIG_MAC80211=m`.
- Project NetHunter mac80211 patch for monitor-frame injection handling.
- Ported `rtl8xxxu.ko`, built from source for this R9 kernel revision, with the selected RTL8188F support/firmware source.
- The ROM's `cfg80211.ko` remains the runtime provider and is intentionally excluded from the package.

The RTL8XXXU port is pinned to commit `e17efc7e23eb89bbf90f1c6b04bcb8512a35d571` from [android-gki-wifi-injection](https://github.com/roainxztar/android-gki-wifi-injection).

**Not included:** external out-of-tree adapter drivers such as separate RTL8812AU/8814AU, MTK or other vendor drivers. Those must be ported and built against this exact kernel ABI separately. The Qualcomm internal WLAN device is not advertised as injection-capable. Monitor mode and packet injection require compatible external hardware, firmware and real-device testing.

### USB gadget

- RNDIS, HID, FunctionFS and mass-storage ConfigFS functions.
- The R9 baseline already includes additional gadget functions such as ACM, ECM and NCM.

### CAN, NFS and SDR

- CAN core from the baseline, with VCAN, VXCAN and SLCAN requested as modules.
- NFS client, NFSv3/v4 and NFSD server requested as modules.
- Media/SDR and digital-TV support, including DVB core, DVB USB v2, RTL28xxU, RTL2832 and RTL2832 SDR module requests.

These options do not guarantee peripheral operation. CAN interfaces, NFS services and SDR devices need compatible hardware/userspace and runtime testing. The module collection script skips optional modules that were not produced; `mac80211.ko` is mandatory for packaging.

## Build outputs

After compilation, final-config checks and ABI verification pass, the workflow creates one compact **non-flashable** ZIP:

`Roains-Nethunter-Sapphire-5.15.211-kernel-modules.zip`

It contains:

- `Image.gz`: gzip-compressed ARM64 kernel Image.
- `modules/`: `mac80211.ko`, `rtl8xxxu.ko` and selected feature modules/dependencies actually produced by this build.
- `kernel.config` and `Module.symvers`.
- ABI audit report, module dependency/load additions, build information and SHA-256 checksums.

The workflow requires both `mac80211.ko` and `rtl8xxxu.ko`; it must not silently publish a payload missing either. Optional CAN, NFS and SDR modules are included only when the kernel build produces them. The ROM's `cfg80211.ko` is intentionally excluded so the existing Qualcomm vendor Wi-Fi provider is retained.

The archive is a kernel-and-modules payload for inspection and later installer integration. It is **not flashable**: it contains no recovery installer, boot image, DTBO, vendor_boot or partition image. Do not flash or install it directly. The earlier ABI baseline probe artifact is diagnostic-only and is not the full kernel/modules payload.

## Installer work is intentionally deferred

The next phase will build and test the project's own recovery installer separately. It will be added to the workflow only after the payload is validated and the device-specific boot and module layout has been confirmed. Any installer must be tested on the actual Sapphire device and ROM before being called flashable.

The installer design must account for the real boot header and ramdisk, active slot, vendor/vendor_dlkm/system_dlkm placement, module dependency metadata, partition mount behavior, backup and rollback. The current experimental installer is not included in this build and is not approved for flashing.

## Compatibility and validation policy

Before considering a ROM supported, verify:

- Exact device identity and hardware variant.
- Compatible vendor symbol CRCs and required vendor modules.
- Boot image header, partition layout and active-slot behavior.
- Device tree / DTBO expectations.
- Successful boot and module loading.
- Runtime tests for each requested feature and attached peripheral.

Android 13–17 is an intended ROM range, not a blanket compatibility guarantee. Do not mix R9 kernel images with R10 images or modules from another kernel release.

## Security and project status

- No KernelSU, SukiSU or other root manager is built into this kernel project.
- External USB Wi-Fi drivers beyond the explicitly ported RTL8XXXU driver are not part of the automated build.
- A configured feature is not considered functional until it has passed device-level testing.
- Use monitor mode and packet injection only on networks and devices you are authorized to test.

Compilation, ABI compatibility, installer correctness, successful boot and real-world feature functionality are separate milestones. This project remains under active development.
