import os
import shutil
import subprocess
import glob
import re

time_steps = [0.5, 1.0, 2.0]
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
case_dir = os.path.join(base_dir, "case")
studies_dir = os.path.join(base_dir, "studies", "time")
controlDict_path = os.path.join(case_dir, "system", "controlDict")

os.makedirs(studies_dir, exist_ok=True)

def update_dt(dt):
    with open(controlDict_path, "r") as f:
        content = f.read()
    new_content = re.sub(r'deltaT\s+[\d\.]+;', f'deltaT {dt};', content)
    with open(controlDict_path, "w") as f:
        f.write(new_content)

def clean_case():
    for f in os.listdir(case_dir):
        if f.isdigit() and f != "0":
            shutil.rmtree(os.path.join(case_dir, f))
    post_dir = os.path.join(case_dir, "postProcessing")
    if os.path.exists(post_dir):
        shutil.rmtree(post_dir)

for dt in time_steps:
    print(f"\n=== Running Time Study for deltaT = {dt} ===")
    clean_case()
    update_dt(dt)
    
    # Run the simulation (Assuming mesh is already generated)
    subprocess.run(["blockMesh", "-case", case_dir], check=True)
    subprocess.run(["buoyantBoussinesqSimpleFoam", "-case", case_dir], check=True)
    
    dest_dir = os.path.join(studies_dir, f"dt_{dt}")
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir)
    
    post_src = os.path.join(case_dir, "postProcessing")
    if os.path.exists(post_src):
        shutil.copytree(post_src, os.path.join(dest_dir, "postProcessing"))
    
    subprocess.run(["python3", os.path.join(base_dir, "scripts", "postProcess.py")], cwd=case_dir)
    
    results_dir = os.path.join(base_dir, "results")
    if os.path.exists(results_dir):
        for f in os.listdir(results_dir):
            src_path = os.path.join(results_dir, f)
            dest_path = os.path.join(dest_dir, f)
            if os.path.isfile(src_path):
                shutil.copy(src_path, dest_path)
            elif os.path.isdir(src_path):
                if os.path.exists(dest_path):
                    shutil.rmtree(dest_path)
                shutil.copytree(src_path, dest_path)
    
print("Time study complete. Reverting deltaT back to 1.0.")
update_dt(1.0)
clean_case()
