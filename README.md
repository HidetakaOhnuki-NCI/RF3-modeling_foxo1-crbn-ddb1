# FOXO1-CRBN RosettaFold3 reproducibility package

We used RosettFold3 (Corley et al. DOI: bioRxiv https://doi.org/10.1101/2025.08.14.670328) 
to explore a candidate protein, which might interact with the Cereblon-DDB1 complex, an adaptor
for the Culin 4 E3 ubiquitin ligase complex. The focus of the modeling was to search for a candidate 
protein that might be affected by a drug, CC-90009. 
      This repository contains the code used for analyses in our manuscript, entitled "Selected next-generation CELMoDs 
induce cereblon-dependent depletion of FOXO1 and block tumor and retinal angiogenesis." It records 
the model-generation conditions, downstream analyses, statistical procedures, and figure-generation 
steps used in the study.
     RosettaFold3 inference was performed on the NIH Biowulf high-performance computing system using
the site-managed "RoseTTAFold/3" module ("rc-foundry" 0.1.9). 

## Scope

The declared release protocol uses 200 diffusion steps, 10 recycles, a
diffusion batch size of 1, and one random seed per replicate model for every
comparison arm.

- Panel A: a ChimeraX command file is provided. The representative structure
  model is not redistributed in this GitHub package.
- Panel B: the executable analysis and input schema are provided for the four
  GSPT1 comparison arms.
- Panel C: the validated 1,310-row FOXO1 residue-contact table is included.
- Panel D: the validated 397-row CRBN residue-contact table for FOXO1 541-580
  with CC-90009 is included.

## Repository map

```text
analysis/          Reusable validation, statistics, and plotting functions
chimerax/          Panel A visualization commands
config/            Machine-readable RF3 protocol
data/manifests/    Raw-model manifest schema
data/processed/    Compact figure-ready tables and provenance
docs/              Methods, workflow, data dictionary, and reproduction guide
figures/           Regenerated Panel C and Panel D PNG files
scripts/           Command-line entry points
tests/             Automated behavior and release-safety checks
```

## Quick start

Create a Python environment and install the analysis dependencies:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Activate the environment using the command appropriate for the operating
system, then regenerate the included data-driven panels:

```bash
python scripts/make_panel_c.py
python scripts/make_panel_d.py
```

Generate Panel B from a protocol-matched input table:

```bash
python scripts/make_panel_b.py --input data/processed/panel_b_gspt1_matched.csv
```

Run the complete verification:

```bash
python -m unittest discover -s tests -v
python scripts/validate_release.py
```

## Figure mapping

| Panel | Analysis unit | Contact or similarity endpoint | Entry point |
|---|---|---|---|
| A | Representative GSPT1-CC-90009-CRBN model | Displayed GSPT1-CRBN heavy-atom contacts at 3.6 A or less | `chimerax/panel_a_interface.cxc` |
| B | One GSPT1 model | Jaccard similarity based on CRBN-GSPT1 contacts below 4.0 A | `scripts/make_panel_b.py` |
| C | One model and one FOXO1 residue | FOXO1-CRBN contact at 6.0 A or less | `scripts/make_panel_c.py` |
| D | One model and one CRBN residue | FOXO1 541-580-CRBN contact at 6.0 A or less | `scripts/make_panel_d.py` |

The thresholds serve different purposes and are not interchangeable.

## RF3 inference protocol

The machine-readable source of truth is `config/rf3_protocol.json`. The
principal settings are:

- checkpoint: `rf3_foundry_01_24_latest_remapped.ckpt`;
- diffusion steps: 200;
- recycles: 10;
- diffusion batch size: 1;
- reference structure: PDB 6XK9;
- DDB1 chain A, CRBN chain B, substrate or peptide chain F, CC-90009 chain L,
  and Zn chain M.

Zn and peptide chain F are supplied to the atom-level conformer-conditioning
track in both drug conditions; CC-90009 is added to this track when present.
Conditioning supplies reference atomic geometry but does not rigidly fix the
output coordinates. The analysis therefore evaluates sequence-dependent
structural compatibility and reproducibility within a conditioned geometry; it
does not measure unconstrained binding-site discovery or binding affinity.

## Data availability

GitHub stores the code, documentation, processed tables, and model-manifest
schema. Raw RF3 structure ensembles should be deposited in an appropriate data
repository and linked through stable identifiers in the manifest. RF3 model
weights and the Foundry source distribution are not included.

## License

No software license has been selected. The authors should add an explicit
license before public release if reuse beyond inspection is intended.
