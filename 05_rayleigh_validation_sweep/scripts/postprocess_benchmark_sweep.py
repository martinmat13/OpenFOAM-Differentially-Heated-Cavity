#!/usr/bin/env python3
"""
Rayleigh Number Parameter Sweep & De Vahl Davis (1983) Benchmark Validation
Evaluates canonical natural convection across Ra = 1e3, 1e4, 1e5, 1e6.
Extracts:
  - Average Nusselt number (Nu_avg)
  - Maximum horizontal velocity (u_max*) and coordinate y/L
  - Maximum vertical velocity (v_max*) and coordinate x/L
Generates comparison plots and validation tables.
"""

import os
import glob
import json
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pyvista as pv

os.environ["PYVISTA_OFF_SCREEN"] = "true"

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

RA_CONFIGS = [
    {'name': 'Ra_1e3', 'Ra': 1e3, 'label': 'Ra = $10^3$', 'nu': 0.02154855, 'alpha': 0.03035007, 'color': '#3498db', 'ls': '-'},
    {'name': 'Ra_1e4', 'Ra': 1e4, 'label': 'Ra = $10^4$', 'nu': 0.00681425, 'alpha': 0.00959754, 'color': '#2ecc71', 'ls': '--'},
    {'name': 'Ra_1e5', 'Ra': 1e5, 'label': 'Ra = $10^5$', 'nu': 0.00215485, 'alpha': 0.00303501, 'color': '#f39c12', 'ls': '-.'},
    {'name': 'Ra_1e6', 'Ra': 1e6, 'label': 'Ra = $10^6$', 'nu': 0.000681425, 'alpha': 0.000959754, 'color': '#e74c3c', 'ls': ':'}
]

def get_latest_sampled_csv(case_dir, function_name, file_pattern):
    search_path = os.path.join(case_dir, "postProcessing", function_name, "*", file_pattern)
    files = glob.glob(search_path)
    if not files:
        return None
    def extract_time(fpath):
        try:
            return float(fpath.split(os.sep)[-2])
        except (ValueError, IndexError):
            return 0.0
    latest_file = sorted(files, key=extract_time)[-1]
    return pd.read_csv(latest_file)

def extract_pyvista_mesh(case_dir):
    foam_file = os.path.join(case_dir, "case.foam")
    if not os.path.exists(foam_file):
        with open(foam_file, 'w') as f:
            f.write("")
    reader = pv.OpenFOAMReader(foam_file)
    if not len(reader.time_values):
        raise RuntimeError(f"No OpenFOAM solution times found in {foam_file}")
    reader.set_active_time_value(reader.time_values[-1])
    mesh = reader.read()
    return mesh["internalMesh"]

