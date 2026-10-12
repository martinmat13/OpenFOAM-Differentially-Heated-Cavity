import pyvista as pv
import numpy as np
import os
import re

os.environ["PYVISTA_OFF_SCREEN"] = "true"

def get_rayleigh_number(results_dir):
    summary_file = os.path.join(results_dir, "analysis_summary.txt")
    ra_str = "UnknownRa"
    if os.path.exists(summary_file):
        with open(summary_file, 'r') as f:
            for line in f:
                if "Rayleigh Number" in line:
                    parts = line.split(":")
                    if len(parts) > 1:
                        try:
                            ra_val = float(parts[1].strip())
                            ra_str = f"Ra{ra_val:.1e}".replace("+", "")
                        except:
                            pass
    return ra_str

def main():
    case_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "case"))
    results_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "results"))
    os.makedirs(results_path, exist_ok=True)
    
    ra_label = get_rayleigh_number(results_path)
    
    foam_file = os.path.join(case_path, "case.foam")
    if not os.path.exists(foam_file):
        with open(foam_file, 'w') as f:
            f.write("")
            
    print(f"Loading OpenFOAM case: {foam_file}")
    reader = pv.OpenFOAMReader(foam_file)
    
    if len(reader.time_values) > 0:
        reader.set_active_time_value(reader.time_values[-1])
        print(f"Reading data at time: {reader.time_values[-1]}")
        
    mesh = reader.read()
    internal_mesh = mesh["internalMesh"]
    internal_mesh = internal_mesh.cell_data_to_point_data()
    
    bounds = internal_mesh.bounds
    x_min, x_max = bounds[0], bounds[1]
    y_min, y_max = bounds[2], bounds[3]
    z_min, z_max = bounds[4], bounds[5]
    z_mid = (z_min + z_max) / 2.0
    
    # Take a 2D slice at z_mid to avoid 3D interpolation warnings
    slice_2d = internal_mesh.slice(normal='z', origin=(0, 0, z_mid))
    
    pv.global_theme.background = 'white'
    pv.global_theme.font.color = 'black'
    pv.global_theme.font.family = 'arial'
    
    sargs = dict(
        title_font_size=20,
        label_font_size=16,
        shadow=False,
        n_labels=5,
        italic=False,
        fmt="%.2f",
        font_family="arial",
        color="black",
        vertical=False,
        position_x=0.25,
        position_y=0.08,
        width=0.5,
        height=0.06
    )

    # 1. Temperature Contour
    if "T" in slice_2d.array_names:
        t_min, t_max = slice_2d["T"].min(), slice_2d["T"].max()
        print(f"Temperature range: [{t_min:.2f}, {t_max:.2f}] K")
        
        plotter = pv.Plotter(off_screen=True, window_size=[1000, 1000])
        plotter.add_text(f"Temperature Contour ({ra_label})", font_size=16, color="black", position="upper_edge")
        sargs_T = sargs.copy()
        sargs_T["title"] = "Temperature (K)"
        sargs_T["fmt"] = "%.1f"
        
        plotter.add_mesh(slice_2d, scalars="T", cmap="inferno", show_edges=False, clim=[t_min, t_max], scalar_bar_args=sargs_T)
        plotter.add_mesh(slice_2d.extract_feature_edges(), color="black", line_width=2)
        plotter.view_xy()
        plotter.camera.zoom(1.05)
        
        out_file = os.path.join(results_path, f"T_contour_{ra_label}.png")
        plotter.screenshot(out_file)
        plotter.close()
        print(f"Saved: {out_file}")

    # 2. Velocity Magnitude & Streamlines overlay
    if "U" in slice_2d.array_names:
        U_mag = np.linalg.norm(slice_2d["U"], axis=1)
        slice_2d["U_mag"] = U_mag
        u_min, u_max = U_mag.min(), U_mag.max()
        print(f"Velocity magnitude range: [{u_min:.5f}, {u_max:.5f}] m/s")
        
        plotter = pv.Plotter(off_screen=True, window_size=[1000, 1000])
        plotter.add_text(f"Velocity Magnitude & Streamlines ({ra_label})", font_size=16, color="black", position="upper_edge")
        sargs_U = sargs.copy()
        sargs_U["title"] = "Velocity Magnitude (m/s)"
        sargs_U["fmt"] = "%.3e" if u_max < 0.01 else "%.3f"
        
        plotter.add_mesh(slice_2d, scalars="U_mag", cmap="viridis", show_edges=False, clim=[u_min, u_max], scalar_bar_args=sargs_U, opacity=0.8)
        
        # Try plotting streamlines using a line source
        try:
            line_start = (x_min + 0.1*(x_max-x_min), (y_min+y_max)/2, z_mid)
            line_end = (x_max - 0.1*(x_max-x_min), (y_min+y_max)/2, z_mid)
            line = pv.Line(line_start, line_end, resolution=100)
            streamlines = slice_2d.streamlines_from_source(line, vectors="U", integration_direction="both", max_length=(x_max-x_min)*10.0)
            if streamlines.n_points > 0:
                plotter.add_mesh(streamlines.tube(radius=(x_max-x_min)*0.002), color="white")
        except Exception as e:
            print(f"Streamlines failed: {e}. Plotting vectors instead.")
            glyphs = slice_2d.glyph(orient="U", scale="U_mag", factor=0.1, tolerance=0.05)
            plotter.add_mesh(glyphs, color="white")
            
        plotter.add_mesh(slice_2d.extract_feature_edges(), color="black", line_width=2)
        plotter.view_xy()
        plotter.camera.zoom(1.05)
        
        out_file = os.path.join(results_path, f"U_streamlines_{ra_label}.png")
        plotter.screenshot(out_file)
        plotter.close()
        print(f"Saved: {out_file}")

if __name__ == "__main__":
    main()

