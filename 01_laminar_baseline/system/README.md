# Mesh, Solver, and Numerics

The dictionaries here define the baseline mesh, SIMPLE run, finite-volume schemes, and solver controls.

- `blockMeshDict`: structured square cavity extruded one cell through depth; boundary patches include hot, cold, adiabatic, and `empty` front/back faces.
- `controlDict`: selects the solver and run/write controls; function objects sample mid-planes and near-wall temperature.
- `fvSchemes`: steady-state time derivative, Gauss linear gradients, bounded Gauss upwind convection, and corrected Laplacians.
- `fvSolution`: pressure-velocity coupling and linear solver controls for SIMPLE.
- `setFieldsDict`: initial field assignment utility.

Read these dictionaries together. In particular, bounded upwind is a robust first-order convection scheme; it should not be described as second-order. Run from `01_laminar_baseline/` with `./Allrun`.
