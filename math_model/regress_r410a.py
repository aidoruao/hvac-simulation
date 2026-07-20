#!/usr/bin/env python3
"""
R410A Helmholtz EOS Coefficient Regression
Generates coefficients from CoolProp synthetic data + constrained optimization.
Outputs: math_model/r410a_coefficients.py
"""

import numpy as np
from scipy.optimize import least_squares
import CoolProp.CoolProp as CP
import json
import os

# === R410A Critical Parameters (CoolProp ground truth) ===
T_c = CP.PropsSI('Tcrit', 'R410A')
rho_c = CP.PropsSI('rhocrit', 'R410A')
R_specific = CP.PropsSI('GAS_CONSTANT', 'R410A') / CP.PropsSI('MOLAR_MASS', 'R410A')

print(f"T_c = {T_c:.6f} K")
print(f"rho_c = {rho_c:.6f} kg/m^3")
print(f"R = {R_specific:.6f} J/(kg*K)")

# === Generate synthetic training data from CoolProp ===
np.random.seed(42)
n_samples = 2000

T_samples = np.random.uniform(200, 500, n_samples)
rho_samples = np.random.uniform(0.1, 2.5 * rho_c, n_samples)

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

# === Helmholtz Residual Functional Form ===
n_poly = 12
n_exp = 6
n_gauss = 4

def helmholtz_residual(delta, tau, coeffs):
    alpha_r = 0.0
    idx = 0
    for i in range(n_poly):
        n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]
        alpha_r += n * (delta ** d) * (tau ** t)
        idx += 3
    for i in range(n_exp):
        n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]; l = coeffs[idx+3]
        alpha_r += n * (delta ** d) * (tau ** t) * np.exp(-(delta ** l))
        idx += 4
    for i in range(n_gauss):
        n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]
        alpha = coeffs[idx+3]; beta = coeffs[idx+4]
        eps = coeffs[idx+5]; gamma = coeffs[idx+6]
        alpha_r += n * (delta ** d) * (tau ** t) * np.exp(
            -alpha * (delta - eps)**2 - beta * (tau - gamma)**2
        )
        idx += 7
    return alpha_r

def helmholtz_delta_deriv(delta, tau, coeffs):
    dad = 0.0
    idx = 0
    for i in range(n_poly):
        n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]
        if d > 0:
            dad += n * d * (delta ** (d-1)) * (tau ** t)
        idx += 3
    for i in range(n_exp):
        n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]; l = coeffs[idx+3]
        exp_term = np.exp(-(delta ** l))
        dad += n * (tau ** t) * exp_term * (d * delta**(d-1) - l * delta**(d+l-1))
        idx += 4
    for i in range(n_gauss):
        n = coeffs[idx]; d = coeffs[idx+1]; t = coeffs[idx+2]
        alpha = coeffs[idx+3]; beta = coeffs[idx+4]
        eps = coeffs[idx+5]; gamma = coeffs[idx+6]
        gauss = np.exp(-alpha*(delta-eps)**2 - beta*(tau-gamma)**2)
        dad += n * (tau ** t) * gauss * (d * delta**(d-1) - 2*alpha*(delta-eps)*delta**d)
        idx += 7
    return dad

n_params = n_poly * 3 + n_exp * 4 + n_gauss * 7
print(f"Total parameters: {n_params}")

np.random.seed(123)
initial_guess = np.zeros(n_params)

for i in range(n_poly):
    initial_guess[i*3] = np.random.uniform(-1, 1)
    initial_guess[i*3+1] = np.random.uniform(1, 4)
    initial_guess[i*3+2] = np.random.uniform(0, 2.5)

offset = n_poly * 3
for i in range(n_exp):
    initial_guess[offset+i*4] = np.random.uniform(-1, 1)
    initial_guess[offset+i*4+1] = np.random.uniform(1, 5)
    initial_guess[offset+i*4+2] = np.random.uniform(0, 3)
    initial_guess[offset+i*4+3] = np.random.uniform(1, 3)

offset2 = offset + n_exp * 4
for i in range(n_gauss):
    initial_guess[offset2+i*7] = np.random.uniform(-1, 1)
    initial_guess[offset2+i*7+1] = np.random.uniform(1, 4)
    initial_guess[offset2+i*7+2] = np.random.uniform(0, 3)
    initial_guess[offset2+i*7+3] = np.random.uniform(0.5, 5)
    initial_guess[offset2+i*7+4] = np.random.uniform(0.5, 5)
    initial_guess[offset2+i*7+5] = np.random.uniform(0.5, 2)
    initial_guess[offset2+i*7+6] = np.random.uniform(0.5, 2)

def residuals(params):
    res = []
    for dp in data_points:
        delta = dp['delta']
        tau = dp['tau']
        target = dp['alpha_delta']
        pred = helmholtz_delta_deriv(delta, tau, params)
        res.append(pred - target)
    return np.array(res)

print("Starting regression...")
result = least_squares(residuals, initial_guess, method='lm', max_nfev=5000)
print(f"Regression complete. Cost: {result.cost:.6e}, nfev: {result.nfev}")

# === Validate against CoolProp on held-out data ===
n_val = 500
T_val = np.random.uniform(220, 480, n_val)
rho_val = np.random.uniform(0.5, 2.0 * rho_c, n_val)

errors = []
for T, rho in zip(T_val, rho_val):
    try:
        P_cp = CP.PropsSI('P', 'T', T, 'D', rho, 'R410A')
        delta = rho / rho_c
        tau = T_c / T
        alpha_d_pred = helmholtz_delta_deriv(delta, tau, result.x)
        P_pred = rho * R_specific * T * (1 + delta * alpha_d_pred)
        rel_err = abs(P_pred - P_cp) / P_cp
        errors.append(rel_err)
    except Exception:
        continue

errors = np.array(errors)
print(f"Validation: mean rel error = {np.mean(errors):.6e}")
print(f"Validation: max rel error = {np.max(errors):.6e}")
print(f"Validation: 95th percentile = {np.percentile(errors, 95):.6e}")

# === Output coefficient module ===
coeffs = result.x
output_lines = [
    '"""',
    'R410A Helmholtz EOS Coefficients',
    'Auto-generated from CoolProp synthetic data via constrained regression.',
    f'T_c = {T_c:.6f} K',
    f'rho_c = {rho_c:.6f} kg/m^3',
    f'R = {R_specific:.6f} J/(kg*K)',
    f'Mean validation error: {np.mean(errors):.6e}',
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
print("Done.")
