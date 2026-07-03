---
tags: [home, hub, tool, v2]
aliases: [v2 Home, Brain Visualizer v2, Neuro-Target Visualizer v2]
---
# 🧠 Neuro-Target Affinity Visualizer — v2

> [!abstract] What this vault is
> The **v2 (enhanced) edition** of the Neuro-Target Affinity Visualizer, by
> **Ayoub Riad**, documented as its **own** neuronal-network vault — **separate
> from, and leaving untouched, the original `Brain_Vault`**. v1 still runs; v2 is
> the side-by-side enhanced copy living in `..\Brain Visualizer v2\`. Every v2
> feature and code change is a note here, wired together with `[[wiki-links]]`.

Press `Ctrl+G` in Obsidian to see the v2 network.

![[interactive-3d.png]]
*v2's interactive 3D — a light folded cortex with the gray→red affinity heat map. All renders: [[Gallery]].*

## 🆕 What v2 adds (vs v1)
Full log: [[Changes from v1]]. Highlights:
- [[Interactive 3D Brain (Plotly)]] — a **rotatable** brain: **gray cortex,
  affected regions ramp gray → red** by intensity.
- [[Interactive Slices]] — scrubbable cross-hair volume viewer.
- [[Gray-to-Red Intensity Map]] — the colour scheme behind the 3-D brain.
- [[Higher-Resolution Surface (fsaverage6)]] + inflated / pial toggle.
- [[Display Threshold Control]] — a user slider feeding every view.
- [[Methods & Provenance Panel]] — live reproducibility report.

## 💻 Code
- [[app (v2)]] — Streamlit UI, **5 view modes**, rendering controls, summary,
  interpretation, methods panel.
- [[visualization (v2)]] — volume builder + static renderers + the new
  interactive renderers.
- **[[_Code Graph Index]]** — every file's **full source** (graphify-mapped):
  [[app]] · [[visualization]] · [[brain_regions]] · [[start_app]] · [[config]] · [[requirements]].

## 🖼️ Images
- [[Gallery]] — real renders of every view mode (interactive 3D, static surface,
  glass brain, stat map).

## 🧩 Concepts
- [[vol_to_surf Projection]] — how a 3-D volume becomes per-vertex surface colour.

## 🗺️ Direction
- [[Enhancement Roadmap]] — what's applied vs what still needs real data
  (PET maps, atlases, molecule mode). Mirrors `..\Brain Visualizer v2\ENHANCEMENT_REPORT.md`.

> [!note] Relationship to v1
> The original tool (`..\Brain Vizualisation\`) and its `Brain_Vault` are
> unchanged. v2 is a **copy** with these enhancements layered on top.
