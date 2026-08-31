# Methodology

## 1. Overview

This project implements a classical image segmentation approach for extracting the liver from abdominal CT images.

The methodology is inspired by the paper:

> Huang Zhanpeng, Zhang Qi, Jiang Shizhong, Chen Guohua,
> *Medical Image Segmentation Based on the Watersheds and Regions Merging*, 2016.

The project was initially developed as part of the **Image Processing course at Politecnico di Bari** and was presented as an examination project.

The implementation is based on a combination of:

* intensity-based similarity analysis,
* Gaussian smoothing,
* multi-scale morphological gradients,
* watershed segmentation,
* Region Adjacency Graphs (RAG),
* intensity-based region merging,
* connected-component analysis,
* hole filling.

The overall objective is to transform a CT image into a binary mask representing the liver region.

---

## 2. Project Development Phases

The project was developed in two main phases.

### Phase 1 — Examination Implementation

The first version was developed for the Image Processing examination.

A **manually selected seed point** was used to initialize the segmentation process. The experiments were initially performed on **slice 60** of the 3D-IRCADb-01 dataset.

The seed coordinates used in the original experiment were:

```text
seed_x = 200
seed_y = 250
```

This configuration was used to reproduce and evaluate the proposed segmentation methodology.

The best result obtained on slice 60 was:

| Metric             |    Result |
| ------------------ | --------: |
| Dice Score         |    0.9313 |
| IoU                |    0.8714 |
| Sensitivity        |    0.9885 |
| Specificity        |    0.9830 |
| Hausdorff Distance | 21.587 px |

These results correspond specifically to the evaluated slice and should not be interpreted as a dataset-wide performance measure.

---

### Phase 2 — Post-Examination Experimentation

After the examination, the project was extended to investigate the robustness of the original approach.

The main limitation identified was the use of a fixed seed coordinate.

A seed such as:

```text
(200, 250)
```

is meaningful for a particular image but cannot be assumed to correspond to the liver location in every CT slice.

Therefore, an automatic seed-selection mechanism was introduced.

The project was subsequently evaluated on multiple slices:

```text
40
50
60
70
80
```

This additional experimentation revealed that automatic seed selection based only on local intensity homogeneity is not sufficient to guarantee robust liver segmentation.

This phase is therefore considered an **experimental extension**, rather than part of the original examination implementation.

---

# 3. Segmentation Pipeline

The complete segmentation workflow is:

```text
3D CT DICOM Volume
        │
        ▼
   Slice Extraction
        │
        ▼
   Seed Selection
        │
        ▼
Weighted Similarity Criterion
        │
        ▼
 Gaussian Smoothing
        │
        ▼
Multi-Scale Morphological Gradient
        │
        ▼
 Watershed Segmentation
        │
        ▼
Region Adjacency Graph
        │
        ▼
 Region Mean Intensities
        │
        ▼
 Intensity-Based Region Merging
        │
        ▼
   Binary Mask
        │
        ▼
Largest Connected Component
        │
        ▼
     Hole Filling
        │
        ▼
  Final Liver Mask
```

---

# 4. CT Data Loading

The input data consists of abdominal CT images stored as DICOM files.

The CT series is loaded and reconstructed into a three-dimensional volume.

The implementation provides dedicated functions for:

* loading the CT volume,
* ordering the slices,
* extracting a selected 2D slice,
* loading the corresponding liver ground-truth mask.

The segmentation algorithm operates on individual 2D CT slices.

---

# 5. Seed Selection

## 5.1 Original Manual Seed

The original examination implementation used a manually selected seed.

For the reference experiment:

```text
Slice: 60
Seed:  (200, 250)
```

The seed identifies a local region expected to belong to the liver.

The intensity statistics around this point are used to define the similarity criterion employed during region merging.

---

## 5.2 Automatic Seed Selection

As a post-examination extension, an automatic seed-selection mechanism was implemented.

Instead of relying on a single predefined coordinate, candidate points are generated inside a central region of the CT image.

For each candidate, the local intensity variability is evaluated.

The candidate with the lowest local standard deviation is selected:

```text
Candidate generation
        ↓
Local intensity analysis
        ↓
Homogeneity scoring
        ↓
Best candidate selection
```

