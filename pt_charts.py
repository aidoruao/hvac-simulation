"""Generate pressure-temperature charts for all refrigerants.

FR-TD-007: Display PT chart interactively.
Step 1: Static matplotlib charts as reference.
Step 2: Interactive Godot UI.
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from refrigerants import Refrigerant


def generate_pt_chart(refrigerant_name: str, t_min: float = -40, t_max: float = 60,
                       output_dir: str = 'assets/pt_charts'):
    """Generate and save a PT chart for a refrigerant."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    r = Refrigerant(refrigerant_name)
    data = r.pt_chart_data(t_min, t_max, points=200)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Saturation curve
    ax.plot(data['temperature_c'], data['pressure_bar'], 
            linewidth=2, color='#2E86AB', label='Saturation Curve')
    
    # Critical point
    T_crit, P_crit = r.critical_point()
    ax.axvline(x=T_crit, color='#E94F37', linestyle='--', alpha=0.5, 
               label=f'Critical Point: {T_crit:.1f}°C')
    ax.axhline(y=P_crit, color='#E94F37', linestyle='--', alpha=0.5)
    ax.plot(T_crit, P_crit, 'ro', markersize=8, label=f'Critical: {P_crit:.1f} bar')
    
    # Reference points
    ax.plot(25, r.saturation_pressure(25), 'go', markersize=8, 
            label=f'25°C: {r.saturation_pressure(25):.1f} bar')
    
    # Styling
    ax.set_xlabel('Temperature (°C)', fontsize=12)
    ax.set_ylabel('Pressure (bar)', fontsize=12)
    ax.set_title(f'Pressure-Temperature Chart — {refrigerant_name}\n'
                 f'Class: {r.info["class"]} | GWP: {r.info["gwp"]} | Status: {r.info["status"]}',
                 fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')
    
    # Safety zone shading for A2L
    if r.info['class'] == 'A2L':
        ax.axhspan(0, P_crit, alpha=0.05, color='orange', label='A2L Zone')
    
    plt.tight_layout()
    
    filename = f'{output_dir}/{refrigerant_name}_pt_chart.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filename}")
    return filename


def generate_comparison_chart(output_dir: str = 'assets/pt_charts'):
    """Generate comparison chart of all refrigerants."""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    colors = {
        'R22': '#E94F37',      # Red - legacy
        'R410A': '#F6AE2D',    # Yellow - current→legacy
        'R134a': '#2E86AB',    # Blue - current
        'R32': '#4CAF50',      # Green - transition
        'R1234yf': '#9C27B0',  # Purple - future
    }
    
    for name in Refrigerant.SUPPORTED:
        r = Refrigerant(name)
        data = r.pt_chart_data(-40, 60, points=200)
        
        ax.plot(data['temperature_c'], data['pressure_bar'],
                linewidth=2, color=colors.get(name, '#333'),
                label=f'{name} ({r.info["class"]}, GWP={r.info["gwp"]})')
    
    ax.set_xlabel('Temperature (°C)', fontsize=12)
    ax.set_ylabel('Pressure (bar)', fontsize=12)
    ax.set_title('Refrigerant Comparison — Pressure-Temperature Curves', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=9)
    
    plt.tight_layout()
    
    filename = f'{output_dir}/all_refrigerants_comparison.png'
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  Saved: {filename}")
    return filename


if __name__ == '__main__':
    print("Generating PT Charts — HVAC Simulation")
    print("=" * 50)
    
    for name in Refrigerant.SUPPORTED:
        print(f"\nGenerating {name}...")
        generate_pt_chart(name)
    
    print(f"\nGenerating comparison chart...")
    generate_comparison_chart()
    
    print(f"\n{'='*50}")
    print("All charts generated in assets/pt_charts/")
