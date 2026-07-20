"""
FR-MA-001-R410A-v4: Separate liquid- and vapor-region Helmholtz residual fits
for R410A using CoolProp synthetic data and scipy.optimize.least_squares.

Each region uses a 12-polynomial / 6-exponential / 4-Gaussian residual-energy
derivative form.  An analytical Jacobian is supplied to speed convergence.
"""

import os
import numpy as np
from scipy.optimize import least_squares

try:
    import CoolProp.CoolProp as CP
except ImportError as e:
    raise ImportError(
        "CoolProp is required to run this regression. "
        "Install it with: pip install CoolProp"
    ) from e

# ---------------------------------------------------------------------------
# Fluid constants (computed from CoolProp for self-consistency)
# ---------------------------------------------------------------------------
FLUID = "R410A"
T_CRITICAL = float(CP.PropsSI("TCRIT", FLUID))          # K
RHO_CRITICAL = float(CP.PropsSI("RHOCRIT", FLUID))      # kg/m^3
MOLAR_MASS = float(CP.PropsSI("MOLARMASS", FLUID))      # kg/mol
GAS_CONSTANT = 8.314462618 / MOLAR_MASS                 # J/(kg*K)

# ---------------------------------------------------------------------------
# Model structure
# ---------------------------------------------------------------------------
N_POLY = 12
N_EXP = 6
N_GAUSS = 4

POLY_P = 3
EXP_P = 4
GAUSS_P = 7
TOTAL_P = N_POLY * POLY_P + N_EXP * EXP_P + N_GAUSS * GAUSS_P


def unpack_params(p):
    """Split flat parameter vector into polynomial, exponential, Gaussian blocks."""
    i = 0
    poly = p[i : i + N_POLY * POLY_P].reshape(N_POLY, POLY_P)
    i += N_POLY * POLY_P
    exp = p[i : i + N_EXP * EXP_P].reshape(N_EXP, EXP_P)
    i += N_EXP * EXP_P
    gauss = p[i : i + N_GAUSS * GAUSS_P].reshape(N_GAUSS, GAUSS_P)
    return poly, exp, gauss


def alpha_delta_model(delta, tau, p):
    """
    Analytical derivative d(alpha^r)/d(delta) for the residual Helmholtz form.

    Numerical safeguards:
      - delta clipped to [1e-6, 10]
      - tau clipped to [0.5, 5]
      - exponential arguments capped at |50|
      - terms with exp(-50) are treated as zero
    """
    delta_c = np.clip(np.asarray(delta, dtype=float), 1e-6, 10.0)
    tau_c = np.clip(np.asarray(tau, dtype=float), 0.5, 5.0)
    delta_c = delta_c[:, None]
    tau_c = tau_c[:, None]

    poly, exp, gauss = unpack_params(p)
    out = np.zeros(delta_c.shape[0])

    # ----- Polynomial terms: n * delta^d * tau^t -----
    n = poly[:, 0]
    d = poly[:, 1]
    t = poly[:, 2]
    out += np.sum(n * d * delta_c ** (d - 1.0) * tau_c ** t, axis=1)

    # ----- Exponential terms: n * delta^d * tau^t * exp(-delta^l) -----
    n = exp[:, 0]
    d = exp[:, 1]
    t = exp[:, 2]
    l = exp[:, 3]
    delta_l = delta_c ** l
    arg = -delta_l
    active = arg >= -50.0
    exp_factor = np.exp(np.clip(arg, -50.0, 50.0))
    deriv_factor = d * delta_c ** (d - 1.0) - l * delta_c ** (d + l - 1.0)
    out += np.sum(n * tau_c ** t * exp_factor * deriv_factor * active, axis=1)

    # ----- Gaussian terms -----
    n = gauss[:, 0]
    d = gauss[:, 1]
    t = gauss[:, 2]
    alpha = gauss[:, 3]
    beta = gauss[:, 4]
    eps = gauss[:, 5]
    gamma = gauss[:, 6]
    g = -alpha * (delta_c - eps) ** 2 - beta * (tau_c - gamma) ** 2
    active = g >= -50.0
    exp_g = np.exp(np.clip(g, -50.0, 50.0))
    deriv_factor = d * delta_c ** (d - 1.0) - 2.0 * alpha * (delta_c - eps) * delta_c ** d
    out += np.sum(n * tau_c ** t * exp_g * deriv_factor * active, axis=1)

    return out


