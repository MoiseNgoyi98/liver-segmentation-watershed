# Liver Segmentation Based on Watershed and Region Merging

A classical medical image segmentation project for liver extraction from abdominal CT images, developed as part of the **Image Processing** course at **Politecnico di Bari**.

The project reproduces and implements a segmentation methodology based on **watershed segmentation and region merging**, inspired by the following paper:

> Huang Zhanpeng, Zhang Qi, Jiang Shizhong, Chen Guohua, *Medical Image Segmentation Based on the Watersheds and Regions Merging*, 2016.

**Author:** Moise Ngoyi Kasanji
**Institution:** Politecnico di Bari
**Course:** Image Processing
**Supervisor:** Prof. Andrea Guerriero

---

## 1. Project Overview

The objective of this project is to extract the **liver region from abdominal CT images** using classical image-processing techniques rather than deep learning.

The implemented pipeline combines:

* seed-based region initialization
* Gaussian smoothing
* multi-scale morphological gradients
* watershed segmentation
* Region Adjacency Graph (RAG)
* intensity-based region merging
* connected-component analysis
* hole filling
* quantitative evaluation against ground-truth liver masks

The project was initially developed and presented as part of the **Image Processing examination**.

After the examination implementation was validated, an additional experimental phase was conducted to investigate the robustness of the method when changing the seed selection strategy and evaluating multiple CT slices.

---

# 2. Project Development

The project can be understood as two complementary phases.

## Phase 1 — Examination Implementation

The first phase corresponds to the implementation presented for the **Image Processing examination**.

A manually selected seed point was used to initialize the segmentation process.

For the original experiment:

```text
Manual seed
    ↓
Similarity criterion
    ↓
Gaussian smoothing
    ↓
Multi-scale morphological gradient
    ↓
Watershed segmentation
    ↓
Region Adjacency Graph
    ↓
Region merging
    ↓
Largest connected component
    ↓
Hole filling
    ↓
Final liver mask
    ↓
Quantitative evaluation
```

The experiment was performed on **slice 60** of the selected 3D-IRCADb1 patient.

### Seed configuration

```text
seed_x = 200
seed_y = 250
```

### Results

| Metric             |       Slice 60 |
| ------------------ | -------------: |
| Dice Score         |     **0.9313** |
| IoU Score          |     **0.8714** |
| Sensitivity        |     **0.9885** |
| Specificity        |     **0.9830** |
| Hausdorff Distance | **21.5870 px** |

These results demonstrate that the proposed classical segmentation pipeline can achieve a strong segmentation result for the evaluated slice.

However, these values should **not** be interpreted as a dataset-wide performance benchmark because they were obtained from a single evaluated slice.

---

# 3. Experimental Extension

After completing the examination implementation, the project was extended to investigate one of its important limitations: **the dependency on the manually selected seed point**.

Using fixed coordinates such as:

```text
seed_x = 200
seed_y = 250
```

can introduce a bias when different CT slices are evaluated because the anatomical position of the liver changes from slice to slice.

Therefore, an experimental automatic seed-selection module was introduced.

The extended workflow became:

```text
CT slice
    ↓
Candidate seed generation
    ↓
Local homogeneity scoring
    ↓
Automatic seed selection
    ↓
Segmentation pipeline
    ↓
Quantitative evaluation
```

The automatic seed detector generates several candidate points inside a central region of the image and selects a candidate according to its local intensity homogeneity.

---

# 4. Multi-Slice Evaluation

The extended implementation was evaluated on five CT slices:

```text
40
50
60
70
80
```

For each slice, the system automatically selected a seed and independently executed the complete segmentation pipeline.

The following metrics were computed:

* Dice Score
* IoU
* Sensitivity
* Specificity
* Hausdorff Distance

The results were also exported to CSV files to facilitate further analysis.

### Experimental results

| Slice |   Dice |    IoU | Sensitivity | Specificity | Hausdorff (px) |
| ----: | -----: | -----: | ----------: | ----------: | -------------: |
|    40 | 0.0000 | 0.0000 |      0.0000 |      0.7269 |       343.7586 |
|    50 | 0.3021 | 0.1779 |      1.0000 |      0.5749 |       277.1372 |
|    60 | 0.0000 | 0.0000 |      0.0000 |      0.9670 |       266.3400 |
|    70 | 0.0000 | 0.0000 |      0.0000 |      1.0000 |              ∞ |
|    80 | 0.0000 | 0.0000 |      0.0000 |      0.7416 |       290.6888 |

The corresponding mean ± standard deviation was:

| Metric             |      Mean ± Std |
| ------------------ | --------------: |
| Dice               | 0.0604 ± 0.1351 |
| IoU                | 0.0356 ± 0.0796 |
| Sensitivity        | 0.2000 ± 0.4472 |
| Specificity        | 0.8021 ± 0.1784 |
| Hausdorff Distance |         ∞ ± NaN |

---

# 5. Interpretation of the Experimental Results

The multi-slice experiment revealed an important limitation of the current automatic seed-selection strategy.

Although the original manually initialized experiment produced a strong Dice score of **0.9313** on slice 60, the automatic strategy did not consistently identify an appropriate liver seed across different slices.

This resulted in substantially poorer segmentation performance.

This experiment is therefore not considered a failure of the entire segmentation methodology. Instead, it identifies a specific weakness in the current implementation:

> **The automatic seed-selection strategy based primarily on local intensity homogeneity is not sufficiently robust for reliable multi-slice liver segmentation.**

This observation is useful because it identifies a concrete direction for future development.

---

# 6. Methodology

