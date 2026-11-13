# Roains-Nethunter-Sapphire

A NetHunter-oriented custom kernel project for the Xiaomi Redmi Note 13 4G family (Sapphire / Sapphiren).

## Target

- **Project:** Roains-Nethunter-Sapphire
- **Kernel display name:** `Nethunter-Roains-Sapphire`
- **Primary device codename:** `sapphire`
- **Installer device check:** accepts `sapphire` / `sapphiren` strings; Sapphiren hardware is not yet validated and should not be considered supported.
- **SoC / architecture:** Qualcomm SM6225 (Snapdragon 685), arm64
- **Active development branch:** `build/r9-nethunter`
- **Kernel release line:** Linux `5.15.211` (Zepharo R9 source baseline)
- **Build system:** Android Common Kernel build system, `common-android13-5.15-lts`
- **Compiler:** pinned Android Clang `r450784e`
- **LTO used by this workflow:** ThinLTO
- **Parallel build jobs:** 2

Android version by itself does not guarantee compatibility. A ROM must retain a compatible Sapphire vendor ABI, boot layout, device tree and module integration. Do not treat an untested ROM as supported.

## Pinned source and configuration

The active workflow fetches the exact kernel source revision:

- **Repository:** [topnotchfreaks/kernel_msm-5.15](https://github.com/topnotchfreaks/kernel_msm-5.15)
- **Commit:** `c3405fe3912bf981aa5129a74410104140a25a93`
- **Expected kernel version:** `5.15.211`

The starting configuration is the R9 baseline stored in `config/r9-kernel.config.gz.b64`. The workflow verifies the important baseline options, then applies the project feature configuration and the NetHunter mac80211 patch.

**LTO clarification:** the archived R9 baseline has Full LTO enabled, but the active workflow explicitly switches the build configuration to **ThinLTO** to reduce peak memory use on the CI runner. CFI and Shadow Call Stack remain enabled. The final generated configuration is checked for ThinLTO; this project does not claim that the current build uses Full LTO.

The workflow pins the RTL8XXXU port source to commit `e17efc7e23eb89bbf90f1c6b04bcb8512a35d571` from [android-gki-wifi-injection](https://github.com/roainxztar/android-gki-wifi-injection). It overlays the selected driver sources onto the exact 5.15.211 kernel tree and builds them there; prebuilt `.ko` files from another kernel are not reused.

## Wireless and module compatibility

The ROM's Qualcomm vendor Wi-Fi stack must be preserved unless ABI evidence proves a safe replacement. This project does **not** blindly replace the ROM's `cfg80211.ko` or Qualcomm WLAN modules.

- `CONFIG_MODULES=y` and `CONFIG_MODVERSIONS=y` are required.
- `cfg80211` and `mac80211` are configured as modules for ABI/build purposes.
- The ROM-provided `cfg80211.ko` remains the runtime provider and is not packaged by this workflow.
- The project builds and packages its patched `mac80211.ko`.
- The NetHunter patch changes mac80211 TX handling for injected monitor frames. It does not apply cfg80211 channel-policy changes or RTL8187/ZD1211RW-specific patches.
- The ported in-tree `rtl8xxxu.ko` is built from source for this kernel and packaged with its embedded RTL8188F firmware support.
- Other out-of-tree USB Wi-Fi adapter drivers are **not** built automatically by this workflow; they must be separately ported/built against this exact kernel ABI.

The build's ABI gate compares the candidate `Module.symvers`, `module_layout`, retained cfg80211 exports, recorded R9 vendor imports, QCA vendor WLAN imports and the new mac80211 module imports. A successful compile alone is not sufficient. If the ABI check fails, the workflow must not produce the flashable ZIP.

The Qualcomm internal WLAN device is not advertised as an injection-capable adapter. External adapter support, monitor mode and packet injection require compatible hardware, firmware and real-device testing.

## Kernel feature configuration

The workflow starts from the R9 configuration and changes only the required or missing options. The configured feature set includes:

- **Wireless:** modular cfg80211/mac80211, NetHunter mac80211 injection changes and the ported RTL8XXXU USB wireless driver.
- **Containers / namespaces:** PID, user, IPC, network and UTS namespaces; cgroups, memory accounting, freezer, CPU sets, CPU accounting, BPF syscall and seccomp support.
- **Container networking / storage foundations:** TUN, VETH, OverlayFS, FUSE, loop devices, device mapper, dm-crypt, netfilter, conntrack, IPv4 NAT and IPv6 NAT.
- **USB gadget:** RNDIS, HID, FunctionFS and mass-storage support (the latter existing in the R9 baseline).
- **CAN:** VCAN, VXCAN and SLCAN modules.
- **NFS:** NFS client, NFSv3/v4 and NFSD server modules.
- **SDR / digital TV:** media and SDR support, DVB core, DVB USB v2, RTL28xxU, RTL2832 and RTL2832 SDR modules.

These are kernel configuration/build capabilities, not proof that every feature works on every ROM or peripheral. Docker/container use also depends on Android userspace, SELinux policy, cgroups, storage and runtime setup. USB HID, SDR, CAN, NFS, monitor mode and injection all require device-level testing.

## Build artifacts

When all build and verification stages pass, GitHub Actions uploads:

- Kernel `Image`.
- Patched `mac80211.ko` and selected feature modules, including `rtl8xxxu.ko` when successfully built.
- Final kernel `.config`, `Module.symvers`, ABI report and build diagnostics.
- Flashable package: `Roains-Nethunter-Sapphire-5.15.211.zip`.

The module packager collects the selected feature modules and available dependencies. It intentionally excludes `cfg80211.ko`, preserving the ROM's vendor copy.

## Installer design and limitations

The ZIP uses the project's own recovery installer under `installer/`. **It does not use AnyKernel or AnyKernel3.**

The custom installer is intended to:

1. Reject devices that do not identify as Sapphire/Sapphiren.
2. Require accessible boot and vendor module locations, including the ROM's existing `cfg80211.ko`.
3. Back up the active boot image and module metadata to `/sdcard/Roains-Nethunter-Backup`.
4. Unpack the current boot image, replace its kernel payload, and repack it while retaining the other unpacked boot components.
5. Install the selected new modules and append their dependency/load entries without replacing the ROM's cfg80211 provider.
6. Restore module files and metadata if a module or boot write fails.

**Important:** this installer has not been declared production-ready until it is tested in recovery on the actual device and ROM. Keep a known-good boot image and a working recovery route. Do not flash an artifact unless its build, ABI verification and installation requirements have passed.

## Compatibility policy

Android 13–17 may be within the project's intended ROM range, but this is not a blanket compatibility guarantee. Before using a ROM, verify:

- Sapphire device identity (Sapphiren remains untested).
- Compatible 5.15 GKI/KMI and vendor symbol CRCs.
- Required vendor modules and their dependencies.
- Boot image header, partition layout and active slot handling.
- Device tree / DTBO expectations.
- Successful boot, module loading and runtime tests.

The same kernel binary may work across ROMs only when their vendor ABI and hardware interfaces are compatible. Separate builds or installer variants should be introduced only when testing demonstrates a real requirement.

## Security and project status

- No KernelSU or SukiSU binaries are built into this project.
- R10 images, configs and artifacts are not used as the R9 build base.
- Do not flash on another device family.
- Do not assume a configured feature is operational until it has been tested on hardware.
- Use monitor mode and packet injection only on networks and devices you are authorized to test.

This is an active development project. Compilation, ABI compatibility, installation success, successful boot and real-world feature functionality are separate validation milestones.
