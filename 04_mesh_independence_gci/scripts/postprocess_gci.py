#!/usr/bin/env python3
"""
Grid Convergence Index (GCI) & Verification Script for Differentially Heated Cavity
Follows the ASME V&V 20-2009 Standard & Roache (1998) Method.
Evaluates 3 systematically refined meshes:
  - Grid 3 (Coarse): 50x50 (h3 = 0.02 m, N3 = 2,500)
  - Grid 2 (Medium): 100x100 (h2 = 0.01 m, N2 = 10,000)
  - Grid 1 (Fine):   200x200 (h1 = 0.005 m, N1 = 40,000)
Refinement ratio r = 2.0 (uniform)
"""

import os
import sys
import glob
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Styling configuration
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['lines.linewidth'] = 2.0

COLORS = {
    'coarse': '#e74c3c',    # Red/Coral
    'medium': '#f39c12',    # Orange
    'fine': '#27ae60',      # Green
    'extrap': '#2980b9',    # Blue
    'benchmark': '#8e44ad', # Purple
    'dark': '#2c3e50'       # Navy/Slate
}

def parse_foam_residuals(log_file):
    """Parse log.foam to extract iteration history of residuals."""
    if not os.path.exists(log_file):
        return pd.DataFrame()
        
    iterations = []
    current_time = 0
    res_data = []
    
    time_pat = re.compile(r"^Time = (\d+)")
    res_pat = re.compile(r"Solving for (Ux|Uy|T|p_rgh), Initial residual = ([\d\.e\-\+]+)")
    
    with open(log_file, 'r') as f:
        curr_step = {}
        for line in f:
            tm = time_pat.match(line)
            if tm:
                if curr_step and 'Time' in curr_step:
                    res_data.append(curr_step)
                current_time = int(tm.group(1))
                curr_step = {'Time': current_time}
            
            rm = res_pat.search(line)
            if rm:
                var = rm.group(1)
                val = float(rm.group(2))
                curr_step[var] = val
        if curr_step and 'Time' in curr_step:
            res_data.append(curr_step)
            
    return pd.DataFrame(res_data)

def get_latest_sampled_csv(case_dir, function_name, file_pattern):
    """Find and load the latest time CSV file from postProcessing."""
    search_path = os.path.join(case_dir, "postProcessing", function_name, "*", file_pattern)
    files = glob.glob(search_path)
    if not files:
        return None
    # Sort by time step
    def extract_time(fpath):
        parts = fpath.split(os.sep)
        try:
            return float(parts[-2])
        except (ValueError, IndexError):
            return 0.0
    latest_file = sorted(files, key=extract_time)[-1]
    return pd.read_csv(latest_file)

