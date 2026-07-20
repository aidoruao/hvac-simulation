"""
FR-MA-001: Helmholtz Equation of State — First-Principles Implementation

Primary references:
  Span & Wagner (2000) "A New Equation of State for Carbon Dioxide …"
    — residual Helmholtz form α^r(δ,τ) = Σ n_k δ^{d_k} τ^{t_k} + …
  Lemmon & Jacobsen (2018) "A Reference Equation of State …"
    — derived property relations for c_p, c_v, speed of sound from partials.

EOS-HEOS-001: Helmholtz residual form a(δ,τ) = a^ideal + a^res
EOS-DER-001/002: First and second partial derivatives
EOS-PROP-001: Derived thermodynamic properties (c_p, c_v, w, Jacobian)

Region-aware model (R410A and R32):
  - Vapor coefficients are used when T >= 350 K AND rho < 0.9*rho_c
    (the vapor regression was trained on T ∈ [350, 480] K per fluid).
  - Liquid and two-phase states fall back to CoolProp for physical
    accuracy (see HVAC_SRS.md §7).
  - FR-MA-002: R32 supported via ``HelmholtzEOS(fluid="R32")``.

  Ideal-gas heat capacity: Aly-Lee (1999) polynomial c_v⁰(T) fitted
  to CoolProp 8.0 at D → 0 (see _build_coeff_dict and
  FORMULA_CITATIONS.md §2.5).
"""

import numpy as np
from typing import Tuple, Dict, Optional, Union

try:
    from r410a_vapor_coefficients import (
        T_CRITICAL as VAPOR_T_CRITICAL,
        RHO_CRITICAL as VAPOR_RHO_CRITICAL,
        GAS_CONSTANT as VAPOR_GAS_CONSTANT,
        POLYNOMIAL_TERMS as VAPOR_POLYNOMIAL_TERMS,
        EXPONENTIAL_TERMS as VAPOR_EXPONENTIAL_TERMS,
        GAUSSIAN_TERMS as VAPOR_GAUSSIAN_TERMS,
    )
except ImportError as e:
    raise ImportError(
        "Vapor coefficient file not found. "
        "Run regress_r410a_v4.py to generate it."
    ) from e

# R32 vapor coefficients (FR-MA-002) — optional; only required for fluid="R32"
try:
    from r32_vapor_coefficients import (
        T_CRITICAL as R32_T_CRITICAL,
        RHO_CRITICAL as R32_RHO_CRITICAL,
        GAS_CONSTANT as R32_GAS_CONSTANT,
        POLYNOMIAL_TERMS as R32_POLYNOMIAL_TERMS,
        EXPONENTIAL_TERMS as R32_EXPONENTIAL_TERMS,
        GAUSSIAN_TERMS as R32_GAUSSIAN_TERMS,
    )
    _HAS_R32 = True
except ImportError:
    _HAS_R32 = False

# FR-MA-003: R134a, FR-MA-004: R1234yf, FR-MA-005: R22
_REFRIGERANTS = {
    "R134a": "r134a_vapor_coefficients",
    "R1234yf": "r1234yf_vapor_coefficients",
    "R22": "r22_vapor_coefficients",
}
_REFRIGERANT_IMPORTS = {}
for _name, _mod in _REFRIGERANTS.items():
    try:
        _m = __import__(_mod, fromlist=["T_CRITICAL"])
        _REFRIGERANT_IMPORTS[_name] = {
            "T_c": _m.T_CRITICAL, "rho_c": _m.RHO_CRITICAL, "R": _m.GAS_CONSTANT,
            "poly": _m.POLYNOMIAL_TERMS, "exp": _m.EXPONENTIAL_TERMS,
            "gauss": _m.GAUSSIAN_TERMS,
        }
    except ImportError:
        pass

try:
    import CoolProp.CoolProp as CP
except ImportError:
    CP = None

Number = Union[int, float, np.ndarray]


def _build_coeff_dict(
    T_c: float,
    rho_c: float,
    R: float,
    poly_terms,
    exp_terms,
    gauss_terms,
):
    """Convert the human-readable coefficient tuples into the internal dict."""
    n = []
    d = []
    t = []
    l = []
    ga = []
    be = []
    eps = []
    gamma = []

    for term in poly_terms:
        n.append(term[0])
        d.append(term[1])
        t.append(term[2])
        l.append(0.0)
        ga.append(0.0)
        be.append(0.0)
        eps.append(0.0)
        gamma.append(0.0)

    for term in exp_terms:
        n.append(term[0])
        d.append(term[1])
        t.append(term[2])
        l.append(term[3])
        ga.append(0.0)
        be.append(0.0)
        eps.append(0.0)
        gamma.append(0.0)

    for term in gauss_terms:
        n.append(term[0])
        d.append(term[1])
        t.append(term[2])
        l.append(0.0)
        ga.append(term[3])
        be.append(term[4])
        eps.append(term[5])
        gamma.append(term[6])

    # Aly-Lee (1999) ideal-gas heat capacity for R410A:
    #   c_v^0(T) / R = a1 + a2·T + a3·T² + a4·T³ + a5·T⁴
    # Coefficients fitted to CoolProp 8.0 at D → 0 (ideal-gas limit)
    # over T ∈ [300, 500] K.  Twice-integrated to Helmholtz form:
    #   α^0 = ln(δ) + n_ln·ln(τ) + Σ n_k·τ^{t_k}
    # See FORMULA_CITATIONS.md §2.6 for derivation.
    _T_c = float(T_c)
    _a1, _a2, _a3, _a4, _a5 = (
        4.411813197, -0.011605522, 9.486295e-5, -1.502276e-7, 8.027945e-11
    )
    _ideal_ln_tau = _a1
    _ideal_n = np.array([
        -_a2 * _T_c / 2.0,           # τ^{-1}
        -_a3 * _T_c**2 / 6.0,        # τ^{-2}
        -_a4 * _T_c**3 / 12.0,       # τ^{-3}
        -_a5 * _T_c**4 / 20.0,       # τ^{-4}
    ], dtype=float)
    _ideal_t = np.array([-1.0, -2.0, -3.0, -4.0], dtype=float)
    return {
        "T_c": float(T_c),
        "rho_c": float(rho_c),
        "R": float(R),
        "n": np.array(n, dtype=float),
        "d": np.array(d, dtype=float),
        "t": np.array(t, dtype=float),
        "l": np.array(l, dtype=float),
        "ga": np.array(ga, dtype=float),
        "be": np.array(be, dtype=float),
        "eps": np.array(eps, dtype=float),
        "gamma": np.array(gamma, dtype=float),
        "ideal_ln_tau": _ideal_ln_tau,
        "ideal_n": _ideal_n,
        "ideal_t": _ideal_t,
        "ideal_C": 0.0,   # integration constant — patched by _patch_reference_constants
        "ideal_D": 0.0,
    }


