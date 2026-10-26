# Physical and Turbulence Dictionaries

The SST case uses the same constant-property Boussinesq setup as the baseline, plus a Reynolds-averaged turbulence model.

- `g`: downward gravitational acceleration.
- `transportProperties`: Newtonian fluid with `nu = 1.5e-5 m^2/s`, `beta = 0.00333333 K^-1`, `TRef = 300 K`, `Pr = 0.71`, and `Prt = 0.85`.
- `turbulenceProperties`: RAS enabled with `kOmegaSST`.

The `0/` directory provides initial `k`, `omega`, `nut`, and `alphat` fields. `Prt` is the turbulent Prandtl number used for turbulent thermal diffusivity. This case is not the laminar De Vahl Davis sweep and should not be treated as its validation result.
