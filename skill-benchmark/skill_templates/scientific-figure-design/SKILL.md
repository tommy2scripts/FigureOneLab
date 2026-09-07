---
name: scientific-figure-design
description: "Design, generate, edit, repair, audit, or peer-review scientific figures, plots, and publication layouts—including heatmaps, spatial omics (Xenium/Visium/CosMx), single-cell (scRNA/scATAC/UMAP), WGS/genomics tracks, microscopy/fluorescence, CNV/SV/ecDNA, uncertainty/replicates, and multi-panel composition. Do NOT use for general graphic design, slide decoration, bioinformatic workflow/pipeline scripts (Nextflow/Snakemake), data processing/normalization without plotting, or statistical modeling when no figure deliverable is requested."
license: "Generated synthesis; see LICENSES.md and provenance.md"
compatibility: "Bundled routing and validation helpers require Python 3.10+ and PyYAML; Matplotlib helpers require Matplotlib; delivered-PDF size verification requires pypdf. Version-sensitive plotting APIs and publisher requirements must be verified against current official documentation when relevant."
metadata:
  version: "0.6.5-opt"
  parent-version: "0.6.4-opt"
  optimization-target: "Outperform K-Dense scientific-visualization on controlled task-level evaluation without increasing scientific-integrity failures"
---

# Scientific Figure Design

## Objective

Optimize scientific visualization decisions, not just plotting syntax or aesthetic polish. Preserve scientific meaning and improve the reader's ability to make the intended inference, then optimize perceptual efficiency, accessibility, layout, implementation robustness, and publication delivery.

The benchmark goal is secondary: outperform the pinned K-Dense scientific-visualization baseline under the same base model/tools/task envelope. Never tune a scientific rule merely because it improves a benchmark score.

## 12 Non-Negotiable Scientific Integrity Gates

1. Do not change the evidence to improve the picture. Never invent, erase, suppress, selectively enhance, or relabel data. Refuse deceptive encodings such as manipulative dual-axis scaling designed to manufacture visual correlation.
2. Preserve meaning of missingness and measurement. Missing, zero, censored, excluded, and below-detection values are not interchangeable. In sparse count data, distinguish biological silence from sampling non-detection. Plot non-detects below experimental limits of detection rather than adding arbitrary constants.
3. Name uncertainty and replication. If a figure shows an interval/error bar, explicitly state whether it represents SD, SEM, or 95% CI, and identify the experimental/biological replicate unit (N). Flag missing sample-size metadata proactively. For derived quantities or compound indices, propagate uncertainty using a method appropriate to the transformation and covariance structure rather than arithmetic averaging of component errors. For rates/proportions over small-denominator units, address spurious sampling variance by showing denominator support, stability indicators, or appropriate shrinkage estimates alongside raw rates.
4. Comparable panels require comparable mappings. If panels are intended for direct quantitative comparison, the mapping from value to position, length, color, or size must be comparable. Signed fold-changes require zero-centered diverging colormaps with neutral zero anchors. Enforce coordinate-system and reference-build concordance across genome tracks.
5. Physical images preserve physical scale. If morphology, spatial structure, or distance is part of the inference, keep calibrated physical scale bars and preserve physical aspect ratios across anisotropic pixel dimensions. In spatial point-pattern analysis, account for tissue geometry boundaries and background density gradients using edge corrections or inhomogeneous intensity models.
6. Accessibility is part of correctness. Do not make a scientifically important distinction depend only on an avoidable hue difference. Use perceptually uniform sequential colormaps for continuous magnitudes and balanced diverging colormaps for deviations around a center, accompanied by redundant visual channels.
7. Aesthetics never override scientific/statistical failures. Visual design may improve hierarchy or spacing, but it may never override a deterministic integrity finding or statistical constraint.
8. Do not pseudoreplicate. Technical subsamples, repeat measurements, or single cells from the same biological specimen are not independent replicates unless explicitly modeled hierarchically. Where hierarchical modeling is not used, aggregate nested observations to the biological donor/animal unit before calculating inferential statistics.
9. Do not infer significance from error-bar overlap. Visual overlap or separation of error bars is not a substitute for formal statistical hypothesis testing. Prohibit claiming absence of effect solely based on overlapping error intervals.
10. Disclose interpretation-changing transforms. Disclose clipping, thresholding, smoothing, normalization, or coordinate transforms. For compositional proportions, account for sum-to-one constraints. Use count-based inferential methods with appropriate between-sample normalization/modeling for count data; do not substitute within-sample metrics such as TPM/RPKM as inferential input. In survival curves, show changing support where late-time interpretation matters. For parametric or nonlinear fits, do not extrapolate beyond tested empirical ranges without explicit visual boundary demarcation and uncertainty.
11. Separate observation from inference and association from causality. Modeled trajectories, diffusion pseudotimes, UMAP embeddings, and network edges must be labeled at the supported evidence level. UMAP/t-SNE coordinates are qualitative embeddings, not quantitative metric distances. Observational correlation networks must use undirected edges unless direction is supported by intervention, time, or formal causal identification.
12. Recalibrate physical scale after geometry changes. Cropping alone preserves pixel scale, but resizing, resampling, or changing display magnification requires recalculating and verifying the displayed scale-bar mapping.

## Executable-Code & Synthetic Smoke Gate

Before describing a figure workflow as executable:

1. Capture whether target libraries are installed. For installed libraries, check function signatures against current official documentation.
2. When specimen data is missing, run a minimal synthetic fixture or smoke test exercising imports, data formatting, plotting, and export.
3. Clearly label code as synthetic-verified versus biological-specimen verified. Unrun code must be honestly labeled pseudocode.

## Runtime Decision Loop

1. State the scientific message: define the exact conclusion the reader should make.
2. State the reader task: value comparison, spatial localization, distribution shape, temporal trajectory, or uncertainty assessment.
3. Identify data semantics and hierarchy: variable types, replicate structure, denominator stability, and coordinate references.
4. Resolve encoding ambiguity: select visual channels matching the reader task; prefer position/length over area/angle for exact comparison.
5. Apply domain playbooks when present: heatmaps/colorbars, single-cell, spatial transcriptomics, WGS/genomics, microscopy, uncertainty/replicates.
6. Compose and render: set physical figure dimensions early and render the actual graphic.
7. Run four-channel QA: scientific/semantic; lexical; visual/perceptual; execution/export.
8. Record provenance: track data inputs, transformations, software versions, and output artifact hashes.
