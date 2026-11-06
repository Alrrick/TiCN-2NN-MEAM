# Use the methods with another material

I share these workflows as a starting point for new research. You can reuse the
steps for building a crystal, running a simulation, and measuring its response.
The potential settings themselves are specific to Ti–C–N.

I recommend first running the [README example](../README.md), then copying one
case into a new folder under `runs/`. Keep your changes there so you can compare
them with my original files.

## 1. Choose a suitable potential

An **interatomic potential** is the mathematical model for how atoms interact.
Choose one tested for your elements, crystal structure, and research question.
Changing element names in `TiCN.meam` does not make it suitable for a new material.

For a MEAM model, check both the element library and the settings for interactions
between elements. Record where the files came from and which version you use.
If you are developing a new potential, you will also need fitting data and
independent tests. My original fitting program is not included here.

When I change a model, I check these settings together:

| Setting or file | What must match |
| --- | --- |
| `pair_style` | The kind of interaction model |
| `pair_coeff` | Potential filenames, element order, and atom-type mapping |
| `mass` | The mass assigned to each atom type |
| `atom_style` and the `.data` file | The format of the atom records |

My type mapping is 1 = Ti, 2 = C, 3 = N. Your material may need a different one.

## 2. Build the starting crystal

Choose the crystal structure, cell dimensions, and mixture of elements.
Check the atom count and composition before running the simulation.
For a random mixture, save the program and random seed used to place the atoms.
That lets someone else create the same starting structure.

I test more than one box size before relying on a result. If a larger box changes
the answer a lot, the smaller box is not yet large enough for that measurement.
This is a **convergence check**: vary a numerical setting until the result changes
little enough for your research goal.

My bulk analysis assumes 512 cubic cells. Only use
`a = (V/512)**(1/3)` when that geometry applies. For another number of cubic
cells, change 512 to the correct count. For a noncubic crystal, measure the
separate box directions instead of using one cube root.

## 3. Let the system settle before measuring

Set the temperature, pressure, time step, and run length for the new material.
Plot temperature, pressure, and energy over time. Choose a measurement window
after the initial changes have settled. I call this part the **production stage**.

My original analyzer uses early log sections, so its default selection should
not be carried over without checking. Choose the right block and row range for
your new run, and record that choice with the results.

Nearby time samples can be related to each other. To estimate uncertainty, I
recommend comparing averages over longer blocks or running independent repeats.
The spread of individual samples alone does not tell you how accurate the mean is.

For formation energy, calculate references for the new material's elements with
the same potential. The Ti, C, and N reference values in my workbook do not apply
to other elements.

## 4. Check stiffness with small deformations

Use the elastic example in the [run guide](reproduction.md). Change the matching
`init_v*.mod` and `potential.mod` files for your structure and potential.

Try several small stretches and shears. Tighten the relaxation settings and
check that the elastic constants stay close to the same values. The constants
form a table called the **elastic tensor**, which describes the response in
different directions.

My scripts report cubic averages and use `B = (C11 + 2*C12)/3`. A crystal with
another symmetry can need different formulas. Also check mechanical stability:
the structure must resist the small shape changes you are measuring.
For stiffness at a nonzero temperature, use a method that includes thermal
motion; my static calculation does not do that.

## 5. Build and test the surface

Choose the crystal face and the elements exposed at the top and bottom.
Build a slab with enough crystal layers and enough vacuum to separate it from
its repeated copies. Test larger thicknesses, areas, and vacuum gaps to check
that the result is stable.

Check whether the two faces are equivalent and whether the slab has the intended
element ratio. Unequal or polar faces may need extra reference-energy choices.
Match the bulk reference to the slab and explain how you calculate surface energy.
Control pressure only in directions where changing the box makes physical sense;
shrinking the vacuum gap changes the system you meant to study.

For layer rippling, export atom types and positions along the direction normal
to the surface. Record the layer definitions and simulation times. My script
groups type 1 as Ti and every other type as X. Change this rule if your material
needs different groups or separate carbon and nitrogen measurements.

Check layer counts, file ranges, and reference distances too. If atoms cross a
periodic boundary, put their positions in a consistent coordinate frame before
averaging. Replace the old width-error formula with a suitable uncertainty
calculation; I describe its limits in the run guide.

## 6. Leave a record others can follow

I recommend saving the exact structures, seeds, potential files, software
versions, commands, logs, and analysis ranges used for each result. Include
scripts that produce your final plots and tables.

If trajectories are too large for Git, put them in a data archive and link to
them. A **checksum**, such as SHA-256, helps readers check that their downloaded
file matches yours. Finally, try your instructions in a fresh copy of the
repository. That is the best way to find missing steps before someone else does.
