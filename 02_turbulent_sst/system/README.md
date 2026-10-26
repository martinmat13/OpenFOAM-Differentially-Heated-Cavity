# Mesh, Solver, and Numerics

The dictionaries configure the structured cavity and the steady RANS calculation.

- `blockMeshDict`: square x-y enclosure represented by one cell through depth.
- `controlDict`: selects `buoyantBoussinesqSimpleFoam`, run/write controls, and line-sampling function objects.
- `fvSchemes`: steady-state formulation, Gauss linear gradients, bounded Gauss upwind convection for flow, temperature, and turbulence transport, and corrected Laplacians.
- `fvSolution`: SIMPLE pressure-velocity coupling, equation solvers, and relaxation controls.
- `setFieldsDict`: initial field utility.

The scheme choice is first-order upwind for the listed convective terms; it trades some accuracy for robustness. Run from `02_turbulent_sst/` with `./Allrun`. Inspect residuals and monitored quantities before deciding that a steady solution is converged.
