# ASME V&V 20 Grid Convergence Index (GCI) Summary

| Variable | Unit | Coarse (50x50) | Medium (100x100) | Fine (200x200) | Extrapolated (h=0) | Apparent Order (p) | $e_a^{21}$ (%) | $GCI_{fine}$ (%) | Asymptotic Ratio ($\chi$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Average Nusselt Number (Nu_avg)** | [-] | 41.1717 | 58.4341 | 59.5341 | **59.6090** | 3.97 | 1.85% | **0.16%** | 15.989 |
| **Max Vertical Velocity (v_max)** | [m/s] | 0.0854 | 0.1285 | 0.1935 | **1.0989** | 0.10 | 33.58% | **584.87%** | 0.999 |
| **Dimensionless v_star** | [-] | 4043.3175 | 6083.4220 | 9159.3787 | **52015.8406** | 0.10 | 33.58% | **584.87%** | 0.999 |
| **Max Horizontal Velocity (u_max)** | [m/s] | 0.0451 | 0.0226 | 0.0278 | **0.0278** | 1.00 | 18.60% | **23.25%** | 1.000 |
| **Dimensionless u_star** | [-] | 2132.7501 | 1069.5014 | 1313.9449 | **1313.9449** | 1.00 | 18.60% | **23.25%** | 1.000 |
| **Center Temperature (T_center)** | [K] | 299.8630 | 300.0360 | 300.0150 | **300.0150** | 1.00 | 0.01% | **0.01%** | 1.000 |

*Notes: The table lists the current script's calculated outputs for safety factor $F_s = 1.25$ and refinement ratio $r = 2.0$. For average Nusselt number, the reported asymptotic ratio is $\chi=15.989$, not approximately 1; the reported fine-grid GCI and extrapolation are therefore not demonstrated uncertainty estimates. See the interpretation and limitations in [README.md](../README.md).*
