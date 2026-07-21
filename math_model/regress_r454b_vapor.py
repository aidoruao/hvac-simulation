"""FR-MA-010: R454B (Opteon XL41) regression from CoolProp mixture + public data."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import CoolProp.CoolProp as CP
import regress_r410a_v4 as base

# R454B = R32 (68.9%) + R1234yf (31.1%)
base.FLUID = "R32[0.689]&R1234yf[0.311]"
# Override critical props from Chemours data sheet
base.T_CRITICAL = 78.1 + 273.15  # 351.25 K
base.RHO_CRITICAL = 443.0         # kg/m3
M = 62.6e-3                       # kg/mol
base.GAS_CONSTANT = 8.314462618 / M
base.MOLAR_MASS = M

rc = base.RHO_CRITICAL
out = os.path.join(os.path.expanduser("~/hvac-simulation/math_model"), "r454b_vapor_coefficients.py")

r, s = base.fit_region("R454B_vapor", 350, 500, 0.1*rc, 0.9*rc, 42, 43, out, 2000, 500)
print(f"\nR454B: mean={s['mean']*100:.4f}% max={s['max']*100:.4f}% {'PASS' if s['mean']<0.01 else 'FAIL'}")
