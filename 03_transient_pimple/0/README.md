# Initial and Boundary Fields

This directory contains the initial fields for the transient `buoyantBoussinesqPimpleFoam` RAS case.

| Field group | Fields | Initial state and purpose |
|---|---|---|
| Flow and thermal | `U`, `p`, `p_rgh`, `T` | Initially quiescent flow, zero pressure fields, and uniform 300 K fluid; the vertical walls impose 310 K and 290 K |
| Turbulence | `k`, `omega`, `nut`, `alphat` | Initialization fields for the `kOmegaSST` model and turbulent heat transport |

Solid boundaries are no-slip. Temperature is zero-gradient on the top and bottom, and the front/back patches are `empty`. Exact patch values and types are given in the OpenFOAM files. See [`../constant/README.md`](../constant/README.md) for fluid and turbulence models and [`../system/README.md`](../system/README.md) for the time-integration setup.
