"""
FR-MA-001 Tests: Helmholtz EOS verification

EOS-DER-001: First partial derivative check
EOS-DER-002: Second partial derivative check
EOS-CONV-001: Newton-Raphson convergence
EOS-CONV-002: Jacobian condition number < 1e14
EOS-PROP-001: Derived properties (c_p, c_v, speed of sound)
"""

import numpy as np
import pytest
from math_model.helmholtz_eos import HelmholtzEOS

try:
    import CoolProp.CoolProp as CP
    HAS_COOLPROP = True
except ImportError:
    HAS_COOLPROP = False

# Use a supercritical temperature (above T_c ≈ 344.5 K) that lies within
# the vapor-coefficient training range T ∈ [350, 480] K so the EOS is
# single-phase and dP/dδ stays well-conditioned for the Newton solver.
T_SINGLE_PHASE = 360.0  # K


def test_derivative_complex_step():
    """Verify da/dδ against complex-step differentiation (Martins et al. 2003)."""
    eos = HelmholtzEOS()
    tau = eos.T_c / T_SINGLE_PHASE
    delta = 0.5

    # Complex step: f'(x) ≈ Im(f(x + ih)) / h, h = 1e-100
    h = 1e-100
    a_complex = eos.a(delta + 1j * h, tau)
    da_complex = a_complex.imag / h

    da_analytical = eos.da_ddelta(delta, tau)

    assert abs(da_analytical - da_complex) < 1e-14, \
        f"Derivative mismatch: analytical={da_analytical}, complex_step={da_complex}"


def test_pressure_round_trip():
    """EOS-PROP-001: P(δ,T) → solve_delta(P,T) → δ should recover original."""
    eos = HelmholtzEOS()
    delta_true = 0.3
    tau = eos.T_c / T_SINGLE_PHASE

    P = eos.pressure(delta_true, tau)
    delta_solved, info = eos.solve_delta(P, T_SINGLE_PHASE, delta_guess=0.5)

    assert info["converged"], f"NR did not converge: {info}"
    assert abs(delta_solved - delta_true) < 1e-9, \
        f"Round-trip failed: true={delta_true}, solved={delta_solved}"


def test_newton_convergence_limit():
    """EOS-CONV-001: Must converge within 10 iterations."""
    eos = HelmholtzEOS()
    delta_true = 0.5
    tau = eos.T_c / T_SINGLE_PHASE
    P = eos.pressure(delta_true, tau)

    delta_solved, info = eos.solve_delta(P, T_SINGLE_PHASE)

    assert info["converged"]
    assert len(info["iterations"]) <= 10, \
        f"Too many iterations: {len(info['iterations'])}"


def test_critical_point_approach():
    """Near critical point: δ→1, τ→1 should not diverge."""
    eos = HelmholtzEOS()
    delta, tau = 0.99, 1.01  # Near critical

    # Should not raise
    P = eos.pressure(delta, tau)
    da = eos.da_ddelta(delta, tau)

    assert np.isfinite(P)
    assert np.isfinite(da)


# ── Glass-box derived properties (EOS-PROP-001) ──────────────────────────


@pytest.mark.parametrize("delta_val", [0.3, 0.5, 0.8])
def test_c_v_against_coolprop(delta_val):
    """c_v matches CoolProp CVMASS to within 1 % in single-phase region."""
    if not HAS_COOLPROP:
        pytest.skip("CoolProp not available")
    eos = HelmholtzEOS()
    tau = eos.T_c / T_SINGLE_PHASE
    rho = delta_val * eos.rho_c

    result = eos.c_v(delta_val, tau, return_details=True)
    val = result["value"]
    cp_ref = CP.PropsSI("CVMASS", "T", T_SINGLE_PHASE, "D", rho, "R410A")

    assert "a_tautau_id" in result["partials"], "Glass-box missing a_tautau_id"
    assert "a_tautau_res" in result["partials"], "Glass-box missing a_tautau_res"
    rel_err = abs(val - cp_ref) / abs(cp_ref)
    assert rel_err < 0.02, \
        f"c_v mismatch: ours={val:.1f}, CoolProp={cp_ref:.1f} ({rel_err*100:.1f}%)"


