# Physical and Model Dictionaries

The `constant/` directory defines the body force and constant-property Boussinesq fluid model used by the laminar baseline.

- `g`: gravity vector, directed downward in the y direction.
- `transportProperties`: Newtonian transport with `nu = 1.5e-5 m^2/s`, `beta = 0.00333333 K^-1`, `TRef = 300 K`, `Pr = 0.71`, and `Prt = 0.85`.
- `turbulenceProperties`: selects the laminar model; this case does not solve turbulence transport equations.

These air properties define a generic reference case and are not a temperature-dependent property model. The benchmark sweep changes `nu` and thermal diffusivity per Rayleigh number; do not copy the baseline viscosity into those cases. See the main [project README](../../README.md) for assumptions and the [benchmark reference](../../05_rayleigh_validation_sweep/README.md) for its property calculation.
