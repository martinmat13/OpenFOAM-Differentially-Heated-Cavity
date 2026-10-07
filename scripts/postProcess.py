import pyvista as pv
import numpy as np
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt

os.environ["PYVISTA_OFF_SCREEN"] = "true"

def get_latest_time_dir(case_dir):
    dirs = [d for d in os.listdir(case_dir) if os.path.isdir(os.path.join(case_dir, d))]
    time_dirs = []
    for d in dirs:
        try:
            time_dirs.append(float(d))
        except ValueError:
            pass
    return str(max(time_dirs)) if time_dirs else None

def plot_contours(case_dir):
    foam_file = os.path.join(case_dir, "case.foam")
    if not os.path.exists(foam_file):
        with open(foam_file, 'w') as f:
            f.write("")
    
    reader = pv.OpenFOAMReader(foam_file)
    if len(reader.time_values) > 0:
        reader.set_active_time_value(reader.time_values[-1])
    mesh = reader.read()
    
    internal_mesh = mesh["internalMesh"]
    
    # Temperature Contour
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(internal_mesh, scalars="T", cmap="inferno", show_edges=False)
    plotter.view_xy()
    plotter.screenshot(os.path.join(case_dir, "..", "results", "T_contour.png"))
    plotter.close()
    
    # Velocity Magnitude
    plotter = pv.Plotter(off_screen=True)
    plotter.add_mesh(internal_mesh, scalars="U", cmap="viridis", show_edges=False)
    plotter.view_xy()
    plotter.screenshot(os.path.join(case_dir, "..", "results", "U_contour.png"))
    plotter.close()

    # Streamlines
    plotter = pv.Plotter(off_screen=True)
    streamlines = internal_mesh.streamlines("U", n_points=500, source_radius=0.4, source_center=(0.5, 0.5, 0.05))
    plotter.add_mesh(streamlines.tube(radius=0.002), scalars="U", cmap="viridis")
    plotter.add_mesh(internal_mesh.outline(), color="k")
    plotter.view_xy()
    plotter.screenshot(os.path.join(case_dir, "..", "results", "streamlines.png"))
    plotter.close()

    print("Generated PyVista contours and streamlines in results/")

def process_metrics(case_dir):
    latest_time = get_latest_time_dir(case_dir)
    if not latest_time:
        return
        
    post_dir = os.path.join(case_dir, "postProcessing")
    
    # MidY
    midY_file = glob.glob(os.path.join(post_dir, "midPlaneY", "*", "midY_T_U.csv"))
    if midY_file:
        # Sort by time directory to get latest
        midY_file = sorted(midY_file)[-1]
        df_y = pd.read_csv(midY_file)
        plt.figure()
        plt.plot(df_y['distance'], df_y['U_1'], label='Uy')
        plt.xlabel('x (m)')
        plt.ylabel('Vertical Velocity (m/s)')
        plt.title('Vertical Velocity on Mid-plane y=0.5')
        plt.grid(True)
        plt.savefig(os.path.join(case_dir, "..", "results", "midY_Uy.png"))
        plt.close()
        print(f"Max Uy on mid-plane y=0.5: {df_y['U_1'].max():.6f}")

    # MidX
    midX_file = glob.glob(os.path.join(post_dir, "midPlaneX", "*", "midX_T_U.csv"))
    if midX_file:
        midX_file = sorted(midX_file)[-1]
        df_x = pd.read_csv(midX_file)
        plt.figure()
        plt.plot(df_x['distance'], df_x['U_0'], label='Ux')
        plt.xlabel('y (m)')
        plt.ylabel('Horizontal Velocity (m/s)')
        plt.title('Horizontal Velocity on Mid-plane x=0.5')
        plt.grid(True)
        plt.savefig(os.path.join(case_dir, "..", "results", "midX_Ux.png"))
        plt.close()
        print(f"Max Ux on mid-plane x=0.5: {df_x['U_0'].max():.6f}")

    # Wall Heat Flux (Nusselt Number calculation)
    flux_files = glob.glob(os.path.join(post_dir, "wallHeatFlux1", "*", "wallHeatFlux.dat"))
    if flux_files:
        flux_file = sorted(flux_files)[-1]
        try:
            # Read the dat file ignoring lines starting with #
            data = pd.read_csv(flux_file, sep='\t', comment='#', header=None)
            # Usually the columns are: time, patchName, min, max, integral
            # Since formats vary, we'll extract simply.
            with open(flux_file, 'r') as f:
                lines = f.readlines()
            
            # Find the last time step data
            # OpenFOAM writes block of data per time step.
            hot_wall_flux = 0.0
            cold_wall_flux = 0.0
            for line in reversed(lines):
                if line.startswith('#'): continue
                parts = line.split()
                if len(parts) >= 3:
                    if 'hotWall' in line:
                        hot_wall_flux = float(parts[2]) # integral is usually col 2 or 4
                    elif 'coldWall' in line:
                        cold_wall_flux = float(parts[2])
                if hot_wall_flux and cold_wall_flux:
                    break
            
            # Calculate Nu
            # Parameters from constant/transportProperties
            # nu = 1e-5, Pr = 0.71, beta = 3e-3
            # alpha = nu / Pr = 1.408e-5
            alpha = 1e-5 / 0.71
            delta_T = 20.0
            area = 0.1 # 1m height x 0.1m depth
            
            # Nu = Integral(alpha * grad(T)) / (Area * alpha * DeltaT) 
            # (Assuming the integral in file is integral of alpha*grad(T) )
            nu_hot = abs(hot_wall_flux) / (area * alpha * delta_T)
            nu_cold = abs(cold_wall_flux) / (area * alpha * delta_T)
            
            print(f"Avg Nusselt Number (Hot Wall): {nu_hot:.4f}")
            print(f"Avg Nusselt Number (Cold Wall): {nu_cold:.4f}")
            
            # Calculate Rayleigh Number
            g = 9.81
            beta = 3e-3
            nu = 1e-5
            L = 1.0
            Ra = (g * beta * delta_T * (L**3)) / (nu * alpha)
            print(f"Rayleigh Number (Ra): {Ra:.2e}")
            
            with open(os.path.join(case_dir, "..", "results", "metrics.txt"), "w") as f:
                f.write(f"Rayleigh Number: {Ra:.2e}\n")
                f.write(f"Nusselt Number (Hot): {nu_hot:.4f}\n")
                f.write(f"Nusselt Number (Cold): {nu_cold:.4f}\n")

        except Exception as e:
            print(f"Failed to read heat flux: {e}")

if __name__ == "__main__":
    case_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "case"))
    os.makedirs(os.path.join(case_path, "..", "results"), exist_ok=True)
    try:
        plot_contours(case_path)
    except Exception as e:
        print(f"PyVista plotting failed: {e}")
    
    try:
        process_metrics(case_path)
    except Exception as e:
        print(f"Metrics processing failed: {e}")
