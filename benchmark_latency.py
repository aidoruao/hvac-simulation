"""Benchmark CoolProp calculation latency.

FR-PF-001: Physics calculation latency < 1 ms per call.
"""

import time
import statistics
from CoolProp.CoolProp import PropsSI
from refrigerants import Refrigerant


def benchmark_propsi(calls: int = 1000):
    """Benchmark raw PropsSI calls."""
    times = []
    
    for _ in range(calls):
        t0 = time.perf_counter_ns()
        PropsSI('P', 'T', 298.15, 'Q', 1, 'R410A')
        t1 = time.perf_counter_ns()
        times.append((t1 - t0) / 1_000_000)  # Convert to ms
    
    return times


def benchmark_refrigerant_wrapper(calls: int = 1000):
    """Benchmark Refrigerant class wrapper."""
    r = Refrigerant('R410A')
    times = []
    
    for _ in range(calls):
        t0 = time.perf_counter_ns()
        r.saturation_pressure(25)
        t1 = time.perf_counter_ns()
        times.append((t1 - t0) / 1_000_000)
    
    return times


def benchmark_full_state(calls: int = 1000):
    """Benchmark full state calculation."""
    r = Refrigerant('R410A')
    times = []
    
    for _ in range(calls):
        t0 = time.perf_counter_ns()
        r.get_state(25, 16.52)
        t1 = time.perf_counter_ns()
        times.append((t1 - t0) / 1_000_000)
    
    return times


def report(name: str, times: list):
    """Print benchmark report."""
    mean = statistics.mean(times)
    median = statistics.median(times)
    p99 = sorted(times)[int(len(times) * 0.99)]
    p999 = sorted(times)[int(len(times) * 0.999)]
    max_val = max(times)
    
    print(f"\n{name}")
    print("-" * 50)
    print(f"  Calls:     {len(times)}")
    print(f"  Mean:      {mean:.4f} ms")
    print(f"  Median:    {median:.4f} ms")
    print(f"  P99:       {p99:.4f} ms")
    print(f"  P99.9:     {p999:.4f} ms")
    print(f"  Max:       {max_val:.4f} ms")
    
    pass_fail = "PASS" if mean < 1.0 else "FAIL"
    print(f"  FR-PF-001: {pass_fail} (target < 1.0 ms)")
    
    return mean < 1.0


if __name__ == '__main__':
    print("HVAC Simulation — Calculation Latency Benchmark")
    print("=" * 50)
    
    # Warmup
    for _ in range(100):
        PropsSI('P', 'T', 298.15, 'Q', 1, 'R410A')
    
    raw_times = benchmark_propsi(1000)
    wrapper_times = benchmark_refrigerant_wrapper(1000)
    state_times = benchmark_full_state(1000)
    
    raw_pass = report("Raw PropsSI (saturation pressure)", raw_times)
    wrapper_pass = report("Refrigerant wrapper", wrapper_times)
    state_pass = report("Full state calculation", state_times)
    
    print(f"\n{'='*50}")
    all_pass = raw_pass and wrapper_pass and state_pass
    print(f"OVERALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"Target: < 1.0 ms mean per calculation")
