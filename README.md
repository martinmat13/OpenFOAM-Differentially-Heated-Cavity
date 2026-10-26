# Differentially Heated Cavity

**OpenFOAM CFD | Natural Convection | Verification | Validation | Reproducible Engineering**

This repository is a teaching and reference project for buoyancy-driven heat transfer in the differentially heated square cavity. It documents a steady laminar baseline, a RANS case, a transient PIMPLE case, a grid-refinement exercise, and a four-point Rayleigh-number benchmark sweep.

> **Use as a learning baseline, not as certified design data.** The Rayleigh sweep is useful for understanding trends and comparing against a canonical numerical benchmark. Its uniform mesh, bounded upwind convection schemes, and near-wall finite-difference heat-flux estimate limit the strength of accuracy claims.

## Project status

- **Author:** Martin Mathew
- **Started:** 2026-10-02
- **OpenFOAM case dictionaries:** OpenFOAM.com v2512
- **Benchmark solver:** `buoyantBoussinesqSimpleFoam`
- **Physics:** incompressible Boussinesq natural convection and heat transfer
- **Dimension:** two-dimensional square cavity, represented by a one-cell-thick 3D mesh with `empty` front/back patches

## Learning path

1. Start with [`01_laminar_baseline/`](01_laminar_baseline/). Read its `0/`, `constant/`, and `system/` notes alongside the OpenFOAM dictionaries.
2. Reproduce the four canonical benchmark cases in [`05_rayleigh_validation_sweep/README.md`](05_rayleigh_validation_sweep/README.md).
3. Compare model changes in [`02_turbulent_sst/`](02_turbulent_sst/) and [`03_transient_pimple/`](03_transient_pimple/). These are separate studies and are not part of the laminar benchmark sweep.
4. Read [`04_mesh_independence_gci/README.md`](04_mesh_independence_gci/README.md) with its stated convergence caveats.
5. Review data sources and validation practice in [`validation/README.md`](validation/README.md).

## Physical problem and assumptions

The square cavity has width and height $L=H=1$ m. The left wall is held at $T_h=310$ K and the right wall at $T_c=290$ K. Top and bottom walls are stationary and adiabatic. Gravity is $\mathbf{g}=(0,-9.81,0)$ m s$^{-2}$. Air is modeled with constant kinematic viscosity and thermal diffusivity under the Boussinesq approximation. Radiation, conjugate heat transfer, property variation, and three-dimensional effects are not modeled.

The dimensionless groups are

$$
Ra=\frac{g\beta\Delta T L^3}{\nu\alpha}, \qquad
Pr=\frac{\nu}{\alpha},
$$

where $\Delta T=20$ K, $\beta=1/300$ K$^{-1}$, and $Pr=0.71$. The sweep varies $\nu$ and $\alpha$ while keeping these other parameters fixed.

## Boundary conditions

| Patch | Velocity | Temperature | Physical meaning |
|---|---|---|---|
| `hotWall` ($x=0$) | No slip | Fixed at 310 K | Heated vertical wall |
| `coldWall` ($x=L$) | No slip | Fixed at 290 K | Cooled vertical wall |
| `adiabaticWalls` ($y=0,H$) | No slip | Zero gradient | Insulated horizontal walls |
| `frontAndBack` | `empty` | `empty` | Two-dimensional constraint |

## Methods at a glance

| Study | Method |
|---|---|
| `01_laminar_baseline` | Steady laminar `buoyantBoussinesqSimpleFoam` |
| `02_turbulent_sst` | Steady RANS using `kOmegaSST` |
| `03_transient_pimple` | Transient `buoyantBoussinesqPimpleFoam`, Euler time integration, adjustable time step |
| `04_mesh_independence_gci` | Three structured grids, nominal refinement ratio 2 |
| `05_rayleigh_validation_sweep` | Four steady laminar cases at $Ra=10^3,10^4,10^5,10^6$, each on a uniform $100\times100\times1$ mesh |

In the benchmark sweep, `system/fvSchemes` uses bounded Gauss upwind for `div(phi,U)` and `div(phi,T)`, Gauss linear gradients, and corrected Gauss linear Laplacians. Do not describe those convection terms as second order. Individual dictionaries are authoritative where case settings differ.

## Benchmark results

