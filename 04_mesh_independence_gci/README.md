# Case 04: Mesh Verification & Grid Convergence Index (GCI) Study

**OpenFOAM CFD | Grid Refinement | Richardson Extrapolation | GCI**

> A three-grid refinement exercise for the **Differentially Heated Cavity**. The reported outputs are useful for learning the GCI workflow, but the Nusselt result does not pass the study's own asymptotic-range check.

---

## 1. Engineering Motivation & Verification Standard

In computational fluid dynamics (CFD), **verification** answers the fundamental question:
> *"Are we solving the governing equations correctly and independently of numerical grid resolution?"*

Grid refinement is one component of numerical verification. Following Richardson-extrapolation and GCI practices described by Roache (1998) and Celik et al. (2008), this subproject calculates three-grid metrics to:
1. Determine the **observed apparent order of convergence ($p$)**.
2. Estimate the **continuum zero-grid spacing solution ($f_{ext}$)** via Richardson extrapolation.
3. Calculate a nominal **Grid Convergence Index ($GCI$)**.
4. Check whether the values are consistent with the **asymptotic range of convergence**.

The computed metrics must be interpreted using that final check. The Nusselt asymptotic ratio is $\chi=15.989$, far from unity, so this dataset does not establish an asymptotic GCI uncertainty estimate. The label “verification exercise” describes the intent and workflow; it is not a claim that every quantity is verified.

---

## 2. Computational Grid Hierarchy

The 2D square cavity ($1.0 \times 1.0$ m) is discretized into three systematically refined, geometrically similar hexahedral meshes with a constant grid refinement ratio $r = 2.0$:

| Grid Level | Name | Dimensions | Total Cells ($N$) | Characteristic Spacing $h$ [m] | Refinement Ratio $r$ |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Grid 3** | Coarse | $50 \times 50$ | 2,500 | $0.020$ | — |
| **Grid 2** | Medium | $100 \times 100$ | 10,000 | $0.010$ | $r_{32} = 2.00$ |
| **Grid 1** | Fine | $200 \times 200$ | 40,000 | $0.005$ | $r_{21} = 2.00$ |

All grids are generated via `blockMesh` using the `buoyantBoussinesqSimpleFoam` steady-state solver.

---

## 3. Mathematical Formulation (ASME V&V 20 / Roache)

For any scalar or field quantity of interest $\phi$ with discrete solutions $f_1$ (Fine), $f_2$ (Medium), and $f_3$ (Coarse):

### 3.1 Step Differences
$$\epsilon_{21} = f_2 - f_1, \quad \epsilon_{32} = f_3 - f_2$$

- **Monotonic Convergence:** $\frac{\epsilon_{32}}{\epsilon_{21}} > 0$
- **Oscillatory Convergence:** $\frac{\epsilon_{32}}{\epsilon_{21}} < 0$

### 3.2 Observed Apparent Order of Convergence ($p$)
For uniform refinement ratio $r = r_{21} = r_{32} = 2.0$:
$$p = \frac{\ln\left| \frac{\epsilon_{32}}{\epsilon_{21}} \right|}{\ln(r)}$$

### 3.3 Richardson Extrapolation (Continuum Solution)
$$f_{ext}^{21} = f_1 + \frac{f_1 - f_2}{r^p - 1}$$

### 3.4 Relative Error Estimates
- **Approximate Relative Error:**
  $$e_a^{21} = \left| \frac{f_1 - f_2}{f_1} \right| \times 100\%$$
- **Extrapolated Relative Error:**
  $$e_{ext}^{21} = \left| \frac{f_{ext}^{21} - f_1}{f_{ext}^{21}} \right| \times 100\%$$

### 3.5 Grid Convergence Index (GCI)
Using the recommended ASME safety factor $F_s = 1.25$ for a three-grid study:
- **Fine Grid Uncertainty:**
  $$GCI_{fine}^{21} = \frac{F_s \cdot e_a^{21}}{r^p - 1}$$
- **Medium Grid Uncertainty:**
  $$GCI_{medium}^{32} = \frac{F_s \cdot e_a^{32} \cdot r^p}{r^p - 1}$$

### 3.6 Verification of Asymptotic Range
$$\chi = \frac{GCI_{32}}{r^p \cdot GCI_{21}} \approx 1.0$$
When $\chi \approx 1.0$, the discrete solutions are verified to lie within the asymptotic convergence regime, confirming the validity of the Richardson extrapolation.

---

## 4. Directory Structure

```
04_mesh_independence_gci/
├── Allclean                    # Cleans all 3 cases and results
├── Allrun                      # Executes all 3 grids sequentially + post-processing
├── README.md                   # Complete technical documentation
├── cases/
│   ├── grid3_coarse/           # 50x50 mesh case
│   │   ├── 0/
│   │   ├── constant/
│   │   ├── system/
│   │   ├── Allrun
│   │   └── Allclean
│   ├── grid2_medium/           # 100x100 mesh case
│   │   ├── 0/
│   │   ├── constant/
│   │   ├── system/
│   │   ├── Allrun
│   │   └── Allclean
│   └── grid1_fine/             # 200x200 mesh case
│       ├── 0/
│       ├── constant/
│       ├── system/
│       ├── Allrun
│       └── Allclean
├── scripts/
│   └── postprocess_gci.py      # Automated ASME V&V 20 calculation & plot generation
└── results/
    ├── gci_summary_table.csv   # Quantified numerical metrics
    ├── gci_summary_table.md    # Markdown table for reporting
    ├── mesh_comparison.png     # Visual mesh zoom diagram
    ├── midY_Uy_comparison.png  # Vertical velocity profile on y=0.5
    ├── midX_Ux_comparison.png  # Horizontal velocity profile on x=0.5
    ├── midY_T_comparison.png   # Temperature profile on y=0.5
    ├── nu_distribution_comparison.png # Heated wall Nusselt number
    ├── gci_error_bars_Nu.png   # Nu convergence with GCI uncertainty bars
    ├── gci_error_bars_velocity.png # v_max convergence with GCI error bars
    └── residuals_convergence.png # Residual histories across all meshes
```

