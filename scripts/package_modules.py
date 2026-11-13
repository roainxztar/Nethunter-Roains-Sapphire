#!/usr/bin/env python3
import pathlib, shutil, subprocess, sys
from collections import defaultdict

src_root = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)

# Feature roots requested by this project. cfg80211 is intentionally retained
# from the ROM; external USB Wi-Fi adapter drivers are not built here.
roots = [
    "mac80211.ko", "vcan.ko", "vxcan.ko", "slcan.ko",
    "nfs.ko", "nfsv3.ko", "nfsv4.ko", "nfsd.ko",
    "dvb-core.ko", "dvb_usb_v2.ko", "dvb-usb-rtl28xxu.ko",
    "rtl2832.ko", "rtl2832_sdr.ko",
]
available = {}
for p in src_root.rglob("*.ko"):
    available.setdefault(p.name, p)

selected = {}
deps = {}
visiting = set()

def collect(name, required=False):
    if name == "cfg80211.ko" or name in selected:
        return
    path = available.get(name)
    if path is None:
        if required:
            raise SystemExit(f"Required feature module missing from build: {name}")
        return
    if name in visiting:
        return
    visiting.add(name)
    raw = subprocess.check_output(["modinfo", "-F", "depends", str(path)], text=True).strip()
    names = [x.strip() + ".ko" for x in raw.split(",") if x.strip()]
    deps[name] = names
    for dep in names:
        if dep != "cfg80211.ko":
            collect(dep, required=False)
    visiting.remove(name)
    selected[name] = path

collect("mac80211.ko", required=True)
for root in roots[1:]:
    collect(root, required=False)

# Keep output deterministic. Dependencies are collected before dependents.
for name, path in sorted(selected.items()):
    shutil.copy2(path, dst / name)

def path_for(name):
    # Store module-relative paths; the installer prefixes the detected module directory.
    return name

with (dst.parent / "modules.dep.additions").open("w") as f:
    for name in sorted(selected):
        f.write(path_for(name) + ":" + "".join(" " + path_for(d) for d in deps.get(name, [])) + "\n")

with (dst.parent / "modules.load.additions").open("w") as f:
    for name in sorted(selected):
        f.write(name + "\n")

print("Packaged new modules:", ", ".join(sorted(selected)))
print("cfg80211.ko intentionally not packaged; ROM vendor module is retained.")
