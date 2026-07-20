#!/usr/bin/env python3
"""Generate pt_data.json from HelmholtzEOS for the Godot PT chart scene.

FR-MA-009 / FR-3D-003/004/005: HelmholtzEOS-driven PT chart data.
Includes saturation curves, critical points, and fluid classification.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "math_model"))
try:
    from helmholtz_eos import HelmholtzEOS
    HAS_HEOS = True
except ImportError:
    HAS_HEOS = False

REFRIGERANTS = {
    "R410A": {"class": "A1", "gwp": 2088, "status": "current→legacy"},
    "R32":    {"class": "A2L", "gwp": 675, "status": "transition"},
    "R134a":  {"class": "A1", "gwp": 1430, "status": "current"},
    "R1234yf":{"class": "A2L", "gwp": 4, "status": "future"},
    "R22":    {"class": "A1", "gwp": 1810, "status": "legacy"},
}

T_MIN, T_MAX, N_PTS = -40, 60, 150

def generate_pt_data():
    if not HAS_HEOS:
        # Fallback: generate from CoolProp via Refrigerant
        from refrigerants import Refrigerant
        data = {}
        for name, info in REFRIGERANTS.items():
            r = Refrigerant(name)
            temps = [T_MIN + (T_MAX - T_MIN) * i / (N_PTS - 1) for i in range(N_PTS)]
            pressures = [r.saturation_pressure(t) for t in temps]
            data[name] = {
                "temperature_c": temps,
                "pressure_bar": pressures,
                "classification": info,
            }
        return data

    # HelmholtzEOS path
    data = {}
    for name, info in REFRIGERANTS.items():
        try:
            eos = HelmholtzEOS(name)
        except ValueError:
            continue
        temps = [T_MIN + (T_MAX - T_MIN) * i / (N_PTS - 1) for i in range(N_PTS)]
        pressures = []
        for t in temps:
            T_K = t + 273.15
            if T_K >= eos.T_c:
                pressures.append(None)
            else:
                P_pa = eos.saturation_pressure(T_K)
                pressures.append(P_pa / 1e5)  # bar

        # Critical point
        T_crit_C = eos.T_c - 273.15

        data[name] = {
            "temperature_c": temps,
            "pressure_bar": pressures,
            "critical_point": {
                "T_c_C": T_crit_C,
                "P_c_bar": None,  # requires P_crit from CoolProp
            },
            "classification": info,
            "source": "HelmholtzEOS",
        }
    return data


if __name__ == "__main__":
    data = generate_pt_data()
    out_path = os.path.join(
        os.path.dirname(__file__), "godot_project", "pt_data.json"
    )
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Generated {out_path} with {len(data)} refrigerants")
    for name in data:
        n_pts = len(data[name]["temperature_c"])
        print(f"  {name}: {n_pts} points, source={data[name].get('source','CoolProp')}")
