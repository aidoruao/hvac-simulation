"""FR-MA-010: R513A (Opteon XP10) regression from CoolProp mixture + public data."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import CoolProp.CoolProp as CP
import regress_r410a_v4 as base

# R513A = R1234yf (56%) + R134a (44%)
base.FLUID = "R1234yf[0.56]&R134a[0.44]"
# Override critical props from Chemours data sheet
base.T_CRITICAL = 96.5 + 273.15  # 369.65 K
base.RHO_CRITICAL = 516.75        # kg/m3
M = 108.4e-3                      # kg/mol
base.GAS_CONSTANT = 8.314462618 / M
base.MOLAR_MASS = M

rc = base.RHO_CRITICAL
out = os.path.join(os.path.expanduser("~/hvac-simulation/math_model"), "r513a_vapor_coefficients.py")

r, s = base.fit_region("R513A_vapor", 350, 500, 0.1*rc, 0.9*rc, 42, 43, out, 2000, 500)
print(f"\nR513A: mean={s['mean']*100:.4f}% max={s['max']*100:.4f}% {'PASS' if s['mean']<0.01 else 'FAIL'}")
