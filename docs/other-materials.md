# Adapting the workflows to another material

Use a separate case directory and preserve the Ti–C–N reference cases. These
workflows provide a template for bulk, elastic, and slab calculations; the
Ti–C–N numerical parameters are material-specific.

## Select and validate an interaction model

Choose an interatomic potential validated for your elements, phases, and target
properties. Replacing the element labels in `TiCN.meam` does not create a new
material model. For MEAM, both element-library entries and all relevant binary
and multi-element screening terms must be consistent. Document the source,
version, fitting domain, and units. If developing a new potential, supply
reference data, fitting objectives, parameter bounds, and independent validation
sets; the original fitting workflow is not present here.

Update `pair_style`, `pair_coeff`, masses, atom types, and data-file atom style
together. The potential index order and the atom-type mapping are separate
parts of the MEAM `pair_coeff` line. Check the ordered list in both places.

## Build and record structures

Generate the appropriate crystal phase and lattice, then converge cell size.
For substitutional alloys, define the substituted sublattice, concentrations,
random seeds, and number of independent realizations. Keep generator scripts
and seeds with the data. Verify stoichiometry, atom counts, IDs, units, box
vectors, and periodicity before dynamics.

The current bulk formula assumes an 8×8×8 conventional cubic supercell. Replace
512 by the actual conventional-cell count only when the cell remains cubic.
For anisotropic or noncubic crystals, derive lattice vectors/parameters from
the relaxed box instead of taking a cube root of the total volume.

## Choose an equilibration and measurement protocol

Set temperature, pressure, timestep, damping, run duration, and averaging window
for the new material. Converge timestep and inspect energy, temperature,
pressure, structure, and atom conservation. Select the production interval
explicitly; the legacy analyzer's early-block defaults are unsuitable as a
general protocol. Record sample count and correlation-aware uncertainties.

Use consistent reference phases and atom/species normalization for energies of
formation. Total potential energy alone is not a formation energy, and the
Ti–C–N workbook's reference energies cannot be transferred to other elements.

## Elastic response

Adapt the matching `init_v*.mod` and `potential.mod` inputs. Converge positive
and negative strain magnitudes and relaxation tolerances. Check the tensor's
symmetry and mechanical stability for the material's actual crystal symmetry.
The current cubic averaging and `(C11+2*C12)/3` formula are not a general
noncubic reduction. A static minimized calculation does not measure
finite-temperature elasticity; choose a suitable finite-temperature method
when needed.

## Surfaces and layer analysis

Construct the desired orientation and termination with converged slab thickness,
lateral dimensions, and vacuum. Check whether the two faces are equivalent,
whether stoichiometry is preserved, and whether polar/charged terminations need
special treatment. Match the bulk reference and state the chemical-potential
convention. Barostat only appropriate periodic material directions; allowing
vacuum to collapse would change the intended system.

For rippling, export atom type and surface-normal position for well-defined
layers at documented timesteps. Change the hard-coded type-1/Ti versus all-other
species split if the new system has a different mapping; distinguish multiple
anion species if necessary. Replace the layer count, file ranges, peak-search
settings, and bulk reference distances. Unwrap coordinates consistently before
pooling positions across frames. Use an uncertainty estimator appropriate for
correlated trajectories instead of treating the legacy width-error formula as
a confidence interval.

## Package a reproducible result

Include the exact input structures, generator seeds, potential checksums,
software versions/build configuration, launch commands, full logs, explicit
analysis windows, and scripts that generate final tables and figures. Store
large trajectories in an appropriate data archive and link them from the
repository with checksums. Validate a fresh checkout using only documented
steps before claiming reproduction of a publication.
