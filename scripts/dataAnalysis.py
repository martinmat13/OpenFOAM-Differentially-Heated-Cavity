import pyvista as pv
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

def analyze_metrics(case_dir):
    """
    Perform efficient data analysis on the OpenFOAM results.
    Calculates Rayleigh Number, average Nusselt Number, and extracts 
    mid-plane velocities directly from the volumetric mesh data using PyVista.
    """
    foam_file = os.path.join(case_dir, "case.foam")
    if not os.path.exists(foam_file):
        with open(foam_file, 'w') as f:
            f.write("")

    # 1. Load the OpenFOAM case using PyVista
    # This is much faster and cleaner than manual text-parsing
    print("Loading OpenFOAM mesh data...")
    reader = pv.OpenFOAMReader(foam_file)
    if len(reader.time_values) > 0:
        reader.set_active_time_value(reader.time_values[-1])
    
    # Read internal mesh and boundary patches
    mesh = reader.read()
    internal = mesh["internalMesh"]
    boundaries = mesh["boundary"]

    # 2. Physics Parameters (From Boussinesq fluid properties)
    L = 1.0           # Characteristic length (Cavity height/width in m)
    delta_T = 20.0    # Temperature difference (Thot - Tcold)
    g = 9.81          # Gravity (m/s^2)
    beta = 3e-3       # Thermal expansion coefficient (1/K)
    nu = 1e-5         # Kinematic viscosity (m^2/s)
    Pr = 0.71         # Prandtl Number
    alpha = nu / Pr   # Thermal diffusivity (m^2/s)

    # 3. Calculate Dimensionless Rayleigh Number
    Ra = (g * beta * delta_T * (L**3)) / (nu * alpha)
    print(f"\n--- Dimensionless Parameters ---")
    print(f"Rayleigh Number (Ra): {Ra:.2e}")
    print(f"Prandtl Number (Pr):  {Pr}")

    # 4. Compute Temperature Gradients and Nusselt Number (Nu)
    print("\n--- Heat Transfer Metrics ---")
    if "T" in internal.cell_data or "T" in internal.point_data:
        # compute_derivative calculates the gradient of the scalar field (T)
        # It creates a 3D vector [dT/dx, dT/dy, dT/dz]
        internal = internal.compute_derivative(scalars="T")
        
        # Extract the hot wall patch
        hot_wall = boundaries["hotWall"]
        # Sample the internal gradient field onto the boundary patch points
        hot_wall = hot_wall.sample(internal)
        
        if "gradient" in hot_wall.point_data:
            # For the hot wall at x=0, the outward normal is (-1, 0, 0)
            # Therefore, the gradient normal to the fluid is -dT/dx
            dT_dx = hot_wall.point_data["gradient"][:, 0]
            
            # Local Nusselt number formula: Nu_local = (L / delta_T) * |dT/dx|
            Nu_local = (L / delta_T) * np.abs(dT_dx)
            
            # Average Nusselt Number
            Nu_avg = np.mean(Nu_local)
            print(f"Average Nusselt Number (Hot Wall): {Nu_avg:.4f}")

            # Plot local Nusselt number profile along the height (Y-axis)
            y_coords = hot_wall.points[:, 1]
            plt.figure(figsize=(8, 6))
            # Sort by Y-coordinate for a clean line plot
            sort_idx = np.argsort(y_coords)
            plt.plot(y_coords[sort_idx], Nu_local[sort_idx], 'r-', linewidth=2, label="Local Nu")
            plt.xlabel('Height, Y (m)')
            plt.ylabel('Local Nusselt Number (Nu)')
            plt.title('Local Nusselt Number Profile along Hot Wall')
            plt.grid(True)
            plt.legend()
            plt.tight_layout()
            
            out_path = os.path.join(case_dir, "..", "results", "Nu_profile.png")
            plt.savefig(out_path)
            plt.close()
            print(f"Saved Nusselt profile plot to: results/Nu_profile.png")
        else:
            print("Gradient extraction failed. Mesh might be empty.")
    else:
        print("Temperature field 'T' not found. Ensure simulation is run first.")

    # 5. Extract Maximum Velocities Efficiently
    print("\n--- Velocity Metrics ---")
    if "U" in internal.cell_data or "U" in internal.point_data:
        # If U is cell data, convert to point data for easier slicing/max checking
        if "U" in internal.cell_data:
            internal = internal.cell_data_to_point_data()
            
        U = internal.point_data["U"]
        U_mag = np.linalg.norm(U, axis=1)
        max_U = np.max(U_mag)
        print(f"Maximum Overall Velocity: {max_U:.5f} m/s")

        # Slice the mesh exactly at the midplanes without relying on OpenFOAM sampleDict
        midY_slice = internal.slice(normal=[0, 1, 0], origin=[0.5, 0.5, 0.05])
        if "U" in midY_slice.point_data:
            Uy = midY_slice.point_data["U"][:, 1] # Vertical velocity
            print(f"Max Vertical Velocity on mid-plane Y=0.5: {np.max(Uy):.5f} m/s")

        midX_slice = internal.slice(normal=[1, 0, 0], origin=[0.5, 0.5, 0.05])
        if "U" in midX_slice.point_data:
            Ux = midX_slice.point_data["U"][:, 0] # Horizontal velocity
            print(f"Max Horizontal Velocity on mid-plane X=0.5: {np.max(Ux):.5f} m/s")

    # 6. Save a neat summary file
    results_file = os.path.join(case_dir, "..", "results", "analysis_summary.txt")
    with open(results_file, "w") as f:
        f.write(f"Rayleigh Number: {Ra:.2e}\n")
        if 'Nu_avg' in locals():
            f.write(f"Average Nusselt Number: {Nu_avg:.4f}\n")
        if 'max_U' in locals():
            f.write(f"Max Velocity: {max_U:.5f} m/s\n")
            
    print(f"\nData analysis complete! Summary saved in results/analysis_summary.txt")

if __name__ == "__main__":
    case_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "case"))
    os.makedirs(os.path.join(case_path, "..", "results"), exist_ok=True)
    try:
        analyze_metrics(case_path)
    except Exception as e:
        print(f"Error during analysis: {e}")
