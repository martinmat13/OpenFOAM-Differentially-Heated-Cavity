# Differentially Heated Cavity

**OpenFOAM CFD | Verification | Validation | Reproducible Engineering**

> A computational engineering study of **Differentially Heated Cavity** using OpenFOAM.

## Project Status

- **Status:** Initial setup
- **Author:** Martin Mathew
- **Started:** 2026-10-02
- **Solver:** `buoyantBoussinesqSimpleFoam`
- **OpenFOAM version:** `OpenFOAM-v2512`
- **Physics:** Natural Convection, Buoyancy, Heat Transfer

---

## 1. Engineering Question

> **How effectively can buoyancy-driven natural convection transfer heat across a closed air cavity?**

**Why does this matter?**

Differentially Heated Cavity (DHC) flows are ubiquitous in engineering. They model everything from double-glazing in energy-efficient windows, cooling of electronic components in sealed enclosures, to large-scale atmospheric and oceanic circulation. Understanding and accurately predicting the heat transfer coefficient (Nusselt number) under natural convection is a fundamental requirement for thermal management design.

---

## 2. Objectives

1. Develop the OpenFOAM model using `buoyantBoussinesqSimpleFoam`.
2. Define physically justified boundary and initial conditions for the classic benchmark problem.
3. Establish numerical convergence for the coupled velocity-temperature fields.
4. Perform mesh-independence testing (specifically resolving wall boundary layers).
5. Calculate engineering quantities (e.g. wall heat flux and Nusselt number).
6. Validate against literature (e.g. De Vahl Davis 1983 benchmark).
7. Quantify numerical error and identify the transition to unsteady flows at high Rayleigh numbers.
8. Perform a controlled parameter study on the Rayleigh number.

---

## 3. Physics

**Physics included:** Natural Convection, Buoyancy (Boussinesq Approximation), Heat Transfer, Fluid Dynamics.

**Assumptions**
- Flow is steady and two-dimensional (at low/moderate Rayleigh numbers).
- Fluid is incompressible, but density variations are retained in the gravity term (Boussinesq approximation).
- Viscous dissipation in the energy equation is negligible.
- Radiation is ignored (purely convective/conductive heat transfer).

---

## 4. Numerical Method

| Item | Method / Value |
|---|---|
| Solver | `buoyantBoussinesqSimpleFoam` |
| OpenFOAM version | `TBD` |
| Fluid model | TBD |
| Solid model | N/A / TBD |
| Turbulence model | TBD |
| Pressure-velocity coupling | TBD |
| Spatial discretization | TBD |
| Temporal discretization | TBD |
| Convergence criteria | TBD |

Detailed methodology: [`docs/methodology.md`](docs/methodology.md)

---

## 5. Geometry

[Add geometry figure here.]

See [`geometry/geometry.md`](geometry/geometry.md).

---

## 6. Boundary Conditions

[Document every boundary condition and its physical justification.]

---

## 7. Verification

Verification asks:

> **Are the governing equations being solved sufficiently independently
> of numerical choices?**

Planned checks:

- mesh independence
- timestep independence
- residual convergence
- mass conservation
- energy conservation
- numerical sensitivity

See [`docs/verification.md`](docs/verification.md).

---

## 8. Validation

Validation asks:

> **Does the mathematical/physical model adequately represent the
> reference physical system?**

Planned comparison quantities:

- temperature
- velocity
- pressure
- heat-transfer coefficient
- Nusselt number
- pressure drop
- heat-transfer rate

See [`docs/validation.md`](docs/validation.md).

---

## 9. Results

### Temperature

[Final temperature field.]

### Flow field

[Velocity / streamline field.]

### Validation

[CFD versus reference comparison.]

---

## 10. Key Results

| Quantity | CFD | Reference | Error |
|---|---:|---:|---:|
| Quantity 1 | TBD | TBD | TBD |
| Quantity 2 | TBD | TBD | TBD |
| Quantity 3 | TBD | TBD | TBD |

---

## 11. Parameter Study

Planned parameters:

- [Parameter 1]
- [Parameter 2]
- [Parameter 3]

Data: `results/csv/parameter_study.csv`

---

## 12. Reproducibility

Run the case:

```bash
./scripts/run.sh
```

Post-process:

```bash
python3 scripts/postProcess.py
```

Plot:

```bash
python3 scripts/plotResults.py
```

---

## 13. Engineering Conclusions

[State what the CFD results mean from an engineering perspective.]

Avoid conclusions based only on visual inspection. Quantify important effects.

---

## 14. Limitations

- [Limitation 1]
- [Limitation 2]
- [Limitation 3]

---

## 15. Documentation

- [Methodology](docs/methodology.md)
- [Verification](docs/verification.md)
- [Validation](docs/validation.md)
- [Results](docs/results.md)
- [Geometry](geometry/geometry.md)
- [Website article](website/article.md)

---

## 16. References

[Add papers, benchmark datasets, standards and official documentation.]

---

## Author

**Martin Mathew**

Computational Engineering | CFD | OpenFOAM | Thermal Management
