---
tags: [roadmap, planning, v2]
aliases: [Roadmap, Future Work, v3]
---
# 🗺️ Enhancement Roadmap

> [!abstract] Applied vs. still-needed
> Mirrors `..\Brain Visualizer v2\ENHANCEMENT_REPORT.md`. Separates what v2
> actually does from what would need **real data + architecture** (and must not
> be faked). Hub: [[Neuro-Target Visualizer v2]].

## ✅ Applied in v2
- [[Interactive 3D Brain (Plotly)]] (gray → red, rotatable) ·
  [[Interactive Slices]] · [[Gray-to-Red Intensity Map]]
- [[Higher-Resolution Surface (fsaverage6)]] + inflate/pial toggle
- [[Display Threshold Control]] · [[Methods & Provenance Panel]]

## 🔴 Needs real data + architecture (not faked)
- **Molecule mode (v3):** SMILES input → RDKit QED / properties + CNS MPO +
  ChEMBL / BindingDB / PDSP / IUPHAR lookup. Prerequisite for everything below.
- **PET / mRNA ground truth:** compare the predicted map to neuromaps PET
  receptor-density (Hansen-style atlas) with **spin-test** spatial nulls.
- **Atlas parcellations** (Glasser / Schaefer / Desikan-Killiany): re-architect
  from fixed MNI points to per-parcel scoring.
- **Region-click interpretability:** click a region → contributing targets
  (needs the molecule layer + click wiring on the interactive renderer).

## Why not now
The current tool is a **manual-input** visualizer; the items above require
external datasets and a redesigned data model. Adding them honestly is the next
phase — see [[Changes from v1]] for what v2 *is*.
