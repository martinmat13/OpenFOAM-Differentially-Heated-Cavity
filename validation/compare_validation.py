import json
import os
import re
import matplotlib.pyplot as plt

def read_openfoam_results(results_file):
    results = {}
    if not os.path.exists(results_file):
        print(f"Results file {results_file} not found.")
        return results
        
    with open(results_file, 'r') as f:
        for line in f:
            if "Rayleigh Number:" in line:
                results["Ra"] = float(line.split(":")[1].strip())
            elif "Average Nusselt Number:" in line:
                results["Nu_avg"] = float(line.split(":")[1].strip())
            elif "Max Velocity:" in line:
                val = re.search(r"([\d\.]+)", line.split(":")[1])
                if val:
                    results["U_max_dim"] = float(val.group(1))
    return results

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    json_file = os.path.join(base_dir, "validation", "benchmark_data.json")
    results_file = os.path.join(base_dir, "results", "analysis_summary.txt")
    
    with open(json_file, 'r') as f:
        benchmarks = json.load(f)
        
    # Extract literature data
    ra_lit = []
    nu_lit = []
    
    # Sort data for clean line plotting
    data_points = []
    for ref in benchmarks["references"]:
        for data in ref["data"]:
            if data["Nu_avg"] is not None:
                data_points.append((data["Ra"], data["Nu_avg"]))
                
    data_points.sort(key=lambda x: x[0])
    ra_lit = [p[0] for p in data_points]
    nu_lit = [p[1] for p in data_points]
                
    # Read OpenFOAM results
    of_results = read_openfoam_results(results_file)
    
    # Plot Comparison
    plt.figure(figsize=(10, 6))
    
    # Plot Literature data
    plt.loglog(ra_lit, nu_lit, 'ko--', label="Literature Benchmarks (De Vahl Davis, Le Quere, Dixit)", linewidth=2, markersize=8)
    
    # Plot our data
    if "Ra" in of_results and "Nu_avg" in of_results:
        plt.loglog(of_results["Ra"], of_results["Nu_avg"], 'r*', markersize=15, label="Current OpenFOAM Simulation")
        
        # Annotate
        plt.annotate(f" OF Result\n Ra={of_results['Ra']:.1e}\n Nu={of_results['Nu_avg']:.2f}", 
                     (of_results["Ra"], of_results["Nu_avg"]),
                     xytext=(-40, 20), textcoords='offset points', color='red', weight='bold',
                     bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="red", alpha=0.8))

    plt.xlabel("Rayleigh Number (Ra)", fontsize=12)
    plt.ylabel("Average Nusselt Number (Nu)", fontsize=12)
    plt.title("Validation: Average Nusselt Number vs Rayleigh Number", fontsize=14)
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.grid(True, which="major", ls="-", alpha=0.5)
    plt.legend(fontsize=11)
    
    out_img = os.path.join(base_dir, "validation", "Nu_vs_Ra_validation.png")
    plt.savefig(out_img, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Validation comparison plot generated: {out_img}")
    
    if "Ra" in of_results and "Nu_avg" in of_results:
        print("\n--- Quick Comparison ---")
        print(f"Simulated Ra: {of_results['Ra']:.2e}")
        print(f"Simulated Nu: {of_results['Nu_avg']:.2f}")
        # Find closest benchmark Ra
        closest_ra = min(ra_lit, key=lambda x: abs(x - of_results['Ra']))
        idx = ra_lit.index(closest_ra)
        print(f"Closest Benchmark Ra: {closest_ra:.2e} -> Benchmark Nu: {nu_lit[idx]:.2f}")

if __name__ == "__main__":
    main()
