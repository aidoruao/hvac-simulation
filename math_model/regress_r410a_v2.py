#!/usr/bin/env python3
"""
R410A Helmholtz EOS Coefficient Regression v2
Fixed: bounded optimization, clipping, better initial guesses, TRF method.
"""

import numpy as np
from scipy.optimize import least_squares
import CoolProp.CoolProp as CP
import os

# === R410A Critical Parameters ===
T_c = CP.PropsSI('Tcrit', 'R410A')
rho_c = CP.PropsSI('rhocrit', 'R410A')
R_specific = CP.PropsSI('GAS_CONSTANT', 'R410A') / CP.PropsSI('MOLAR_MASS', 'R410A')

print(f"T_c = {T_c:.6f} K")
print(f"rho_c = {rho_c:.6f} kg/m^3")
print(f"R = {R_specific:.6f} J/(kg*K)")

# === Generate synthetic training data ===
np.random.seed(42)
n_samples = 2000

# Safer ranges: avoid extreme delta/tau that cause overflow
T_min, T_max = 220, 480
rho_min, rho_max = 0.5, 2.0 * rho_c

T_samples = np.random.uniform(T_min, T_max, n_samples)
rho_samples = np.random.uniform(rho_min, rho_max, n_samples)

data_points = []

for T, rho in zip(T_samples, rho_samples):
    try:
        P = CP.PropsSI('P', 'T', T, 'D', rho, 'R410A')
        tau = T_c / T
        delta = rho / rho_c
        alpha_delta = (P / (rho * R_specific * T) - 1) / delta
        data_points.append({
            'T': T, 'rho': rho, 'tau': tau, 'delta': delta,
            'P': P, 'alpha_delta': alpha_delta
        })
    except Exception:
        continue

print(f"Generated {len(data_points)} valid data points")

# === Helmholtz Functional Form with Clipping ===
n_poly = 12
n_exp = 6
n_gauss = 4

def safe_delta_tau(delta, tau):
    """Clip to prevent overflow in power operations."""
    delta = np.clip(delta, 1e-6, 10.0)
    tau = np.clip(tau, 0.5, 5.0)
    return delta, tau

def helmholtz_delta_deriv(delta, tau, coeffs):
    delta, tau = safe_delta_tau(delta, tau)
    dad = 0.0
    idx = 0

    # Polynomial: n * d * delta^(d-1) * tau^t
    for i in range(n_poly):
        n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]
        if abs(d) > 0.01:
            dad += n * d * (delta ** (d-1)) * (tau ** t)
        idx += 3

    # Exponential: n * tau^t * exp(-delta^l) * (d*delta^(d-1) - l*delta^(d+l-1))
    for i in range(n_exp):
        n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]; l = coeffs[idx+3]
        dl = delta ** l
        if dl > 50:  # exp(-50) is negligible
            idx += 4
            continue
        exp_term = np.exp(-dl)
        term = d * (delta ** (d-1)) - l * (delta ** (d+l-1))
        dad += n * (tau ** t) * exp_term * term
        idx += 4

    # Gaussian: n * tau^t * exp(-alpha*(delta-eps)^2 - beta*(tau-gamma)^2) * (...)
    for i in range(n_gauss):
        n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]
        alpha = coeffs[idx+3]; beta = coeffs[idx+4]
        eps = coeffs[idx+5]; gamma = coeffs[idx+6]
        gauss_arg = alpha * (delta - eps)**2 + beta * (tau - gamma)**2
        if gauss_arg > 50:
            idx += 7
            continue
        gauss = np.exp(-gauss_arg)
        term = d * (delta ** (d-1)) - 2 * alpha * (delta - eps) * (delta ** d)
        dad += n * (tau ** t) * gauss * term
        idx += 7

    return dad

n_params = n_poly * 3 + n_exp * 4 + n_gauss * 7
print(f"Total parameters: {n_params}")

