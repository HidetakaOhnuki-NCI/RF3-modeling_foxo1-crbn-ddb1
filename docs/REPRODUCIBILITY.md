# Reproducibility guide

## Software

The analysis requires Python 3.11 or later and the versions listed in
`requirements.txt`. The package was verified with Python 3.13, NumPy 2.5.2,
pandas 3.0.5, SciPy 1.18.1, Matplotlib 3.11.1, and Pillow 12.3.0. UCSF
ChimeraX 1.12 is used only for Panel A.

RF3 model generation requires a separate RosettaCommons Foundry installation
and checkpoint `rf3_foundry_01_24_latest_remapped.ckpt`.

## RF3 command pattern

Foundry uses Hydra-style argument assignment. A model-generation call follows
this pattern:

```text
rf3 fold inputs=INPUT_FILE out_dir=OUTPUT_DIRECTORY ckpt_path=CHECKPOINT_FILE seed=SEED diffusion_batch_size=1 num_steps=200 n_recycles=10
```

Use `ground_truth_conformer_selection=[M,F]` without CC-90009 and
`ground_truth_conformer_selection=[M,L,F]` with CC-90009. Replace the capitalized
tokens with environment-specific values; do not commit local absolute paths.

## Analysis commands

From the package root:

```bash
python scripts/make_panel_c.py
python scripts/make_panel_d.py
python -m unittest discover -s tests -v
python scripts/validate_release.py
```

Generate Panel B from the model-level metrics table:

```bash
python scripts/make_panel_b.py --input data/processed/panel_b_gspt1_matched.csv
```

The script rejects an incomplete table, unequal arm sizes, duplicate seeds
within an arm, nonfinite Jaccard values, and any model record not generated
with 200 diffusion steps, 10 recycles, and a diffusion batch size of 1.

## Expected included outputs

- `figures/panel_c_foxo1_residue_contacts.png`
- `figures/panel_d_crbn_541_580_contacts.png`
- a JSON validation report written to standard output by
  `scripts/validate_release.py`

Panel A uses its representative structure model, and Panel B uses its
model-level metrics input.

## Raw-model deposition

Raw CIF or PDB ensembles are not suitable for routine GitHub storage. Deposit
them in a stable data repository, retain the original filenames, calculate
SHA-256 checksums, and populate `data/manifests/raw_model_manifest_schema.csv`.
The manifest must use archive-relative paths rather than workstation paths.