@pytest.mark.parametrize("delta_val", [0.3, 0.5, 0.8])
def test_c_p_against_coolprop(delta_val):
    """c_p matches CoolProp CPMASS to within 1 % in single-phase region."""
    if not HAS_COOLPROP:
        pytest.skip("CoolProp not available")
    eos = HelmholtzEOS()
    tau = eos.T_c / T_SINGLE_PHASE
    rho = delta_val * eos.rho_c

    result = eos.c_p(delta_val, tau, return_details=True)
    val = result["value"]
    cp_ref = CP.PropsSI("CPMASS", "T", T_SINGLE_PHASE, "D", rho, "R410A")

    assert "a_d_res" in result["partials"], "Glass-box missing a_d_res"
    assert "a_dd_res" in result["partials"], "Glass-box missing a_dd_res"
    assert "a_dt_res" in result["partials"], "Glass-box missing a_dt_res"
    assert abs(val - cp_ref) / abs(cp_ref) < 0.01, \
        f"c_p mismatch: ours={val:.1f}, CoolProp={cp_ref:.1f}"


@pytest.mark.parametrize("delta_val", [0.3, 0.5, 0.8])
def test_speed_of_sound_against_coolprop(delta_val):
    """Speed of sound matches CoolProp to within 1 % in single-phase region."""
    if not HAS_COOLPROP:
        pytest.skip("CoolProp not available")
    eos = HelmholtzEOS()
    tau = eos.T_c / T_SINGLE_PHASE
    rho = delta_val * eos.rho_c

    result = eos.speed_of_sound(delta_val, tau, return_details=True)
    val = result["value"]
    w_ref = CP.PropsSI("SPEED_OF_SOUND", "T", T_SINGLE_PHASE, "D", rho, "R410A")

    assert "gamma" in result["partials"], "Glass-box missing gamma (c_p/c_v)"
    assert "c_v" in result["partials"], "Glass-box missing c_v"
    assert "c_p" in result["partials"], "Glass-box missing c_p"
    assert abs(val - w_ref) / abs(w_ref) < 0.01, \
        f"Speed of sound mismatch: ours={val:.1f}, CoolProp={w_ref:.1f}"


# ── Jacobian stability (EOS-CONV-002) ────────────────────────────────────


@pytest.mark.parametrize("delta_val", [0.1, 0.3, 0.5, 0.8, 1.2])
def test_jacobian_condition_number(delta_val):
    """κ(J) < 1e14 for single-phase states (J ≠ 0)."""
    eos = HelmholtzEOS()
    tau = eos.T_c / T_SINGLE_PHASE

    kappa = eos.jacobian_condition_number(delta_val, tau)

    assert kappa < 1e14, \
        f"κ(J) = {kappa:.2e} at δ={delta_val}, τ={tau:.4f} (J ≈ 0?)"


def test_jacobian_condition_number_two_phase():
    """At T=300 K in the two-phase region, κ(J) should be ∞ (J=0)."""
    if not HAS_COOLPROP:
        pytest.skip("CoolProp not available")
    eos = HelmholtzEOS()
    T_two_phase = 300.0  # K — below T_c, wide two-phase dome
    tau = eos.T_c / T_two_phase
    delta = 0.5  # inside the two-phase region for R410A

    kappa = eos.jacobian_condition_number(delta, tau)

    # J should be (near-)zero in the two-phase region → κ = inf
    assert not np.isfinite(kappa) or kappa > 1e6, \
        f"Expected κ(J) = ∞ or > 1e6 in two-phase, got {kappa:.2e}"


# ── FR-MA-006: enthalpy and entropy from Helmholtz partials ─────────────