---

## 5. Execution Instructions

### Complete Automated Execution
To run all three meshes from start to finish and produce the complete verification report:
```bash
cd 04_mesh_independence_gci
./Allrun
```

### Individual Grid Execution
Each grid can be independently tested:
```bash
cd cases/grid2_medium
./Allrun
```

### Standalone Post-Processing & GCI Computation
```bash
python3 scripts/postprocess_gci.py
```

---

## 6. Reported Grid-Refinement Calculations

The post-processing pipeline reports the following values. The table is retained as the output of the current calculation; its GCI and extrapolation columns are not equally interpretable for all quantities.

| Variable | Unit | Coarse (50x50) | Medium (100x100) | Fine (200x200) | Extrapolated ($h \to 0$) | Apparent Order ($p$) | $e_a^{21}$ (%) | $GCI_{fine}$ (%) | Asymptotic Ratio ($\chi$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Average Nusselt ($\overline{Nu}$)** | [-] | 41.1717 | 58.4341 | 59.5341 | **59.6090** | 3.97 | 1.85% | **0.16%** | 15.989 |
| **Max Vertical Velocity ($v_{max}$)** | [m/s] | 0.0854 | 0.1285 | 0.1935 | **1.0989** | 0.10 | 33.58% | **584.87%** | 0.999 |
| **Dimensionless $v^*$** | [-] | 4043.32 | 6083.42 | 9159.38 | **52015.84** | 0.10 | 33.58% | **584.87%** | 0.999 |
| **Max Horizontal Velocity ($u_{max}$)** | [m/s] | 0.0451 | 0.0226 | 0.0278 | **0.0278** | 1.00 | 18.60% | **23.25%** | 1.000 |
| **Dimensionless $u^*$** | [-] | 2132.75 | 1069.50 | 1313.94 | **1313.94** | 1.00 | 18.60% | **23.25%** | 1.000 |
| **Center Temperature ($T_{center}$)** | [K] | 299.8630 | 300.0360 | 300.0150 | **300.0150** | 1.00 | 0.01% | **0.01%** | 1.000 |

### Interpretation and limitations

1. **Nusselt refinement is monotonic but not demonstrably asymptotic.** The reported values increase from 41.1717 to 58.4341 to 59.5341. The fine/medium difference is 1.85%, and the script calculates $GCI_{fine}=0.16\%$ and $\overline{Nu}_{ext}=59.6090$. However, the reported $\chi=15.989$ is not approximately one. Therefore, the extrapolation and GCI must not be presented as a validated uncertainty interval or proof of grid independence. The apparent order alone does not supersede this failed check.
2. **Velocity metrics are not converged by this calculation.** The vertical-velocity extrapolation is 1.0989 m/s despite a finest-grid value of 0.1935 m/s; its reported GCI is 584.87%. The horizontal-velocity values are non-monotonic (0.0451, 0.0226, 0.0278 m/s). These values show strong sensitivity to the grid and/or extraction, not reliable continuum estimates.
3. **The center temperature is insensitive in the reported sequence.** Its values vary by only a small fraction of a kelvin, but that agreement does not establish convergence of gradients, wall heat flux, or velocity peaks.
4. **Treat the boundary-layer interpretation as qualitative.** The report quotes a scale $\delta\sim L Ra^{-1/4}$ at $Ra\approx2\times10^9$, but the three-grid results alone do not quantify boundary-layer thickness or demonstrate that it is resolved.

Before claiming formal verification, check the input conditions and mesh hierarchy, ensure quantities of interest are extracted consistently, obtain monotonic/asymptotic behavior where appropriate, and rerun the analysis with a justified uncertainty method. These results are separate from and cannot supply a grid-error estimate for the $Ra=10^3$–$10^6$ sweep.

## 7. References

1. Celik, I. B., Ghia, U., Roache, P. J., Freitas, C. J., Coleman, H., & Raad, P. E. (2008). “Procedure for estimation and reporting of uncertainty due to discretization in CFD applications.” *Journal of Fluids Engineering*, 130(7), 078001. [https://doi.org/10.1115/1.2960953](https://doi.org/10.1115/1.2960953).
2. Roache, P. J. (1998). *Verification and Validation in Computational Science and Engineering*. Hermosa Publishers.
3. ASME. *V&V 20: Standard for Verification and Validation in Computational Fluid Dynamics and Heat Transfer*. Consult the applicable edition for formal engineering work.

## Author
**Martin Mathew**  
Computational Engineering | CFD | OpenFOAM | Thermal Verification