The purpose of this extension is to reduce the dependency of the segmentation algorithm on manually specified coordinates.

However, the experiments demonstrated that local homogeneity alone does not provide sufficient anatomical information to reliably identify the liver.

Consequently, automatic seed detection should be considered an experimental component requiring further improvement.

---

# 6. Weighted Similarity Criterion

The seed region is used to estimate local intensity statistics.

The implementation computes:

* mean intensity,
* standard deviation,
* lower intensity threshold,
* upper intensity threshold.

For the reference experiment, the values were:

```text
Mean intensity          : 110.7431
Standard deviation      : 12.8512
Lower threshold         : 72.1893
Upper threshold         : 149.2968
```

These statistics define the intensity range used during region selection and merging.

The objective is to identify neighboring regions whose intensity characteristics are sufficiently similar to the seed region.

---

# 7. Gaussian Smoothing

Before computing the morphological gradient, Gaussian smoothing is applied to the CT slice.

The current configuration uses:

```text
Gaussian sigma = 1.0
```

The purpose of this operation is to reduce small-scale intensity fluctuations and noise while preserving the main anatomical structures and boundaries.

The smoothed image is subsequently used to compute the morphological gradient.

---

# 8. Multi-Scale Morphological Gradient

A morphological gradient is computed at multiple spatial scales.

The current configuration uses:

```text
Gradient scales = [1, 2, 3]
```

The multi-scale approach allows image structures to be analyzed at different spatial resolutions.

The resulting gradient image emphasizes intensity transitions and anatomical boundaries, which are subsequently used by the watershed algorithm.

---

# 9. Watershed Segmentation

The watershed transformation is applied to the multi-scale gradient image.

The watershed algorithm interprets the gradient image as a topographic surface:

* low-gradient areas correspond to relatively homogeneous regions,
* high-gradient areas correspond to boundaries.

The output is a labeled image in which each region receives a unique label.

These regions form the initial over-segmentation used by the subsequent region-merging stage.

---

# 10. Region Adjacency Graph

The watershed regions are represented using a **Region Adjacency Graph (RAG)**.

In this graph:

* each node represents a watershed region,
* an edge connects two nodes when the corresponding regions are spatially adjacent.

The RAG provides a structured representation of the spatial relationships between segmented regions.

This representation is used to perform region merging.

---

# 11. Region Mean Intensities

For every watershed region, the mean CT intensity is computed.

The region mean is then compared with the intensity interval derived from the seed region.

This allows regions to be evaluated according to their similarity to the expected liver intensity characteristics.

---

# 12. Recursive Region Merging

The region-merging stage starts from the watershed region containing the seed point.

Neighboring regions are recursively examined.

A region is selected when its intensity is compatible with the similarity criterion defined from the seed region.

The process can be summarized as:

```text
Seed region
     ↓
Examine neighboring regions
     ↓
Compare region intensity
     ↓
Accept compatible regions
     ↓
Expand to their neighbors
     ↓
Repeat recursively
```

The selected watershed regions are finally combined into a binary mask.

This step reduces the over-segmentation produced by the watershed transformation.

---

# 13. Connected Component Selection

The binary merged mask may contain multiple disconnected regions.

To remove isolated regions and retain the dominant anatomical structure, connected-component analysis is performed.

The implementation retains the **largest connected component**.

This provides a simple spatial constraint that helps eliminate small unrelated regions.

---

# 14. Hole Filling

The resulting liver region may contain internal gaps or holes.

A binary hole-filling operation is therefore applied to the largest connected component.

The final result is a binary liver mask:

```text
0 → Background
1 → Liver
```

---

# 15. Quantitative Evaluation

The predicted liver mask is compared against the corresponding ground-truth liver mask provided by the dataset.

The project evaluates the segmentation using the following metrics.

### Dice Score

The Dice coefficient measures the overlap between the predicted mask and the ground truth.

Higher values indicate better segmentation overlap.

### Intersection over Union

IoU measures the ratio between the intersection and union of the predicted and reference regions.

### Sensitivity

Sensitivity measures the proportion of liver pixels correctly identified by the segmentation.

### Specificity

Specificity measures the proportion of background pixels correctly classified as background.

