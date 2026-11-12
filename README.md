# Roains-Nethunter-Sapphire

Build target: Xiaomi Redmi Note 13 4G family (`sapphire` / `sapphiren`), Qualcomm SM6225-AD (Snapdragon 685), Linux 5.15.189.

## Current build configuration

The GitHub Actions workflow:

1. Fetches ChicKernel's `android13-5.15-lts` source branch.
2. Strictly checks and applies the adapted NetHunter 5.15 Wi-Fi injection patch.
3. Starts from ChicKernel's `chickernel_defconfig` and enables missing supported options for NetHunter, chroot environments and device functionality.
4. Compiles the kernel, modules and device-tree targets.
5. Publishes a validation artifact with the kernel image, installed modules, configuration and available DTB/DTBO build outputs.

The workflow currently requests the following configuration groups:

- **Namespaces:** PID, network, IPC, UTS and user namespaces.
- **Cgroups and isolation:** cgroups, memory accounting, freezer, CPU sets, process accounting/scheduling, BPF and seccomp.
- **Container/chroot foundations:** OverlayFS, FUSE, loop devices, device mapper, VETH, TUN, bridge, VLAN, netfilter, conntrack, iptables and nftables.
- **NetHunter wireless foundations:** cfg80211, mac80211, wireless and rfkill, together with the adapted 5.15 Wi-Fi injection patch.
- **USB gadget / HID:** USB gadget and ConfigFS functions for HID, FunctionFS, mass storage, ACM, RNDIS, ECM and NCM.
- **Bluetooth foundations:** Bluetooth, USB Bluetooth transport and UART HCI transport.
- **Network filesystems:** NFS client and NFS server options.
- **Kernel inspection/debugging:** IKCONFIG, Kprobes, Kprobe events and kallsyms.

These are configuration targets requested by the workflow; the current compilation and its generated `.config` must complete successfully before they can be confirmed in the build artifact. Hardware-dependent functions such as monitor mode, packet injection, USB adapter compatibility and Bluetooth dongle support still require testing on the actual phone and peripherals.

## Not included in this build

- **No KernelSU, SukiSU or other built-in root manager.** This is intentionally a no-root kernel; root can be installed separately by the user.
- External USB Wi-Fi adapter drivers (including Realtek and MediaTek adapter families) are not compiled by this project. Compatible drivers can be installed separately.
- CAN bus and SDR driver families have not yet been integrated into the current workflow; they are candidates for a later build after source and kernel-version compatibility checks.
- Enabling container-related kernel options does not by itself guarantee Docker Engine support on Android. Docker also depends on Android userspace, cgroups, permissions, SELinux policy and storage-driver support.

## Packaging and device-tree safety

Packaging is deliberately separate from compilation. No generic Qualcomm DTB/DTBO will be substituted for a Sapphire/Sapphiren device tree. A flashable **AnyKernel3** ZIP will only be assembled after the correct device DTB/DTBO and boot-image layout are verified. Device-tree outputs from a build are not considered flash-ready until their compatibility is established.

## Hardware and runtime validation

Wi-Fi injection depends on the actual radio, driver, firmware and hardware capabilities; applying the patch or enabling configuration options alone cannot guarantee it. The same applies to USB HID gadget operation, Bluetooth peripherals, Docker and other userspace-dependent NetHunter features.
