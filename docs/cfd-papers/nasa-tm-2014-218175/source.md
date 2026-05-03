# NASA TM-2014-218175 — Implementation, verification, and validation of the SA turbulence model in OVERFLOW (stand-in)

> **Stand-in for the original NTRS PDF.** Replace with the full PDF via Git
> LFS when ingestion goes live. Source URL:
> <https://ntrs.nasa.gov/citations/20140017079>
> Excerpt of: NASA TM-2014-218175 (Aug 2014), abstract + §1 Introduction.

The Spalart-Allmaras (SA) one-equation turbulence model has been
re-implemented and re-verified in the NASA OVERFLOW structured-grid
RANS solver against the canonical verification cases curated by the
NASA Langley Turbulence Modeling Resource (TMR), now maintained at
<https://tmbwg.github.io/turbmodels/> as of the 2026-02 site relocation.
The verification matrix covered the 2D zero-pressure-gradient flat plate,
the 2D bump-in-channel, and the 2D NACA 0012 airfoil. Grid convergence
was demonstrated on five successively refined grids per case, with the
finest 2D NACA-0012 grid containing approximately **1.7M cells at wall
y⁺ ≤ 1** at Reynolds number 6×10⁶ and Mach 0.15.

Verification compared C_f, C_p, and integrated C_l / C_d against the
TMR reference solutions from CFL3D and FUN3D within ±0.5% on the finest
grid for all three canonical cases. Validation extended to the 3D
ONERA-M6 wing at transonic Mach 0.84, with C_p distributions at seven
spanwise stations agreeing with experimental data of Schmitt &
Charpin (AGARD AR-138) to within experimental uncertainty.

The implementation includes both the standard SA model and the SA-neg
modification of Allmaras et al. (2012) for improved robustness when the
working variable goes negative on coarse grids. A residual-based
convergence criterion of 1×10⁻¹⁰ density residual was used for all
verification runs; grid-convergence indices (GCI) per Roache (1994)
are reported for all integrated quantities.
