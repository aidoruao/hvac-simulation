"""
FR-MA-001-L3: Expanded Helmholtz term count (20/10/6) for non-R410A fluids.
Re-runs R32, R134a, R1234yf, R22 vapour regressions with 136 parameters.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

import CoolProp.CoolProp as CP
import regress_r410a_v4 as base

# Override term counts — must be done BEFORE any function that references
# N_POLY/N_EXP/N_GAUSS is called (but after import so globals are accessible).
base.N_POLY = 20
base.N_EXP  = 10
base.N_GAUSS = 6
base.TOTAL_P = base.N_POLY * base.POLY_P + base.N_EXP * base.EXP_P + base.N_GAUSS * base.GAUSS_P

# Rebind the helpers that reference the overridden globals
def _build_initial_params_v2():
    poly = base.np.zeros((base.N_POLY, base.POLY_P))
    for i in range(base.N_POLY):
        poly[i, 0] = -0.5 + i * (1.0 / max(base.N_POLY - 1, 1))
        poly[i, 1] = 1.0 + (i % 3)
        poly[i, 2] = float(i % 3)
    exp = base.np.zeros((base.N_EXP, base.EXP_P))
    for i in range(base.N_EXP):
        exp[i, 0] = 0.1 * ((-1) ** i)
        exp[i, 1] = 1.0 + (i % 3)
        exp[i, 2] = float(i % 3)
        exp[i, 3] = 1.0
    gauss = base.np.zeros((base.N_GAUSS, base.GAUSS_P))
    for i in range(base.N_GAUSS):
        gauss[i, 0] = 0.05 * ((-1) ** i)
        gauss[i, 1] = 2.0
        gauss[i, 2] = 1.0
        gauss[i, 3] = 1.0
        gauss[i, 4] = 1.0
        gauss[i, 5] = 1.0
        gauss[i, 6] = 1.0
    return base.np.concatenate([poly.ravel(), exp.ravel(), gauss.ravel()])

def _build_bounds_v2():
    lb_poly = base.np.tile(base.np.array([-5.0, 0.5, -1.0]), (base.N_POLY, 1))
    ub_poly = base.np.tile(base.np.array([5.0, 4.0, 3.0]), (base.N_POLY, 1))
    lb_exp  = base.np.tile(base.np.array([-5.0, 0.5, -1.0, 0.1]), (base.N_EXP, 1))
    ub_exp  = base.np.tile(base.np.array([5.0, 4.0, 3.0, 3.0]), (base.N_EXP, 1))
    lb_gauss = base.np.tile(base.np.array([-5.0, 0.5, -1.0, 0.1, 0.1, 0.1, 0.1]), (base.N_GAUSS, 1))
    ub_gauss = base.np.tile(base.np.array([5.0, 4.0, 3.0, 5.0, 5.0, 3.0, 3.0]), (base.N_GAUSS, 1))
    return (base.np.concatenate([lb_poly.ravel(), lb_exp.ravel(), lb_gauss.ravel()]),
            base.np.concatenate([ub_poly.ravel(), ub_exp.ravel(), ub_gauss.ravel()]))

base.build_initial_params = _build_initial_params_v2
base.build_bounds = _build_bounds_v2

FLUIDS = {
    "R32":     "r32_vapor_coefficients.py",
    "R134a":   "r134a_vapor_coefficients.py",
    "R1234yf": "r1234yf_vapor_coefficients.py",
    "R22":     "r22_vapor_coefficients.py",
}

base_dir = os.path.expanduser("~/hvac-simulation/math_model")
results = {}

for fluid, out_name in FLUIDS.items():
    print(f"\n{'='*60}")
    print(f"FR-MA-001-L3: {fluid} with {base.N_POLY}P/{base.N_EXP}E/{base.N_GAUSS}G = {base.TOTAL_P} params")
    print(f"{'='*60}")

    base.FLUID = fluid
    base.T_CRITICAL = float(CP.PropsSI("TCRIT", fluid))
    base.RHO_CRITICAL = float(CP.PropsSI("RHOCRIT", fluid))
    base.MOLAR_MASS = float(CP.PropsSI("MOLARMASS", fluid))
    base.GAS_CONSTANT = 8.314462618 / base.MOLAR_MASS
    rc = base.RHO_CRITICAL

    r, s = base.fit_region(
        name=f"{fluid}_vapor_v2",
        T_min=350.0, T_max=500.0,
        rho_min=0.1 * rc, rho_max=0.9 * rc,
        train_seed=42, val_seed=43,
        out_path=os.path.join(base_dir, out_name),
        n_train=2000, n_val=500,
    )
    results[fluid] = s
    print(f"\n{fluid}: mean_err={s['mean']*100:.4f}%, max={s['max']*100:.4f}%, "
          f"{'PASS' if s['mean'] < 0.01 else 'FAIL'}")

print(f"\n{'='*60}")
print("SUMMARY — FR-MA-001-L3 expanded term count (20P/10E/6G)")
print(f"{'='*60}")
for fluid, s in results.items():
    status = "PASS" if s["mean"] < 0.01 else "FAIL"
    print(f"  {fluid}: mean={s['mean']*100:.4f}%  max={s['max']*100:.4f}%  {status}")