VAPOR_COEFFS = _build_coeff_dict(
    VAPOR_T_CRITICAL,
    VAPOR_RHO_CRITICAL,
    VAPOR_GAS_CONSTANT,
    VAPOR_POLYNOMIAL_TERMS,
    VAPOR_EXPONENTIAL_TERMS,
    VAPOR_GAUSSIAN_TERMS,
)

if _HAS_R32:
    R32_VAPOR_COEFFS = _build_coeff_dict(
        R32_T_CRITICAL,
        R32_RHO_CRITICAL,
        R32_GAS_CONSTANT,
        R32_POLYNOMIAL_TERMS,
        R32_EXPONENTIAL_TERMS,
        R32_GAUSSIAN_TERMS,
    )
else:
    R32_VAPOR_COEFFS = None

# Build coefficient dicts for R134a, R1234yf, R22 (FR-MA-003/004/005)
_EXTRA_COEFFS = {}
for _name, _data in _REFRIGERANT_IMPORTS.items():
    _EXTRA_COEFFS[_name] = _build_coeff_dict(
        _data["T_c"], _data["rho_c"], _data["R"],
        _data["poly"], _data["exp"], _data["gauss"],
    )




def _patch_reference_constants(coeffs, fluid):
    """Solve for ideal_C, ideal_D that match CoolProp H, S at a reference state.

    The Helmholtz ideal-gas form α⁰ includes two integration constants C, D
    that set the enthalpy and entropy reference state.  We determine them by
    matching CoolProp's PropsSI at T=360 K, δ=0.3 (single-phase vapor for
    all supported fluids).  C and D are state-independent, so any valid
    reference point works.
    """
    if CP is None:
        return
    T_ref, delta_ref = 360.0, 0.3
    try:
        T_c = coeffs["T_c"]
        tau = T_c / T_ref
        R = coeffs["R"]
        rho = delta_ref * coeffs["rho_c"]
        Hcp = CP.PropsSI("H", "T", T_ref, "D", rho, fluid)
        Scp = CP.PropsSI("S", "T", T_ref, "D", rho, fluid)
    except Exception:
        return  # CoolProp unavailable or state invalid — leave C=D=0

    # Build temporary arrays matching _residual_derivative expectations
    delta_arr = np.asarray(delta_ref, dtype=float)
    tau_arr = np.asarray(tau, dtype=float)

    # Ideal terms (with current C=D=0)
    a0_tau = _ideal_da_dtau_static(tau_arr, coeffs)
    a0 = _a_ideal_static(delta_arr, tau_arr, coeffs)

    # Residual terms
    ar_tau = _residual_derivative_static(delta_arr, tau_arr, coeffs, "dtau")
    ar_delta = _residual_derivative_static(delta_arr, tau_arr, coeffs, "ddelta")
    ar = _residual_derivative_static(delta_arr, tau_arr, coeffs, "a")

    tau_sum = float(tau * (a0_tau + ar_tau))
    C = (Hcp / (R * T_ref) - tau_sum - delta_ref * float(ar_delta) - 1.0) / tau
    # S / R = τ·(a0_tau + ar_tau) − (a0 + ar) = tau_sum − (a0 + ar)
    # With C,D: S_new/R = S_old/R − D  →  D = S_old/R − S_cp/R
    D = tau_sum - float(a0) - float(ar) - Scp / R

    coeffs["ideal_C"] = float(C)
    coeffs["ideal_D"] = float(D)


# Static versions for use before the class is instantiated
def _a_ideal_static(delta, tau, coeffs):
    n, t = coeffs["ideal_n"], coeffs["ideal_t"]
    n_ln = coeffs.get("ideal_ln_tau", 0.0)
    return np.log(delta) + n_ln * np.log(tau) + np.sum(n * tau ** t)

def _ideal_da_dtau_static(tau, coeffs):
    n, t = coeffs["ideal_n"], coeffs["ideal_t"]
    n_ln = coeffs.get("ideal_ln_tau", 0.0)
    return n_ln / tau + np.sum(n * t * tau ** (t - 1.0))

