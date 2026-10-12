import re
import matplotlib.pyplot as plt
import os

def parse_foam_log(log_path):
    times = []
    p_rgh_res = []
    Ux_res = []
    Uy_res = []
    T_res = []
    k_res = []
    omega_res = []
    
    co_max = []
    co_mean = []
    delta_t = []
    
    current_time = None
    
    with open(log_path, 'r') as f:
        for line in f:
            # Time
            m_time = re.match(r'^Time = ([\d\.e\+\-]+)', line)
            if m_time:
                current_time = float(m_time.group(1))
                times.append(current_time)
                continue
                
            # Courant Number mean: 0.267778 max: 2.03106
            m_co = re.search(r'Courant Number mean: ([\d\.e\+\-]+) max: ([\d\.e\+\-]+)', line)
            if m_co and current_time is not None:
                # Add to the latest time, assuming it's printed before Time = ... wait
                # Actually Courant is printed BEFORE Time=... in OpenFOAM.
                co_mean.append(float(m_co.group(1)))
                co_max.append(float(m_co.group(2)))
                
            # deltaT = 0.0833333
            m_dt = re.search(r'^deltaT = ([\d\.e\+\-]+)', line)
            if m_dt and current_time is not None:
                delta_t.append(float(m_dt.group(1)))
                
            # Residuals: DILUPBiCGStab:  Solving for Ux, Initial residual = 0.00571398, Final residual = ...
            # We only want the first PIMPLE iteration's residuals for a given time step.
            # To simplify, we just grab the last seen residual for that time step or the first. 
            # Usually we plot the initial residual.
            m_res = re.search(r'Solving for ([a-zA-Z_]+), Initial residual = ([\d\.e\+\-]+)', line)
            if m_res and current_time is not None:
                field = m_res.group(1)
                res = float(m_res.group(2))
                
                # We want to match length with times. We append only if length of array is < len(times)
                if field == 'p_rgh' and len(p_rgh_res) < len(times): p_rgh_res.append(res)
                elif field == 'Ux' and len(Ux_res) < len(times): Ux_res.append(res)
                elif field == 'Uy' and len(Uy_res) < len(times): Uy_res.append(res)
                elif field == 'T' and len(T_res) < len(times): T_res.append(res)
                elif field == 'k' and len(k_res) < len(times): k_res.append(res)
                elif field == 'omega' and len(omega_res) < len(times): omega_res.append(res)
                
    # Fix lengths in case some were missed at the end
    min_len = min(len(times), len(p_rgh_res), len(Ux_res), len(Uy_res), len(T_res))
    times = times[:min_len]
    p_rgh_res = p_rgh_res[:min_len]
    Ux_res = Ux_res[:min_len]
    Uy_res = Uy_res[:min_len]
    T_res = T_res[:min_len]
    
    if len(k_res) > min_len: k_res = k_res[:min_len]
    if len(omega_res) > min_len: omega_res = omega_res[:min_len]
    if len(co_max) > min_len: co_max = co_max[:min_len]
    if len(delta_t) > min_len: delta_t = delta_t[:min_len]

    return times, p_rgh_res, Ux_res, Uy_res, T_res, k_res, omega_res, co_max, delta_t

if __name__ == "__main__":
    case_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_path = os.path.join(case_path, "log.foam")
    
    if not os.path.exists(log_path):
        print(f"Log file not found: {log_path}")
        exit(1)
        
    times, p, ux, uy, t, k, omega, co, dt = parse_foam_log(log_path)
    
    if not times:
        print("No time data found in log.foam.")
        exit(1)
        
    # Plot residuals
    plt.figure(figsize=(10, 6))
    plt.semilogy(times, p, label='p_rgh', linewidth=1.5)
    plt.semilogy(times, ux, label='Ux', linewidth=1.5)
    plt.semilogy(times, uy, label='Uy', linewidth=1.5)
    plt.semilogy(times, t, label='T', linewidth=1.5)
    if k: plt.semilogy(times[:len(k)], k, label='k', linewidth=1.5)
    if omega: plt.semilogy(times[:len(omega)], omega, label='omega', linewidth=1.5)
    
    plt.xlabel('Time (s)', fontsize=12)
    plt.ylabel('Initial Residual', fontsize=12)
    plt.title('Transient Residuals over Time (PIMPLE)', fontsize=14)
    plt.grid(True, which="both", ls="--", alpha=0.7)
    plt.legend(loc='upper right', framealpha=0.9)
    plt.tight_layout()
    
    res_dir = os.path.join(case_path, "results")
    os.makedirs(res_dir, exist_ok=True)
    plt.savefig(os.path.join(res_dir, "residuals.png"), dpi=300)
    print(f"Saved residual plot to {res_dir}/residuals.png")
    
    # Calculate Metrics
    max_co = max(co) if co else 0
    avg_dt = sum(dt)/len(dt) if dt else 0
    total_time = times[-1]
    
    metrics = f"""
# Transient Simulation Metrics
- Total Physical Time Reached: {total_time:.2f} s
- Max Courant Number Encountered: {max_co:.3f}
- Average Time Step (deltaT): {avg_dt:.4f} s
- Final T Residual: {t[-1]:.2e}
- Final Ux Residual: {ux[-1]:.2e}
"""
    with open(os.path.join(res_dir, "transient_metrics.txt"), 'w') as f:
        f.write(metrics)
    print(metrics)
