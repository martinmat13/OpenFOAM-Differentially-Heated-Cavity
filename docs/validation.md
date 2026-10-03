# Validation

## 1. Reference Case

## 1. Reference Case

**Reference:** De Vahl Davis, G. (1983). "Natural convection of air in a square cavity: a bench mark numerical solution". *International Journal for Numerical Methods in Fluids*, 3(3), 249-264.

**Reference geometry:** 2D Square Cavity (H = W)

**Reference conditions:** 
- Adiabatic top and bottom walls
- Isothermal vertical walls at $T_H$ and $T_C$
- Prandtl number ($Pr$) = 0.71 (Air)
- Rayleigh numbers ($Ra$) = $10^3, 10^4, 10^5, 10^6$

## 2. Validation Quantities

| Quantity | CFD | Reference | Absolute error | Relative error |
|---|---:|---:|---:|---:|
| Max vertical velocity ($U_{y, max}$) on mid-plane $y=0.5$ | TBD | TBD | TBD | TBD |
| Max horizontal velocity ($U_{x, max}$) on mid-plane $x=0.5$ | TBD | TBD | TBD | TBD |
| Average Nusselt number ($\overline{Nu}$) | TBD | TBD | TBD | TBD |

## 3. Error Definition

Relative error:

    Error = |CFD - Reference| / |Reference| * 100

## 4. Spatial Comparison

[Temperature / velocity / pressure profiles.]

## 5. Discussion

Discuss agreement and disagreement without selectively choosing favourable
results.

Possible sources:

- physical-property assumptions
- boundary-condition uncertainty
- geometry simplification
- turbulence modelling
- numerical discretization
- experimental uncertainty

## 6. Validation Conclusion

[State quantitatively how well the model reproduces the reference.]
