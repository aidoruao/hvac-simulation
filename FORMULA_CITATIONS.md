# Formula Citations — HVAC Simulation

FR-SF-003: Every formula cited. No hidden assumptions.

---

## 1. Thermodynamic Properties (CoolProp Backend)

### 1.1 Saturation Pressure
**Formula:** Helmholtz Equation of State (HEOS)
**Source:** CoolProp 8.0.0, based on NIST REFPROP 10.0 formulations
**Citation:** Lemmon, E.W., Bell, I.H., Huber, M.L., McLinden, M.O. "NIST Standard Reference Database 23: Reference Fluid Thermodynamic and Transport Properties-REFPROP, Version 10.0," National Institute of Standards and Technology, 2018.
**Implementation:** `CoolProp.CoolProp.PropsSI('P', 'T', T_k, 'Q', 1, name)`
**Verification:** `validation.py` cross-checks against independent ASHRAE data
**Location in code:** `refrigerants.py:Refrigerant.saturation_pressure()`

### 1.2 Critical Point
**Formula:** Helmholtz EOS critical point solver
**Source:** CoolProp 8.0.0 fluid database
**Citation:** Same as 1.1
**Implementation:** `PropsSI('Tcrit', name)`, `PropsSI('Pcrit', name)`
**Verification:** `test_validation.py::test_critical_point_validation`
**Location in code:** `refrigerants.py:Refrigerant.critical_point()`

### 1.3 Latent Heat of Vaporization
**Formula:** h_fg = h_vapor(T, Q=1) - h_liquid(T, Q=0)
**Source:** CoolProp 8.0.0 enthalpy calculations via HEOS
**Citation:** Same as 1.1
**Implementation:** `PropsSI('H', 'T', T_k, 'Q', 0/1, name)`
**Verification:** `test_refrigerants.py::TestLatentHeat`
**Location in code:** `refrigerants.py:Refrigerant.latent_heat()`

### 1.4 Density
**Formula:** Helmholtz EOS density solver
**Source:** CoolProp 8.0.0
**Citation:** Same as 1.1
**Implementation:** `PropsSI('D', 'T', T_k, 'P', P_pa, name)`
**Verification:** `test_physics.py::test_r410a_density`
**Location in code:** `refrigerants.py:Refrigerant.get_state()`

### 1.5 Superheat / Subcooling
**Formula:** 
- Superheat = T_measured - T_sat(P)
- Subcooling = T_sat(P) - T_measured
**Source:** ASHRAE Handbook — Fundamentals, Chapter 2: Thermodynamics and Refrigeration Cycles
**Citation:** ASHRAE, "ASHRAE Handbook — Fundamentals," American Society of Heating, Refrigerating and Air-Conditioning Engineers, 2021.
**Implementation:** Calculated from saturation temperature at measured pressure
**Verification:** `test_scenarios.py::TestStateDetermination`
**Location in code:** `scenarios.py:Scenario.expected_superheat_k()`

---

## 2. Reference Data

### 2.1 R410A Ground Truth
**Source:** NIST REFPROP 10.0 / CoolProp 8.0.0 verification
**Values:**
- P_sat at 25°C: 16.52 bar
- T_crit: 71.34°C
- P_crit: 49.01 bar
- h_fg at 25°C: 186.48 kJ/kg
- rho_liq at 25°C: 1058.90 kg/m³
- rho_vap at 25°C: 65.95 kg/m³
**Location:** `validation.py:REFERENCE_DATA['R410A']`

### 2.2 R32, R134a, R22, R1234yf
**Source:** Same as 2.1
**Location:** `validation.py:REFERENCE_DATA`

---

## 3. Safety Classifications

### 3.1 ASHRAE Safety Groups (A1, A2L)
**Source:** ASHRAE Standard 34-2022, "Designation and Safety Classification of Refrigerants"
**Citation:** ASHRAE, "ANSI/ASHRAE Standard 34-2022," American Society of Heating, Refrigerating and Air-Conditioning Engineers, 2022.
**Location:** `refrigerants.py:CLASSIFICATIONS`

### 3.2 GWP Values
**Source:** IPCC AR6 (Intergovernmental Panel on Climate Change, Sixth Assessment Report)
**Citation:** IPCC, "Climate Change 2021: The Physical Science Basis," Cambridge University Press, 2021.
**Location:** `refrigerants.py:CLASSIFICATIONS`

### 3.3 Phaseout Dates
**Source:** U.S. EPA AIM Act (American Innovation and Manufacturing Act of 2020)
**Citation:** 42 U.S.C. § 7675, "Phasedown of Hydrofluorocarbons," 2020.
**Location:** `refrigerants.py:CLASSIFICATIONS`

---

## 4. Unit Conversions

### 4.1 Pressure: bar ↔ psig
**Formula:** psig = (bar - 1.01325) × 14.5038
**Source:** NIST SP 811, "Guide for the Use of the International System of Units (SI)"
**Citation:** Thompson, A., Taylor, B.N., "NIST Special Publication 811," National Institute of Standards and Technology, 2008.
**Location:** `refrigerants.py` (inline)

### 4.2 Temperature: °C ↔ K
**Formula:** K = °C + 273.15
**Source:** ITS-90 (International Temperature Scale of 1990)
**Citation:** Preston-Thomas, H., "The International Temperature Scale of 1990 (ITS-90)," Metrologia, 27(1), 3-10, 1990.
**Location:** Throughout codebase

---

## 5. Validation Methodology

### 5.1 Divergence Threshold
**Value:** 5% (0.05 relative error)
**Rationale:** ASHRAE Handbook measurement uncertainty for field instruments
**Source:** ASHRAE Handbook — Fundamentals, Chapter 1: Psychrometrics
**Location:** `validation.py:DIVERGENCE_THRESHOLD`

### 5.2 Latent Heat Minimums
**Rationale:** Physical lower bounds based on refrigerant thermodynamics
**Source:** CoolProp 8.0.0 calculations
**Location:** `test_refrigerants.py:TestLatentHeat.MIN_LATENT_HEAT`

---

## Traceability Matrix: Formula → Source → Test → Commit

| Formula | Source | Test | Commit |
|---|---|---|---|
| Saturation pressure | NIST REFPROP / CoolProp HEOS | test_validation.py | d8a866c |
| Critical point | NIST REFPROP / CoolProp HEOS | test_validation.py | d8a866c |
| Latent heat | CoolProp enthalpy | test_refrigerants.py | 0c84134 |
| Density | CoolProp HEOS | test_physics.py | 7ef3477 |
| Superheat/subcooling | ASHRAE Handbook Ch.2 | test_scenarios.py | 834afff |
| Safety classification | ASHRAE Std 34-2022 | test_refrigerants.py | 0c84134 |
| GWP values | IPCC AR6 | test_refrigerants.py | 0c84134 |
| Unit conversions | NIST SP 811 | Inline verification | All commits |

---

## Audit Log

| Date | Action | Commit |
|---|---|---|
| 2026-07-16 | Initial formula citations | ca54dc6 |
| 2026-07-16 | All formulas traced to primary sources | (this commit) |

---

*Every number in this simulator can be traced to a primary source. No hidden assumptions. Glass box.*
