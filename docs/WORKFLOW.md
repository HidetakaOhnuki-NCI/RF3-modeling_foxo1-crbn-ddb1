# Analysis workflow

## 1. Prepare RF3 inputs

Use PDB 6XK9 to define the reference DDB1, CRBN, Zn, CC-90009, and substrate
geometry. Generate every comparison arm with the settings in
`config/rf3_protocol.json`. Record condition, construct, seed, RF3 settings,
output filename, and SHA-256 checksum in the raw-model manifest.

## 2. Generate structure ensembles

Use one seed per replicate, 200 diffusion steps, 10 recycles, and a diffusion
batch size of 1. Do not combine outputs generated under different inference
settings in a biological comparison.

## 3. Extract geometric endpoints

- Panel A: select a representative hard-clash-free GSPT1 model and display
  GSPT1-CRBN contacts at 3.6 A or less.
- Panel B: extract CRBN residues below the strict 4.0-A GSPT1 interface cutoff
  and calculate Jaccard similarity to PDB 6XK9.
- Panel C: map binary 6.0-A CRBN contacts from peptide-local ordinals to FOXO1
  positions 1-655.
- Panel D: extract binary 6.0-A FOXO1 541-580 contacts for CRBN residues 46-442.

## 4. Validate study design

Before statistical analysis, verify unique seeds, complete comparison arms,
expected replicate counts, valid chain assignments, RF3 settings, and residue
coverage. The public Panel B script fails if any record is not 200 steps and 10
recycles.

## 5. Calculate statistics

- Panel B: one-sided Mann-Whitney U tests on model-level Jaccard similarity.
- Panel C: two-sided Fisher exact tests per FOXO1 position, with separate
  Benjamini-Hochberg correction for the two CC-90009 states.
- Panel D: one-sided Fisher exact tests per candidate CRBN residue, with
  Benjamini-Hochberg correction within the FOXO1 541-580 tile.
- Panels C and D: Wilson 95% confidence intervals for binomial proportions.

## 6. Generate panels

Run the panel scripts from the package root. Panel C and Panel D use included
figure-ready CSVs. Panel B accepts the model-level metrics table defined in the
data dictionary. Panel A uses the representative structure model.

## 7. Audit the public release

Run the unittest suite and `scripts/validate_release.py`. The release audit
checks required files, protocol settings, data coverage, checksums, generated
figures, and accidental disclosure of private filesystem paths.
