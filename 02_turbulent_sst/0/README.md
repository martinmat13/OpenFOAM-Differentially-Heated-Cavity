# Initial and Boundary Fields

This directory contains the initial fields for the steady `buoyantBoussinesqSimpleFoam` SST case.

| Field group | Fields | Initial state and purpose |
|---|---|---|
| Flow and thermal | `U`, `p`, `p_rgh`, `T` | Quiescent velocity, zero pressure fields, and uniform 300 K fluid; hot/cold side temperatures are imposed in `T` |
| Turbulence | `k`, `omega`, `nut`, `alphat` | Initial turbulence variables and turbulent transport fields required by the selected RAS model |

All solid walls are stationary; top and bottom are adiabatic for `T`, and front/back faces use `empty` for the two-dimensional mesh. Check the field files for the exact OpenFOAM patch types and values. Model coefficients are in [`../constant/README.md`](../constant/README.md); mesh and numerical settings are in [`../system/README.md`](../system/README.md).
