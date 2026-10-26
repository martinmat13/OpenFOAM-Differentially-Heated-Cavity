# De Vahl Davis (1983) Benchmark Validation Summary

| Rayleigh Number ($Ra$) | Quantity | OpenFOAM (CFD) | De Vahl Davis (1983) | Error (%) | Coordinate ($x/L$ or $y/L$) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Ra = $10^3$** | Average Nusselt ($\overline{Nu}$) | **1.072** | 1.118 | 4.13% | Wall ($x=0$) |
| | Max Horizontal Velocity ($u_{max}^*$) | **3.35** | 3.65 | 8.22% | $y/L = 0.819$ (Bench: 0.813) |
| | Max Vertical Velocity ($v_{max}^*$) | **3.38** | 3.70 | 8.65% | $x/L = 0.171$ (Bench: 0.178) |
| **Ra = $10^4$** | Average Nusselt ($\overline{Nu}$) | **2.326** | 2.243 | 3.71% | Wall ($x=0$) |
| | Max Horizontal Velocity ($u_{max}^*$) | **16.45** | 16.18 | 1.67% | $y/L = 0.819$ (Bench: 0.823) |
| | Max Vertical Velocity ($v_{max}^*$) | **19.79** | 19.62 | 0.88% | $x/L = 0.121$ (Bench: 0.119) |
| **Ra = $10^5$** | Average Nusselt ($\overline{Nu}$) | **4.586** | 4.519 | 1.47% | Wall ($x=0$) |
| | Max Horizontal Velocity ($u_{max}^*$) | **35.96** | 34.73 | 3.53% | $y/L = 0.859$ (Bench: 0.855) |
| | Max Vertical Velocity ($v_{max}^*$) | **68.37** | 68.59 | 0.31% | $x/L = 0.070$ (Bench: 0.066) |
| **Ra = $10^6$** | Average Nusselt ($\overline{Nu}$) | **8.975** | 8.800 | 1.99% | Wall ($x=0$) |
| | Max Horizontal Velocity ($u_{max}^*$) | **66.88** | 64.63 | 3.48% | $y/L = 0.859$ (Bench: 0.850) |
| | Max Vertical Velocity ($v_{max}^*$) | **217.86** | 219.36 | 0.68% | $x/L = 0.040$ (Bench: 0.038) |

*Notes: Reference velocities are non-dimensionalized by $\alpha/L$. Prandtl number $Pr = 0.71$. Each case uses a $100 \times 100$ in-plane mesh and bounded Gauss upwind convection schemes. The hot-wall Nusselt estimate uses $T(x=0.005\,\mathrm{m},y)$ and a finite difference.*

Four-point log-log fit: $\overline{Nu} = 0.1331\,Ra^{0.3064}$ (descriptive fit over these cases only).

Reference: De Vahl Davis, G. (1983), “Natural convection of air in a square cavity: A bench mark numerical solution,” *International Journal for Numerical Methods in Fluids*, 3(3), 249–264. [https://doi.org/10.1002/fld.1650030305](https://doi.org/10.1002/fld.1650030305).
