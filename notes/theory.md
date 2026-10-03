# Theory: Differentially Heated Cavity

## 1. Physical Problem
The Differentially Heated Cavity (DHC) is a classic benchmark in computational fluid dynamics for evaluating natural convection in a closed space. The setup consists of a square cavity where one vertical wall is maintained at a high temperature ($T_H$) and the opposing vertical wall is kept at a cold temperature ($T_C$). The horizontal walls (top and bottom) are adiabatic (perfectly insulated). 

Due to the temperature difference, the fluid near the hot wall heats up, its density decreases, and it rises due to buoyancy. Conversely, the fluid near the cold wall cools, becomes denser, and sinks. This creates a continuous recirculating flow (a convection roll or cell).

## 2. Important Dimensionless Numbers

The flow regimes and heat transfer characteristics in this case are completely governed by a set of non-dimensional parameters.

### Rayleigh Number ($Ra$)
The Rayleigh number is the primary driving parameter in natural convection, expressing the ratio of buoyancy-driven momentum transport to thermal diffusion.

$$ Ra = \frac{g \beta (T_H - T_C) L^3}{\nu \alpha} = \frac{g \beta \Delta T L^3 Pr}{\nu^2} $$

where:
- $g$: Acceleration due to gravity ($m/s^2$)
- $\beta$: Thermal expansion coefficient [$1/K$]
- $\Delta T$: Temperature difference ($T_H - T_C$) [$K$]
- $L$: Characteristic length (cavity width) [$m$]
- $\nu$: Kinematic viscosity [$\mu / \rho$, $m^2/s$]
- $\alpha$: Thermal diffusivity [$k / (\rho C_p)$, $m^2/s$]

**Physical meaning:** 
- Low $Ra$ ($< 10^3$): Conduction dominates, flow is very weak.
- Moderate $Ra$ ($10^3 - 10^7$): Laminar convection dominates.
- High $Ra$ ($> 10^8$): The flow transitions to turbulence, thermal boundary layers become very thin.

### Prandtl Number ($Pr$)
The Prandtl number is the ratio of momentum diffusivity to thermal diffusivity.

$$ Pr = \frac{\nu}{\alpha} = \frac{c_p \mu}{k} $$

**Physical meaning:** It depends entirely on the fluid. For air at room temperature, $Pr \approx 0.71$. For water, $Pr \approx 7.0$. It determines the relative thickness of the momentum and thermal boundary layers.

### Nusselt Number ($Nu$)
The Nusselt number expresses the ratio of convective to conductive heat transfer across the boundary.

$$ Nu = \frac{h L}{k} = \frac{q L}{k \Delta T} $$

where $q$ is the convective heat flux. In computational engineering, we validate natural convection simulations by integrating the heat flux at the hot/cold walls to determine the average Nusselt number ($\overline{Nu}$) and comparing it with literature (e.g., De Vahl Davis, 1983).

## 3. The Boussinesq Approximation
Instead of solving the fully compressible Navier-Stokes equations, which is computationally expensive for low-speed natural convection, we use the **Boussinesq approximation**.

1. Density variations are neglected in all equations except in the buoyancy/gravity term of the momentum equation.
2. The fluid density $\rho$ is assumed to vary linearly with temperature:
   $$ \rho = \rho_{ref} [1 - \beta (T - T_{ref})] $$

By substituting this into the gravity term, the momentum equation incorporates buoyancy as a linear source term driven by local temperature differences:
$$ \vec{F}_{buoyancy} = - \rho_{ref} \vec{g} \beta (T - T_{ref}) $$

## 4. OpenFOAM Parameters
In the provided OpenFOAM case (`constant/transportProperties`):
- `nu`: Kinematic viscosity ($\nu$)
- `beta`: Thermal expansion coefficient ($\beta$)
- `TRef`: Reference temperature ($T_{ref}$)
- `Pr`: Laminar Prandtl number ($Pr$)
- `Prt`: Turbulent Prandtl number ($Pr_t$)

The simulation solver `buoyantBoussinesqSimpleFoam` assumes a constant reference density implicitly ($\rho = 1$ inherently in the incompressible formulation, rendering the kinematic pressure $p/\rho$ identical to pressure).

## 5. Flow Structures
As $Ra$ increases:
1. **Conduction regime:** Straight, vertical isotherms.
2. **Boundary layer regime ($Ra > 10^4$):** The flow concentrates near the walls. The core becomes stratified (horizontal isotherms in the middle).
3. **Instability ($Ra > 10^7$):** Internal waves, secondary rolls in the corners, eventually leading to turbulence.
