# Roains-Nethunter-Sapphire

Build target: Xiaomi Redmi Note 13 4G family (sapphire / sapphiren), Qualcomm Khaje, Linux 5.15.189.

The GitHub Actions workflow:
1. Fetches the pinned ChicKernel `android13-5.15-lts` source branch.
2. Strictly checks and applies the repository's adapted NetHunter 5.15 Wi-Fi injection patch.
3. Configures the kernel from ChicKernel's `chickernel_defconfig`, adding missing supported NetHunter/chroot options.
4. Compiles the kernel, modules and device-tree targets.
5. Publishes a validation artifact containing the image, installed modules, configuration and available DTB/DTBO build outputs.

**Packaging is deliberately separate from compilation.** No generic Qualcomm DTB/DTBO will be substituted for a Sapphire/Sapphiren device tree. A flashable AnyKernel3 ZIP will only be assembled after the correct device DTB/DTBO and boot-image layout are verified. External USB Wi-Fi adapter drivers are not built into this project; users may install compatible drivers separately.

Wi-Fi injection depends on the actual radio/driver and cannot be guaranteed by configuration alone. Docker Engine inside Android chroots also depends on Android userspace, cgroups, permissions, SELinux policy and storage-driver support.
