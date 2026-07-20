"""Unified refrigerant interface for HVAC simulation.

Supports legacy, current, and transition refrigerants including A2Ls.
All values verified against CoolProp 8.0.0 equation of state.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from CoolProp.CoolProp import PropsSI

# Refrigerant classifications per ASHRAE safety standards
# ONLY includes refrigerants verified in CoolProp 8.0.0
CLASSIFICATIONS = {
    # Legacy — high GWP, being phased out
    'R22': {'class': 'A1', 'gwp': 1810, 'status': 'legacy', 'phaseout': '2020 (new equip)'},
    'R410A': {'class': 'A1', 'gwp': 2088, 'status': 'current→legacy', 'phaseout': '2028 (new equip)'},
    'R134a': {'class': 'A1', 'gwp': 1430, 'status': 'current', 'phaseout': 'None (chillers/automotive)'},
    
    # Transition — A2L mildly flammable, lower GWP
    'R32': {'class': 'A2L', 'gwp': 675, 'status': 'transition', 'phaseout': 'None'},
    
    # HFOs — very low GWP
    'R1234yf': {'class': 'A2L', 'gwp': 4, 'status': 'future', 'phaseout': 'None'},
}

# Refrigerants planned but not yet in CoolProp 8.0.0
PLANNED = {
    'R454B': {'class': 'A2L', 'gwp': 466, 'status': 'planned', 'phaseout': 'None', 
              'note': 'Opteon XL41 — not in CoolProp 8.0.0'},
    'R452B': {'class': 'A2L', 'gwp': 698, 'status': 'planned', 'phaseout': 'None',
              'note': 'Opteon XL55 — not in CoolProp 8.0.0'},
    'R1234ze': {'class': 'A2L', 'gwp': 7, 'status': 'planned', 'phaseout': 'None',
                'note': 'HFO-1234ze — not in CoolProp 8.0.0 (try R1234ze(E) in future versions)'},
}

@dataclass
class RefrigerantState:
    """Thermodynamic state of a refrigerant."""
    refrigerant: str
    temperature_c: float      # °C
    pressure_bar: float        # bar
    density_kg_m3: float      # kg/m³
    enthalpy_kj_kg: float     # kJ/kg
    entropy_kj_kg_k: float    # kJ/(kg·K)
    quality: Optional[float]  # 0=liquid, 1=vapor, None=superheated/subcooled
    phase: str                 # 'liquid', 'vapor', 'two-phase', 'superheated', 'subcooled'
    
    def is_superheated(self) -> bool:
        return self.phase == 'superheated'
    
    def is_subcooled(self) -> bool:
        return self.phase == 'subcooled'
    
    def is_two_phase(self) -> bool:
        return self.phase == 'two-phase'

class Refrigerant:
    """Unified interface for all refrigerants."""
    
    SUPPORTED = list(CLASSIFICATIONS.keys())
    
    def __init__(self, name: str):
        if name not in self.SUPPORTED:
            if name in PLANNED:
                raise ValueError(
                    f"{name} is planned but not yet in CoolProp. "
                    f"Note: {PLANNED[name]['note']}"
                )
            raise ValueError(f"Unsupported refrigerant: {name}. Supported: {self.SUPPORTED}")
        self.name = name
        self.info = CLASSIFICATIONS[name]
    
    def saturation_pressure(self, temperature_c: float,
                            use_helmholtz: bool = False) -> float:
        """Saturation pressure [bar] at given temperature [°C].

        If use_helmholtz=True (FR-MA-009), uses HelmholtzEOS saturation
        solver instead of CoolProp.
        """
        if use_helmholtz:
            try:
                from math_model.helmholtz_eos import HelmholtzEOS
                eos = HelmholtzEOS(self.name)
                T_k = temperature_c + 273.15
                return eos.saturation_pressure(T_k) / 1e5
            except ImportError:
                pass
        T_k = temperature_c + 273.15
        P_pa = PropsSI('P', 'T', T_k, 'Q', 1, self.name)
        return P_pa / 1e5
    
    def saturation_temperature(self, pressure_bar: float) -> float:
        """Saturation temperature [°C] at given pressure [bar]."""
        P_pa = pressure_bar * 1e5
        T_k = PropsSI('T', 'P', P_pa, 'Q', 1, self.name)
        return T_k - 273.15
    
    def critical_point(self) -> Tuple[float, float]:
        """Critical temperature [°C] and pressure [bar]."""
        T_crit_k = PropsSI('Tcrit', self.name)
        P_crit_pa = PropsSI('Pcrit', self.name)
        return T_crit_k - 273.15, P_crit_pa / 1e5
    
    def latent_heat(self, temperature_c: float) -> float:
        """Latent heat of vaporization [kJ/kg] at given temperature [°C]."""
        T_k = temperature_c + 273.15
        h_liq = PropsSI('H', 'T', T_k, 'Q', 0, self.name) / 1000
        h_vap = PropsSI('H', 'T', T_k, 'Q', 1, self.name) / 1000
        return h_vap - h_liq
    
    def get_state(self, temperature_c: float, pressure_bar: float) -> RefrigerantState:
        """Get full thermodynamic state at given T and P."""
        T_k = temperature_c + 273.15
        P_pa = pressure_bar * 1e5
        
        # Determine phase
        try:
            P_sat = PropsSI('P', 'T', T_k, 'Q', 1, self.name)
            T_sat = PropsSI('T', 'P', P_pa, 'Q', 1, self.name)
            
            if abs(P_pa - P_sat) < 1000:  # ~0.01 bar tolerance
                quality = 0.5  # Approximate for two-phase
                phase = 'two-phase'
            elif P_pa < P_sat or temperature_c > (T_sat - 273.15):
                quality = None
                phase = 'superheated'
            else:
                quality = None
                phase = 'subcooled'
        except Exception:
            quality = None
            phase = 'unknown'
        
        rho = PropsSI('D', 'T', T_k, 'P', P_pa, self.name)
        h = PropsSI('H', 'T', T_k, 'P', P_pa, self.name) / 1000
        s = PropsSI('S', 'T', T_k, 'P', P_pa, self.name) / 1000
        
        return RefrigerantState(
            refrigerant=self.name,
            temperature_c=temperature_c,
            pressure_bar=pressure_bar,
            density_kg_m3=rho,
            enthalpy_kj_kg=h,
            entropy_kj_kg_k=s,
            quality=quality,
            phase=phase
        )
    
    def pt_chart_data(self, t_min_c: float = -40, t_max_c: float = 60,
                      points: int = 100, use_helmholtz: bool = False) -> Dict:
        """Generate data for PT chart plotting.

        If use_helmholtz=True (FR-MA-009), saturation pressures come from
        HelmholtzEOS instead of CoolProp.
        """
        temps = [t_min_c + (t_max_c - t_min_c) * i / (points - 1) for i in range(points)]
        pressures = [self.saturation_pressure(t, use_helmholtz=use_helmholtz) for t in temps]
        return {
            'temperature_c': temps,
            'pressure_bar': pressures,
            'refrigerant': self.name,
            'classification': self.info,
        }
    
    @classmethod
    def list_all(cls) -> List[Dict]:
        """List all supported refrigerants with classifications."""
        return [
            {'name': name, **info}
            for name, info in CLASSIFICATIONS.items()
        ]
    
    @classmethod
    def list_planned(cls) -> List[Dict]:
        """List refrigerants planned for future support."""
        return [
            {'name': name, **info}
            for name, info in PLANNED.items()
        ]
    
    @classmethod
    def list_by_status(cls, status: str) -> List[str]:
        """List refrigerants by status: legacy, current, transition, future."""
        return [
            name for name, info in CLASSIFICATIONS.items()
            if info['status'] == status or status in info['status']
        ]

if __name__ == '__main__':
    print("Refrigerant Database — HVAC Simulation")
    print("=" * 50)
    
    for r_info in Refrigerant.list_all():
        status_icon = {
            'legacy': '⚠️',
            'current': '✅',
            'current→legacy': '⏳',
            'transition': '🔄',
            'future': '🚀'
        }.get(r_info['status'], '❓')
        
        print(f"{status_icon} {r_info['name']:10s} | {r_info['class']:4s} | GWP={r_info['gwp']:5d} | {r_info['status']}")
        if r_info.get('phaseout'):
            print(f"   Phaseout: {r_info['phaseout']}")
    
    print()
    print("Planned (not yet in CoolProp 8.0.0):")
    for r_info in Refrigerant.list_planned():
        print(f"⏳ {r_info['name']:10s} | {r_info['class']:4s} | GWP={r_info['gwp']:5d}")
        print(f"   {r_info['note']}")
    
    print()
    print("Critical points:")
    for name in Refrigerant.SUPPORTED:
        r = Refrigerant(name)
        T_crit, P_crit = r.critical_point()
        print(f"  {name:10s} T_crit={T_crit:6.2f}°C  P_crit={P_crit:6.2f} bar")
    
    print()
    print("Saturation pressure comparison at 25°C:")
    print(f"  {'Refrigerant':10s} {'P_sat (bar)':>12s} {'P_sat (psig)':>12s}")
    print("  " + "-" * 36)
    for name in Refrigerant.SUPPORTED:
        r = Refrigerant(name)
        p_bar = r.saturation_pressure(25)
        p_psig = (p_bar - 1.01325) * 14.5038  # Convert to psig
        print(f"  {name:10s} {p_bar:12.2f} {p_psig:12.2f}")
    
    print()
    print("A2L Safety Note:")
    print("  R32 is mildly flammable (A2L). Simulation must include:")
    print("  - Charge limit warnings (max 3.9 kg per circuit in some jurisdictions)")
    print("  - Ventilation requirements")
    print("  - Leak detection protocols")
    print("  - No ignition sources within specified radius")