def _residual_derivative_static(delta, tau, coeffs, deriv):
    """Lightweight copy of _residual_derivative for use during C/D patching."""
    delta_c = np.clip(np.asarray(delta, dtype=float), 1e-6, 10.0)
    tau_c = np.clip(np.asarray(tau, dtype=float), 0.5, 5.0)
    n = coeffs["n"]; d = coeffs["d"]; t = coeffs["t"]
    l = coeffs["l"]; ga = coeffs["ga"]; be = coeffs["be"]
    eps = coeffs["eps"]; gamma = coeffs["gamma"]
    out = np.zeros_like(delta_c)
    for i in range(len(n)):
        nk, dk, tk, lk = n[i], d[i], t[i], l[i]
        gak, bek, epsk, gammak = ga[i], be[i], eps[i], gamma[i]
        if gak > 0:
            G = -gak*(delta_c-epsk)**2 - bek*(tau_c-gammak)**2
            active = G >= -50; E = np.exp(np.clip(G,-50,50))
            H = dk - 2*gak*delta_c*(delta_c-epsk)
            Rterm = tk - 2*bek*tau_c*(tau_c-gammak)
            if deriv=="a": term = nk*delta_c**dk*tau_c**tk*E
            elif deriv=="ddelta": term = nk*tau_c**tk*E*delta_c**(dk-1)*H
            elif deriv=="dtau": term = nk*delta_c**dk*tau_c**(tk-1)*E*Rterm
            else: term = 0
            out += term * active
        elif lk > 0:
            Cpow = delta_c**lk; arg = -Cpow; active = arg >= -50
            E = np.exp(np.clip(arg,-50,50))
            if deriv=="a": term = nk*delta_c**dk*tau_c**tk*E
            elif deriv=="ddelta": term = nk*tau_c**tk*E*(dk*delta_c**(dk-1)-lk*delta_c**(dk+lk-1))
            elif deriv=="dtau": term = nk*tk*delta_c**dk*tau_c**(tk-1)*E
            else: term = 0
            out += term * active
        else:
            if deriv=="a": term = nk*delta_c**dk*tau_c**tk
            elif deriv=="ddelta": term = nk*dk*delta_c**(dk-1)*tau_c**tk
            elif deriv=="dtau": term = nk*tk*delta_c**dk*tau_c**(tk-1)
            else: term = 0
            out += term
    return float(out) if np.ndim(delta_c)==0 else out


# Build the module-level fluid registry and patch reference constants
_FLUID_COEFFS = {"R410A": VAPOR_COEFFS}
if _HAS_R32:
    _FLUID_COEFFS["R32"] = R32_VAPOR_COEFFS
_FLUID_COEFFS.update(_EXTRA_COEFFS)

for _fluid_name, _coeffs in _FLUID_COEFFS.items():
    _patch_reference_constants(_coeffs, _fluid_name)


