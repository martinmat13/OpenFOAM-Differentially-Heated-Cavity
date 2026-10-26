# Initial and Boundary Fields

This directory contains the initial fields read by the laminar `buoyantBoussinesqSimpleFoam` case.

| Field | Initial value | Patch treatment |
|---|---|---|
| `T` | Uniform 300 K | `hotWall` 310 K, `coldWall` 290 K, horizontal walls zero gradient, front/back `empty` |
| `U` | Uniform zero | No slip on solid walls; front/back `empty` |
| `p`, `p_rgh` | Uniform zero | Pressure-related conditions defined per patch in the field files |
| `alphat` | Uniform zero | Calculated wall values; front/back `empty` |

The patch names are defined in `system/blockMeshDict`. For the model, transport properties, and solver settings, see [`../constant/README.md`](../constant/README.md) and [`../system/README.md`](../system/README.md). These are initialization fields, not experimental data.
