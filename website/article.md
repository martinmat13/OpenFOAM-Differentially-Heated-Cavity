---
title: "The 'Hello World' of Thermal CFD: The Differentially Heated Cavity"
author: "Martin Mathew"
date: "2026-10-07"
category: "Thermal CFD"
tags: ["OpenFOAM", "Natural Convection", "CFD", "Validation"]
---

# Differentially Heated Cavity: Baseline and Foundations of a Thermal Case

If you are embarking on a journey to master computational heat transfer, the **Differentially Heated Cavity (DHC)** is your starting line. It is the "Hello World" of thermal CFD—a deceptively simple problem that encapsulates the complex coupling between fluid dynamics and thermodynamics. 

In this article, we will break down the fundamental setup of a 2D DHC using OpenFOAM, walking through the physics, methodology, solving process, neat post-processing, and finally, validation against standard benchmarks. This will serve as a foundational guide for any master project involving natural convection.

---

## 1. The Physical Problem

Imagine a square box filled with air. The left wall is heated to a higher temperature ($T_H$), and the right wall is cooled to a lower temperature ($T_C$). The top and bottom walls are perfectly insulated (adiabatic). 

There is no fan driving the air. Instead, the air near the hot wall heats up, expands, and becomes less dense. Gravity pulls the denser, cooler air downwards, forcing the lighter, hotter air upwards. This buoyancy-driven flow creates a continuous circulation loop known as **natural convection**.

**Why does this matter?**
Understanding this mechanism is crucial for engineering applications ranging from double-glazing in windows and passive cooling of electronics to large-scale oceanic circulation models.

---

## 2. Setting Up the Case in OpenFOAM

To simulate this, we use OpenFOAM, specifically the `buoyantBoussinesqSimpleFoam` solver. Let's break down the setup.

### The Boussinesq Approximation
Instead of using a fully compressible solver (which is computationally expensive), we use the **Boussinesq approximation**. It assumes that density variations are negligible in all terms of the governing equations *except* the buoyancy source term in the momentum equation. This is a highly accurate and efficient assumption for small temperature differences.

### Geometry and Mesh
- **Domain**: A 2D square cavity ($H = 1.0\text{ m}, W = 1.0\text{ m}$). In OpenFOAM, this is modeled as a 3D block with a thickness of 1 element (e.g., $D = 0.1\text{ m}$) and `empty` boundary conditions on the front and back faces.
- **Mesh**: A structured, uniform hexahedral grid generated via `blockMesh`.

### Boundary Conditions
Proper boundary conditions (BCs) are the bridge between reality and the mathematical model.

| Boundary | Variable | Condition Type | Physical Meaning |
|---|---|---|---|
| **Hot Wall** (Left) | Temperature (`T`) | `fixedValue` ($310\text{ K}$) | Isothermal heating |
| | Velocity (`U`) | `noSlip` | Stationary wall |
| **Cold Wall** (Right) | Temperature (`T`) | `fixedValue` ($290\text{ K}$) | Isothermal cooling |
| | Velocity (`U`) | `noSlip` | Stationary wall |
| **Top & Bottom** | Temperature (`T`) | `zeroGradient` | Perfectly insulated (adiabatic) |
| | Velocity (`U`) | `noSlip` | Stationary walls |

---

## 3. Numerical Methodology and Models

Our physics are governed by the Navier-Stokes equations, coupled with the energy equation.

1. **Solver**: `buoyantBoussinesqSimpleFoam` solves the steady-state, incompressible equations with Boussinesq buoyancy.
2. **Algorithm**: SIMPLE (Semi-Implicit Method for Pressure Linked Equations) handles the pressure-velocity coupling.
3. **Discretization Schemes** (in `system/fvSchemes`):
   - *Gradients*: `Gauss linear` (Second-order central).
   - *Divergence*: `bounded Gauss upwind` (First-order upwind for stability, though second-order `linearUpwind` is preferred for high accuracy at higher Rayleigh numbers).
   - *Laplacians*: `Gauss linear corrected`.

To keep the heavily coupled momentum and energy equations stable during the iterative solving process, **relaxation factors** (defined in `system/fvSolution`) are essential. We typically relax pressure ($0.7$), velocity ($0.3$), and temperature ($0.5$).

---

## 4. Solving and Convergence

Running the solver is straightforward, but knowing *when* to stop is engineering. We monitor:
- **Residuals**: The error in solving the linear system for each equation. We aim for $p\_rgh < 10^{-2}$, and $U, T < 10^{-4}$.
- **Monitors**: It is best practice to monitor physical quantities during the run, such as the maximum vertical velocity or the wall heat flux, to ensure they reach a steady plateau.

---

## 5. Post-Processing: Neat and Automated

Visualizing a bunch of numbers is where the physics actually comes to life. While ParaView is great for exploration, automated Python scripts using **PyVista** and **Pandas** allow for reproducible, neat post-processing.

Here is the temperature contour and velocity magnitude contour generated automatically using our high-quality PyVista script:

![Temperature Contour for Ra=4.2e9](/home/martin8991/OpenFOAM_cases/Thermal/OpenFOAM-Differentially-Heated-Cavity/results/T_contour_Ra4.2e09.png)

![Velocity Contour for Ra=4.2e9](/home/martin8991/OpenFOAM_cases/Thermal/OpenFOAM-Differentially-Heated-Cavity/results/U_contour_Ra4.2e09.png)

A standard post-processing pipeline for this case extracts:
1. **Contour Plots**: Generating high-quality images directly from OpenFOAM data using PyVista.
2. **Mid-plane Profiles**: Plotting the vertical velocity ($U_y$) along the horizontal mid-plane ($y=0.5$) and horizontal velocity ($U_x$) along the vertical mid-plane ($x=0.5$).
3. **Engineering Metrics**: The most important metric is the **Nusselt Number ($Nu$)**, which represents the ratio of convective to conductive heat transfer. 

---

## 6. Benchmark and Validation (Ra = $10^5$)

Before we can trust our model to simulate novel, complex designs, we must prove it can accurately replicate a known truth. For the DHC, the gold standard is the **De Vahl Davis (1983)** benchmark.

To match the standard **Ra = $10^5$** benchmark, you should configure `constant/transportProperties` as follows:
- **Prandtl Number (`Pr`)**: 0.71
- **Kinematic Viscosity (`nu`)**: 1e-3 m²/s
- **Thermal Expansion (`beta`)**: 7.176e-4 1/K
- **Temperature Difference (`Delta T`)**: 20 K (e.g. 310 K and 290 K)

Running this exact case will yield results that can be directly compared to the literature:
- **Max Mid-plane X Velocity ($U_{x, max}$)**: Target dimensionless is 34.73
- **Max Mid-plane Y Velocity ($U_{y, max}$)**: Target dimensionless is 68.59
- **Average Nusselt Number ($\overline{Nu}$)**: Target is 4.519

If the relative error between our OpenFOAM results and the benchmark is sufficiently low, we can confidently say our baseline thermal case is **validated**.

---

## 7. Conclusion

By setting up, running, and validating the Differentially Heated Cavity, we have laid a rock-solid foundation. We have confirmed that our numerical schemes, boundary conditions, and fluid property implementations correctly model buoyancy-driven flows. 

With this baseline established, the master project can confidently expand into more complex geometries, transient turbulent flows, or coupled conjugate heat transfer scenarios.
