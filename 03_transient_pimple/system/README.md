# Mesh, Time Integration, and Numerics

The system dictionaries define the transient cavity calculation.

- `blockMeshDict`: structured square cavity with a single cell through depth.
- `controlDict`: selects `buoyantBoussinesqPimpleFoam`, starts at time zero, sets a nominal `deltaT = 0.01`, enables automatic time-step adjustment with `maxCo = 1`, and writes at run-time intervals.
- `fvSchemes`: Euler time integration, Gauss linear gradients, bounded Gauss upwind convection, and corrected Laplacians.
- `fvSolution`: PIMPLE pressure-velocity coupling and linear solver controls.
- `setFieldsDict`: initial field utility.

Because the time step is adjustable, inspect the written time-step and Courant-number history when interpreting transient results. Run from `03_transient_pimple/` using its `./Allrun`; this case is independent of the steady benchmark sweep.
