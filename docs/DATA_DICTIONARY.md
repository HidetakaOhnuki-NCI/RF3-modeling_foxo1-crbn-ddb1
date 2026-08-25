# Data dictionary

## Panel B matched-model table

| Column | Definition |
|---|---|
| `condition_id` | One of the four required GSPT1 comparison arms |
| `seed` | Unique RF3 random seed within an arm |
| `num_steps` | RF3 diffusion steps; required value 200 |
| `n_recycles` | RF3 trunk recycles; required value 10 |
| `diffusion_batch_size` | Structures sampled per diffusion call; required value 1 |
| `jaccard_similarity` | Intersection divided by union of predicted and reference CRBN interface-residue sets |

## Panel C FOXO1-residue table

| Column | Definition |
|---|---|
| `foxo1_position` | Canonical human FOXO1 residue position, 1-655 |
| `cc90009` | `absent` or `present` |
| `native_contact_n` | Native-model contact count |
| `native_total_n` | Native-model denominator at the position |
| `randomized_contact_n` | Randomized-model contact count |
| `randomized_total_n` | Randomized-model denominator at the position |
| `fisher_two_sided_p` | Two-sided Fisher exact p value |
| `native_frequency` | Native contact proportion from 0 to 1 |
| `native_frequency_pct` | Native contact percentage |
| `native_wilson95_low`, `native_wilson95_high` | Native Wilson 95% interval bounds as proportions |
| `randomized_frequency` | Randomized contact proportion from 0 to 1 |
| `randomized_frequency_pct` | Randomized contact percentage |
| `randomized_wilson95_low`, `randomized_wilson95_high` | Randomized Wilson 95% interval bounds as proportions |
| `bh_q` | Benjamini-Hochberg-adjusted p value within the CC-90009 state |
| `significant` | Whether `bh_q` is 0.05 or less |

## Panel D CRBN-residue table

| Column | Definition |
|---|---|
| `source_tile` | FOXO1 source tile; fixed to `tile_0541_0580` |
| `crbn_residue_id` | PDB 6XK9 chain-B CRBN residue number, 46-442 |
| `native_contact_n`, `native_total_n` | Native contact count and denominator |
| `native_contact_fraction` | Native contact proportion |
| `native_wilson95_low`, `native_wilson95_high` | Native Wilson 95% interval bounds |
| `randomized_contact_n`, `randomized_total_n` | Randomized contact count and denominator |
| `randomized_contact_fraction` | Randomized contact proportion |
| `randomized_wilson95_low`, `randomized_wilson95_high` | Randomized Wilson 95% interval bounds |
| `tested` | Whether the residue was in the native-contact candidate set |
| `fisher_one_sided_p` | Native-greater-than-randomized Fisher exact p value |
| `bh_q_within_tile` | Benjamini-Hochberg q value within the FOXO1 541-580 tile |
| `significant_within_tile_q0p05` | Whether the within-tile q value is 0.05 or less |

## Raw-model manifest

| Column | Definition |
|---|---|
| `model_id` | Stable model identifier |
| `panel` | Figure panel supported by the model |
| `condition_id` | Experimental or computational condition identifier |
| `construct_id` | Protein or peptide construct identifier |
| `seed` | RF3 random seed |
| `num_steps`, `n_recycles`, `diffusion_batch_size` | RF3 inference settings |
| `relative_archive_path` | Path relative to the root of the external archive |
| `sha256` | SHA-256 checksum of the raw model file |
| `external_archive_id` | Stable repository identifier assigned at deposition |
