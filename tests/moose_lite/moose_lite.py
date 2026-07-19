"""
FR-PH-003: MOOSE-inspired Steady-State Heat Conduction Solver

Equation: d/dr (k * r * dT/dr) = 0 (cylindrical coordinates)

Analytical (constant k): T(r) = T_in + (T_out - T_in) * ln(r/r_in) / ln(r_out/r_in)

Origin: Coupled API to conduction with CoolProp properties (future).
"""

import numpy as np
from scipy import integrate

def solve_steady_pipe_heat_conduction(r_in, r_out, T_in, T_out, k=400.0):
    """Solve 1D steady-state heat conduction through a pipe wall.

    Args:
        r_in: Inner radius (m)
        r_out: Outer radius (m)
        T_in: Inner surface temperature (K)
        T_out: Outer surface temperature (K)
        k: Thermal conductivity (W/m-K), default copper 400
    Returns:
        r_mesh: Radial mesh points
        T_numerical: Numerical temperature profile
        T_analytical: Analytical temperature profile
        error: Max absolute difference
    """
    def ode(r, T):
        # d2T/dr2 + (1/r) * dT/dr = 0
        return np.vstack([T[1], -(1.0 / r) * T[1]])

    def bc(Ta, Tb):
        return np.array([Ta[0] - T_in, Tb[0] - T_out]).flatten()

    r_mesh = np.linspace(r_in, r_out, 100)
    T_init = np.vstack([np.linspace(T_in, T_out, 100), np.zeros(100)])

    sol = integrate.solve_bvp(ode, bc, r_mesh, T_init)

    T_analytical = T_in + (T_out - T_in) * np.log(r_mesh / r_in) / np.log(r_out / r_in)

    error = np.max(np.abs(sol.y[0] - T_analytical))

    return sol.x, sol.y[0], T_analytical, error

if __name__ == '__main__':
    r_in = 0.007932   # 3/8 inch copper tube, inner radius (m)
    r_out = 0.009525  # 1/2 inch copper tube, outer radius (m)
    T_in = 273.15     # 32 Fahrenheit (K)
    T_out = 298.15    # 75 Fahrenheit (K)
    k = 400.0         # Copper thermal conductivity (W/m-K)

    r_mesh, T_num, T_ana, err = solve_steady_pipe_heat_conduction(r_in, r_out, T_in, T_out, k)
    print(f"Max error vs analytical: {err:.2e} K")
    print(f"Heat flux q = {2 * np.pi * k * (T_out - T_in) / np.log(r_out / r_in):.2f} W/m")
