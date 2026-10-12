#!/usr/bin/env python3
"""
Generate PyVista contour snapshots and 3-panel comparison figures for
Grid Convergence Study (Coarse vs Medium vs Fine).
"""

import os
import pyvista as pv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

os.environ["PYVISTA_OFF_SCREEN"] = "true"

def extract_field_slice(case_dir, field_name):
    foam_file = os.path.join(case_dir, "case.foam")
    if not os.path.exists(foam_file):
        with open(foam_file, 'w') as f:
            f.write("")
    reader = pv.OpenFOAMReader(foam_file)
    if len(reader.time_values) > 0:
        reader.set_active_time_value(reader.time_values[-1])
    mesh = reader.read()
    internal = mesh["internalMesh"]
    return internal

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    cases_dir = os.path.join(project_root, "cases")
    results_dir = os.path.join(project_root, "results")
    os.makedirs(results_dir, exist_ok=True)
    
    grids = [
        ('grid3_coarse', 'Coarse (50x50)'),
        ('grid2_medium', 'Medium (100x100)'),
        ('grid1_fine',   'Fine (200x200)')
    ]
    
    # Generate individual screenshots
    for gname, glabel in grids:
        cpath = os.path.join(cases_dir, gname)
        mesh = extract_field_slice(cpath, "T")
        
        # T contour
        p = pv.Plotter(off_screen=True, window_size=[1000, 1000])
        p.add_mesh(mesh, scalars="T", cmap="inferno", show_edges=False, clim=[290, 310], scalar_bar_args={'title': 'Temperature (K)', 'vertical': True})
        p.view_xy()
        p.screenshot(os.path.join(results_dir, f"T_contour_{gname}.png"))
        p.close()

        # U contour
        p = pv.Plotter(off_screen=True, window_size=[1000, 1000])
        p.add_mesh(mesh, scalars="U", cmap="viridis", show_edges=False, scalar_bar_args={'title': 'Velocity (m/s)', 'vertical': True})
        p.view_xy()
        p.screenshot(os.path.join(results_dir, f"U_contour_{gname}.png"))
        p.close()
        
    # Stitch 3-panel side-by-side comparison for Temperature
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=300)
    for idx, (gname, glabel) in enumerate(grids):
        img_path = os.path.join(results_dir, f"T_contour_{gname}.png")
        img = plt.imread(img_path)
        axes[idx].imshow(img)
        axes[idx].set_title(f"{glabel}\nThermal Stratification & Boundary Layer", fontsize=13, pad=10)
        axes[idx].axis('off')
    plt.suptitle("Temperature Field Comparison Across Mesh Resolutions ($Ra \\approx 2 \\times 10^9$)", fontsize=16, y=0.98)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "T_contour_comparison_3panel.png"), bbox_inches='tight')
    plt.close()

    # Stitch 3-panel side-by-side comparison for Velocity
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=300)
    for idx, (gname, glabel) in enumerate(grids):
        img_path = os.path.join(results_dir, f"U_contour_{gname}.png")
        img = plt.imread(img_path)
        axes[idx].imshow(img)
        axes[idx].set_title(f"{glabel}\nConvection Jet & Circulation Velocity", fontsize=13, pad=10)
        axes[idx].axis('off')
    plt.suptitle("Velocity Field Comparison Across Mesh Resolutions ($Ra \\approx 2 \\times 10^9$)", fontsize=16, y=0.98)
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, "U_contour_comparison_3panel.png"), bbox_inches='tight')
    plt.close()
    
    print("PyVista contour comparisons successfully generated!")

if __name__ == "__main__":
    main()
