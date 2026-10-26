# Validation Reference Data

This directory holds literature benchmark values and a small comparison utility. Validation here means comparison with published numerical results; the current cavity project does not contain a new experimental dataset.

## De Vahl Davis (1983)

[`benchmark_data.json`](benchmark_data.json) contains the four reference points used by [`../05_rayleigh_validation_sweep/`](../05_rayleigh_validation_sweep/README.md):

| Field | Definition | Units |
|---|---|---|
| `Ra` | Rayleigh number | dimensionless |
| `Nu_avg` | Mean Nusselt number | dimensionless |
| `u_max_dimless` | Peak horizontal velocity, scaled by $\alpha/L$ | dimensionless |
| `y_umax` | Vertical coordinate of positive horizontal-velocity peak, divided by $L$ | dimensionless |
| `v_max_dimless` | Peak vertical velocity, scaled by $\alpha/L$ | dimensionless |
| `x_vmax` | Horizontal coordinate of upward-velocity peak, divided by $L$ | dimensionless |

**Source:** De Vahl Davis, G. (1983). “Natural convection of air in a square cavity: A bench mark numerical solution.” *International Journal for Numerical Methods in Fluids*, 3(3), 249–264. [https://doi.org/10.1002/fld.1650030305](https://doi.org/10.1002/fld.1650030305).

The source describes a two-dimensional square cavity with differentially heated vertical walls and $Pr=0.71$. The values in the JSON are transcribed from the published numerical benchmark tables, not digitized from a plot. They are numerical reference values, not measurements; the article's stated solution accuracy is not supplied as a statistical uncertainty for each table entry. Do not invent error bars from the rounded values.

The validation sweep reads this JSON file directly, keeping the published comparison values and benchmark coordinates in one location. The local copy at `literature/fld.1650030305.pdf` is excluded from Git pending confirmation of redistribution rights. The DOI link is the preferred public citation; do not add the PDF to a public repository without permission.

## Additional literature records

The JSON also contains higher-Rayleigh-number entries attributed to Le Quéré (1991) and Dixit and Babu (2006). These are not used by the four-case sweep. Before using or extending those points, add complete citation metadata and check the original source's variable definitions, units, conditions, and reported accuracy. Do not treat missing uncertainty metadata as zero uncertainty.

## Comparison utility

`compare_validation.py` generates `Nu_vs_Ra_validation.png` from the literature records and a legacy project summary file. It is not the post-processor used by the `05_rayleigh_validation_sweep`; that study uses its own script and writes the CSV and Markdown outputs alongside the case results.

## Reference-data practice

For any new dataset, record:

- full bibliographic citation and persistent DOI or stable URL;
- physical and numerical conditions, including geometry, $Ra$, $Pr$, and boundary conditions;
- variable definitions, nondimensionalization, and units;
- uncertainty or accuracy as reported by the source, or explicitly state that it is not provided;
- whether values were transcribed, digitized, or recomputed, with any digitization and preprocessing details;
- license or permission status before redistributing source data or documents.
