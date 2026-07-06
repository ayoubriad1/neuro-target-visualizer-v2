# Circuit propagation (experimental)

Design notes for the "🔗 Circuit propagation (experimental)" results
section (`connectome.py`, wired into `interpretation.py`/`app.py`).

## What problem this solves

Every other view in this app answers "where does the compound bind?" A
pharmacological effect doesn't stay confined to its binding site, though -
it propagates through functional circuits. The textbook example: a
dopaminergic compound acting on the striatum affects motor control, mood,
*and* cognition simultaneously, not because the drug binds all three
domains directly, but because the striatum feeds separate parallel
cortico-striato-thalamo-cortical loops (Alexander, DeLong & Strick 1986)
that terminate in motor, limbic, and associative cortex respectively.

This section estimates, for regions the user did **not** select, a
"propagated effect" score based on real functional connectivity to the
regions they did - a first, deliberately simple step toward "where might
this effect spread," not just "where does it bind."

## Data source and how it was computed

A 28×28 group-average **functional connectivity** matrix
(`data/connectivity_matrix.csv`), computed once (not at app runtime) by
[`scripts/compute_connectivity_matrix.py`](../scripts/compute_connectivity_matrix.py)
from real fMRI data:

- **Source**: nilearn's `fetch_development_fmri` - naturalistic "movie
  watching" fMRI (participants watched the short animated film *Partly
  Cloudy*) from Richardson, Lisandrelli, Riobueno-Naylor & Saxe (2018),
  *"Development of the social brain from age three to twelve years,"*
  Nature Communications 9:1027. 15 adult subjects (of 33 available),
  fMRIPrep-preprocessed, provided by nilearn already resampled to 4mm
  resolution in MNI152NLin2009cAsym space.
- **Extraction**: each of this app's 28 atlas region masks
  (`atlas_regions.get_region_mask`) is resampled onto the functional data's
  grid and used as an ROI for `nilearn.maskers.NiftiMapsMasker`, with
  confound regression (motion, framewise displacement, aCompCor, CSF, white
  matter), detrending, band-pass filtering (0.01-0.1 Hz), and z-scoring.
- **Connectivity**: per-subject Pearson correlation between all 28 regional
  timeseries (`nilearn.connectome.ConnectivityMeasure`), Fisher
  z-transformed, averaged across subjects, transformed back to a
  correlation - the standard way to average correlation coefficients.
- **Sanity check**: the resulting matrix reproduces well-known
  neuroanatomy - e.g. Putamen's strongest connections are Caudate, Insula,
  Primary Motor Cortex and Thalamus, matching the established
  sensorimotor/limbic cortico-striato-thalamic loops. This isn't proof of
  correctness, but it's the kind of check that would fail loudly if the
  masking or resampling pipeline were wrong.

Regenerating the matrix (e.g. with more subjects, or after an atlas region
changes) is a matter of re-running the script - nothing about it is
hand-tuned or opaque.

## Important caveats

- **Functional, not structural, connectivity.** This is a measure of
  "these regions' activity tends to move together," not literal
  axonal/white-matter wiring. Two regions can be functionally coupled
  without a direct anatomical tract between them (e.g. via a third region),
  and a real anatomical tract can exist without strong functional coupling
  in this particular dataset/task.
- **Naturalistic movie-watching, not resting-state.** A commonly used and
  reasonable substitute for connectivity estimation, but the specific
  cognitive engagement of watching a film is not identical to rest.
- **Coarse resolution, slightly different template.** 4mm voxels and
  MNI152NLin2009cAsym space (vs. this app's native FSL MNI152 2mm) -
  acceptable for whole-region averages, not for fine-grained claims.
- **The propagation formula is a simple linear model**, not a validated
  pharmacokinetic, circuit, or network-diffusion simulation:
  `propagated[j] = sum_i connectivity[i,j] * affinity[i]` over selected
  regions `i` with positive connectivity to candidate `j`. It has one hop
  (no multi-step spreading through intermediate regions), ignores
  connection sign for anything other than exclusion, and its output scale
  is relative (rescaled 0-100% against the strongest propagated region) -
  **not** comparable to the directly-entered affinity percentages.
- Deliberately rendered as its **own, separate results section** - never
  blended into the same 3-D heatmap as directly-entered/measured affinity,
  so a linear estimate can never be visually mistaken for part of the same
  measurement.

## Adding more data / improving this later

- Re-run `scripts/compute_connectivity_matrix.py` with more subjects (up to
  all 33 available adults) for a more stable estimate.
- A structural (diffusion-MRI tractography) connectome would be a
  meaningfully different and complementary signal - no such matrix, matched
  to this app's exact mixed cortical/subcortical region set, was readily
  available at the time this was built (see the "spin test" discussion in
  `docs/RECEPTOR_WEIGHTING.md` for the same "no unified parcellation
  object" problem in a different feature).
- A multi-hop propagation model (e.g. network diffusion / random-walk with
  restart) would capture indirect, multi-step spread instead of this
  single-hop weighted sum - a natural extension once the one-hop version
  has been validated against real pharmacological literature.