def residuals(p, delta, tau, y_target):
    return alpha_delta_model(delta, tau, p) - y_target


def jacobian(p, delta, tau, y_target):
    """Analytical Jacobian of the residuals w.r.t. all model parameters."""
    delta_c = np.clip(np.asarray(delta, dtype=float), 1e-6, 10.0)
    tau_c = np.clip(np.asarray(tau, dtype=float), 0.5, 5.0)
    delta_c = delta_c[:, None]
    tau_c = tau_c[:, None]
    ld = np.log(delta_c)
    lt = np.log(tau_c)

    poly, exp, gauss = unpack_params(p)
    N = delta_c.shape[0]
    J = np.zeros((N, TOTAL_P))
    col = 0

    # ----- Polynomial terms -----
    n = poly[:, 0]
    d = poly[:, 1]
    t = poly[:, 2]
    base = d * delta_c ** (d - 1.0) * tau_c ** t
    J[:, col : col + N_POLY * POLY_P : POLY_P] = base
    J[:, col + 1 : col + N_POLY * POLY_P : POLY_P] = (
        n * delta_c ** (d - 1.0) * tau_c ** t * (1.0 + d * ld)
    )
    J[:, col + 2 : col + N_POLY * POLY_P : POLY_P] = n * base * lt
    col += N_POLY * POLY_P

    # ----- Exponential terms -----
    n = exp[:, 0]
    d = exp[:, 1]
    t = exp[:, 2]
    l = exp[:, 3]
    C = delta_c ** l
    arg = -C
    active = arg >= -50.0
    E = np.exp(np.clip(arg, -50.0, 50.0))
    H = d - l * C
    base = delta_c ** (d - 1.0) * E * H
    m = n * tau_c ** t * base

    J[:, col : col + N_EXP * EXP_P : EXP_P] = tau_c ** t * base * active
    J[:, col + 1 : col + N_EXP * EXP_P : EXP_P] = (
        n * tau_c ** t * delta_c ** (d - 1.0) * E * (H * ld + 1.0) * active
    )
    J[:, col + 2 : col + N_EXP * EXP_P : EXP_P] = m * lt * active
    J[:, col + 3 : col + N_EXP * EXP_P : EXP_P] = (
        -n * tau_c ** t * delta_c ** (d - 1.0) * E * C
        * (1.0 + d * ld + l * ld * (1.0 - C)) * active
    )
    col += N_EXP * EXP_P

    # ----- Gaussian terms -----
    n = gauss[:, 0]
    d = gauss[:, 1]
    t = gauss[:, 2]
    alpha = gauss[:, 3]
    beta = gauss[:, 4]
    eps = gauss[:, 5]
    gamma = gauss[:, 6]
    G = -alpha * (delta_c - eps) ** 2 - beta * (tau_c - gamma) ** 2
    active = G >= -50.0
    E = np.exp(np.clip(G, -50.0, 50.0))
    H = d - 2.0 * alpha * delta_c * (delta_c - eps)
    base = delta_c ** (d - 1.0) * E * H
    m = n * tau_c ** t * base

    J[:, col : col + N_GAUSS * GAUSS_P : GAUSS_P] = tau_c ** t * base * active
    J[:, col + 1 : col + N_GAUSS * GAUSS_P : GAUSS_P] = (
        n * tau_c ** t * delta_c ** (d - 1.0) * E * (H * ld + 1.0) * active
    )
    J[:, col + 2 : col + N_GAUSS * GAUSS_P : GAUSS_P] = m * lt * active
    J[:, col + 3 : col + N_GAUSS * GAUSS_P : GAUSS_P] = (
        n * tau_c ** t * delta_c ** (d - 1.0) * E
        * (-2.0 * delta_c * (delta_c - eps) - H * (delta_c - eps) ** 2) * active
    )
    J[:, col + 4 : col + N_GAUSS * GAUSS_P : GAUSS_P] = -m * (tau_c - gamma) ** 2 * active
    J[:, col + 5 : col + N_GAUSS * GAUSS_P : GAUSS_P] = (
        n * tau_c ** t * delta_c ** (d - 1.0) * E * 2.0 * alpha
        * (delta_c + H * (delta_c - eps)) * active
    )
    J[:, col + 6 : col + N_GAUSS * GAUSS_P : GAUSS_P] = m * 2.0 * beta * (tau_c - gamma) * active

    return J


