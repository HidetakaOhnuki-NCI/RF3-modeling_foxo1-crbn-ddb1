# Computational Methods

## RosettaFold3 structure generation

Protein complex structures are generated using RosettaFold3 (RF3; Foundry
checkpoint `rf3_foundry_01_24_latest_remapped.ckpt`), with the experimentally
determined DDB1-CRBN-GSPT1-CC-90009 structure (PDB 6XK9) as the reference.
Inputs comprise human DDB1 (UniProt Q16531-1; chain A, observed template
residues 2-1140), human CRBN (UniProt Q96SW2-1; chain B, observed template
residues 46-442), the CRBN-bound Zn ion (chain M), CC-90009 where specified
(chain L), and GSPT1 or a FOXO1 peptide (chain F).

The release protocol uses 200 diffusion steps, 10 recycles, a diffusion batch
size of 1, and one random seed per replicate model in every comparison arm.
Zn and chain F are specified through the RF3
`ground_truth_conformer_selection` option in both CC-90009 conditions; chain L
is added when CC-90009 is present. This atom-level conditioning supplies
reference geometry but does not rigidly fix the output coordinates. The
analysis evaluates the reproducibility and sequence compatibility of
conditioned interfaces rather than unrestricted binding-site discovery.

## GSPT1 control analysis

The protocol-matched analysis requires 50 structures for each of four arms:
GSPT1 wild type with and without CC-90009, GSPT1 G575N with CC-90009, and
randomized GSPT1 with CC-90009. GSPT1 comprises UniProt P15170-2 residues
437-632. CRBN residues with at least one heavy atom less than 4.0 A from a
GSPT1 heavy atom constitute the predicted interface. Similarity to the CRBN
interface in PDB 6XK9 is quantified by the Jaccard index, defined as the size of
the intersection divided by the size of the union of the predicted and
reference CRBN residue sets.

Jaccard distributions are compared using prespecified one-sided Mann-Whitney U
tests: GSPT1 wild type with CC-90009 versus wild type without CC-90009, and
GSPT1 wild type with CC-90009 versus G575N with CC-90009. Each dot represents
one independently seeded structure model. Box plots show the median and
interquartile range; whiskers extend to 1.5 times the interquartile range, and
triangles indicate arithmetic means.

The representative structure for Panel A is selected from hard-clash-free
models with a GSPT1-CRBN minimum heavy-atom distance of 6.0 A or less, a CRBN
interface Jaccard similarity of at least 0.5, and a GSPT1 Gly575-to-CC-90009
distance of 6.0 A or less. Gly575 corresponds to G574 in PDB 6XK9 chain-F
author numbering. Displayed GSPT1-CRBN contacts in ChimeraX use a separate
3.6-A maximum distance.

## FOXO1 peptide modeling and Panel C analysis

Human FOXO1 (UniProt Q12778; 655 residues) is divided into 32 overlapping
peptide tiles. Tiles are 40 residues long and start every 20 residues, except
the terminal tile, which comprises residues 621-655. For each tile, 100
sequence-randomized peptides provide position-matched controls. The complete
design contains 12,800 structures: 32 tiles, two sequence classes, two
CC-90009 states, and 100 models per combination.

A FOXO1 residue is classified as contacting CRBN when at least one heavy-atom
pair between peptide chain F and CRBN chain B is separated by 6.0 A or less.
Each model contributes one binary observation per modeled FOXO1 residue.
Peptide-local residue ordinal is mapped to the corresponding FOXO1 position;
randomized residues retain the source-position mapping regardless of amino-acid
identity. Hard-clash models remain in the denominator.

Native and randomized contact proportions are compared at each FOXO1 position
using a two-sided Fisher exact test. Benjamini-Hochberg correction is applied
separately across the 655 positions in the CC-90009-absent and
CC-90009-present conditions. Positions with q values of 0.05 or less are
marked with black asterisks. Wilson 95% confidence intervals are calculated for
each binomial proportion. Positions represented by one tile have 100 model
evaluations per sequence class and condition; overlapping positions represented
by two tiles have 200 evaluations.

## Panel D CRBN-residue analysis

Panel D uses the FOXO1 541-580 tile in the presence of CC-90009. For each CRBN
residue from 46 through 442, contact proportions are calculated from 100 native
FOXO1 models and 100 position-matched randomized-peptide models using the same
6.0-A heavy-atom definition. Native-greater-than-randomized enrichment is
tested using a one-sided Fisher exact test, followed by Benjamini-Hochberg
correction across candidate CRBN residues within the tile. Wilson 95%
confidence intervals accompany each proportion.

Dark-blue arrowheads mark CRBN residues containing at least one heavy atom
within 6.0 A of a GSPT1 heavy atom in experimental PDB 6XK9. These annotations
identify GSPT1-proximal residues in the experimental structure and are not
additional statistical tests.

## Interpretation boundary

Model-level contact frequency is a geometric structural-sampling endpoint. It
does not estimate binding affinity, dissociation constant, occupancy, free
energy, ubiquitination, or degradation.
