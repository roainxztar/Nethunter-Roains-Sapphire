#!/usr/bin/env bash
set -euo pipefail
DEFCONFIG="$1"
KERNEL_SRC="$2"
CFG="$KERNEL_SRC/scripts/config"
test -x "$CFG" || chmod +x "$CFG"

# Preserve the original R9 configuration; change only missing or required options.
"$CFG" --file "$DEFCONFIG" --set-str LOCALVERSION "-Nethunter-Roains-Sapphire"
"$CFG" --file "$DEFCONFIG" --disable LOCALVERSION_AUTO

# This vendor kernel must retain exports used by prebuilt vendor_dlkm modules.
# The inherited R9 whitelist points to a buildbot-only absolute path; disable
# symbol trimming rather than risk dropping symbols required by external modules.
"$CFG" --file "$DEFCONFIG" --disable TRIM_UNUSED_KSYMS
"$CFG" --file "$DEFCONFIG" --set-str UNUSED_KSYMS_WHITELIST ""

# Wireless framework: modules, not built-in. Keep the ROM's existing cfg80211.ko
# as the provider for Qualcomm's vendor WLAN driver; build patched mac80211.ko.
"$CFG" --file "$DEFCONFIG" --module CFG80211
"$CFG" --file "$DEFCONFIG" --module MAC80211

# Container / Docker foundations missing from the original R9 configuration.
for opt in PID_NS USER_NS IPC_NS CGROUP_PIDS CGROUP_DEVICE; do
  "$CFG" --file "$DEFCONFIG" --enable "$opt"
done

# USB gadget: R9 already has HID, FunctionFS, mass storage, ACM, ECM and NCM.
# Add only the missing RNDIS function.
"$CFG" --file "$DEFCONFIG" --enable USB_CONFIGFS_RNDIS

# CAN: retain existing CAN core/RAW/BCM/GW and add missing interfaces as modules.
for opt in CAN_VCAN CAN_VXCAN CAN_SLCAN; do
  "$CFG" --file "$DEFCONFIG" --module "$opt"
done

# NFS client/server support as modules.
"$CFG" --file "$DEFCONFIG" --module NFS_FS
"$CFG" --file "$DEFCONFIG" --enable NFS_V3
"$CFG" --file "$DEFCONFIG" --enable NFS_V4
"$CFG" --file "$DEFCONFIG" --module NFSD
"$CFG" --file "$DEFCONFIG" --enable NFSD_V3
"$CFG" --file "$DEFCONFIG" --enable NFSD_V4

# SDR / RTL-SDR support. Do not build external USB Wi-Fi adapter drivers.
"$CFG" --file "$DEFCONFIG" --enable MEDIA_SUPPORT
"$CFG" --file "$DEFCONFIG" --enable MEDIA_USB_SUPPORT
"$CFG" --file "$DEFCONFIG" --enable MEDIA_SDR_SUPPORT
"$CFG" --file "$DEFCONFIG" --enable MEDIA_DIGITAL_TV_SUPPORT
"$CFG" --file "$DEFCONFIG" --module DVB_CORE
"$CFG" --file "$DEFCONFIG" --module DVB_USB_V2
"$CFG" --file "$DEFCONFIG" --module DVB_USB_RTL28XXU
"$CFG" --file "$DEFCONFIG" --module DVB_RTL2832
"$CFG" --file "$DEFCONFIG" --module DVB_RTL2832_SDR

# IPv6 NAT is absent in the R9 baseline; useful for container networking.
"$CFG" --file "$DEFCONFIG" --enable IP6_NF_NAT

echo "Configured feature requests in $DEFCONFIG"