The complete segmentation pipeline is composed of the following stages:

```text
DICOM CT volume
       ↓
CT slice extraction
       ↓
Seed selection
       ↓
Weighted similarity criterion
       ↓
Gaussian smoothing
       ↓
Multi-scale morphological gradient
       ↓
Watershed segmentation
       ↓
Region Adjacency Graph
       ↓
Region mean intensity computation
       ↓
Recursive region merging
       ↓
Binary merged mask
       ↓
Largest connected component
       ↓
Hole filling
       ↓
Final liver mask
       ↓
Ground-truth comparison
       ↓
Quantitative metrics
```

The implementation is deliberately modular so that individual components can be improved independently.

---

# 7. Dataset

The experiments use the **3D-IRCADb-01** dataset.

The medical dataset is **not included in this repository**.

Expected local structure:

```text
data/
└── 3Dircadb1/
    └── 3Dircadb1.4/
        ├── PATIENT_DICOM/
        └── MASKS_DICOM/
            └── liver/
```

The dataset should be obtained from the appropriate official source and placed locally according to the structure above.

---

# 8. Repository Structure

```text
Project_Liver_Segmentation/
│
├── data/                              # Local medical dataset (ignored)
│
├── outputs/                           # Generated results (ignored)
│   └── evaluation/
│       ├── metrics_per_slice.csv
│       ├── metrics_summary.csv
│       ├── seeds/
│       └── visualizations/
│
├── src/
│   └── liver_segmentation/
│       ├── config.py
│       ├── data_io.py
│       ├── evaluation.py
│       ├── pipeline.py
│       ├── postprocessing.py
│       ├── preprocessing.py
│       ├── rag.py
│       ├── region_merging.py
│       ├── seed_detection.py
│       ├── similarity.py
│       ├── visualization.py
│       └── watershed_segmentation.py
│
├── scripts/
│   ├── evaluate.py
│   ├── evaluate_multiple_slices.py
│   ├── evaluate_segmentation.py
│   ├── run_segmentation.py
│   ├── visualize_evaluation.py
│   └── visualize_seeds.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

# 9. Installation

Clone the repository and create a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

# 10. Running the Segmentation

To execute the segmentation pipeline:

```bash
python scripts/run_segmentation.py
```

Alternatively, when using the package/module structure:

```bash
python -m scripts.run_segmentation
```

---

# 11. Single-Slice Evaluation

The original examination experiment can be evaluated using:

```bash
python -m scripts.evaluate_segmentation
```

This evaluates the configured slice against the corresponding ground-truth liver mask.

---

# 12. Multi-Slice Evaluation

The experimental multi-slice evaluation can be executed with:

```bash
python -m scripts.evaluate_multiple_slices
```

The current experiment evaluates:

```text
40, 50, 60, 70, 80
```

Results are stored locally in:

```text
outputs/evaluation/
```

including:

```text
metrics_per_slice.csv
metrics_summary.csv
```

---

# 13. Visualization

The project also provides scripts for visual inspection of the segmentation results.

To visualize the selected seeds:

```bash
python -m scripts.visualize_seeds
```

To generate multi-slice segmentation comparisons:

```bash
python -m scripts.visualize_evaluation
```

These visualizations make it possible to compare the predicted segmentation with the ground-truth masks.

---

# 14. Design Principles

The implementation follows several software-engineering principles:

* modular processing functions
* separation between processing and visualization
* configuration-based parameters
* reusable segmentation components
* explicit intermediate results
* reproducible experiments
* quantitative evaluation
* separation of experimental outputs from source code

The pipeline is designed so that individual components, such as seed detection or region merging, can be replaced without rewriting the entire system.

---

# 15. Limitations

The current implementation has several limitations.

### Seed dependence

The original method relies on a manually selected seed point, while the current automatic strategy is not sufficiently robust across different slices.

### 2D evaluation

The current experiments operate on individual 2D CT slices rather than performing complete 3D liver segmentation.

### Limited evaluation

The reported experiments were conducted on a limited number of slices from a single patient.

Consequently, the results should not be interpreted as a general clinical or dataset-wide benchmark.

### Classical segmentation limitations

Watershed segmentation can produce a large number of regions, making the quality of the final result highly dependent on the gradient representation, similarity criterion, seed selection, and region-merging strategy.

---

# 16. Future Work

Several improvements could be investigated in future versions:

* anatomically informed automatic seed detection
* multi-seed initialization
* adaptive seed selection
* improved region similarity criteria
* 3D watershed segmentation
* multi-slice and multi-patient evaluation
* parameter sensitivity analysis
* comparison with alternative classical segmentation methods
* comparison with modern deep-learning approaches
* statistical analysis across a larger dataset

The automatic seed-selection experiment provides a concrete starting point for these future improvements.

---

# 17. Academic Context

This repository represents the implementation developed for the **Image Processing** course at **Politecnico di Bari**.

The first phase corresponds to the methodology implemented and presented for the course examination.

The subsequent automatic-seed and multi-slice experiments were developed as an extension to investigate the robustness and limitations of the original implementation.

The project therefore documents both:

1. the successful reproduction and implementation of the original experimental approach;
2. the subsequent investigation of its limitations and possible directions for improvement.

---

# 18. Citation

If this implementation or methodology is referenced, please cite the original paper:

> Huang Zhanpeng, Zhang Qi, Jiang Shizhong, Chen Guohua, "Medical Image Segmentation Based on the Watersheds and Regions Merging", 2016.

---

## Author

**Moise Ngoyi Kasanji**
Master's student in Data Science & Artificial Intelligence
Politecnico di Bari
