# Roains-Nethunter-Sapphire

> ## ⚠️ IMPORTANT — READ BEFORE BUILDING OR FLASHING
>
> **This project is for the Sapphire device family (Xiaomi Redmi Note 13 4G). It is not intended to be exclusive to ProjectRYU 3 Android 16.** The goal is to use the **Nethunter-Roains-Sapphire kernel project** on other compatible Sapphire ROMs and Android versions too (for example, Android 15 or Android 16).
>
> **A different ROM or Android version may require a separate kernel build and/or a ROM-specific flashable ZIP.** Do not assume that the currently compiled kernel or ZIP for ProjectRYU 3 Android 16 will work on another ROM.
>
> Before adapting the package for another ROM, inspect that ROM's own `boot.img`, `vendor_boot.img` and `init_boot.img` (if present), then verify the kernel source/ABI, vendor compatibility, modules, device tree, boot-image layout and partition requirements. Reuse the compiled kernel only when those checks show it is compatible; otherwise build a suitable kernel for the target environment.
>
> **Device target remains Sapphire.** ROM/Android-version compatibility must be verified separately for each target. An untested ROM must not be described as supported or safe to flash.

A custom NetHunter-oriented Linux kernel project for the Xiaomi Redmi Note 13 4G family.

- **Project:** Roains-Nethunter-Sapphire
- **Target devices:** Xiaomi Redmi Note 13 4G family — `sapphire` / `sapphiren`
- **SoC:** Qualcomm SM6225-AD (Snapdragon 685)
- **Kernel base:** ChicKernel 5.15
- **Target kernel version:** Linux 5.15.189
- **Kernel display/local version:** `Nethunter-Roains-Sapphire`
- **Architecture:** arm64
- **Root-manager policy:** no KernelSU or SukiSU binaries built into the kernel; users may use a compatible root solution separately.

> This README distinguishes project goals and requested configuration from features that have actually passed build and on-device testing. A configuration option being enabled does not by itself prove that a hardware feature works.

## Project goals

The goal is to provide a device-specific kernel with NetHunter-oriented networking, wireless testing foundations, USB gadget/HID support, container/chroot foundations, and a reliable installation package for Sapphire-family devices.

Main goals:

- NetHunter-oriented Wi-Fi stack and the adapted Linux 5.15 Wi-Fi injection patch.
- Wireless monitor-mode and packet-injection capability, subject to compatible hardware, driver and firmware.
- Linux namespaces, cgroups, networking and filesystem features needed by chroot/container environments.
- USB gadget and HID functions for supported USB workflows.
- Bluetooth and network-filesystem foundations.
- Correct Sapphire/Sapphiren device-tree handling.
- A validated, device-specific flashable ZIP with a custom installer.
- Reproducible GitHub Actions builds and downloadable build artifacts.

## Source and build configuration

The intended build uses ChicKernel's `android13-5.15-lts` source branch and starts from `chickernel_defconfig`. The build process must verify the source revision, apply the adapted NetHunter 5.15 patch cleanly, enable only options supported by this source tree, and retain the generated final `.config` for audit.

Build settings and targets:

- Linux 5.15.189 kernel line for the target device.
- arm64 architecture.
- LLVM/Clang toolchain; the project build plan pins LLVM/Clang 14 for reproducibility.
- NetHunter patch and device-supported configuration changes.
- Kernel image, loadable modules and device-tree build outputs.
- Build artifacts must include the final kernel configuration and build information so features can be checked instead of assumed.

The build must fail rather than silently continue if the patch does not apply, required configuration checks fail, compilation fails, or expected outputs are missing.

## Kernel feature configuration

The following are the requested feature groups. Their final availability must be checked in the generated `.config` and build outputs.

### NetHunter wireless and networking

- `cfg80211`, `mac80211`, wireless and `rfkill` foundations.
- Adapted NetHunter Wi-Fi injection patch for the 5.15 kernel line.
- Networking support used by wireless testing and packet analysis.
- Monitor mode and packet injection require real-device testing with the actual internal or external Wi-Fi chipset, driver and firmware.

### Namespaces and container/chroot foundations

- PID, network, IPC, UTS and user namespaces.
- Cgroups and supported resource accounting/control options, including memory accounting, freezer, CPU sets and process accounting/scheduling.
- BPF and seccomp where supported by the source and device configuration.
- OverlayFS, FUSE, loop devices and device mapper.
- VETH, TUN, bridge and VLAN networking.
- Netfilter, conntrack, iptables and nftables.

These kernel features are prerequisites or useful foundations; they do not alone provide a complete Docker installation on Android. Userspace, permissions, cgroup layout, SELinux policy and storage-driver support also matter.

### USB gadget and HID

Requested ConfigFS gadget functions include:

- HID
- FunctionFS
- Mass storage
- ACM
- RNDIS
- ECM
- NCM

Actual USB gadget/HID operation must be tested on the phone with the relevant cable, host and userspace tools.

