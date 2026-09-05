(.venv) user@moses-ngoyi:~/Documenti/University_of_Politecnico_di_BARI/Cours_master_one/Images_Processing/Project_Liver_Segmentation$ cat README.md
# Liver Segmentation Using Watershed and Region Merging

A reproducible implementation of a classical medical image segmentation
method for liver extraction from abdominal CT images, based on watershed
segmentation and recursive region merging.

This project reproduces the methodology described in the paper:

> Medical Image Segmentation Based on the Watersheds and Regions Merging

The implementation uses the 3D-IRCADb-01 dataset and focuses on
slice-based liver segmentation from DICOM CT volumes.

---

## Overview

Liver segmentation is an important preprocessing step in medical image
analysis and computer-aided diagnosis.

The objective of this project is to reproduce and implement a classical
image segmentation pipeline combining:

- CT image preprocessing
- Gaussian smoothing
- Multi-scale morphological gradients
- Watershed segmentation
- Region Adjacency Graph (RAG)
- Region-based intensity analysis
- Recursive region merging
- Connected-component filtering
- Hole filling

The final output is a binary mask representing the segmented liver region.

---

## Methodology

The implemented pipeline follows the following processing sequence:

```text
DICOM CT Volume
       │
       ▼
CT Slice Extraction
       │
       ▼
Seed Detection
       │
       ▼
Weighted Similarity Criterion
       │
       ▼
Gaussian Smoothing
       │
       ▼
Multi-scale Morphological Gradient
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
Recursive Region Merging
       │
       ▼
Binary Merged Mask
       │
       ▼
Largest Connected Component
       │
       ▼
Hole Filling
       │
       ▼
Final Liver Segmentation
```

A detailed description of the methodology is available in:

[Methodology](docs/methodology.md)

Experimental results and multi-slice evaluation are documented in:

[Experiments](docs/experiments.md)

---

## Dataset

The project uses the **3D-IRCADb-01** dataset.

The dataset contains abdominal CT scans together with manually annotated

organ masks.

For this project, CT DICOM images and corresponding liver masks are used

to evaluate the segmentation pipeline.

The medical dataset itself is **not included in this repository**.

Users must obtain the dataset from its official source and configure the

local dataset path before running the experiments.

---

## Project Structure

```text
liver-segmentation-watershed/
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── docs/
│   ├── experiments.md
│   ├── methodology.md
│   └── figures/
│       ├── multi_slice/
│       └── reference/
│
├── scripts/
│   ├── evaluate_multiple_slices.py
│   ├── evaluate_segmentation.py
│   ├── run_segmentation.py
│   ├── visualize_evaluation.py
│   └── visualize_seeds.py
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
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Installation

### 1. Clone the repository

```text
git clone git@github.com:MoiseNgoyi98/liver-segmentation-watershed.git
cd liver-segmentation-watershed
```

### 2. Create a virtual environment

Python 3.11 is recommended.

```text
python3.11 -m venv .venv
```

### 3. Activate the virtual environment

On Linux/macOS:

```text
source .venv/bin/activate
```

### 4. Install dependencies

```text
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Configuration

The segmentation pipeline uses a configuration object defined in:

```text
src/liver_segmentation/config.py
```

The configuration contains parameters related to:

-  CT dataset location
-  selected slice
-  seed detection
-  Gaussian smoothing
-  morphological gradient scales
-  region merging
-  post-processing

Before running the pipeline, make sure that the dataset paths correspond

to your local installation of 3D-IRCADb-01.

---

## Running the Segmentation

The main segmentation pipeline can be executed using:

```text
python scripts/run_segmentation.py
```

The pipeline processes the selected CT slice and produces the corresponding

liver segmentation.

---

## Evaluation

The repository provides evaluation utilities for comparing the predicted

segmentation with the reference liver mask.

The implemented metrics include:

-  Dice Similarity Coefficient (DSC)
-  Intersection over Union (IoU)
-  Sensitivity
-  Specificity
-  Hausdorff Distance

Evaluation scripts are available in:

```text
scripts/evaluate_segmentation.py
scripts/evaluate_multiple_slices.py
```

---

## Results

The reproduced segmentation experiment achieved the following results on

the evaluated reference slice:

| Metric | Score |
|--------|------:|
| Dice Score | 0.9313 |
| IoU Score | 0.8714 |
| Sensitivity | 0.9885 |
| Specificity | 0.9830 |
| Hausdorff Distance | 21.587 |

These results demonstrate a strong overlap between the predicted liver

segmentation and the reference annotation for the evaluated slice.

---

## Visual Results

### Segmentation Pipeline

[Segmentation Pipeline](docs/figures/reference/segmentation_pipeline.png)

### Slice 60 Comparison

[Slice 60 Comparison](docs/figures/reference/slice_60_comparison.png)

### Multi-Slice Evaluation

The repository also contains visual comparisons for several CT slices:

| Slice | Result |
|-------|--------|
| 40 | [View result](docs/figures/multi_slice/slice_40_comparison.png) |
| 50 | [View result](docs/figures/multi_slice/slice_50_comparison.png) |
| 60 | [View result](docs/figures/multi_slice/slice_60_comparison.png) |
| 70 | [View result](docs/figures/multi_slice/slice_70_comparison.png) |
| 80 | [View result](docs/figures/multi_slice/slice_80_comparison.png) |

More details about the experiments are available in:

[Experimental Results](docs/experiments.md)

---

## Reproducibility

The project is organized into modular components covering:

-  data loading
-  preprocessing
-  seed detection
-  watershed segmentation
-  region merging
-  post-processing
-  evaluation
-  visualization

This modular structure makes it possible to reproduce individual stages

of the segmentation pipeline and evaluate different experimental

configurations.

The original medical dataset is intentionally excluded from version

control.

---

## Continuous Integration

GitHub Actions is used to perform automated checks on every push to

`main` and on pull requests targeting `main`.

The current CI workflow verifies:

-  Python environment setup
-  dependency installation
-  successful imports of the main project modules

The workflow configuration is located at:

```text
.github/workflows/ci.yml
```

---

## Technologies

The project is implemented in Python using:

-  Python 3.11
-  NumPy
-  SciPy
-  scikit-image
-  pydicom
-  NetworkX
-  pandas
-  Matplotlib

---

## Limitations

This project is primarily a reproduction and implementation of a classical

image segmentation methodology.

The current implementation has several limitations:

-  evaluation is performed on selected CT slices;
-  the approach is based on intensity and region-based criteria;
-  watershed segmentation can produce over-segmentation;
-  region merging depends on the selected parameters;
-  the medical dataset is not distributed with the repository.

---

## Future Work

Potential extensions include:

-  evaluation on a larger number of CT slices;
-  quantitative comparison across multiple patients;
-  parameter sensitivity analysis;
-  improved automatic seed detection;
-  comparison with alternative classical segmentation methods;
-  comparison with modern deep-learning-based segmentation approaches.

---

## License

This project is released under the MIT License.

See [LICENSE](LICENSE) for details.

---

## Author

**Moise Ngoyi Kasanji**

Master's student in Data Science and Artificial Intelligence

Politecnico di Bari, Italy

GitHub:

[MoiseNgoyi98](https://github.com/MoiseNgoyi98)
(.venv) user@moses-ngoyi:~/Documenti/University_of_Politecnico_di_BARI/Cours_master_one/Images_Processing/Project_Liver_Segmentation$