# ---------------------------------------------------------------------------
# Initial guesses and bounds
# ---------------------------------------------------------------------------
def build_initial_params():
    """Physically reasonable, deterministic initial parameter vector."""
    poly = np.zeros((N_POLY, POLY_P))
    for i in range(N_POLY):
        poly[i, 0] = -0.5 + i * (1.0 / (N_POLY - 1))
        poly[i, 1] = 1.0 + (i % 3)
        poly[i, 2] = float(i % 3)

    exp = np.zeros((N_EXP, EXP_P))
    for i in range(N_EXP):
        exp[i, 0] = 0.1 * ((-1) ** i)
        exp[i, 1] = 1.0 + (i % 3)
        exp[i, 2] = float(i % 3)
        exp[i, 3] = 1.0

    gauss = np.zeros((N_GAUSS, GAUSS_P))
    for i in range(N_GAUSS):
        gauss[i, 0] = 0.05 * ((-1) ** i)
        gauss[i, 1] = 2.0
        gauss[i, 2] = 1.0
        gauss[i, 3] = 1.0
        gauss[i, 4] = 1.0
        gauss[i, 5] = 1.0
        gauss[i, 6] = 1.0

    return np.concatenate([poly.ravel(), exp.ravel(), gauss.ravel()])


def build_bounds():
    lb_poly = np.tile(np.array([-5.0, 0.5, -1.0]), (N_POLY, 1))
    ub_poly = np.tile(np.array([5.0, 4.0, 3.0]), (N_POLY, 1))

    lb_exp = np.tile(np.array([-5.0, 0.5, -1.0, 0.1]), (N_EXP, 1))
    ub_exp = np.tile(np.array([5.0, 4.0, 3.0, 3.0]), (N_EXP, 1))

    lb_gauss = np.tile(
        np.array([-5.0, 0.5, -1.0, 0.1, 0.1, 0.1, 0.1]), (N_GAUSS, 1)
    )
    ub_gauss = np.tile(
        np.array([5.0, 4.0, 3.0, 5.0, 5.0, 3.0, 3.0]), (N_GAUSS, 1)
    )

    lb = np.concatenate([lb_poly.ravel(), lb_exp.ravel(), lb_gauss.ravel()])
    ub = np.concatenate([ub_poly.ravel(), ub_exp.ravel(), ub_gauss.ravel()])
    return lb, ub


# ---------------------------------------------------------------------------
# Data generation and target computation
# ---------------------------------------------------------------------------
def generate_points(n_points, T_min, T_max, rho_min, rho_max, seed):
    """Generate n_points valid (T, rho, P) samples in the requested box."""
    rng = np.random.default_rng(seed)
    points = []
    attempts = 0
    while len(points) < n_points and attempts < n_points * 50:
        attempts += 1
        T = rng.uniform(T_min, T_max)
        rho = rng.uniform(rho_min, rho_max)
        try:
            P = CP.PropsSI("P", "T", T, "D", rho, FLUID)
            if np.isfinite(P) and P > 0.0:
                points.append((T, rho, P))
        except Exception:
            continue
    if len(points) < n_points:
        raise RuntimeError(
            f"Only generated {len(points)}/{n_points} valid CoolProp points "
            f"in T=[{T_min},{T_max}], rho=[{rho_min},{rho_max}]."
        )
    return np.array(points)