# === Better Initial Guesses ===
np.random.seed(123)
initial_guess = np.zeros(n_params)

# Polynomial: small n, d in [1,3], t in [0,2]
for i in range(n_poly):
    initial_guess[i*3] = np.random.uniform(-0.5, 0.5)
    initial_guess[i*3+1] = np.random.uniform(1.0, 3.0)
    initial_guess[i*3+2] = np.random.uniform(0.0, 2.0)

# Exponential: small n, d in [1,3], t in [0,2], l in [0.5,2]
offset = n_poly * 3
for i in range(n_exp):
    initial_guess[offset+i*4] = np.random.uniform(-0.5, 0.5)
    initial_guess[offset+i*4+1] = np.random.uniform(1.0, 3.0)
    initial_guess[offset+i*4+2] = np.random.uniform(0.0, 2.0)
    initial_guess[offset+i*4+3] = np.random.uniform(0.5, 2.0)

# Gaussian: small n, d in [1,3], t in [0,2], alpha/beta in [0.5,3], eps/gamma in [0.5,2]
offset2 = offset + n_exp * 4
for i in range(n_gauss):
    initial_guess[offset2+i*7] = np.random.uniform(-0.5, 0.5)
    initial_guess[offset2+i*7+1] = np.random.uniform(1.0, 3.0)
    initial_guess[offset2+i*7+2] = np.random.uniform(0.0, 2.0)
    initial_guess[offset2+i*7+3] = np.random.uniform(0.5, 3.0)
    initial_guess[offset2+i*7+4] = np.random.uniform(0.5, 3.0)
    initial_guess[offset2+i*7+5] = np.random.uniform(0.5, 2.0)
    initial_guess[offset2+i*7+6] = np.random.uniform(0.5, 2.0)

# === Bounds to prevent overflow ===
lb = np.full(n_params, -10.0)
ub = np.full(n_params, 10.0)

# Polynomial bounds
for i in range(n_poly):
    lb[i*3] = -5.0;   ub[i*3] = 5.0      # n
    lb[i*3+1] = 0.5;  ub[i*3+1] = 4.0    # d
    lb[i*3+2] = -1.0; ub[i*3+2] = 3.0    # t

# Exponential bounds
for i in range(n_exp):
    lb[offset+i*4] = -5.0;   ub[offset+i*4] = 5.0
    lb[offset+i*4+1] = 0.5;  ub[offset+i*4+1] = 4.0
    lb[offset+i*4+2] = -1.0; ub[offset+i*4+2] = 3.0
    lb[offset+i*4+3] = 0.1;  ub[offset+i*4+3] = 3.0   # l bounded!

# Gaussian bounds
for i in range(n_gauss):
    lb[offset2+i*7] = -5.0;   ub[offset2+i*7] = 5.0
    lb[offset2+i*7+1] = 0.5;  ub[offset2+i*7+1] = 4.0
    lb[offset2+i*7+2] = -1.0; ub[offset2+i*7+2] = 3.0
    lb[offset2+i*7+3] = 0.1;  ub[offset2+i*7+3] = 5.0  # alpha
    lb[offset2+i*7+4] = 0.1;  ub[offset2+i+7+4] = 5.0  # beta
    lb[offset2+i+7+5] = 0.1;  ub[offset2+i*7+5] = 3.0  # eps
    lb[offset2+i*7+6] = 0.1;  ub[offset2+i+7+6] = 3.0  # gamma

# === Residuals with NaN guard ===
def residuals(params):
    res = []
    for dp in data_points:
        delta = dp['delta']
        tau = dp['tau']
        target = dp['alpha_delta']
        pred = helmholtz_delta_deriv(delta, tau, params)
        if not np.isfinite(pred):
            res.append(1e6)  # penalty for NaN/Inf
        else:
            res.append(pred - target)
    return np.array(res)

