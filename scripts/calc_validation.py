import os
import pandas as pd
import numpy as np
import glob

# Resolve paths
script_dir = os.path.dirname(os.path.abspath(__file__))
case_dir = os.path.join(script_dir, "..", "case")
results_dir = os.path.join(script_dir, "..", "results")
os.makedirs(results_dir, exist_ok=True)

def get_latest_time_dir(base_dir):
    dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    time_dirs = []
    for d in dirs:
        try: time_dirs.append(float(d))
        except ValueError: pass
    return str(int(max(time_dirs))) if time_dirs else None

# Read properties
nu, pr, beta = 1.5e-5, 0.71, 0.00333333
with open(os.path.join(case_dir, "constant", "transportProperties"), "r") as f:
    for line in f:
        if line.startswith("nu "): nu = float(line.split()[1].replace(';', ''))
        elif line.startswith("Pr "): pr = float(line.split()[1].replace(';', ''))
        elif line.startswith("beta "): beta = float(line.split()[1].replace(';', ''))

alpha = nu / pr
deltaT = 20.0
g = 9.81

# Read scale for L
L = 1.0
with open(os.path.join(case_dir, "system", "blockMeshDict"), "r") as f:
    for line in f:
        if line.startswith("scale "): L *= float(line.split()[1].replace(';', ''))

Ra = (g * beta * deltaT * (L**3)) / (nu * alpha)

post_dir = os.path.join(case_dir, "postProcessing")
latest_time = get_latest_time_dir(os.path.join(post_dir, "nearHotWall"))
if not latest_time:
    print("No postProcessing data found.")
    exit(1)

# 1. Nusselt number
t_file = os.path.join(post_dir, "nearHotWall", latest_time, "nearWallLine_T.csv")
if os.path.exists(t_file):
    df_T = pd.read_csv(t_file)
    dist_wall = L / 50.0 / 2.0  # half cell width
    df_T['dTdx'] = (df_T['T'] - 310) / dist_wall
    df_T['Nu_local'] = - (L / deltaT) * df_T['dTdx']
    Nu_avg = np.trapz(df_T['Nu_local'], df_T['distance']) / L
else:
    Nu_avg = 0.0

# 2. Maximum dimensionless horizontal velocity
x_file = os.path.join(post_dir, "midPlaneX", latest_time, "midX_T_U.csv")
if os.path.exists(x_file):
    df_midX = pd.read_csv(x_file)
    df_midX['u_star'] = df_midX['U_0'] * L / alpha
    max_u_star = df_midX['u_star'].max()
    loc_max_u = df_midX.loc[df_midX['u_star'].idxmax(), 'distance'] / L
else:
    max_u_star, loc_max_u = 0.0, 0.0

# 3. Maximum dimensionless vertical velocity
y_file = os.path.join(post_dir, "midPlaneY", latest_time, "midY_T_U.csv")
if os.path.exists(y_file):
    df_midY = pd.read_csv(y_file)
    df_midY['v_star'] = df_midY['U_1'] * L / alpha
    max_v_star = df_midY['v_star'].max()
    loc_max_v = df_midY.loc[df_midY['v_star'].idxmax(), 'distance'] / L
else:
    max_v_star, loc_max_v = 0.0, 0.0

# Print results
print(f"--- Scientific Validation Report (Physical Air L={L:.4f}m) ---")
print(f"Computed Ra = {Ra:.2e}")
print(f"Nu_avg = {Nu_avg:.4f} (Benchmark: 1.118)")
print(f"u*_max = {max_u_star:.4f} at y/L = {loc_max_u:.4f} (Benchmark: 3.649)")
print(f"v*_max = {max_v_star:.4f} at x/L = {loc_max_v:.4f} (Benchmark: 3.697)")

# Save summary
summary_path = os.path.join(results_dir, "analysis_summary.txt")
with open(summary_path, "w") as f:
    f.write(f"Rayleigh Number: {Ra:.2e}\n")
    f.write(f"Nu_avg: {Nu_avg:.4f}\n")
    f.write(f"u*_max: {max_u_star:.4f}\n")
    f.write(f"v*_max: {max_v_star:.4f}\n")
print(f"Summary saved to {summary_path}")
