"""
FR-PH-003: Tests for MOOSE-inSpired Steady-State Heat Conduction Solver

"""

import numpy as np
import pytest
from scipy import integrate

from moose_lite import solve_steady_pipe_heat_conduction

def test_analytical_verification():
    """Verify numerical solution against analytical for constant k."""
    r_in = 0.007932
    r_out = 0.009525
    T_in = 273.15
    T_out = 298.15
    k = 400.0

    r_mesh, T_num, T_ana, err = solve_steady_pipe_heat_conduction(r_in, r_out, T_in, T_out, k)

    # Analytical: T(r) = T_in + (T_out - T_in) * ln(r/r_in) / ln(r_out/r_in)
    T_analytical = T_in + (T_out - T_in) * np.log(r_mesh / r_in) / np.log(r_out / r_in)

    assert err < 1e-9, f"Max error too large: {err}"
    assert np.max(np.abs(T_num - T_analytical)) < 1e-9

def test_heat_flux_conservation():
    """Verify the heat flux is conserved across radius."""
    r_in = 0.007932
    r_out = 0.009525
    T_in = 273.15
    T_out = 298.15
    k = 400.0

    r_mesh, T_num, T_ana, err = solve_steady_pipe_heat_conduction(r_in, r_out, T_in, T_out, k)

    # Calculate heat flux at two different radii
    idx = len(r_mesh) // 2
    q_inner = -2 * np.pi * k * r_mesh[0] * (np.gradient(T_num)[0] / np.gradient(r_mesh)[0])
    q_outer = -2 * np.pi * k * r_mesh[-1] * (np.gradient(T_num)[-1] / np.gradient(r_mesh)[-1])

    # For steady-state, should be constant (within numerical tolerance)
    assert np.abs(q_inner - q_outer) < 1e3, f"Heat flux not conserved: q_inner={q_inner:}, q_outer={q_outer}"