### Hausdorff Distance

The Hausdorff distance evaluates the maximum boundary discrepancy between the predicted segmentation and the reference segmentation.

A lower value indicates better boundary agreement.

---

# 16. Multi-Slice Evaluation

After the original single-slice experiment, the implementation was extended to evaluate several CT slices automatically.

The evaluated slices were:

```text
40, 50, 60, 70, 80
```

For each slice, the following metrics are stored:

```text
Dice
IoU
Sensitivity
Specificity
Hausdorff Distance
```

The results are exported as CSV files containing both per-slice measurements and summary statistics.

This experiment was introduced to determine whether the segmentation methodology generalizes beyond the original reference slice.

---

# 17. Experimental Findings

The multi-slice experiment showed significant variability between slices.

For the automatic seed-selection experiment, the obtained results were:

| Slice |   Dice |    IoU | Sensitivity | Specificity | Hausdorff |
| ----: | -----: | -----: | ----------: | ----------: | --------: |
|    40 | 0.0000 | 0.0000 |      0.0000 |      0.7269 |  343.7586 |
|    50 | 0.3021 | 0.1779 |      1.0000 |      0.5749 |  277.1372 |
|    60 | 0.0000 | 0.0000 |      0.0000 |      0.9670 |  266.3400 |
|    70 | 0.0000 | 0.0000 |      0.0000 |      1.0000 |         ∞ |
|    80 | 0.0000 | 0.0000 |      0.0000 |      0.7416 |  290.6888 |

The mean Dice score in this experiment was:

```text
0.0604 ± 0.1351
```

These results demonstrate that the current automatic seed-selection strategy is not yet robust enough for reliable multi-slice segmentation.

Importantly, these results are reported as an experimental finding rather than being hidden or replaced by the stronger single-slice result.

---

# 18. Current Limitations

Several limitations remain in the current implementation.

### Fixed anatomical assumptions

The original method depends strongly on the location of the seed region.

### Automatic seed selection

The current automatic method relies primarily on local intensity homogeneity. A homogeneous region is not necessarily the liver.

### 2D processing

The current implementation processes individual CT slices rather than exploiting the complete 3D anatomical information available in the volume.

### Limited evaluation

The current experiments focus on a small number of slices from a single patient.

Therefore, the reported results should not be interpreted as a general benchmark of liver segmentation performance.

### Sensitivity to intensity characteristics

CT intensity distributions can vary between patients and anatomical locations, which can affect threshold-based region merging.

---

# 19. Future Improvements

Potential future extensions include:

1. Anatomically informed seed detection.
2. Multi-seed initialization.
3. 3D region growing and region merging.
4. Patient-level normalization.
5. Evaluation across multiple patients.
6. Evaluation across complete CT volumes.
7. Robust handling of empty or disconnected predictions.
8. Parameter sensitivity analysis.
9. Comparison with alternative classical segmentation methods.
10. Comparison with modern deep-learning-based segmentation approaches.

A particularly promising direction is to combine **automatic seed detection with anatomical constraints and multi-scale information**, rather than selecting a seed solely from local intensity homogeneity.

---

# 20. Reproducibility

The implementation is organized into modular Python components.

The main processing stages are separated into:

```text
src/liver_segmentation/
```

while executable experiment scripts are located in:

```text
scripts/
```

The main dependencies are listed in:

```text
requirements.txt
```

The dataset itself is intentionally excluded from version control because it consists of medical imaging data.

Generated experimental outputs are also excluded from Git using `.gitignore`.

This repository therefore contains the reproducible **source code and experimental methodology**, while the medical dataset must be obtained and configured separately.

---

## Summary

The project started as an examination-oriented reproduction of a watershed and region-merging liver segmentation methodology using a manually selected seed.

The post-examination development focused on investigating one of the main limitations of this approach: its dependency on manually fixed seed coordinates.

An automatic seed-selection mechanism and multi-slice evaluation framework were subsequently introduced.

The experiments showed that removing the manually fixed seed does not automatically improve segmentation quality. Instead, the results highlight the importance of incorporating anatomical information and more robust initialization strategies.

The project therefore provides both a **working classical segmentation pipeline** and an experimental analysis of its limitations and possible directions for future improvement.
