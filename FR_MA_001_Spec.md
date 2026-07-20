# FR-MA-001: Mathematical Modeling — Equation of State Derivations

**Document ID:** HVAC-MA-001
**Status:** IN PROGRESS
**Target Version:** SRS v1.6
**Parent Requirement:** FR-PH-001 (Multi-refrigerant physics)
**Depends On:** FR-PH-003 (MOOSE-inspired solver — BVP infrastructure proven)

---

## 1. Purpose

Move from "black box" CoolProp calls to **first-principles thermodynamic derivations**. Every EOS evaluation must be traceable to its mathematical origin — partial derivatives, Jacobian matrices, and convergence criteria documented.

This is the bridge from "simulation" to **"provably correct thermodynamic engine"**.

---

## 2. Scope

| Deliverable | Description | Verification |
|-------------|-------------|------------|
| EOS-HEOS-001 | Helmholtz EOS residual form: a(δ,τ) = a^ideal(δ,τ) + a^res(δ,τ) | Analytical derivative check against CoolProp |
| EOS-DER-001 | First partials: (∂a/∂δ)_τ, (∂a/∂τ)_δ | Finite difference convergence |
| EOS-DER-002 | Second partials: (∂²a/∂δ²)_τ, (∂²a/∂τ²)_δ, (∂²a/∂δ∂τ) | Cross-derivative symmetry check |
| EOS-PROP-001 | Derived properties: P(δ,τ), u(δ,τ), s(δ,τ), h(δ,τ), c_p, c_v, w | Round-trip against CoolProp REFPROP |
| EOS-CONV-001 | Newton-Raphson solver for δ(P,T) with Jacobian | Convergence within 1e-12, 10 iterations max |
| EOS-JAC-001 | Analytical Jacobian for NR solver | Condition number < 1e14 |

---

## 3. Mathematical Foundation

### 3.1 Reduced Variables
```
δ = ρ/ρ_c    (reduced density)
τ = T_c/T    (inverse reduced temperature)
```

### 3.2 Helmholtz Residual Form
```
a(δ,τ) = a^ideal(δ,τ) + a^res(δ,τ)

where:
a^ideal = ln(δ) + Σ n_k * τ^{i_k}   (polynomial + exponential terms)
a^res   = Σ n_k * δ^{d_k} * τ^{t_k} * exp(-δ^{l_k})   (Gaussian bell terms)
```

### 3.3 Pressure Equation
```
P = ρRT[1 + δ(∂a^res/∂δ)_τ]
```

### 3.4 Newton-Raphson for δ(P,T)
```
f(δ) = P(δ,T) - P_target = 0
J = df/dδ = ρRT[1 + 2δ(∂a^res/∂δ)_τ + δ²(∂²a^res/∂δ²)_τ]
δ_{n+1} = δ_n - f(δ_n)/J(δ_n)
```

---

## 4. Verification Strategy

| Test | Method | Tolerance | Reference |
|------|--------|-----------|-----------|
| Derivative check | Complex step differentiation | 1e-15 | Martins et al. 2003 |
| Cross-derivative symmetry | ∂²a/∂δ∂τ == ∂²a/∂τ∂δ | 1e-14 | Mathematical identity |
| Round-trip P(δ,T)→δ(P,T)→P | Full EOS cycle | 1e-9 relative | CoolProp 8.0.0 |
| Critical point convergence | δ→1, τ→1 | 1e-12 | NIST REFPROP 10.0 |

---

## 5. Implementation Plan

| Phase | File | Content |
|-------|------|---------|
| P0 | `math_model/helmholtz_eos.py` | Base EOS class with R410A coefficients |
| P0 | `math_model/test_helmholtz_eos.py` | Derivative and round-trip tests |
| P1 | `math_model/newton_solver.py` | NR solver with analytical Jacobian |
| P1 | `math_model/test_newton_solver.py` | Convergence and critical point tests |
| P2 | `math_model/derived_properties.py` | c_p, c_v, w, s, h from EOS |
| P2 | `math_model/test_derived_properties.py` | Against CoolProp REFPROP data |

---

## 6. Citation

| Source | Citation |
|--------|----------|
| Helmholtz EOS formulation | Lemmon, E.W., et al. "NIST REFPROP 10.0," NIST, 2018 |
| Complex step derivatives | Martins, J.R.R.A., et al. "The complex-step derivative approximation," ACM TOMS, 29(3), 245-262, 2003 |
| Thermodynamic property derivations | Span, R. "Multiparameter Equations of State," Springer, 2000. ISBN: 978-3-642-63619-7 |

---

*Glass box: every derivative traced to its formula. No hidden convergence. No black box.*
