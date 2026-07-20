"""FR-MA-004: R1234yf vapor-region Helmholtz residual fit."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from regress_r410a_v4 import fit_region
import CoolProp.CoolProp as CP
import regress_r410a_v4 as mod

F = "R1234yf"
mod.FLUID = F
mod.T_CRITICAL = float(CP.PropsSI("TCRIT", F))
mod.RHO_CRITICAL = float(CP.PropsSI("RHOCRIT", F))
mod.MOLAR_MASS = float(CP.PropsSI("MOLARMASS", F))
mod.GAS_CONSTANT = 8.314462618 / mod.MOLAR_MASS
rc = mod.RHO_CRITICAL
base = os.path.expanduser("~/hvac-simulation/math_model")

print(f"R1234yf — T_c={mod.T_CRITICAL:.3f}K, rho_c={rc:.3f}kg/m3, R={mod.GAS_CONSTANT:.3f}J/kgK")
r, s = fit_region("R1234yf_vapor", 350, 500, 0.1*rc, 0.9*rc, 42, 43,
                  os.path.join(base, "r1234yf_vapor_coefficients.py"), 2000, 500)
print(f"\nR1234yf: mean_err={s['mean']*100:.4f}%, max={s['max']*100:.4f}%, {'PASS' if s['mean']<0.01 else 'FAIL'}")