def generate_stratified_points(n_points, T_min, T_max, rho_min, rho_max, seed,
                               single_phase_only=False):
    """Generate n_points stratified (T, rho, P) samples.

    Stratification concentrates more points near the region boundaries:
      - T: finer grid near T_max (saturation boundary at ~340 K)
      - rho: finer grid near rho_min (low-density liquid boundary)

    Uses a beta(2, 1) transform to bias sampling toward the upper T bound
    and lower rho bound without completely excluding the interior.

    If single_phase_only=True, rejects points where CoolProp reports
    0 < Q < 1 (two-phase).  This is required for the compressed-liquid
    region because the saturation dome extends well above rho_c.
    """
    rng = np.random.default_rng(seed)
    points = []
    attempts = 0
    while len(points) < n_points and attempts < n_points * 50:
        attempts += 1
        # Stratified T: bias toward T_max with Beta(2, 1)
        u_T = rng.beta(2.0, 1.0)
        T = T_min + u_T * (T_max - T_min)
        # Stratified rho: bias toward rho_min with 1 - Beta(2, 1)
        u_rho = 1.0 - rng.beta(2.0, 1.0)
        rho = rho_min + u_rho * (rho_max - rho_min)
        try:
            if single_phase_only:
                Q = CP.PropsSI("Q", "T", T, "D", rho, FLUID)
                if 0.0 < Q < 1.0:
                    continue  # skip two-phase states
            P = CP.PropsSI("P", "T", T, "D", rho, FLUID)
            if np.isfinite(P) and P > 0.0:
                points.append((T, rho, P))
        except Exception:
            continue
    if len(points) < n_points:
        raise RuntimeError(
            f"Only generated {len(points)}/{n_points} valid CoolProp points "
            f"in T=[{T_min},{T_max}], rho=[{rho_min},{rho_max}]."
        )
    return np.array(points)


def compute_targets(data):
    """Convert (T, rho, P) data to reduced variables and target alpha_delta."""
    T, rho, P = data[:, 0], data[:, 1], data[:, 2]
    delta = rho / RHO_CRITICAL
    tau = T_CRITICAL / T
    Z = P / (rho * GAS_CONSTANT * T)
    alpha_delta = (Z - 1.0) / delta
    return delta, tau, alpha_delta


# ---------------------------------------------------------------------------
# Coefficient output
# ---------------------------------------------------------------------------
def write_coefficients(p, path):
    poly, exp, gauss = unpack_params(p)
    lines = [
        f"T_CRITICAL = {float(T_CRITICAL)!r}",
        f"RHO_CRITICAL = {float(RHO_CRITICAL)!r}",
        f"GAS_CONSTANT = {float(GAS_CONSTANT)!r}",
        "",
        "POLYNOMIAL_TERMS = ["
        + ", ".join(f"({float(n)!r}, {float(d)!r}, {float(t)!r})" for n, d, t in poly)
        + "]",
        "",
        "EXPONENTIAL_TERMS = ["
        + ", ".join(f"({float(n)!r}, {float(d)!r}, {float(t)!r}, {float(l)!r})" for n, d, t, l in exp)
        + "]",
        "",
        "GAUSSIAN_TERMS = ["
        + ", ".join(
            f"({float(n)!r}, {float(d)!r}, {float(t)!r}, {float(alpha)!r}, "
            f"{float(beta)!r}, {float(eps)!r}, {float(gamma)!r})"
            for n, d, t, alpha, beta, eps, gamma in gauss
        )
        + "]",
    ]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------
def validate(p, data):
    T, rho, P_true = data[:, 0], data[:, 1], data[:, 2]
    delta = rho / RHO_CRITICAL
    tau = T_CRITICAL / T
    alpha_d = alpha_delta_model(delta, tau, p)
    P_pred = rho * GAS_CONSTANT * T * (1.0 + delta * alpha_d)
    rel_err = np.abs(P_pred - P_true) / np.abs(P_true)
    return {
        "mean": float(np.mean(rel_err)),
        "max": float(np.max(rel_err)),
        "p95": float(np.percentile(rel_err, 95.0)),
        "p99": float(np.percentile(rel_err, 99.0)),
    }


