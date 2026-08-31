# Experimental Evaluation

## 1. Purpose

This document describes the experiments conducted during the development of the liver segmentation project.

The experiments are divided into two stages:

1. **Reference experiment** — the implementation developed for the Image Processing examination.
2. **Post-examination experiments** — additional experiments performed to investigate the robustness of the method.

This distinction is important because the reference experiment and the subsequent experiments use different seed-selection strategies.

---

## 2. Reference Experiment — Examination

The initial implementation was evaluated on **CT slice 60** from the 3D-IRCADb-01 dataset.

A manually selected seed point was used:

```text
Slice ID : 60
Seed     : (200, 250)
```

The segmentation pipeline used:

* Gaussian smoothing;
* multi-scale morphological gradient;
* watershed segmentation;
* Region Adjacency Graph construction;
* intensity-based region merging;
* largest connected-component selection;
* hole filling.

### Results

| Metric             |      Score |
| ------------------ | ---------: |
| Dice               |     0.9313 |
| IoU                |     0.8714 |
| Sensitivity        |     0.9885 |
| Specificity        |     0.9830 |
| Hausdorff Distance | 21.5870 px |

These results represent the **reference implementation used for the examination**.

They are not intended to represent performance across the entire dataset.

---

## 3. Motivation for Further Experiments

After the examination, a limitation of the original implementation was identified.

The seed coordinates were fixed:

```text
seed_x = 200
seed_y = 250
```

This assumption is problematic when processing different CT slices because the anatomical position of the liver is not necessarily represented by the same pixel coordinates in every image.

Therefore, an automatic seed-selection strategy was investigated.

The objective was to reduce the dependency on manual initialization and evaluate whether the segmentation method could generalize better across multiple slices.

---

## 4. Automatic Seed Selection

The automatic strategy generates several candidate points inside a central region of the image.

Each candidate is evaluated according to local intensity homogeneity.

The local score is based on the standard deviation of a small neighborhood:

```text
lower local variability
        ↓
higher homogeneity
        ↓
preferred seed candidate
```

The candidate with the highest homogeneity score is selected as the seed.

The strategy was tested on five slices:

```text
40
50
60
70
80
```

The automatically selected seeds were:

| Slice | Automatic Seed |
| ----: | -------------: |
|    40 |     (409, 102) |
|    50 |     (255, 178) |
|    60 |     (409, 332) |
|    70 |     (409, 409) |
|    80 |     (409, 102) |

These coordinates demonstrate that the seed position changes according to the image.

---

## 5. Multi-Slice Evaluation

The automatic seed-selection strategy was evaluated on slices 40, 50, 60, 70 and 80.

The following metrics were computed for each slice:

* Dice Score;
* Intersection over Union (IoU);
* Sensitivity;
* Specificity;
* Hausdorff Distance.

### Results

| Slice |   Dice |    IoU | Sensitivity | Specificity | Hausdorff |
| ----: | -----: | -----: | ----------: | ----------: | --------: |
|    40 | 0.0000 | 0.0000 |      0.0000 |      0.7269 |  343.7586 |
|    50 | 0.3021 | 0.1779 |      1.0000 |      0.5749 |  277.1372 |
|    60 | 0.0000 | 0.0000 |      0.0000 |      0.9670 |  266.3400 |
|    70 | 0.0000 | 0.0000 |      0.0000 |      1.0000 |         ∞ |
|    80 | 0.0000 | 0.0000 |      0.0000 |      0.7416 |  290.6888 |

### Aggregate Results

| Metric             | Mean ± Standard Deviation |
| ------------------ | ------------------------: |
| Dice               |           0.0604 ± 0.1351 |
| IoU                |           0.0356 ± 0.0796 |
| Sensitivity        |           0.2000 ± 0.4472 |
| Specificity        |           0.8021 ± 0.1784 |
| Hausdorff Distance |                         ∞ |

The Hausdorff summary becomes infinite because at least one slice produced an empty prediction, making the boundary distance undefined/infinite for that case.

---

## 6. Interpretation

The multi-slice experiment does **not** show an improvement over the reference experiment.

The original manually initialized experiment achieved:

```text
Dice = 0.9313
```

on slice 60.

The automatic seed experiment produced substantially lower results on the evaluated slices.

This indicates that selecting a seed solely according to local intensity homogeneity is insufficient for reliable liver initialization.

A locally homogeneous region is not necessarily part of the liver.

---

## 7. Important Experimental Conclusion

The automatic seed-selection experiment should therefore be interpreted as a **negative experimental result** rather than as a failed project.

The experiment identified an important limitation of the proposed strategy:

> Removing manual initialization does not necessarily improve segmentation robustness if the automatic initialization mechanism does not incorporate sufficient anatomical information.

This finding provides a clear direction for future development.

---

## 8. Current Experimental Status

At the current stage, the project contains:

### Stable reference pipeline

```text
Manual seed
     ↓
Segmentation
     ↓
Evaluation
```

This pipeline reproduces the reference examination result on slice 60.

### Experimental extension

```text
Automatic seed detection
          ↓
Multi-slice segmentation
          ↓
Quantitative evaluation
```

This extension demonstrates the limitations of the current automatic initialization strategy.

---

## 9. Generated Experimental Outputs

The evaluation scripts generate:

```text
outputs/
└── evaluation/
    ├── metrics_per_slice.csv
    ├── metrics_summary.csv
    ├── seeds/
    │   ├── slice_40_seed.png
    │   ├── slice_50_seed.png
    │   ├── slice_60_seed.png
    │   ├── slice_70_seed.png
    │   └── slice_80_seed.png
    │
    └── visualizations/
        ├── slice_40_comparison.png
        ├── slice_50_comparison.png
        ├── slice_60_comparison.png
        ├── slice_70_comparison.png
        └── slice_80_comparison.png
```

These generated files are excluded from version control by `.gitignore`.

The source code required to reproduce the experiments remains available in the repository.

---

## 10. Future Experimental Directions

Possible future experiments include:

1. Anatomically constrained seed detection.
2. Multiple seed candidates instead of a single automatically selected point.
3. Seed selection using liver-specific intensity and spatial information.
4. 3D seed propagation between adjacent slices.
5. Evaluation over complete CT volumes.
6. Evaluation across multiple patients.
7. Parameter sensitivity analysis.
8. Comparison between manual and automatic initialization.
9. Robust handling of empty segmentation outputs.
10. Comparison with other classical segmentation approaches.

The next major improvement should therefore focus on **anatomically informed initialization**, rather than simply increasing the number of candidate points.