The sweep compares mean Nusselt number and dimensionless mid-plane velocity peaks with De Vahl Davis (1983). The velocity scale is $U_s=\alpha/L$; the complete table and method are in [`05_rayleigh_validation_sweep/results/benchmark_validation_summary.md`](05_rayleigh_validation_sweep/results/benchmark_validation_summary.md).

| $Ra$ | $\overline{Nu}$ (CFD / benchmark) | $u^*_\max$ (CFD / benchmark) | $v^*_\max$ (CFD / benchmark) |
|---:|---:|---:|---:|
| $10^3$ | 1.072 / 1.118 | 3.35 / 3.649 | 3.38 / 3.697 |
| $10^4$ | 2.326 / 2.243 | 16.45 / 16.178 | 19.79 / 19.617 |
| $10^5$ | 4.586 / 4.519 | 35.96 / 34.73 | 68.37 / 68.59 |
| $10^6$ | 8.975 / 8.800 | 66.88 / 64.63 | 217.86 / 219.36 |

Across the four cases, relative errors are 1.47–4.13% for $\overline{Nu}$, 1.67–8.22% for $u^*_\max$, and 0.31–8.65% for $v^*_\max$. The larger velocity discrepancies occur at $Ra=10^3$; precision in one quantity should not be generalized to the others.

The four-point least-squares fit is $\overline{Nu}=0.1331Ra^{0.3064}$. This is a descriptive fit over this data range, not a universal correlation. See the [sweep article](website/rayleigh_benchmark_validation.mdx) for profiles, physical interpretation, and limitations.

## Verification and uncertainty

The separate grid study reports $\overline{Nu}=41.1717$, 58.4341, and 59.5341 on coarse, medium, and fine grids, and calculates $GCI_{fine}=0.16\%$. However, its reported asymptotic ratio is $\chi=15.989$, not approximately 1. The data therefore do **not** demonstrate that the grids are in the asymptotic range; do not interpret that GCI as a validated uncertainty bound. See [`04_mesh_independence_gci/README.md`](04_mesh_independence_gci/README.md).

The Rayleigh sweep itself has no sweep-specific mesh refinement or formal numerical uncertainty estimate. The Nusselt number is estimated from a temperature sample at $x=0.005$ m, close to but not on the hot wall. These limitations matter when interpreting the benchmark differences.

## Reproducing the Rayleigh sweep

Requirements: OpenFOAM.com v2512 (or a compatible installation exposing the named solvers and `blockMesh`) and Python 3 with NumPy, pandas, Matplotlib, and PyVista.

```bash
cd 05_rayleigh_validation_sweep
./Allrun
```

Run an individual case from its own directory with `./Allrun`. The master runner executes the four cases and writes the CSV, Markdown table, and plots under `05_rayleigh_validation_sweep/results/`. The case scripts stop on solver failure; logs are written as `log.blockMesh` and `log.foam`.

## Repository map

```text
01_laminar_baseline/          Steady laminar reference case
02_turbulent_sst/              Steady k-omega SST case
03_transient_pimple/           Transient PIMPLE case
04_mesh_independence_gci/      Grid refinement and GCI exercise
05_rayleigh_validation_sweep/  De Vahl Davis benchmark sweep
validation/                    Literature values and comparison utility
website/                       Project articles and figure assets
```

Each case directory has its own `Allrun` and `Allclean`. Inspect the scripts and preserve any outputs you need before running a clean operation.

## References

1. De Vahl Davis, G. (1983). “Natural convection of air in a square cavity: A bench mark numerical solution.” *International Journal for Numerical Methods in Fluids*, 3(3), 249–264. [https://doi.org/10.1002/fld.1650030305](https://doi.org/10.1002/fld.1650030305).
2. Celik, I. B., Ghia, U., Roache, P. J., Freitas, C. J., Coleman, H., & Raad, P. E. (2008). “Procedure for estimation and reporting of uncertainty due to discretization in CFD applications.” *Journal of Fluids Engineering*, 130(7), 078001. [https://doi.org/10.1115/1.2960953](https://doi.org/10.1115/1.2960953).
3. OpenCFD Ltd. *OpenFOAM v2512 Documentation*. [https://doc.openfoam.com/](https://doc.openfoam.com/).