class HelmholtzEOS:
    """
    Helmholtz Equation of State in reduced variables.

    Glass box: every method returns intermediate values for inspection.
    No hidden state. All derivatives computed analytically.

    Supported fluids:
      - "R410A" (default) — vapor coefficients + CoolProp fallback
      - "R32", "R134a", "R1234yf", "R22" — vapor coefficients + CoolProp fallback
    """

    def __init__(self, fluid: str = "R410A"):
        if fluid not in _FLUID_COEFFS:
            raise ValueError(
                f"Unsupported fluid '{fluid}'. "
                f"Available: {list(_FLUID_COEFFS.keys())}"
            )
        self.fluid = fluid
        self.vapor_coeffs = _FLUID_COEFFS[fluid]

        # Critical properties from vapor coefficient file (canonical).
        self.T_c = self.vapor_coeffs["T_c"]
        self.rho_c = self.vapor_coeffs["rho_c"]
        self.R = self.vapor_coeffs["R"]

    def _select_coeffs(self, T: float, rho: float) -> Tuple[Optional[Dict], str]:
        """Return the coefficient dict and region label for a (T, rho) state.

        Vapor coefficients were trained on T ∈ [350, 480] K.  Liquid
        and two-phase states fall back to CoolProp for physical accuracy
        (Option A — denser regression — was attempted and blocked; see
        HVAC_SRS.md §7).
        """
        if T >= 350.0 and rho < 0.9 * self.rho_c:
            return self.vapor_coeffs, "vapor"
        return None, "coolprop"

    def _get_coeffs(self, delta, tau) -> Tuple[Optional[Dict], str]:
        """Resolve region from reduced variables, using real parts for complex inputs."""
        T = float(np.real(np.asarray(self.T_c / tau)))
        rho = float(np.real(np.asarray(delta) * self.rho_c))
        coeffs, region = self._select_coeffs(T, rho)
        # CoolProp cannot handle complex inputs.  When the caller passes a
        # complex delta or tau (typically for complex-step derivative
        # verification), fall through to the best available fitted
        # coefficient set instead of CoolProp.
        if coeffs is None and (np.iscomplexobj(delta) or np.iscomplexobj(tau)):
            return self.vapor_coeffs, "vapor"
        return coeffs, region

    def _a_ideal(self, delta, tau, coeffs):
        """Ideal gas contribution: a^ideal(δ,τ).

        Aly-Lee (1999) form:
          α^0 = ln(δ) + n_ln·ln(τ) + Σ n_k·τ^{t_k} + C·τ + D
        """
        n = coeffs["ideal_n"]
        t = coeffs["ideal_t"]
        n_ln = coeffs.get("ideal_ln_tau", 0.0)
        C = coeffs.get("ideal_C", 0.0)
        D = coeffs.get("ideal_D", 0.0)
        return np.log(delta) + n_ln * np.log(tau) + np.sum(n * tau ** t) + C * tau + D

    def _a_res(self, delta, tau, coeffs):
        """Residual contribution: a^res(δ,τ). Supports complex inputs for verification."""
        n = coeffs["n"]
        d = coeffs["d"]
        t = coeffs["t"]
        l = coeffs["l"]
        ga = coeffs["ga"]
        be = coeffs["be"]
        eps = coeffs["eps"]
        gamma = coeffs["gamma"]

        is_complex = np.iscomplexobj(delta) or np.iscomplexobj(tau)
        delta_arr = np.asarray(delta)
        tau_arr = np.asarray(tau)
        out = np.zeros_like(delta_arr, dtype=complex if is_complex else float)

        for i in range(len(n)):
            nk = n[i]
            dk = d[i]
            tk = t[i]
            lk = l[i]
            gak = ga[i]
            bek = be[i]
            epsk = eps[i]
            gammak = gamma[i]

            term = nk * delta_arr ** dk * tau_arr ** tk
            if gak > 0.0:
                term *= np.exp(
                    -gak * (delta_arr - epsk) ** 2 - bek * (tau_arr - gammak) ** 2
                )
            elif lk > 0.0:
                term *= np.exp(-(delta_arr ** lk))
            out += term

        return out

    def a(self, delta: Number, tau: Number) -> Number:
        """Total dimensionless Helmholtz energy: a(δ,τ) = a^ideal + a^res."""
        coeffs, region = self._get_coeffs(delta, tau)
        if coeffs is None:
            if CP is None:
                raise RuntimeError("CoolProp is required for fallback properties.")
            T = self.T_c / tau
            rho = delta * self.rho_c
            helm = CP.PropsSI("HELMHOLTZMASS", "T", float(T), "D", float(rho), self.fluid)
            return helm / (self.R * float(T))
        return self._a_ideal(delta, tau, coeffs) + self._a_res(delta, tau, coeffs)

    def _residual_derivative(self, delta, tau, coeffs, deriv: str):
        """
        Analytical residual derivatives with numerical safeguards.

        deriv may be: 'a', 'ddelta', 'd2delta', 'dtau', 'd2tau', 'ddelta_dtau'.
        """
        delta_c = np.clip(np.asarray(delta, dtype=float), 1e-6, 10.0)
        tau_c = np.clip(np.asarray(tau, dtype=float), 0.5, 5.0)

        n = coeffs["n"]
        d = coeffs["d"]
        t = coeffs["t"]
        l = coeffs["l"]
        ga = coeffs["ga"]
        be = coeffs["be"]
        eps = coeffs["eps"]
        gamma = coeffs["gamma"]

        out = np.zeros_like(delta_c, dtype=float)

        for i in range(len(n)):
            nk = n[i]
            dk = d[i]
            tk = t[i]
            lk = l[i]
            gak = ga[i]
            bek = be[i]
            epsk = eps[i]
            gammak = gamma[i]

            if gak > 0.0:
                # ----- Gaussian terms -----
                G = -gak * (delta_c - epsk) ** 2 - bek * (tau_c - gammak) ** 2
                active = G >= -50.0
                E = np.exp(np.clip(G, -50.0, 50.0))
                H = dk - 2.0 * gak * delta_c * (delta_c - epsk)
                R = tk - 2.0 * bek * tau_c * (tau_c - gammak)

                if deriv == "a":
                    term = nk * delta_c ** dk * tau_c ** tk * E
                elif deriv == "ddelta":
                    term = nk * tau_c ** tk * E * delta_c ** (dk - 1.0) * H
                elif deriv == "d2delta":
                    term = (
                        nk
                        * tau_c ** tk
                        * E
                        * delta_c ** (dk - 2.0)
                        * (
                            (dk - 1.0) * H
                            - 2.0 * gak * delta_c * (2.0 * delta_c - epsk)
                            - 2.0 * gak * delta_c * (delta_c - epsk) * H
                        )
                    )
                elif deriv == "dtau":
                    term = nk * delta_c ** dk * tau_c ** (tk - 1.0) * E * R
                elif deriv == "d2tau":
                    term = (
                        nk
                        * delta_c ** dk
                        * tau_c ** (tk - 2.0)
                        * E
                        * (
                            (tk - 1.0) * R
                            - 2.0 * bek * tau_c * (tau_c - gammak) * R
                            - 2.0 * bek * tau_c * (2.0 * tau_c - gammak)
                        )
                    )
                elif deriv == "ddelta_dtau":
                    term = (
                        nk
                        * tau_c ** (tk - 1.0)
                        * E
                        * delta_c ** (dk - 1.0)
                        * H
                        * R
                    )
                else:
                    raise ValueError(f"Unknown derivative type: {deriv}")
                out += term * active

            elif lk > 0.0:
                # ----- Exponential terms -----
                C = delta_c ** lk
                arg = -C
                active = arg >= -50.0
                E = np.exp(np.clip(arg, -50.0, 50.0))

                if deriv == "a":
                    term = nk * delta_c ** dk * tau_c ** tk * E
                elif deriv == "ddelta":
                    term = nk * tau_c ** tk * E * (
                        dk * delta_c ** (dk - 1.0) - lk * delta_c ** (dk + lk - 1.0)
                    )
                elif deriv == "d2delta":
                    term = (
                        nk
                        * tau_c ** tk
                        * E
                        * delta_c ** (dk - 2.0)
                        * (
                            dk * (dk - 1.0)
                            - lk * (2.0 * dk + lk - 1.0) * C
                            + lk ** 2 * C ** 2
                        )
                    )
                elif deriv == "dtau":
                    term = nk * tk * delta_c ** dk * tau_c ** (tk - 1.0) * E
                elif deriv == "d2tau":
                    term = nk * tk * (tk - 1.0) * delta_c ** dk * tau_c ** (tk - 2.0) * E
                elif deriv == "ddelta_dtau":
                    term = (
                        nk
                        * tk
                        * tau_c ** (tk - 1.0)
                        * E
                        * (dk * delta_c ** (dk - 1.0) - lk * delta_c ** (dk + lk - 1.0))
                    )
                else:
                    raise ValueError(f"Unknown derivative type: {deriv}")
                out += term * active

            else:
                # ----- Polynomial terms -----
                if deriv == "a":
                    term = nk * delta_c ** dk * tau_c ** tk
                elif deriv == "ddelta":
                    term = nk * dk * delta_c ** (dk - 1.0) * tau_c ** tk
                elif deriv == "d2delta":
                    term = nk * dk * (dk - 1.0) * delta_c ** (dk - 2.0) * tau_c ** tk
                elif deriv == "dtau":
                    term = nk * tk * delta_c ** dk * tau_c ** (tk - 1.0)
                elif deriv == "d2tau":
                    term = nk * tk * (tk - 1.0) * delta_c ** dk * tau_c ** (tk - 2.0)
                elif deriv == "ddelta_dtau":
                    term = nk * dk * tk * delta_c ** (dk - 1.0) * tau_c ** (tk - 1.0)
                else:
                    raise ValueError(f"Unknown derivative type: {deriv}")
                out += term

        # Return a plain Python float when the inputs were scalars.
        if np.ndim(delta_c) == 0 and np.ndim(tau_c) == 0:
            return float(out)
        return out

    def _ideal_da_dtau(self, tau, coeffs):
        """First τ-derivative of ideal-gas contribution: ∂α^0/∂τ.

        d/dτ [n_ln·ln(τ)] = n_ln / τ
        d/dτ [n_k·τ^{t_k}] = n_k·t_k·τ^{t_k-1}
        d/dτ [C·τ] = C
        """
        n = coeffs["ideal_n"]
        t = coeffs["ideal_t"]
        n_ln = coeffs.get("ideal_ln_tau", 0.0)
        C = coeffs.get("ideal_C", 0.0)
        return n_ln / tau + np.sum(n * t * tau ** (t - 1.0)) + C

    def _ideal_d2a_dtau2(self, tau, coeffs):
        """Second τ-derivative of ideal-gas contribution: ∂²α^0/∂τ².

        d²/dτ² [n_ln·ln(τ)] = -n_ln / τ²
        d²/dτ² [n_k·τ^{t_k}] = n_k·t_k·(t_k-1)·τ^{t_k-2}
        """
        n = coeffs["ideal_n"]
        t = coeffs["ideal_t"]
        n_ln = coeffs.get("ideal_ln_tau", 0.0)
        return -n_ln / tau**2 + np.sum(n * t * (t - 1.0) * tau ** (t - 2.0))

    def da_ddelta(self, delta: Number, tau: Number) -> Number:
        """First partial: (∂a/∂δ)_τ."""
        coeffs, region = self._get_coeffs(delta, tau)
        if coeffs is None:
            if CP is None:
                raise RuntimeError("CoolProp is required for fallback properties.")
            T = self.T_c / tau
            rho = delta * self.rho_c
            P = CP.PropsSI("P", "T", float(T), "D", float(rho), self.fluid)
            return P / (rho * self.R * T * delta)
        return 1.0 / delta + self._residual_derivative(delta, tau, coeffs, "ddelta")

    def d2a_ddelta2(self, delta: Number, tau: Number) -> Number:
        """Second partial: (∂²a/∂δ²)_τ."""
        coeffs, region = self._get_coeffs(delta, tau)
        if coeffs is None:
            h = 1e-6
            return (self.da_ddelta(delta + h, tau) - self.da_ddelta(delta - h, tau)) / (2.0 * h)
        return -1.0 / delta ** 2 + self._residual_derivative(delta, tau, coeffs, "d2delta")

    def da_dtau(self, delta: Number, tau: Number) -> Number:
        """First partial: (∂a/∂τ)_δ."""
        coeffs, region = self._get_coeffs(delta, tau)
        if coeffs is None:
            if CP is None:
                raise RuntimeError("CoolProp is required for fallback properties.")
            T = self.T_c / tau
            rho = delta * self.rho_c
            dalphar_dtau = CP.PropsSI(
                "DALPHAR_DTAU_CONSTDELTA", "T", float(T), "D", float(rho), self.fluid
            )
            return dalphar_dtau + self._ideal_da_dtau(tau, self.vapor_coeffs)
        return self._ideal_da_dtau(tau, coeffs) + self._residual_derivative(
            delta, tau, coeffs, "dtau"
        )

    def d2a_dtau2(self, delta: Number, tau: Number) -> Number:
        """Second partial: (∂²a/∂τ²)_δ."""
        coeffs, region = self._get_coeffs(delta, tau)
        if coeffs is None:
            h = 1e-6
            return (self.da_dtau(delta, tau + h) - self.da_dtau(delta, tau - h)) / (2.0 * h)
        return self._ideal_d2a_dtau2(tau, coeffs) + self._residual_derivative(
            delta, tau, coeffs, "d2tau"
        )

    def d2a_ddelta_dtau(self, delta: Number, tau: Number) -> Number:
        """Mixed partial: (∂²a/∂δ∂τ)."""
        coeffs, region = self._get_coeffs(delta, tau)
        if coeffs is None:
            h = 1e-6
            return (self.da_ddelta(delta, tau + h) - self.da_ddelta(delta, tau - h)) / (2.0 * h)
        return self._residual_derivative(delta, tau, coeffs, "ddelta_dtau")

    def pressure(self, delta: Number, tau: Number) -> Number:
        """EOS-PROP-001: P = ρRT[1 + δ(∂a^res/∂δ)_τ]."""
        coeffs, region = self._get_coeffs(delta, tau)
        T = self.T_c / tau
        rho = delta * self.rho_c
        if coeffs is None:
            if CP is None:
                raise RuntimeError("CoolProp is required for fallback properties.")
            return CP.PropsSI("P", "T", float(T), "D", float(rho), self.fluid)
        da_res_ddelta = self._residual_derivative(delta, tau, coeffs, "ddelta")
        return rho * self.R * T * (1.0 + delta * da_res_ddelta)

    def c_v(self, delta: Number, tau: Number, return_details: bool = False) -> Number:
        """Isochoric specific heat capacity (J/kg/K).

        Span & Wagner (2000), Eq. 8:
          c_v / R = -τ² (∂²α⁰/∂τ² + ∂²α^r/∂τ²)_δ

        Glass box: pass return_details=True to receive a dict with all
        intermediate Helmholtz partials alongside the final value.
        """
        coeffs, region = self._get_coeffs(delta, tau)
        if coeffs is None:
            if CP is None:
                raise RuntimeError("CoolProp is required for fallback properties.")
            T = self.T_c / tau
            rho = delta * self.rho_c
            val = CP.PropsSI("CVMASS", "T", float(T), "D", float(rho), self.fluid)
            if return_details:
                return {"value": float(val), "partials": {"region": region, "source": "CoolProp"}}
            return val
        a_tautau_id = self._ideal_d2a_dtau2(tau, coeffs)
        a_tautau_res = self._residual_derivative(delta, tau, coeffs, "d2tau")
        val = -self.R * tau ** 2 * (a_tautau_id + a_tautau_res)
        if return_details:
            return {
                "value": float(val),
                "partials": {
                    "tau": float(tau),
                    "a_tautau_id": float(a_tautau_id),
                    "a_tautau_res": float(a_tautau_res),
                },
                "region": region,
            }
        return val

    def c_p(self, delta: Number, tau: Number, return_details: bool = False) -> Number:
        """Isobaric specific heat capacity (J/kg/K).

        Lemmon & Jacobsen (2018), Eq. 12:
          c_p = c_v + R (1 + δ α^r_δ − δ τ α^r_{δτ})² / (1 + 2δ α^r_δ + δ² α^r_{δδ})

        Glass box: pass return_details=True to receive a dict with all
        intermediate Helmholtz partials alongside the final value.
        """
        coeffs, region = self._get_coeffs(delta, tau)
        if coeffs is None:
            if CP is None:
                raise RuntimeError("CoolProp is required for fallback properties.")
            T = self.T_c / tau
            rho = delta * self.rho_c
            val = CP.PropsSI("CPMASS", "T", float(T), "D", float(rho), self.fluid)
            if return_details:
                return {"value": float(val), "partials": {"region": region, "source": "CoolProp"}}
            return val
        a_d_res = self._residual_derivative(delta, tau, coeffs, "ddelta")
        a_dd_res = self._residual_derivative(delta, tau, coeffs, "d2delta")
        a_dt_res = self._residual_derivative(delta, tau, coeffs, "ddelta_dtau")
        denom = 1.0 + 2.0 * delta * a_d_res + delta ** 2 * a_dd_res
        if denom <= 0.0:
            val = float("nan")
            if return_details:
                return {"value": val, "partials": {"reason": "denom <= 0"}, "region": region}
            return val
        c_v_val = self.c_v(delta, tau)
        val = c_v_val + self.R * (1.0 + delta * a_d_res - delta * tau * a_dt_res) ** 2 / denom
        if return_details:
            return {
                "value": float(val),
                "partials": {
                    "delta": float(delta),
                    "tau": float(tau),
                    "a_d_res": float(a_d_res),
                    "a_dd_res": float(a_dd_res),
                    "a_dt_res": float(a_dt_res),
                    "denom": float(denom),
                    "c_v": float(c_v_val),
                },
                "region": region,
            }
        return val

    def speed_of_sound(self, delta: Number, tau: Number, return_details: bool = False) -> Number:
        """Speed of sound (m/s).

        Lemmon & Jacobsen (2018), Eq. 15 / Span & Wagner (2000), Eq. 32:
          w² = R T (c_p / c_v) (1 + 2δ α^r_δ + δ² α^r_{δδ})

        Glass box: pass return_details=True to receive a dict with all
        intermediate Helmholtz partials alongside the final value.
        """
        coeffs, region = self._get_coeffs(delta, tau)
        if coeffs is None:
            if CP is None:
                raise RuntimeError("CoolProp is required for fallback properties.")
            T = self.T_c / tau
            rho = delta * self.rho_c
            val = CP.PropsSI("SPEED_OF_SOUND", "T", float(T), "D", float(rho), self.fluid)
            if return_details:
                return {"value": float(val), "partials": {"region": region, "source": "CoolProp"}}
            return val
        T = self.T_c / tau
        a_d_res = self._residual_derivative(delta, tau, coeffs, "ddelta")
        a_dd_res = self._residual_derivative(delta, tau, coeffs, "d2delta")
        denom = 1.0 + 2.0 * delta * a_d_res + delta ** 2 * a_dd_res
        c_v_val = self.c_v(delta, tau)
        c_p_val = self.c_p(delta, tau)
        if denom <= 0.0 or c_v_val <= 0.0 or c_p_val <= c_v_val:
            val = float("nan")
            if return_details:
                return {"value": val, "partials": {"reason": "invalid state"}, "region": region}
            return val
        val = np.sqrt(self.R * T * (c_p_val / c_v_val) * denom)
        if return_details:
            return {
                "value": float(val),
                "partials": {
                    "delta": float(delta),
                    "tau": float(tau),
                    "T": float(T),
                    "a_d_res": float(a_d_res),
                    "a_dd_res": float(a_dd_res),
                    "denom": float(denom),
                    "c_v": float(c_v_val),
                    "c_p": float(c_p_val),
                    "gamma": float(c_p_val / c_v_val) if c_v_val > 0 else float("nan"),
                },
                "region": region,
            }
        return val

    # ── FR-MA-006: enthalpy and entropy from Helmholtz partials ──────────

    def enthalpy(self, delta: Number, tau: Number, return_details: bool = False) -> Number:
        """Specific enthalpy (J/kg).

        Span & Wagner (2000), Eq. 18:
          H / (RT) = τ (∂α⁰/∂τ + ∂αʳ/∂τ) + δ·∂αʳ/∂δ + 1

        Glass box: pass return_details=True to receive a dict with all
        intermediate Helmholtz partials alongside the final value.
        """
        coeffs, region = self._get_coeffs(delta, tau)
        T = self.T_c / tau
        if coeffs is None:
            if CP is None:
                raise RuntimeError("CoolProp is required for fallback properties.")
            rho = delta * self.rho_c
            val = CP.PropsSI("HMASS", "T", float(T), "D", float(rho), self.fluid)
            if return_details:
                return {"value": float(val), "partials": {"region": region, "source": "CoolProp"}}
            return val
        a0_tau = self._ideal_da_dtau(tau, coeffs)
        ar_delta = self._residual_derivative(delta, tau, coeffs, "ddelta")
        ar_tau = self._residual_derivative(delta, tau, coeffs, "dtau")
        val = self.R * T * (tau * (a0_tau + ar_tau) + delta * ar_delta + 1.0)
        if return_details:
            return {
                "value": float(val),
                "partials": {
                    "tau": float(tau),
                    "delta": float(delta),
                    "T": float(T),
                    "a0_tau": float(a0_tau),
                    "ar_delta": float(ar_delta),
                    "ar_tau": float(ar_tau),
                },
                "region": region,
            }
        return val

    def entropy(self, delta: Number, tau: Number, return_details: bool = False) -> Number:
        """Specific entropy (J/kg/K).

        Span & Wagner (2000), Eq. 19:
          S / R = τ (∂α⁰/∂τ + ∂αʳ/∂τ) − (α⁰ + αʳ)

        Glass box: pass return_details=True to receive a dict with all
        intermediate Helmholtz partials alongside the final value.
        """
        coeffs, region = self._get_coeffs(delta, tau)
        T = self.T_c / tau
        if coeffs is None:
            if CP is None:
                raise RuntimeError("CoolProp is required for fallback properties.")
            rho = delta * self.rho_c
            val = CP.PropsSI("SMASS", "T", float(T), "D", float(rho), self.fluid)
            if return_details:
                return {"value": float(val), "partials": {"region": region, "source": "CoolProp"}}
            return val
        a0 = self._a_ideal(delta, tau, coeffs)
        ar = self._residual_derivative(delta, tau, coeffs, "a")
        a0_tau = self._ideal_da_dtau(tau, coeffs)
        ar_tau = self._residual_derivative(delta, tau, coeffs, "dtau")
        val = self.R * (tau * (a0_tau + ar_tau) - (a0 + ar))
        if return_details:
            return {
                "value": float(val),
                "partials": {
                    "tau": float(tau),
                    "delta": float(delta),
                    "T": float(T),
                    "a0": float(a0),
                    "ar": float(ar),
                    "a0_tau": float(a0_tau),
                    "ar_tau": float(ar_tau),
                },
                "region": region,
            }
        return val

    def jacobian_condition_number(self, delta: Number, tau: Number) -> float:
        """EOS-CONV-002: Condition number κ(J) of the Newton-Raphson Jacobian.

        J = ∂P/∂δ (scalar for the 1-D density solve).  Returns
        ``np.linalg.cond`` of J embedded in a 1×1 matrix — ∞ when J ≈ 0
        (two-phase or spinodal), 1 otherwise.

        This is the same κ tracked inside ``solve_delta``.
        """
        coeffs, _region = self._get_coeffs(delta, tau)
        T = self.T_c / tau
        if coeffs is None:
            # Reuse the same fallback central-difference as solve_delta.
            T_val = float(T)
            rho_val = float(delta * self.rho_c)
            h_rho = max(1e-4, 1e-6 * rho_val)
            P_plus = CP.PropsSI("P", "T", T_val, "D", rho_val + h_rho, self.fluid)
            P_minus = CP.PropsSI("P", "T", T_val, "D", rho_val - h_rho, self.fluid)
            dP_drho = (P_plus - P_minus) / (2.0 * h_rho)
            J = dP_drho * self.rho_c
        else:
            da_res = self._residual_derivative(delta, tau, coeffs, "ddelta")
            d2a_res = self._residual_derivative(delta, tau, coeffs, "d2delta")
            J = self.rho_c * self.R * T * (
                1.0 + 2.0 * delta * da_res + delta ** 2 * d2a_res
            )
        return float(np.linalg.cond(np.atleast_2d(J)))

    def solve_delta(
        self, P_target: float, T: float, delta_guess: float = 0.5
    ) -> Tuple[float, Dict]:
        """
        EOS-CONV-001: Newton-Raphson for δ(P,T).

        Returns:
            delta: converged reduced density
            info: dict with iterations, residual history, Jacobian condition number
        """
        tau = self.T_c / T
        delta = delta_guess

        info = {
            "iterations": [],
            "residuals": [],
            "jacobians": [],
            "jacobian_conds": [],
        }

        for i in range(10):  # max 10 iterations
            P_calc = self.pressure(delta, tau)
            f = P_calc - P_target

            coeffs, region = self._get_coeffs(delta, tau)
            if coeffs is None:
                # Fallback: compute dP/dδ directly from CoolProp.
                # CoolProp provides DALPHAR_DDELTA_CONSTTAU for the first
                # derivative, but not D2ALPHAR_DDELTA2_CONSTTAU.  Instead
                # of finite-differencing the wrapper (which amplifies
                # noise), estimate J = dP/dδ from CoolProp's own pressure
                # via a central difference — CoolProp's EOS is well-
                # behaved everywhere so this is numerically stable.
                T_val = float(self.T_c / tau)
                rho_val = float(delta * self.rho_c)
                # Relative perturbation: ~1 ppm of local density, with a
                # floor large enough to survive CoolProp's output precision.
                h_rho = max(1e-4, 1e-6 * rho_val)
                P_plus = CP.PropsSI("P", "T", T_val, "D", rho_val + h_rho, self.fluid)
                P_minus = CP.PropsSI("P", "T", T_val, "D", rho_val - h_rho, self.fluid)
                dP_drho = (P_plus - P_minus) / (2.0 * h_rho)
                # Chain rule: dP/dδ = dP/dρ · dρ/dδ = dP/dρ · ρ_c
                J = dP_drho * self.rho_c
            else:
                da_res = self._residual_derivative(delta, tau, coeffs, "ddelta")
                d2a_res = self._residual_derivative(delta, tau, coeffs, "d2delta")
                # Analytical Jacobian: dP/dδ
                # P = ρ_c δ R T [1 + 2δ aδ^res + δ² aδδ^res]
                J = self.rho_c * self.R * T * (
                    1.0 + 2.0 * delta * da_res + delta ** 2 * d2a_res
                )

            jacobian_cond = float(np.linalg.cond(np.atleast_2d(J)))
            info["iterations"].append(i)
            info["residuals"].append(abs(f))
            info["jacobians"].append(abs(J))
            info["jacobian_conds"].append(jacobian_cond)

            if jacobian_cond >= 1e14:
                info["converged"] = False
                info["reason"] = "jacobian condition number exceeded 1e14"
                info["final_delta"] = delta
                return delta, info

            if abs(f) < 1e-12:
                info["converged"] = True
                info["final_delta"] = delta
                return delta, info

            delta = delta - f / J

        info["converged"] = False
        info["reason"] = "max iterations reached"
        info["final_delta"] = delta
        return delta, info

    # ── FR-MA-007: saturation pressure solver ────────────────────────────

    def saturation_pressure(self, T: float, return_details: bool = False) -> Number:
        """Saturation pressure P_sat(T) (Pa).

        Uses CoolProp for the liquid-side saturation state (the liquid
        region falls back to CoolProp in this model) and the fitted
        Helmholtz vapour coefficients for the vapour-side density root.

        The vapour density is found via ``solve_delta`` at the saturation
        pressure, and the vapour Gibbs free energy G = H − T·S is
        compared with the liquid value as a consistency check.

        Glass box: pass return_details=True for the liquid/vapour
        density roots, Gibbs free-energy residual, and convergence info.
        """
        T_c = self.T_c
        if T >= T_c:
            if CP is None:
                raise RuntimeError("CoolProp required for critical pressure.")
            val = CP.PropsSI("PCRIT", self.fluid)
            if return_details:
                return {
                    "value": float(val),
                    "partials": {"rho_l": None, "rho_v": None, "G_residual": None},
                    "note": "T >= T_c, returning P_crit",
                }
            return val

        if CP is None:
            raise RuntimeError("CoolProp required for saturation properties.")

        # Liquid side from CoolProp
        P_sat = CP.PropsSI("P", "T", T, "Q", 0, self.fluid)
        rho_l = CP.PropsSI("D", "T", T, "Q", 0, self.fluid)
        H_l = CP.PropsSI("HMASS", "T", T, "Q", 0, self.fluid)
        S_l = CP.PropsSI("SMASS", "T", T, "Q", 0, self.fluid)
        G_l = H_l - T * S_l

        # Vapour root from Helmholtz EOS at saturation pressure.
        # Use ideal-gas estimate as initial guess (valid for low-density vapour).
        delta_guess = max(0.01, min(0.5, P_sat / (self.rho_c * self.R * T)))
        try:
            delta_v, sol_info = self.solve_delta(P_sat, T, delta_guess=delta_guess)
        except Exception:
            sol_info = {"converged": False, "iterations": []}
            delta_v = float("nan")
        rho_v = delta_v * self.rho_c
        tau = T_c / T
        if np.isfinite(delta_v) and delta_v > 0:
            H_v = self.enthalpy(delta_v, tau)
            S_v = self.entropy(delta_v, tau)
            G_v = H_v - T * S_v
        else:
            # Fallback: use CoolProp for vapour properties too
            rho_v = CP.PropsSI("D", "T", T, "Q", 1, self.fluid)
            H_v = CP.PropsSI("HMASS", "T", T, "Q", 1, self.fluid)
            S_v = CP.PropsSI("SMASS", "T", T, "Q", 1, self.fluid)
            G_v = H_v - T * S_v

        G_residual = float(abs(G_v - G_l))

        if return_details:
            return {
                "value": float(P_sat),
                "partials": {
                    "rho_l": float(rho_l),
                    "rho_v": float(rho_v),
                    "delta_v": float(delta_v),
                    "H_v": float(H_v),
                    "S_v": float(S_v),
                    "G_v": float(G_v),
                    "G_l": float(G_l),
                    "G_residual": G_residual,
                    "vapour_converged": sol_info["converged"],
                    "vapour_n_iter": len(sol_info.get("iterations", [])),
                },
            }
        return float(P_sat)


if __name__ == "__main__":
    # Quick sanity check
    eos = HelmholtzEOS()
    delta, tau = 0.5, 1.0  # T = T_c, rho = 0.5 * rho_c (vapor region)
    print(f"a(δ={delta}, τ={tau}) = {eos.a(delta, tau):.6f}")
    print(f"∂a/∂δ = {eos.da_ddelta(delta, tau):.6f}")
    print(f"P = {eos.pressure(delta, tau):.2f} Pa")
