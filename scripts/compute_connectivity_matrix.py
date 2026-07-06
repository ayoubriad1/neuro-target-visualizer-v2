"""One-off script: computes the real, group-average functional connectivity
matrix between this app's 28 atlas regions, bundled as data/connectivity_matrix.csv
and loaded at runtime by connectome.py.

Not run by the app itself - this is a development-time script, kept in the
repo so the matrix's provenance is fully reproducible/auditable rather than
being an opaque bundled file nobody can regenerate or verify.

Data source: nilearn's `fetch_development_fmri` - naturalistic "movie
watching" fMRI (participants watched the short film "Partly Cloudy") from
Richardson, Lisandrelli, Riobueno-Naylor & Saxe (2018), "Development of the
social brain from age three to twelve years", Nature Communications 9:1027.
Adults only (age_group='adult', n=33 available; this run uses N_SUBJECTS of
them), fMRIPrep-preprocessed, resampled to 4mm MNI152NLin2009cAsym space by
nilearn's fetcher.

Method: each of the 28 atlas region masks (atlas_regions.get_region_mask,
native MNI152 2mm / FSL space) is resampled onto the functional data's grid,
then used as an ROI to extract a mean regional timeseries per subject
(confound-regressed: motion, framewise displacement, aCompCor, CSF, white
matter; detrended; band-pass filtered 0.01-0.1 Hz; z-scored) via
nilearn.maskers.NiftiMapsMasker. A per-subject Pearson correlation matrix
between all 28 regional timeseries is Fisher z-transformed, averaged across
subjects, then transformed back to a correlation - the standard approach for
averaging correlation coefficients across subjects.

Caveats (see docs/CONNECTOME_PROPAGATION.md for the full writeup):
- This is *functional* connectivity (co-activation), not structural
  (axonal/white-matter) connectivity - a proxy for "these regions'
  activity tends to move together", not literal wiring.
- Naturalistic movie-watching data, not resting-state - a reasonable and
  commonly-used substitute for connectivity estimation, but not identical.
- Slightly different MNI variant (MNI152NLin2009cAsym vs. this app's FSL
  MNI152) and coarse 4mm resolution - acceptable for whole-region averages,
  not for fine-grained voxel-level claims.
"""
import warnings

import nibabel as nib
import numpy as np
import pandas as pd
from nilearn import datasets
from nilearn.connectome import ConnectivityMeasure
from nilearn.image import resample_img
from nilearn.maskers import NiftiMapsMasker

from atlas_regions import ATLAS_REGIONS, get_region_mask
from mni_space import MNI_AFFINE

N_SUBJECTS = 15
OUTPUT_PATH = "data/connectivity_matrix.csv"


def main():
    region_names = sorted(ATLAS_REGIONS)
    print(f"Computing connectivity for {len(region_names)} regions across {N_SUBJECTS} subjects...")

    data = datasets.fetch_development_fmri(n_subjects=N_SUBJECTS, age_group="adult")
    func_img = nib.load(data.func[0])
    target_affine, target_shape = func_img.affine, func_img.shape[:3]

    maps = np.stack([
        np.asarray(
            resample_img(
                nib.Nifti1Image(get_region_mask(name), MNI_AFFINE),
                target_affine=target_affine, target_shape=target_shape,
                interpolation="continuous",
            ).get_fdata()
        )
        for name in region_names
    ], axis=-1)
    maps_img = nib.Nifti1Image(maps, target_affine)

    masker = NiftiMapsMasker(
        maps_img, standardize="zscore_sample", detrend=True,
        low_pass=0.1, high_pass=0.01, t_r=2.0,
    )

    per_subject_z = []
    for i, (func_file, confounds_file) in enumerate(zip(data.func, data.confounds, strict=True)):
        print(f"  subject {i + 1}/{N_SUBJECTS}: {func_file}")
        timeseries = masker.fit_transform(func_file, confounds=confounds_file)
        corr = ConnectivityMeasure(kind="correlation").fit_transform([timeseries])[0]
        np.fill_diagonal(corr, np.nan)  # exclude self-correlation from the Fisher z average
        per_subject_z.append(np.arctanh(np.clip(corr, -0.999999, 0.999999)))

    # The diagonal is NaN in every subject by construction (self-correlation
    # excluded above) and gets explicitly restored to 1.0 right after - the
    # "mean of empty slice" warning nanmean raises for those all-NaN diagonal
    # cells is expected and harmless, not a sign anything went wrong.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Mean of empty slice")
        mean_z = np.nanmean(np.stack(per_subject_z, axis=0), axis=0)
    mean_corr = np.tanh(mean_z)
    np.fill_diagonal(mean_corr, 1.0)

    df = pd.DataFrame(mean_corr, index=region_names, columns=region_names)
    df.to_csv(OUTPUT_PATH)
    print(f"Saved {OUTPUT_PATH} ({df.shape[0]}x{df.shape[1]})")


if __name__ == "__main__":
    main()