def load_benchmark_data(project_root):
    benchmark_path = os.path.abspath(
        os.path.join(project_root, "..", "validation", "benchmark_data.json")
    )
    with open(benchmark_path, encoding="utf-8") as benchmark_file:
        sources = json.load(benchmark_file)["references"]

    reference = next(
        (
            source
            for source in sources
            if source["author"] == "De Vahl Davis" and source["year"] == 1983
        ),
        None,
    )
    if reference is None:
        raise ValueError(f"De Vahl Davis (1983) data not found in {benchmark_path}")

    return {
        float(point["Ra"]): {
            "Nu_avg": point["Nu_avg"],
            "u_max": point["u_max_dimless"],
            "y_umax": point["y_umax"],
            "v_max": point["v_max_dimless"],
            "x_vmax": point["x_vmax"],
        }
        for point in reference["data"]
    }

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    cases_dir = os.path.join(project_root, "cases")
    results_dir = os.path.join(project_root, "results")
    os.makedirs(results_dir, exist_ok=True)
    benchmark_data = load_benchmark_data(project_root)

    print("=" * 80)
    print(" RAYLEIGH NUMBER BENCHMARK VALIDATION SWEEP (DE VAHL DAVIS 1983)")
    print("=" * 80)

    L = 1.0
    T_hot = 310.0
    T_cold = 290.0
    delta_T = 20.0
    dx_sample = 0.005 # line sampled at x = 0.005

    results = []
    plot_data = {}

    for cfg in RA_CONFIGS:
        cname = cfg['name']
        cpath = os.path.join(cases_dir, cname)
        Ra = cfg['Ra']
        alpha = cfg['alpha']

        print(f"-> Processing {cfg['label']} ...")
        df_y = get_latest_sampled_csv(cpath, "midPlaneY", "midY_T_U.csv")
        df_x = get_latest_sampled_csv(cpath, "midPlaneX", "midX_T_U.csv")
        df_w = get_latest_sampled_csv(cpath, "nearHotWall", "nearWallLine_T.csv")

        if df_y is None or df_x is None or df_w is None:
            missing = [
                name
                for name, sample in (
                    ("midPlaneY", df_y),
                    ("midPlaneX", df_x),
                    ("nearHotWall", df_w),
                )
                if sample is None
            ]
            raise FileNotFoundError(
                f"Missing sampled data for {cname}: {', '.join(missing)}. "
                "Run the case before post-processing."
            )

        # Dimensionless velocities and coordinates
        df_y['v_star'] = df_y['U_1'] * L / alpha
        df_y['x_dim'] = df_y['distance'] / L

        df_x['u_star'] = df_x['U_0'] * L / alpha
        df_x['y_dim'] = df_x['distance'] / L

        # Local Nusselt number along hot wall:
        # Nu(y) = (T_hot - T(x=0.005, y)) / (dx * delta_T) * L
        df_w['Nu'] = (T_hot - df_w['T']) / (dx_sample * delta_T) * L
        Nu_avg = df_w['Nu'].mean()

        # Maximum dimensionless velocities and locations
        v_max_star = df_y['v_star'].max()
        x_vmax = df_y.loc[df_y['v_star'].idxmax(), 'x_dim']

        u_max_star = df_x['u_star'].max()
        y_umax = df_x.loc[df_x['u_star'].idxmax(), 'y_dim']

        bench = benchmark_data[Ra]
        err_Nu = abs(Nu_avg - bench['Nu_avg']) / bench['Nu_avg'] * 100.0
        err_u = abs(u_max_star - bench['u_max']) / bench['u_max'] * 100.0
        err_v = abs(v_max_star - bench['v_max']) / bench['v_max'] * 100.0

        results.append({
            'Ra': Ra,
            'Label': cfg['label'],
            'Nu_CFD': Nu_avg,
            'Nu_Bench': bench['Nu_avg'],
            'Nu_Error_Pct': err_Nu,
            'u_CFD': u_max_star,
            'u_Bench': bench['u_max'],
            'y_umax_CFD': y_umax,
            'y_umax_Bench': bench['y_umax'],
            'u_Error_Pct': err_u,
            'v_CFD': v_max_star,
            'v_Bench': bench['v_max'],
            'x_vmax_CFD': x_vmax,
            'x_vmax_Bench': bench['x_vmax'],
            'v_Error_Pct': err_v
        })

        plot_data[cname] = {
            'cfg': cfg,
            'midY': df_y,
            'midX': df_x,
            'wall': df_w
        }

    if len(results) != len(RA_CONFIGS):
        raise RuntimeError(
            f"Expected {len(RA_CONFIGS)} Rayleigh cases, processed {len(results)}"
        )

    df_res = pd.DataFrame(results)
    nu_slope, nu_intercept = np.polyfit(
        np.log10(df_res["Ra"]), np.log10(df_res["Nu_CFD"]), 1
    )
    # Save summary tables
    csv_out = os.path.join(results_dir, "benchmark_validation_summary.csv")
    df_res.to_csv(csv_out, index=False)

    md_out = os.path.join(results_dir, "benchmark_validation_summary.md")
    with open(md_out, "w") as f:
        f.write("# De Vahl Davis (1983) Benchmark Validation Summary\n\n")
        f.write("| Rayleigh Number ($Ra$) | Quantity | OpenFOAM (CFD) | De Vahl Davis (1983) | Error (%) | Coordinate ($x/L$ or $y/L$) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: |\n")
        for r in results:
            f.write(f"| **{r['Label']}** | Average Nusselt ($\\overline{{Nu}}$) | **{r['Nu_CFD']:.3f}** | {r['Nu_Bench']:.3f} | {r['Nu_Error_Pct']:.2f}% | Wall ($x=0$) |\n")
            f.write(f"| | Max Horizontal Velocity ($u_{{max}}^*$) | **{r['u_CFD']:.2f}** | {r['u_Bench']:.2f} | {r['u_Error_Pct']:.2f}% | $y/L = {r['y_umax_CFD']:.3f}$ (Bench: {r['y_umax_Bench']:.3f}) |\n")
            f.write(f"| | Max Vertical Velocity ($v_{{max}}^*$) | **{r['v_CFD']:.2f}** | {r['v_Bench']:.2f} | {r['v_Error_Pct']:.2f}% | $x/L = {r['x_vmax_CFD']:.3f}$ (Bench: {r['x_vmax_Bench']:.3f}) |\n")
        f.write(
            "\n*Notes: Reference velocities are non-dimensionalized by "
            "$\\alpha/L$. Prandtl number $Pr = 0.71$. Each case uses a "
            "$100 \\times 100$ in-plane mesh and bounded Gauss upwind "
            "convection schemes. The hot-wall Nusselt estimate uses "
            "$T(x=0.005\\,\\mathrm{m},y)$ and a finite difference.*\n\n"
        )
        f.write(
            f"Four-point log-log fit: "
            f"$\\overline{{Nu}} = {10**nu_intercept:.4f}"
            f"\\,Ra^{{{nu_slope:.4f}}}$ (descriptive fit over these cases only).\n\n"
        )
        f.write(
            "Reference: De Vahl Davis, G. (1983), “Natural convection of air "
            "in a square cavity: A bench mark numerical solution,” "
            "*International Journal for Numerical Methods in Fluids*, 3(3), "
            "249–264. [https://doi.org/10.1002/fld.1650030305]"
            "(https://doi.org/10.1002/fld.1650030305).\n"
        )

    print(f"Summary table saved to {md_out}")

    # =========================================================================
    # PLOT 1: Nu vs Ra Scaling Curve (Log-Log)
    # =========================================================================
    plt.figure(figsize=(9, 6))
    ra_vals = [r['Ra'] for r in results]
    nu_of = [r['Nu_CFD'] for r in results]
    nu_bench = [r['Nu_Bench'] for r in results]

    plt.loglog(ra_vals, nu_bench, 'ks--', markersize=9, linewidth=2, label="De Vahl Davis (1983) Benchmark", zorder=3)
    plt.loglog(ra_vals, nu_of, 'ro-', markersize=8, linewidth=2, label="Current OpenFOAM ($100 \\times 100$)", zorder=4)

    # Power law trendline: Nu = C * Ra^n
    log_ra = np.log10(ra_vals)
    log_nu = np.log10(nu_of)
    slope, intercept = np.polyfit(log_ra, log_nu, 1)
    ra_fit = np.logspace(3, 6, 100)
    nu_fit = (10**intercept) * (ra_fit**slope)
    plt.loglog(ra_fit, nu_fit, 'b:', label=rf"Power Law Fit: $\overline{{Nu}} = {10**intercept:.3f} \cdot Ra^{{{slope:.3f}}}$", zorder=2)

    plt.title("Scaling of Average Nusselt Number with Rayleigh Number", pad=12)
    plt.xlabel("Rayleigh Number ($Ra$)")
    plt.ylabel(r"Average Nusselt Number ($\overline{Nu}$)")
    plt.grid(True, which="both", linestyle=":", alpha=0.5)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "nu_vs_ra_scaling.png"))
    plt.close()

    # =========================================================================
    # PLOT 2: Dimensionless Peak Velocities vs Ra
    # =========================================================================
    plt.figure(figsize=(9, 6))
    u_of = [r['u_CFD'] for r in results]
    u_bench = [r['u_Bench'] for r in results]
    v_of = [r['v_CFD'] for r in results]
    v_bench = [r['v_Bench'] for r in results]

    plt.loglog(ra_vals, v_bench, 's--', color='#8e44ad', markersize=8, label=r"Benchmark $v_{max}^*$ (De Vahl Davis)")
    plt.loglog(ra_vals, v_of, 'o-', color='#9b59b6', markersize=8, label=r"OpenFOAM $v_{max}^*$ ($y=0.5$)")
    plt.loglog(ra_vals, u_bench, 's--', color='#2980b9', markersize=8, label=r"Benchmark $u_{max}^*$ (De Vahl Davis)")
    plt.loglog(ra_vals, u_of, 'o-', color='#3498db', markersize=8, label=r"OpenFOAM $u_{max}^*$ ($x=0.5$)")

    plt.title("Dimensionless Peak Velocities vs. Rayleigh Number", pad=12)
    plt.xlabel("Rayleigh Number ($Ra$)")
    plt.ylabel(r"Dimensionless Velocity ($u^*, v^* = U \cdot L / \alpha$)")
    plt.grid(True, which="both", linestyle=":", alpha=0.5)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "velocity_vs_ra_scaling.png"))
    plt.close()

    # =========================================================================
    # PLOT 3: Midplane Temperature Profiles across Ra
    # =========================================================================
    plt.figure(figsize=(9, 6))
    for cfg in RA_CONFIGS:
        cname = cfg['name']
        if cname in plot_data:
            df_y = plot_data[cname]['midY']
            theta = (df_y['T'] - T_cold) / delta_T
            plt.plot(df_y['x_dim'], theta, label=cfg['label'], color=cfg['color'], linestyle=cfg['ls'])

    # Add analytical conduction line
    x_pure = np.linspace(0, 1, 100)
    plt.plot(x_pure, 1.0 - x_pure, 'k:', alpha=0.6, label="Pure Conduction ($Ra \\to 0$)")

    plt.title("Dimensionless Temperature Profile $\\theta(x)$ along Midplane $y=0.5$", pad=12)
    plt.xlabel("Horizontal Position $x/L$")
    plt.ylabel("Dimensionless Temperature $\\theta = (T - T_c) / \\Delta T$")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "temperature_midplane_sweep.png"))
    plt.close()

    # =========================================================================
    # PLOT 4: Midplane Vertical Velocity Profiles across Ra
    # =========================================================================
    plt.figure(figsize=(9, 6))
    for cfg in RA_CONFIGS:
        cname = cfg['name']
        if cname in plot_data:
            df_y = plot_data[cname]['midY']
            plt.plot(df_y['x_dim'], df_y['v_star'], label=cfg['label'], color=cfg['color'], linestyle=cfg['ls'])

    plt.title("Dimensionless Vertical Velocity $v^*(x)$ along Midplane $y=0.5$", pad=12)
    plt.xlabel("Horizontal Position $x/L$")
    plt.ylabel(r"Dimensionless Vertical Velocity $v^* = U_y \cdot L / \alpha$")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "vertical_velocity_sweep.png"))
    plt.close()

    # =========================================================================
    # PLOT 5: Midplane Horizontal Velocity Profiles across Ra
    # =========================================================================
    plt.figure(figsize=(9, 6))
    for cfg in RA_CONFIGS:
        cname = cfg['name']
        if cname in plot_data:
            df_x = plot_data[cname]['midX']
            plt.plot(df_x['y_dim'], df_x['u_star'], label=cfg['label'], color=cfg['color'], linestyle=cfg['ls'])

    plt.title("Dimensionless Horizontal Velocity $u^*(y)$ along Midplane $x=0.5$", pad=12)
    plt.xlabel("Vertical Position $y/L$")
    plt.ylabel(r"Dimensionless Horizontal Velocity $u^* = U_x \cdot L / \alpha$")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "horizontal_velocity_sweep.png"))
    plt.close()

    # =========================================================================
    # PLOT 6: Local Nusselt Number along Heated Wall
    # =========================================================================
    plt.figure(figsize=(9, 6))
    for cfg in RA_CONFIGS:
        cname = cfg['name']
        if cname in plot_data:
            df_w = plot_data[cname]['wall']
            plt.plot(df_w['distance'], df_w['Nu'], label=f"{cfg['label']} (Avg: {plot_data[cname]['wall']['Nu'].mean():.2f})", color=cfg['color'], linestyle=cfg['ls'])

    plt.title("Local Nusselt Number $Nu(y)$ Distribution along Heated Wall", pad=12)
    plt.xlabel("Vertical Coordinate along Wall $y/L$")
    plt.ylabel("Local Nusselt Number $Nu(y)$")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend(frameon=True, facecolor="white", edgecolor="none", shadow=True)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "local_nu_comparison_sweep.png"))
    plt.close()

    # =========================================================================
    # PLOT 7: 4-Panel PyVista Temperature Contours (Flow Regimes)
    # =========================================================================
    fig, axes = plt.subplots(1, 4, figsize=(20, 5), dpi=300)
    for idx, cfg in enumerate(RA_CONFIGS):
        cname = cfg['name']
        cpath = os.path.join(cases_dir, cname)
        mesh = extract_pyvista_mesh(cpath)

        plotter = pv.Plotter(off_screen=True, window_size=[800, 800])
        plotter.add_mesh(mesh, scalars="T", cmap="inferno", show_edges=False, clim=[290, 310])
        plotter.view_xy()
        shot_file = os.path.join(results_dir, f"T_contour_{cname}.png")
        plotter.screenshot(shot_file)
        plotter.close()

        img = plt.imread(shot_file)
        axes[idx].imshow(img)
        bench = benchmark_data[cfg['Ra']]
        axes[idx].set_title(f"{cfg['label']}\n$\\overline{{Nu}} = {results[idx]['Nu_CFD']:.2f}$ (Bench: {bench['Nu_avg']:.2f})", fontsize=12, pad=10)
        axes[idx].axis('off')

    plt.suptitle("Regimes of Natural Convection: From Conduction to Boundary Layer Thinning ($Ra = 10^3 \\to 10^6$)", fontsize=15, y=0.98)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "flow_regimes_4panel.png"), bbox_inches='tight')
    plt.close()
    print("Generated 4-panel regime comparison contour!")

    print("=" * 80)
    print(" POST-PROCESSING & VALIDATION SWEEP COMPLETE")
    print(f" All publication assets saved in: {results_dir}")
    print("=" * 80)

if __name__ == "__main__":
    main()
