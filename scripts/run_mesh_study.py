import os
import shutil
import subprocess
import glob
import re

resolutions = [20, 40, 80]
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
case_dir = os.path.join(base_dir, "case")
studies_dir = os.path.join(base_dir, "studies", "mesh")
blockMesh_path = os.path.join(case_dir, "system", "blockMeshDict")

os.makedirs(studies_dir, exist_ok=True)

def update_mesh(N):
    with open(blockMesh_path, "r") as f:
        content = f.read()
    new_content = re.sub(r'\(\d+\s+\d+\s+1\)', f'({N} {N} 1)', content)
    with open(blockMesh_path, "w") as f:
        f.write(new_content)

def clean_case():
    for f in os.listdir(case_dir):
        if f.isdigit() and f != "0":
            shutil.rmtree(os.path.join(case_dir, f))
    post_dir = os.path.join(case_dir, "postProcessing")
    if os.path.exists(post_dir):
        shutil.rmtree(post_dir)

for N in resolutions:
    print(f"\n=== Running Mesh Study for {N}x{N} ===")
    clean_case()
    update_mesh(N)
    
    subprocess.run(["blockMesh", "-case", case_dir], check=True)
    subprocess.run(["buoyantBoussinesqSimpleFoam", "-case", case_dir], check=True)
    
    dest_dir = os.path.join(studies_dir, str(N))
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
    
print("Mesh study complete. Reverting mesh back to 40x40.")
update_mesh(40)
clean_case()
