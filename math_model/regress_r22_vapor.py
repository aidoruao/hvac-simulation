"""FR-MA-005: R22 vapor-region Helmholtz residual fit."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from regress_r410a_v4 import fit_region
import CoolProp.CoolProp as CP
import regress_r410a_v4 as mod

F = "R22"
mod.FLUID = F
mod.T_CRITICAL = float(CP.PropsSI("TCRIT", F))
mod.RHO_CRITICAL = float(CP.PropsSI("RHOCRIT", F))
mod.MOLAR_MASS = float(CP.PropsSI("MOLARMASS", F))
mod.GAS_CONSTANT = 8.314462618 / mod.MOLAR_MASS
rc = mod.RHO_CRITICAL
base = os.path.expanduser("~/hvac-simulation/math_model")

print(f"R22 — T_c={mod.T_CRITICAL:.3f}K, rho_c={rc:.3f}kg/m3, R={mod.GAS_CONSTANT:.3f}J/kgK")
r, s = fit_region("R22_vapor", 350, 500, 0.1*rc, 0.9*rc, 42, 43,
                  os.path.join(base, "r22_vapor_coefficients.py"), 2000, 500)
print(f"\nR22: mean_err={s['mean']*100:.4f}%, max={s['max']*100:.4f}%, {'PASS' if s['mean']<0.01 else 'FAIL'}")