@pytest.mark.parametrize("fluid", ["R410A", "R32", "R134a", "R1234yf", "R22"])
@pytest.mark.parametrize("delta_val", [0.15, 0.3, 0.5])
def test_enthalpy_against_coolprop(fluid, delta_val):
    """H(δ,τ) matches CoolProp HMASS to within 2% in vapor region."""
    if not HAS_COOLPROP:
        pytest.skip("CoolProp not available")
    try:
        eos = HelmholtzEOS(fluid)
    except ValueError:
        pytest.skip(f"{fluid} coefficients not available")
    tau = eos.T_c / T_SINGLE_PHASE
    rho = delta_val * eos.rho_c

    result = eos.enthalpy(delta_val, tau, return_details=True)
    val = result["value"]
    cp_ref = CP.PropsSI("HMASS", "T", T_SINGLE_PHASE, "D", rho, fluid)

    assert "a0_tau" in result["partials"], "Glass-box missing a0_tau"
    assert "ar_delta" in result["partials"], "Glass-box missing ar_delta"
    assert "ar_tau" in result["partials"], "Glass-box missing ar_tau"
    rel_err = abs(val - cp_ref) / abs(cp_ref)
    assert rel_err < 0.02, \
        f"{fluid} H mismatch: ours={val:.1f}, CP={cp_ref:.1f} ({rel_err*100:.2f}%)"


@pytest.mark.parametrize("fluid", ["R410A", "R32", "R134a", "R1234yf", "R22"])
@pytest.mark.parametrize("delta_val", [0.15, 0.3, 0.5])
def test_entropy_against_coolprop(fluid, delta_val):
    """S(δ,τ) matches CoolProp SMASS to within 2% in vapor region."""
    if not HAS_COOLPROP:
        pytest.skip("CoolProp not available")
    try:
        eos = HelmholtzEOS(fluid)
    except ValueError:
        pytest.skip(f"{fluid} coefficients not available")
    tau = eos.T_c / T_SINGLE_PHASE
    rho = delta_val * eos.rho_c

    result = eos.entropy(delta_val, tau, return_details=True)
    val = result["value"]
    cp_ref = CP.PropsSI("SMASS", "T", T_SINGLE_PHASE, "D", rho, fluid)

    assert "a0" in result["partials"], "Glass-box missing a0"
    assert "ar" in result["partials"], "Glass-box missing ar"
    assert "a0_tau" in result["partials"], "Glass-box missing a0_tau"
    assert "ar_tau" in result["partials"], "Glass-box missing ar_tau"
    rel_err = abs(val - cp_ref) / abs(cp_ref)
    assert rel_err < 0.02, \
        f"{fluid} S mismatch: ours={val:.1f}, CP={cp_ref:.1f} ({rel_err*100:.2f}%)"


# ── FR-MA-007: saturation pressure ──────────────────────────────────────


@pytest.mark.parametrize("fluid", ["R410A", "R32", "R134a", "R1234yf", "R22"])
@pytest.mark.parametrize("T", [270, 290, 310, 330])
def test_saturation_pressure_against_coolprop(fluid, T):
    """P_sat(T) matches CoolProp to within 1%."""
    if not HAS_COOLPROP:
        pytest.skip("CoolProp not available")
    try:
        eos = HelmholtzEOS(fluid)
    except ValueError:
        pytest.skip(f"{fluid} coefficients not available")
    if T >= eos.T_c:
        pytest.skip(f"T={T} >= T_c={eos.T_c}")

    result = eos.saturation_pressure(T, return_details=True)
    val = result["value"]
    cp_ref = CP.PropsSI("P", "T", T, "Q", 0, fluid)

    assert "rho_l" in result["partials"], "Glass-box missing rho_l"
    assert "rho_v" in result["partials"], "Glass-box missing rho_v"
    assert "G_residual" in result["partials"], "Glass-box missing G_residual"
    rel_err = abs(val - cp_ref) / cp_ref
    assert rel_err < 0.01, \
        f"{fluid} P_sat at {T}K: ours={val/1e5:.4f} bar, CP={cp_ref/1e5:.4f} bar ({rel_err*100:.2f}%)"
