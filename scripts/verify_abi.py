#!/usr/bin/env python3
import argparse, base64, gzip, pathlib, re, struct, subprocess, sys
from collections import defaultdict

def read_manifest(path):
    raw = gzip.decompress(base64.b64decode(pathlib.Path(path).read_text()))
    imports, exports = [], defaultdict(list)
    for line in raw.decode().splitlines():
        kind, module, symbol, crc = line.split("\t")
        item = (module, symbol, int(crc, 16))
        if kind == "I": imports.append(item)
        elif kind == "E": exports[symbol].append((module, int(crc, 16)))
    return imports, exports

def read_symvers(path):
    out = defaultdict(list)
    for line in pathlib.Path(path).read_text(errors="replace").splitlines():
        p = line.split()
        if len(p) >= 3 and p[0].startswith("0x"):
            out[p[1]].append((p[2], int(p[0], 16)))
    return out

def module_versions(path):
    text = subprocess.check_output(["readelf", "-SW", str(path)], text=True)
    m = re.search(r"\[\s*\d+\]\s+__versions\s+\S+\s+\S+\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)", text)
    if not m: return {}
    off, size = (int(x, 16) for x in m.groups())
    data = pathlib.Path(path).read_bytes()[off:off+size]
    result = {}
    for i in range(0, len(data)-63, 64):
        crc = struct.unpack_from("<I", data, i)[0]
        name = data[i+8:i+64].split(b"\0", 1)[0].decode(errors="replace")
        if name: result[name] = crc
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symvers", required=True)
    ap.add_argument("--module", required=True)
    ap.add_argument("--r9-baseline", required=True)
    ap.add_argument("--qca-baseline", required=True)
    ap.add_argument("--report", required=True)
    a = ap.parse_args()

    sym = read_symvers(a.symvers)
    r9_imports, r9_exports = read_manifest(a.r9_baseline)
    qca_imports, qca_exports = read_manifest(a.qca_baseline)
    for k, v in qca_exports.items():
        r9_exports[k].extend(v)

    layout = {crc for _, name, crc in r9_imports if name == "module_layout"}
    lines = []
    errors = []
    unresolved = 0
    if layout != {0x0222dd63}:
        errors.append(f"Unexpected R9 module_layout CRC set: {sorted(hex(x) for x in layout)}")
    kernel_layout = sym.get("module_layout", [])
    if not any(crc == 0x0222dd63 for _, crc in kernel_layout):
        errors.append(f"Candidate kernel module_layout CRC is not 0x0222dd63: {kernel_layout}")

    # The ROM's cfg80211.ko is retained. Its exported ABI must match the
    # cfg80211 module built from this candidate source/config.
    cfg_checked = cfg_bad = 0
    for name, providers in r9_exports.items():
        cfg_providers = [(m, c) for m, c in providers if "cfg80211" in m]
        if not cfg_providers: continue
        candidate = [(m, c) for m, c in sym.get(name, []) if "cfg80211" in m]
        if candidate:
            cfg_checked += 1
            if not any(c == old for _, c in candidate for _, old in cfg_providers):
                cfg_bad += 1
                errors.append(f"cfg80211 export CRC mismatch: {name}")

    # Compare vendor imports with candidate kernel/module exports. If a symbol
    # is supplied by another retained vendor module, use its recorded CRC.
    checked = 0
    for module, name, expected in r9_imports:
        providers = sym.get(name, [])
        if providers:
            checked += 1
            if not any(crc == expected for _, crc in providers):
                errors.append(f"vendor import CRC mismatch: {module}:{name} expected {expected:08x} got {[hex(c) for _,c in providers]}")
        elif name in r9_exports:
            if not any(crc == expected for _, crc in r9_exports[name]):
                errors.append(f"vendor-provider CRC mismatch: {module}:{name}")
        else:
            unresolved += 1

    # Check QCA vendor WLAN imports against the candidate kernel and the
    # original ROM cfg80211 export table.
    qca_checked = 0
    for module, name, expected in qca_imports:
        providers = sym.get(name, [])
        if providers:
            qca_checked += 1
            if not any(crc == expected for _, crc in providers):
                # A cfg80211 export is allowed only if it exactly matches the
                # retained ROM module's export CRC.
                if not any(crc == expected for _, crc in r9_exports.get(name, [])):
                    errors.append(f"QCA import CRC mismatch: {name}")
        elif name in r9_exports:
            qca_checked += 1
            if not any(crc == expected for _, crc in r9_exports[name]):
                errors.append(f"QCA vendor-provider CRC mismatch: {name}")
        else:
            unresolved += 1

    # Check every symbol imported by the new mac80211.ko.
    new_imports = module_versions(a.module)
    new_checked = 0
    for name, expected in new_imports.items():
        providers = sym.get(name, [])
        if providers:
            new_checked += 1
            if not any(crc == expected for _, crc in providers):
                errors.append(f"mac80211 import CRC mismatch: {name}")
        elif name in r9_exports:
            new_checked += 1
            if not any(crc == expected for _, crc in r9_exports[name]):
                errors.append(f"mac80211 vendor-provider CRC mismatch: {name}")
        else:
            errors.append(f"mac80211 unresolved import: {name}")

    lines += [
        "Roains-Nethunter-Sapphire ABI audit",
        f"R9 module_layout baseline: 0x0222dd63",
        f"Vendor imports compared with candidate Module.symvers: {checked}",
        f"QCA vendor imports checked: {qca_checked}",
        f"cfg80211 exports checked: {cfg_checked}",
        f"mac80211 imports checked: {new_checked}",
        f"Unresolved vendor symbols (review): {unresolved}",
        f"ABI errors: {len(errors)}",
    ]
    lines += errors
    pathlib.Path(a.report).write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if errors: sys.exit(1)

if __name__ == "__main__": main()
