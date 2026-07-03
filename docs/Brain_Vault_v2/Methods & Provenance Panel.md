---
tags: [feature, reproducibility, v2]
aliases: [Methods Panel, Provenance, Reproducibility]
---
# 🔬 Methods & Provenance Panel

> [!info] Live reproducibility report
> A new expander at the bottom of the page that reports the exact runtime
> configuration — cheap to build, disproportionately credibility-boosting for a
> thesis tool. Part of [[Changes from v1]] · hub [[Neuro-Target Visualizer v2]].

Reports (live, from real state — nothing hard-coded):
- coordinate space (MNI152, 2 mm), region model (25 MNI points → Gaussian blobs),
- activation σ (surface 12 mm / glass-stat 6 mm),
- cortical surface + inflate state ([[Higher-Resolution Surface (fsaverage6)]]),
- colormap, [[Display Threshold Control|threshold]], kcal/mol → % mapping,
- library versions (nilearn / matplotlib / numpy / Python) + timestamp,
- an explicit **data-provenance** line: *values are user-entered; no external
  PET/mRNA/atlas data is used* (see [[Enhancement Roadmap]]).

Implemented as an `st.expander` in [[app (v2)]]. This is the honest counterpart to
the bigger items still on the roadmap — it states plainly what the tool does and
does **not** use.