print("Starting bounded regression with TRF...")
result = least_squares(
    residuals, initial_guess,
    method='trf',
    bounds=(lb, ub),
    max_nfev=5000,
    ftol=1e-10, xtol=1e-10, gtol=1e-10,
    verbose=2
)
print(f"\nRegression complete.")
print(f"Cost: {result.cost:.6e}")
print(f"nfev: {result.nfev}")
print(f"njev: {result.njev}")
print(f"Status: {result.status}")
print(f"Message: {result.message}")

# === Validate ===
n_val = 500
T_val = np.random.uniform(230, 470, n_val)
rho_val = np.random.uniform(1.0, 1.8 * rho_c, n_val)

errors = []
for T, rho in zip(T_val, rho_val):
    try:
        P_cp = CP.PropsSI('P', 'T', T, 'D', rho, 'R410A')
        delta = rho / rho_c
        tau = T_c / T
        alpha_d_pred = helmholtz_delta_deriv(delta, tau, result.x)
        if not np.isfinite(alpha_d_pred):
            continue
        P_pred = rho * R_specific * T * (1 + delta * alpha_d_pred)
        rel_err = abs(P_pred - P_cp) / max(abs(P_cp), 1.0)
        errors.append(rel_err)
    except Exception:
        continue

errors = np.array(errors)
print(f"\nValidation on {len(errors)} points:")
print(f"  mean rel error = {np.mean(errors):.6e}")
print(f"  max rel error  = {np.max(errors):.6e}")
print(f"  95th percentile = {np.percentile(errors, 95):.6e}")
print(f"  99th percentile = {np.percentile(errors, 99):.6e}")

# === Output coefficient module ===
coeffs = result.x
output_lines = [
    '"""',
    'R410A Helmholtz EOS Coefficients',
    'Auto-generated from CoolProp synthetic data via bounded TRF regression.',
    f'T_c = {T_c:.6f} K',
    f'rho_c = {rho_c:.6f} kg/m^3',
    f'R = {R_specific:.6f} J/(kg*K)',
    f'Mean validation error: {np.mean(errors):.6e}',
    f'Max validation error: {np.max(errors):.6e}',
    '"""',
    '',
    f'T_CRITICAL = {T_c}',
    f'RHO_CRITICAL = {rho_c}',
    f'GAS_CONSTANT = {R_specific}',
    '',
    '# Term structure: (n, d, t) for polynomial',
    'POLYNOMIAL_TERMS = [',
]

idx = 0
for i in range(n_poly):
    n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]
    output_lines.append(f"    ({n:.10e}, {d:.6f}, {t:.6f}),")
    idx += 3

output_lines.append("    ]")
output_lines.append("")
output_lines.append("# Term structure: (n, d, t, l) for exponential")
output_lines.append("EXPONENTIAL_TERMS = [")

for i in range(n_exp):
    n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]; l = coeffs[idx+3]
    output_lines.append(f"    ({n:.10e}, {d:.6f}, {t:.6f}, {l:.6f}),")
    idx += 4

output_lines.append("    ]")
output_lines.append("")
output_lines.append("# Term structure: (n, d, t, alpha, beta, eps, gamma) for Gaussian")
output_lines.append("GAUSSIAN_TERMS = [")

for i in range(n_gauss):
    n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]
    alpha = coeffs[idx+3]; beta = coeffs[idx+4]
    eps = coeffs[idx+5]; gamma = coeffs[idx+6]
    output_lines.append(f"    ({n:.10e}, {d:.6f}, {t:.6f}, {alpha:.6f}, {beta:.6f}, {eps:.6f}, {gamma:.6f}),")
    idx += 7

output_lines.append("    ]")
output_lines.append("")

out_path = os.path.join(os.path.dirname(__file__), 'r410a_coefficients.py')
with open(out_path, 'w') as f:
    f.write('\n'.join(output_lines))

print(f"\nWrote coefficients to {out_path}")
print("done.")
