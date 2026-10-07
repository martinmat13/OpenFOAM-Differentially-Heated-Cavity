# Theory: Differentially Heated Cavity

## 1. Physical Problem
The Differentially Heated Cavity (DHC) is a classic benchmark in computational fluid dynamics for evaluating natural convection in a closed space. The setup consists of a square cavity where one vertical wall is maintained at a high temperature ($T_H$) and the opposing vertical wall is kept at a cold temperature ($T_C$). The horizontal walls (top and bottom) are adiabatic (perfectly insulated). 

Due to the temperature difference, the fluid near the hot wall heats up, its density decreases, and it rises due to buoyancy. Conversely, the fluid near the cold wall cools, becomes denser, and sinks. This creates a continuous recirculating flow (a convection roll or cell).

## 2. Important Dimensionless Numbers

The flow regimes and heat transfer characteristics in this case are completely governed by a set of non-dimensional parameters.

### Grashof Number ($Gr$)
Before discussing the Rayleigh number, it is helpful to introduce the Grashof number. It represents the ratio of buoyancy forces to viscous forces acting on a fluid. 

$$ Gr = \frac{g \beta (T_H - T_C) L^3}{\nu^2} $$

**Physical meaning:** 
- If $Gr$ is high, buoyancy forces are strong enough to overcome the fluid's internal friction (viscosity), leading to vigorous fluid motion. 
- In natural convection, $Gr$ plays the same role that the Reynolds number ($Re$) plays in forced convection. It dictates whether the flow will be laminar or turbulent.

### Prandtl Number ($Pr$)
The Prandtl number is an intrinsic property of the fluid itself. It is the ratio of momentum diffusivity (kinematic viscosity) to thermal diffusivity.

$$ Pr = \frac{\nu}{\alpha} = \frac{c_p \mu}{k} $$

**Physical meaning:** 
- **$Pr \approx 1$ (e.g., air $\approx 0.71$):** Momentum and heat diffuse through the fluid at roughly the same rate. The velocity and thermal boundary layers will be of similar thickness.
- **$Pr \gg 1$ (e.g., water $\approx 7.0$, engine oil $\approx 10^4$):** Heat diffuses very slowly compared to momentum. The thermal boundary layer is much thinner than the velocity boundary layer.
- **$Pr \ll 1$ (e.g., liquid metals $\approx 0.01$):** Heat diffuses much faster than momentum. The fluid becomes uniformly hot very quickly before it even has a chance to move significantly.

### Rayleigh Number ($Ra$)
The Rayleigh number is the primary driving parameter in natural convection, expressing the ratio of buoyancy-driven momentum transport to thermal diffusion. It is simply the product of the Grashof and Prandtl numbers.

$$ Ra = Gr \cdot Pr = \frac{g \beta (T_H - T_C) L^3}{\nu \alpha} $$

where:
- $g$: Acceleration due to gravity ($m/s^2$)
- $\beta$: Thermal expansion coefficient ($1/K$). This dictates how much the fluid expands when heated. For an ideal gas, $\beta \approx 1/T_{ref}$.
- $\nu$: Kinematic viscosity ($\mu / \rho$, $m^2/s$). Represents the fluid's resistance to flow.
- $\alpha$: Thermal diffusivity ($k / (\rho C_p)$, $m^2/s$). Represents how fast heat can spread through the fluid bulk.

**Physical meaning in reality:** 
- **Low $Ra$ ($&lt; 10^3$):** Buoyancy is too weak to overcome viscosity and thermal diffusion. The fluid is practically stationary, and heat transfers primarily via **pure conduction**, just like a solid block.
- **Moderate $Ra$ ($10^3 - 10^7$):** Buoyancy wins. **Laminar convection** dominates, and a steady, predictable recirculating vortex forms in the cavity.
- **High $Ra$ ($&gt; 10^8$):** The flow becomes chaotic and unsteady. The boundary layers near the walls become extremely thin, and the flow transitions to **turbulence**.

### Nusselt Number ($Nu$)
The Nusselt number expresses the ratio of convective to conductive heat transfer across the boundary.

$$ Nu = \frac{h L}{k} = \frac{q L}{k \Delta T} $$

where $q$ is the convective heat flux. 

**Physical meaning:** 
- If $Nu = 1$, the fluid is completely stationary, and all heat transfer is purely by conduction. 
- If $Nu = 10$, convection is transferring 10 times more heat than conduction would on its own. In CFD, calculating the average Nusselt number ($\overline{Nu}$) on the hot/cold walls is the primary way we validate natural convection simulations against experimental or benchmark data (e.g., De Vahl Davis, 1983).

## 3. The Boussinesq Approximation
Instead of solving the fully compressible Navier-Stokes equations, which is computationally expensive for low-speed natural convection, we use the **Boussinesq approximation**.

1. Density variations are neglected in all equations except in the buoyancy/gravity term of the momentum equation.
2. The fluid density $\rho$ is assumed to vary linearly with temperature:
$$ \rho = \rho_{ref} (1 - \beta (T - T_{ref})) $$

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
2. **Boundary layer regime ($Ra &gt; 10^4$):** The flow concentrates near the walls. The core becomes stratified (horizontal isotherms in the middle).
3. **Instability ($Ra &gt; 10^7$):** Internal waves, secondary rolls in the corners, eventually leading to turbulence.
