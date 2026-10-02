# Numerical Methodology

## 1. Problem Definition

The problem modeled is the two-dimensional natural convection of a fluid inside a square cavity. The left wall is heated to $T_H$, and the right wall is cooled to $T_C$. The horizontal top and bottom walls are adiabatic. The flow is driven solely by density differences caused by the thermal gradients (buoyancy).

## 2. Governing Equations

The flow is modeled using the incompressible steady-state Navier-Stokes equations under the Boussinesq approximation. The equations solved by the OpenFOAM solver are:

### Continuity (Mass Conservation)
$$ \nabla \cdot \vec{u} = 0 $$

### Momentum Conservation (Boussinesq)
$$ \nabla \cdot (\vec{u} \otimes \vec{u}) = - \nabla p_k + \nabla \cdot (\nu \nabla \vec{u}) + \vec{g} \beta (T - T_{ref}) $$
Where $p_k$ is the kinematic pseudo-pressure (incorporating the hydrostatic part), $\nu$ is the kinematic viscosity, and $\vec{g} \beta (T - T_{ref})$ is the buoyancy source term.

### Energy Conservation
$$ \nabla \cdot (\vec{u} T) = \nabla \cdot (\alpha \nabla T) $$
Where $\alpha = \nu / Pr$ is the thermal diffusivity. 

## 3. Physical Properties

These are configured in `constant/transportProperties`. The default values in the simulation aim for a specific Rayleigh number.

| Property | Symbol | Value (Default) | Source |
|---|---|---:|---|
| Kinematic viscosity | $\nu$ | 1.0e-05 $m^2/s$ | OpenFOAM config |
| Thermal expansion | $\beta$ | 3.0e-03 $1/K$ | OpenFOAM config |
| Reference temperature| $T_{ref}$ | 300 $K$ | OpenFOAM config |
| Prandtl number | $Pr$ | 0.7 | OpenFOAM config |

## 4. Geometry

- **Type**: 2D Square Cavity (Represented as a 3D block with 1 element thickness).
- **Dimensions**: $W = 1.0 m, H = 1.0 m, D = 0.1 m$.
- **Coordinate System**: Cartesian. The bottom-left corner is at $(0,0,0)$. Gravity acts in the $-Y$ direction: $\vec{g} = (0, -9.81, 0)$.

## 5. Boundary Conditions

Located in the `0` directory.

| Boundary | Variable | Condition Type | Physical Meaning |
|---|---|---|---|
| `hotWall` (left) | `T` | `fixedValue` (310 K) | Isothermal hot wall |
| `hotWall` (left) | `U` | `noSlip` | Stationary wall |
| `coldWall` (right) | `T` | `fixedValue` (290 K) | Isothermal cold wall |
| `coldWall` (right) | `U` | `noSlip` | Stationary wall |
| `adiabaticWalls` | `T` | `zeroGradient` | Perfectly insulated (no heat flux) |
| `adiabaticWalls` | `U` | `noSlip` | Stationary walls |
| `frontAndBack` | All | `empty` | Enforces 2D calculation |

## 6. Initial Conditions
- $T_{initial} = 300\ K$
- $U_{initial} = (0, 0, 0)\ m/s$

## 7. Solver
- **Solver**: `buoyantBoussinesqSimpleFoam` (Steady-state, incompressible, Boussinesq buoyancy).
- **Algorithm**: SIMPLE (Semi-Implicit Method for Pressure Linked Equations).

## 8. Numerical Schemes
Configured in `system/fvSchemes`.

- **Time derivative (`ddtSchemes`)**: `steadyState` (local time stepping towards steady solution).
- **Gradient (`gradSchemes`)**: `Gauss linear` (Second-order, central differencing).
- **Divergence (`divSchemes`)**: `bounded Gauss upwind` (First-order upwind for numerical stability. Note: For accurate results at higher $Ra$, this should be changed to second-order like `linearUpwind`).
- **Laplacian (`laplacianSchemes`)**: `Gauss linear corrected` (Second-order, conservative).

## 9. Convergence
Configured in `system/fvSolution`.

- **Residual thresholds**:
  - $p\_rgh < 10^{-2}$ (or tighter depending on needs)
  - $U < 10^{-4}$
  - $T < 10^{-2}$
- Relaxation factors are heavily applied to stabilize the energy-velocity coupling ($p\_rgh = 0.7$, $U = 0.3$, $T = 0.5$).

## 10. Post-processing Definitions
- **Average Nusselt Number ($\overline{Nu}$)**: Computed by integrating the normal temperature gradient along the hot wall and multiplying by $L/T_{diff}$. Handled natively by the OpenFOAM `wallHeatFlux` function object.
- **Mid-plane velocity**: The maximum $Y$-velocity at $Y=0.5$.
