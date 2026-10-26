# Physical and Turbulence Dictionaries

The transient case uses a constant-property Boussinesq fluid with a RANS closure.

- `g`: downward gravitational acceleration.
- `transportProperties`: Newtonian fluid with `nu = 1.5e-5 m^2/s`, `beta = 0.00333333 K^-1`, `TRef = 300 K`, `Pr = 0.71`, and `Prt = 0.85`.
- `turbulenceProperties`: RAS with `kOmegaSST`.

The turbulence model and initial fields do not make the calculation a validation of a turbulent physical regime. It is a separate transient modeling exercise. See [`../system/README.md`](../system/README.md) for the PIMPLE and time-step controls.
