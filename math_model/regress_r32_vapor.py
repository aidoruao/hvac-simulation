"""
FR-MA-002: R32 vapor-region Helmholtz residual fit.
Reuses the FR-MA-001 regress_r410a_v4.py framework with R32 fluid constants.
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from regress_r410a_v4 import (
    fit_region, T_CRITICAL, RHO_CRITICAL, FLUID as _,
)
import CoolProp.CoolProp as CP

FLUID_R32 = "R32"
T_CRITICAL_R32 = float(CP.PropsSI("TCRIT", FLUID_R32))
RHO_CRITICAL_R32 = float(CP.PropsSI("RHOCRIT", FLUID_R32))

# Override the module-level constants for R32
import regress_r410a_v4 as mod
mod.FLUID = FLUID_R32
mod.T_CRITICAL = T_CRITICAL_R32
mod.RHO_CRITICAL = RHO_CRITICAL_R32
mod.MOLAR_MASS = float(CP.PropsSI("MOLARMASS", FLUID_R32))
mod.GAS_CONSTANT = 8.314462618 / mod.MOLAR_MASS

print("=" * 60)
print(f"R32 VAPOR REGION FIT — FR-MA-002 PoC")
print("=" * 60)
print(f"Fluid: {FLUID_R32}")
print(f"T_c = {T_CRITICAL_R32:.6f} K")
print(f"rho_c = {RHO_CRITICAL_R32:.6f} kg/m^3")
print(f"R = {mod.GAS_CONSTANT:.6f} J/(kg*K)")

base = os.path.expanduser("~/hvac-simulation/math_model")

result, stats = fit_region(
    name="R32_vapor",
    T_min=350.0, T_max=500.0,
    rho_min=0.1 * RHO_CRITICAL_R32,
    rho_max=0.9 * RHO_CRITICAL_R32,
    train_seed=42, val_seed=43,
    out_path=os.path.join(base, "r32_vapor_coefficients.py"),
    n_train=2000, n_val=500,
)

print("\n" + "=" * 60)
if stats["mean"] < 0.01:
    print("PoC PASSED — R32 vapor coefficients < 1% mean error")
else:
    print(f"PoC FAILED — mean error {stats['mean']*100:.2f}% > 1%")
print("=" * 60)