# ---------------------------------------------------------------------------
# Region-specific regression
# ---------------------------------------------------------------------------
def fit_region(name, T_min, T_max, rho_min, rho_max, train_seed, val_seed, out_path,
               n_train=2000, n_val=500, stratified=False, single_phase_only=False):
    print("\n" + "=" * 60)
    print(f"R410A {name.upper()} REGION FIT")
    print("=" * 60)
    print(f"T range   = [{T_min}, {T_max}] K")
    print(f"rho range = [{rho_min:.3f}, {rho_max:.3f}] kg/m^3")
    if single_phase_only:
        print("  (single-phase only — two-phase states rejected)")

    print(f"\nGenerating {n_train} training points for the {name} region"
          + (" (stratified)" if stratified else "") + " ...")
    gen = generate_stratified_points if stratified else generate_points
    kwargs = {"single_phase_only": single_phase_only} if stratified else {}
    train_data = gen(n_train, T_min, T_max, rho_min, rho_max, train_seed, **kwargs)
    delta_tr, tau_tr, y_tr = compute_targets(train_data)
    print(f"  Target alpha_delta range: [{y_tr.min():.6e}, {y_tr.max():.6e}]")

    x0 = build_initial_params()
    lb, ub = build_bounds()

    print(f"Fitting {TOTAL_P} parameters with least_squares ...")
    result = least_squares(
        residuals,
        x0,
        jac=jacobian,
        args=(delta_tr, tau_tr, y_tr),
        method="trf",
        tr_solver="lsmr",
        bounds=(lb, ub),
        max_nfev=5000,
        ftol=1e-10,
        xtol=1e-10,
        gtol=1e-10,
        verbose=1,
    )
    print(f"Optimization finished: {result.message.strip()}")
    print(f"  nfev = {result.nfev}, njev = {result.njev}, cost = {result.cost:.6e}")

    print(f"\nGenerating {n_val} validation points for the {name} region ...")
    val_data = generate_points(n_val, T_min, T_max, rho_min, rho_max, val_seed)
    stats = validate(result.x, val_data)

    print("\nValidation relative pressure errors:")
    print(f"  mean = {stats['mean']:.6e}")
    print(f"  max  = {stats['max']:.6e}")
    print(f"  95th percentile = {stats['p95']:.6e}")
    print(f"  99th percentile = {stats['p99']:.6e}")

    target_met = stats["mean"] < 0.01
    print(f"  Mean < 1% target: {'PASSED' if target_met else 'FAILED'}")

    write_coefficients(result.x, out_path)
    print(f"\nWrote {name} coefficients to: {out_path}")
    return result, stats


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("R410A split-region Helmholtz residual regression")
    print("=" * 60)
    print(f"Fluid: {FLUID}")
    print(f"T_CRITICAL  = {T_CRITICAL:.6f} K")
    print(f"RHO_CRITICAL = {RHO_CRITICAL:.6f} kg/m^3")
    print(f"GAS_CONSTANT = {GAS_CONSTANT:.6f} J/(kg*K)")

    base = os.path.expanduser("~/hvac-simulation/math_model")

    # Liquid region (FR-MA-001-L1: denser stratified sampling for <1% error)
    fit_region(
        name="liquid",
        T_min=220.0,
        T_max=340.0,
        rho_min=1.05 * RHO_CRITICAL,
        rho_max=3.0 * RHO_CRITICAL,
        train_seed=42,
        val_seed=43,
        out_path=os.path.join(base, "r410a_liquid_coefficients.py"),
        n_train=5000,
        n_val=1000,
        stratified=True,
        single_phase_only=True,
    )

    # Vapor region
    fit_region(
        name="vapor",
        T_min=350.0,
        T_max=480.0,
        rho_min=0.1 * RHO_CRITICAL,
        rho_max=0.9 * RHO_CRITICAL,
        train_seed=12345,
        val_seed=12346,
        out_path=os.path.join(base, "r410a_vapor_coefficients.py"),
    )

    print("\n" + "=" * 60)
    print("All region fits complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