def compute_gci(f1, f2, f3, r=2.0, Fs=1.25):
    """
    Computes ASME V&V 20 Richardson Extrapolation & GCI.
    f1 = Fine grid value
    f2 = Medium grid value
    f3 = Coarse grid value
    r  = Grid refinement ratio (r21 = r32 = r)
    Fs = Safety factor (1.25 for 3 grids)
    """
    eps21 = f2 - f1
    eps32 = f3 - f2
    
    ratio = eps32 / eps21 if abs(eps21) > 1e-12 else 1.0
    
    if ratio <= 0:
        conv_regime = "Oscillatory"
        p = 1.0
        f_ext = f1
        ea21 = abs(eps21 / f1) * 100.0 if abs(f1) > 1e-12 else 0.0
        ea32 = abs(eps32 / f2) * 100.0 if abs(f2) > 1e-12 else 0.0
        eext21 = abs((f_ext - f1) / f_ext) * 100.0 if abs(f_ext) > 1e-12 else 0.0
        gci_fine = Fs * ea21
        gci_med = Fs * ea32
        asymptotic = 1.0
    else:
        conv_regime = "Monotonic"
        p = np.log(abs(ratio)) / np.log(r)
        # Avoid unphysical singularity if p <= 0
        p = max(0.1, min(p, 5.0))
        
        denominator = (r**p) - 1.0
        f_ext = f1 + (f1 - f2) / denominator
        ea21 = abs((f1 - f2) / f1) * 100.0 if abs(f1) > 1e-12 else 0.0
        ea32 = abs((f2 - f3) / f2) * 100.0 if abs(f2) > 1e-12 else 0.0
        eext21 = abs((f_ext - f1) / f_ext) * 100.0 if abs(f_ext) > 1e-12 else 0.0
        gci_fine = (Fs * ea21) / denominator
        gci_med = (Fs * ea32 * (r**p)) / denominator
        asymptotic = gci_med / ((r**p) * gci_fine) if abs(gci_fine) > 1e-12 else 1.0

    return {
        'f_coarse': f3,
        'f_medium': f2,
        'f_fine': f1,
        'regime': conv_regime,
        'order_p': p,
        'f_extrap': f_ext,
        'ea21_pct': ea21,
        'ea32_pct': ea32,
        'eext21_pct': eext21,
        'gci_fine_pct': gci_fine,
        'gci_med_pct': gci_med,
        'asymptotic_ratio': asymptotic
    }

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    cases_dir = os.path.join(project_root, "cases")
    results_dir = os.path.join(project_root, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    print("=" * 80)
    print(" OPENFOAM MESH VERIFICATION & ASME V&V 20 GCI ANALYSIS")
    print(" Differentially Heated Cavity (2D)")
    print("=" * 80)
    
    grid_configs = [
        {'name': 'grid3_coarse', 'label': 'Coarse (50x50)', 'cells': 2500, 'h': 0.02, 'color': COLORS['coarse'], 'ls': '--'},
        {'name': 'grid2_medium', 'label': 'Medium (100x100)', 'cells': 10000, 'h': 0.01, 'color': COLORS['medium'], 'ls': '-.'},
        {'name': 'grid1_fine',   'label': 'Fine (200x200)',   'cells': 40000, 'h': 0.005, 'color': COLORS['fine'], 'ls': '-'}
    ]
    
    data = {}
    for g in grid_configs:
        cpath = os.path.join(cases_dir, g['name'])
        if not os.path.exists(cpath):
            print(f"Error: Case path {cpath} not found.")
            return
            
        print(f"-> Extracting solution data for: {g['label']} ...")
        df_y = get_latest_sampled_csv(cpath, "midPlaneY", "midY_T_U.csv")
        df_x = get_latest_sampled_csv(cpath, "midPlaneX", "midX_T_U.csv")
        df_wall = get_latest_sampled_csv(cpath, "nearHotWall", "nearWallLine_T.csv")
        df_res = parse_foam_residuals(os.path.join(cpath, "log.foam"))
        
        data[g['name']] = {
            'config': g,
            'midY': df_y,
            'midX': df_x,
            'wall': df_wall,
            'residuals': df_res
        }
        
    # Check that data is available
    if any(data[g['name']]['midY'] is None for g in grid_configs):
        print("Error: Missing sampled CSV data in one or more cases. Run cases first.")
        return

    # Physical parameters
    T_hot = 310.0
    T_cold = 290.0
    delta_T = 20.0
    L = 1.0
    nu = 1.5e-5
    Pr = 0.71
    alpha = nu / Pr

    # Extract Key Metrics per Grid
    metrics = {}
    for g in grid_configs:
        gname = g['name']
        df_y = data[gname]['midY']
        df_x = data[gname]['midX']
        df_w = data[gname]['wall']
        
        # Max vertical velocity and location
        v_max = df_y['U_1'].max()
        x_vmax = df_y.loc[df_y['U_1'].idxmax(), 'distance']
        v_star = v_max * L / alpha
        
        # Max horizontal velocity and location
        u_max = abs(df_x['U_0']).max()
        y_umax = df_x.loc[abs(df_x['U_0']).idxmax(), 'distance']
        u_star = u_max * L / alpha
        
        # Center Temperature
        center_row = df_y.iloc[(df_y['distance'] - 0.5).abs().argsort()[:1]]
        T_center = center_row['T'].values[0]
        
        # Local Nusselt number along hot wall:
        # Sampled at x = 0.005. Nu(y) = (T_hot - T(y)) / (dx * delta_T) * L
        dx_sample = 0.005
        df_w['Nu'] = (T_hot - df_w['T']) / (dx_sample * delta_T)
        Nu_avg = df_w['Nu'].mean()
        Nu_max = df_w['Nu'].max()
        
        metrics[gname] = {
            'N_cells': g['cells'],
            'h': g['h'],
            'Nu_avg': Nu_avg,
            'Nu_max': Nu_max,
            'v_max': v_max,
            'v_star': v_star,
            'x_vmax': x_vmax,
            'u_max': u_max,
            'u_star': u_star,
            'y_umax': y_umax,
            'T_center': T_center
        }
        
    # Run GCI Analysis on target quantities
    target_vars = [
        ('Average Nusselt Number (Nu_avg)', 'Nu_avg', '[-]'),
        ('Max Vertical Velocity (v_max)', 'v_max', '[m/s]'),
        ('Dimensionless v_star', 'v_star', '[-]'),
        ('Max Horizontal Velocity (u_max)', 'u_max', '[m/s]'),
        ('Dimensionless u_star', 'u_star', '[-]'),
        ('Center Temperature (T_center)', 'T_center', '[K]')
    ]
    
    gci_results = []
    for var_label, var_key, unit in target_vars:
        f1 = metrics['grid1_fine'][var_key]
        f2 = metrics['grid2_medium'][var_key]
        f3 = metrics['grid3_coarse'][var_key]
        res = compute_gci(f1, f2, f3, r=2.0, Fs=1.25)
        res['variable'] = var_label
        res['unit'] = unit
        gci_results.append(res)
        
    df_gci = pd.DataFrame(gci_results)
    
    # Save GCI Summary CSV
    csv_file = os.path.join(results_dir, "gci_summary_table.csv")
    df_gci.to_csv(csv_file, index=False)
    print(f"-> GCI summary table saved to: {csv_file}")
    
    # Generate Markdown Summary Table
    md_file = os.path.join(results_dir, "gci_summary_table.md")
    with open(md_file, "w") as f:
        f.write("# ASME V&V 20 Grid Convergence Index (GCI) Summary\n\n")
        f.write("| Variable | Unit | Coarse (50x50) | Medium (100x100) | Fine (200x200) | Extrapolated (h=0) | Apparent Order (p) | $e_a^{21}$ (%) | $GCI_{fine}$ (%) | Asymptotic Ratio ($\chi$) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for r in gci_results:
            f.write(f"| **{r['variable']}** | {r['unit']} | {r['f_coarse']:.4f} | {r['f_medium']:.4f} | {r['f_fine']:.4f} | **{r['f_extrap']:.4f}** | {r['order_p']:.2f} | {r['ea21_pct']:.2f}% | **{r['gci_fine_pct']:.2f}%** | {r['asymptotic_ratio']:.3f} |\n")
        f.write("\n*Notes: Safety Factor $F_s = 1.25$ for 3-grid study. Refinement ratio $r = 2.0$. Asymptotic ratio $\\chi \\approx 1.0$ indicates solutions reside within the asymptotic convergence regime.*\n")
    print(f"-> GCI markdown table saved to: {md_file}")
    
    # =========================================================================
    # PLOTTING
    # =========================================================================
    
    # Plot 1: Vertical Velocity Comparison along Mid-plane y = 0.5
    plt.figure(figsize=(9, 6))
    for g in grid_configs:
        df_y = data[g['name']]['midY']
        plt.plot(df_y['distance'], df_y['U_1'], label=g['label'], color=g['color'], linestyle=g['ls'])
    plt.title("Vertical Velocity Profile ($U_y$) along Midplane $y = 0.5$", pad=12)
    plt.xlabel("Horizontal Position $x$ (m)")
    plt.ylabel("Vertical Velocity $U_y$ (m/s)")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "midY_Uy_comparison.png"))
    plt.close()
    
    # Plot 2: Horizontal Velocity Comparison along Mid-plane x = 0.5
    plt.figure(figsize=(9, 6))
    for g in grid_configs:
        df_x = data[g['name']]['midX']
        plt.plot(df_x['distance'], df_x['U_0'], label=g['label'], color=g['color'], linestyle=g['ls'])
    plt.title("Horizontal Velocity Profile ($U_x$) along Midplane $x = 0.5$", pad=12)
    plt.xlabel("Vertical Position $y$ (m)")
    plt.ylabel("Horizontal Velocity $U_x$ (m/s)")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "midX_Ux_comparison.png"))
    plt.close()

    # Plot 3: Temperature Profile along Mid-plane y = 0.5
    plt.figure(figsize=(9, 6))
    for g in grid_configs:
        df_y = data[g['name']]['midY']
        plt.plot(df_y['distance'], df_y['T'], label=g['label'], color=g['color'], linestyle=g['ls'])
    plt.title("Temperature Profile ($T$) along Midplane $y = 0.5$", pad=12)
    plt.xlabel("Horizontal Position $x$ (m)")
    plt.ylabel("Temperature $T$ (K)")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "midY_T_comparison.png"))
    plt.close()

    # Plot 4: Local Nusselt Number Distribution along Hot Wall
    plt.figure(figsize=(9, 6))
    for g in grid_configs:
        df_w = data[g['name']]['wall']
        plt.plot(df_w['distance'], df_w['Nu'], label=f"{g['label']} (Avg: {metrics[g['name']]['Nu_avg']:.2f})", color=g['color'], linestyle=g['ls'])
    plt.title("Local Nusselt Number ($Nu$) Distribution along Heated Wall", pad=12)
    plt.xlabel("Vertical Position along Wall $y$ (m)")
    plt.ylabel("Local Nusselt Number $Nu(y)$")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "nu_distribution_comparison.png"))
    plt.close()

    # Plot 5: GCI Error Bands for Average Nusselt Number
    nu_res = [r for r in gci_results if r['variable'].startswith('Average Nusselt')][0]
    h_vals = [0.0, 0.005, 0.01, 0.02]
    nu_vals = [nu_res['f_extrap'], nu_res['f_fine'], nu_res['f_medium'], nu_res['f_coarse']]
    yerr = [
        0.0,
        nu_res['f_fine'] * (nu_res['gci_fine_pct'] / 100.0),
        nu_res['f_medium'] * (nu_res['gci_med_pct'] / 100.0),
        0.0
    ]
    
    plt.figure(figsize=(9, 6))
    plt.errorbar(h_vals[1:3], nu_vals[1:3], yerr=yerr[1:3], fmt='o', color=COLORS['dark'], 
                 ecolor=COLORS['fine'], elinewidth=2, capsize=6, capthick=2, label="Computed Solutions with GCI Error Bands")
    plt.plot(h_vals[3], nu_vals[3], 's', color=COLORS['coarse'], markersize=8, label="Coarse Grid (50x50)")
    plt.plot(0.0, nu_res['f_extrap'], '*', color=COLORS['extrap'], markersize=14, label=f"Richardson Extrapolated Continuum $Nu_{{ext}} = {nu_res['f_extrap']:.3f}$")
    
    # Fit line to illustrate convergence trend
    h_dense = np.linspace(0, 0.022, 100)
    p_fit = nu_res['order_p']
    C_fit = (nu_res['f_fine'] - nu_res['f_extrap']) / ((0.005)**p_fit)
    nu_fit = nu_res['f_extrap'] + C_fit * (h_dense**p_fit)
    plt.plot(h_dense, nu_fit, 'k--', alpha=0.5, label=f"Asymptotic Power Law ($O(h^{{{p_fit:.2f}}}))$")
    
    plt.title(r"Richardson Extrapolation & $GCI_{fine}$ Uncertainty Window for $\overline{Nu}$", pad=12)
    plt.xlabel("Grid Spacing $h$ (m)")
    plt.ylabel(r"Average Nusselt Number $\overline{Nu}$")
    plt.xlim(-0.002, 0.025)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "gci_error_bars_Nu.png"))
    plt.close()

    # Plot 6: GCI Error Bands for Peak Vertical Velocity
    v_res = [r for r in gci_results if r['variable'].startswith('Max Vertical Velocity')][0]
    v_vals = [v_res['f_extrap'], v_res['f_fine'], v_res['f_medium'], v_res['f_coarse']]
    v_yerr = [
        0.0,
        v_res['f_fine'] * (v_res['gci_fine_pct'] / 100.0),
        v_res['f_medium'] * (v_res['gci_med_pct'] / 100.0),
        0.0
    ]
    
    plt.figure(figsize=(9, 6))
    plt.errorbar(h_vals[1:3], v_vals[1:3], yerr=v_yerr[1:3], fmt='o', color=COLORS['dark'],
                 ecolor=COLORS['fine'], elinewidth=2, capsize=6, capthick=2, label="Computed $v_{max}$ with GCI Error Bands")
    plt.plot(h_vals[3], v_vals[3], 's', color=COLORS['coarse'], markersize=8, label="Coarse Grid (50x50)")
    plt.plot(0.0, v_res['f_extrap'], '*', color=COLORS['extrap'], markersize=14, label=f"Richardson Extrapolated $v_{{max,ext}} = {v_res['f_extrap']:.4f}$ m/s")
    
    C_fit_v = (v_res['f_fine'] - v_res['f_extrap']) / ((0.005)**v_res['order_p'])
    v_fit = v_res['f_extrap'] + C_fit_v * (h_dense**v_res['order_p'])
    plt.plot(h_dense, v_fit, 'k--', alpha=0.5, label=f"Asymptotic Power Law ($O(h^{{{v_res['order_p']:.2f}}}))$")
    
    plt.title(r"Richardson Extrapolation & $GCI_{fine}$ Uncertainty Window for $v_{max}$", pad=12)
    plt.xlabel("Grid Spacing $h$ (m)")
    plt.ylabel("Maximum Vertical Velocity $v_{max}$ (m/s)")
    plt.xlim(-0.002, 0.025)
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "gci_error_bars_velocity.png"))
    plt.close()

    # Plot 7: Residuals History Across All Grids
    plt.figure(figsize=(10, 6))
    for g in grid_configs:
        df_res = data[g['name']]['residuals']
        if not df_res.empty and 'Ux' in df_res.columns:
            plt.plot(df_res['Time'], df_res['Ux'], label=f"{g['label']} - Ux", color=g['color'], linestyle='-', alpha=0.8)
            if 'T' in df_res.columns:
                plt.plot(df_res['Time'], df_res['T'], label=f"{g['label']} - T", color=g['color'], linestyle='--', alpha=0.8)
    plt.yscale('log')
    plt.title("Residual Convergence History Across Grid Hierarchy", pad=12)
    plt.xlabel("Iteration Step")
    plt.ylabel("Initial Residual (log scale)")
    plt.grid(True, which="both", linestyle=":", alpha=0.5)
    plt.legend(ncol=2, frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "residuals_convergence.png"))
    plt.close()

    # Plot 8: Mesh Visual Comparison Diagram
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for idx, g in enumerate(grid_configs):
        ax = axes[idx]
        nx = int(np.sqrt(g['cells']))
        # Draw subset of mesh (10x10 representation or full corner)
        step = 1.0 / nx
        x_edges = np.linspace(0, 0.2, int(0.2 / step) + 1)
        y_edges = np.linspace(0, 0.2, int(0.2 / step) + 1)
        for x in x_edges:
            ax.axvline(x, color=g['color'], linewidth=0.8, alpha=0.8)
        for y in y_edges:
            ax.axhline(y, color=g['color'], linewidth=0.8, alpha=0.8)
        ax.set_xlim(0, 0.2)
        ax.set_ylim(0, 0.2)
        ax.set_title(f"{g['label']}\n$\Delta x = {g['h']}$ m ({g['cells']} cells)")
        ax.set_xlabel("x (m) [Corner Zoom]")
        ax.set_ylabel("y (m)" if idx == 0 else "")
        ax.set_aspect('equal')
    plt.suptitle("Grid Hierarchy Corner Detail (Bottom-Left Heated Wall Joint)", fontsize=14, y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "mesh_comparison.png"), bbox_inches='tight')
    plt.close()

    print("=" * 80)
    print(" GCI ANALYSIS & VERIFICATION COMPLETE")
    print(f" All publication plots generated in: {results_dir}")
    print("=" * 80)

if __name__ == "__main__":
    main()
