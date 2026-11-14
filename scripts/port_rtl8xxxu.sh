#!/usr/bin/env bash
# Overlay the sapphire Wi-Fi injection fork's rtl8xxxu driver onto the exact R9 source.
set -euo pipefail

KERNEL="${1:?usage: port_rtl8xxxu.sh KERNEL_SOURCE_DIR}"
REPO="https://github.com/roainxztar/android-gki-wifi-injection.git"
PIN="e17efc7e23eb89bbf90f1c6b04bcb8512a35d571"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

git init "$TMP/src"
git -C "$TMP/src" remote add origin "$REPO"
git -C "$TMP/src" fetch --depth=1 origin "$PIN"
git -C "$TMP/src" checkout --detach FETCH_HEAD
test "$(git -C "$TMP/src" rev-parse HEAD)" = "$PIN"

SRC="$TMP/src/driver"
DEST="$KERNEL/drivers/net/wireless/realtek/rtl8xxxu"
test -f "$DEST/Kconfig"

for file in rtl8xxxu.h rtl8xxxu_regs.h rtl8xxxu_core.c rtl8188fufw_fw.h \
            rtl8xxxu_8188e.c rtl8xxxu_8188f.c rtl8xxxu_8192c.c \
            rtl8xxxu_8192e.c rtl8xxxu_8192f.c rtl8xxxu_8710b.c \
            rtl8xxxu_8723a.c rtl8xxxu_8723b.c; do
    test -s "$SRC/$file"
    install -m 0644 "$SRC/$file" "$DEST/$file"
done

# RTL8XXXU_UNTESTED is a bool used by the driver at compile time. A plain
# "depends on RTL8XXXU" evaluates to m when RTL8XXXU=m, which prevents this
# bool from being enabled. Permit it whenever the driver is built-in or a
# module, but not when the driver is disabled.
grep -qE '^[[:space:]]*depends on RTL8XXXU$' "$DEST/Kconfig"
sed -i 's/^\([[:space:]]*depends on \)RTL8XXXU$/\1RTL8XXXU != n/' "$DEST/Kconfig"
grep -qE '^[[:space:]]*depends on RTL8XXXU != n$' "$DEST/Kconfig"

cat > "$DEST/Makefile" <<'EOF'
# SPDX-License-Identifier: GPL-2.0-only
obj-$(CONFIG_RTL8XXXU) += rtl8xxxu.o
rtl8xxxu-y := rtl8xxxu_core.o rtl8xxxu_8192e.o rtl8xxxu_8723b.o \
              rtl8xxxu_8723a.o rtl8xxxu_8192c.o rtl8xxxu_8188f.o \
              rtl8xxxu_8188e.o rtl8xxxu_8710b.o rtl8xxxu_8192f.o
EOF

grep -q 'rtl8188fufw_data' "$DEST/rtl8188fufw_fw.h"
echo "RTL8XXXU port applied from $PIN"
