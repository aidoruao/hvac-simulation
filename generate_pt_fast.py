#!/usr/bin/env python3
"""Fast PT data generation for all refrigerants including blends."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "math_model"))
import CoolProp.CoolProp as CP

FLUIDS = {
    "R410A":   ("R410A",   "A1", 2088),
    "R32":     ("R32",     "A2L", 675),
    "R134a":   ("R134a",   "A1", 1430),
    "R1234yf": ("R1234yf", "A2L", 4),
    "R22":     ("R22",     "A1", 1810),
    "R454B":   ("R32[0.689]&R1234yf[0.311]", "A2L", 466),
    "R513A":   ("R1234yf[0.56]&R134a[0.44]", "A1", 631),
}

data = {}
for name, (cp_name, cls, gwp) in FLUIDS.items():
    pts = []
    try: T_c = CP.PropsSI("TCRIT", cp_name)
    except: T_c = 370  # default for blends
    if T_c <= 0: T_c = 370
    T_c_C = T_c - 273.15
    for t_c in range(-20, 61, 2):
        T = t_c + 273.15
        if T >= T_c:
            continue
        try:
            P = CP.PropsSI("P", "T", T, "Q", 0, cp_name)
            pts.append({"T": t_c, "P": round(P / 1e5, 4)})
        except Exception:
            pass

    data[name] = {
        "critical_point": {"T": round(T_c_C, 1), "P": None},
        "saturation_curve": pts,
        "safety_class": cls,
        "gwp": gwp,
        "status": "current",
    }

# Merge with existing pt_data.json structure
out = os.path.join(os.path.dirname(__file__), "godot_project", "pt_data.json")
with open(out, "w") as f:
    json.dump(data, f, indent=2)
print(f"Generated {out} with {len(data)} refrigerants")
for name, d in data.items():
    print(f"  {name}: {len(d['saturation_curve'])} points, T_c={d['critical_point']['T']}°C")