### Bluetooth, filesystems and diagnostics

- Bluetooth core and supported USB Bluetooth and UART HCI transports.
- NFS client and server options where supported.
- IKCONFIG, Kprobes, Kprobe events and kallsyms for kernel inspection/debugging.

## External USB Wi-Fi adapters

External USB Wi-Fi adapter driver families, including Realtek and MediaTek, are **not promised as built-in kernel modules by this project**. Users can build or install compatible external drivers separately. Driver compatibility must match the exact kernel source, configuration, toolchain and device environment.

A driver being available for another kernel version does not prove it will load on this build.

## Features not yet integrated or verified

The following must not be advertised as working until source compatibility, compilation and device tests are complete:

- CAN bus driver families.
- SDR driver families.
- Any additional external Wi-Fi adapter drivers not explicitly integrated into this repository.
- Monitor mode and packet injection on the target phone and selected adapter.
- USB HID/gadget workflows and individual Bluetooth peripherals.
- Docker Engine or other container runtimes on Android.

## Device-tree and boot-image safety

This project targets the `sapphire` / `sapphiren` device family. Device-tree outputs must be identified and matched to the correct target before packaging.

- Do not substitute a generic Qualcomm DTB/DTBO for a device-specific Sapphire/Sapphiren DTB/DTBO.
- Preserve the target device's required boot-image layout and partition expectations.
- Verify the kernel image format, DTB/DTBO selection, ramdisk handling and any required boot header details against the actual device.
- Never label a ZIP as flash-ready solely because a kernel image or DTB was produced.

## Flashable ZIP and installer plan

The project intends to provide one custom, device-aware flashable ZIP with an AnyKernel3-based installer structure. The package is intended to support both:

1. **SukiSU app installation flow**, using the compatible AnyKernel3/manager-supported installation method.
2. **OrangeFox recovery installation**, by flashing the ZIP from recovery.

The package must use the same verified kernel payload and device checks for both installation paths. It must not contain KernelSU or SukiSU kernel binaries; the SukiSU app is an installation/management route, not a requirement to build SukiSU into this kernel.

Planned packaging contents:

- AnyKernel3 installer framework and project-specific installer scripts.
- Correct kernel image and only the verified device-specific DTB/DTBO payload required by the target.
- Correct module payload, if modules are shipped, with matching kernel release/version and dependency metadata.
- Device compatibility checks that reject unsupported targets instead of flashing blindly.
- Safe backup/restore behavior for the partitions/files the installer changes.
- Clear installer output and useful failure messages.
- ZIP integrity and archive-layout validation before release.

The installer must be checked for compatibility with the SukiSU app's supported ZIP installation mechanism and with OrangeFox recovery. Do not assume that a ZIP accepted by one route is automatically accepted by the other.

### Packaging release gate

A flashable ZIP is **not considered ready for release** until all of the following are verified:

- The kernel boots on the target device.
- The expected modules load successfully and match the running kernel.
- The live system can confirm the intended wireless monitor-mode and packet-injection behavior with supported hardware.
- The correct device tree and boot-image layout are confirmed.
- Installation and boot are tested through OrangeFox recovery.
- Installation is tested through the intended SukiSU app workflow.
- The resulting system boots and core functions work after each installation route.

Until these checks pass, packaging remains a work in progress and must not be described as tested or production-ready.

## Build and validation workflow

The GitHub Actions workflow should:

1. Check out the intended kernel source and record its revision.
2. Set the target architecture and pinned toolchain.
3. Apply and verify the adapted NetHunter patch.
4. Configure the kernel from the target defconfig and apply only supported missing options.
5. Save and audit the final `.config`.
6. Build the kernel, modules and device-tree outputs.
7. Stage outputs without mixing incompatible device trees or module releases.
8. Run artifact and package checks.
9. Publish clearly named artifacts with build logs, configuration and version details.

Recommended artifact naming:

- `Nethunter-Roains-Sapphire-5.15-kernel`
- `Nethunter-Roains-Sapphire-5.15-boot-payload`
- A separately named flashable ZIP only after the packaging release gates above pass.

A successful compile is not proof of successful boot, working monitor mode, packet injection, USB HID, Bluetooth, or container runtime support. Those require separate runtime validation.

## Installation and safety

- Confirm the exact device variant before flashing.
- Keep a known-good boot image/firmware backup and a recovery route available.
- Do not flash a package built for a different device or kernel base.
- Read installer output and stop if a device check or payload validation fails.
- The user is responsible for understanding the risks of kernel flashing; an incorrect image or device tree can prevent the phone from booting.

## Project status

This project is under active development. Build configuration, compiled support, packaging compatibility and real-device functionality are separate milestones. Only features verified in the source/configuration and tested on the target device should be marked as supported in release notes.

## Credits

- ChicKernel, as the kernel source base.
- The Linux kernel and NetHunter communities.
- AnyKernel3, for the installer framework when integrated and validated.
- Device and driver maintainers whose work is used by this project.
