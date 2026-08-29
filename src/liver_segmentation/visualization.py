from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage.segmentation import find_boundaries


def _save(
    figure,
    output_path: Path | None,
) -> None:
    """Save a figure when an output path is provided."""
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)

        figure.savefig(
            output_path,
            dpi=300,
            bbox_inches="tight",
            pad_inches=0,
        )


def save_single_image(
    image: np.ndarray,
    title: str,
    output_path: Path | None = None,
    cmap: str | None = "gray",
) -> None:
    """Save one image using a clean publication-style layout."""
    figure, axis = plt.subplots(figsize=(6, 6))

    axis.imshow(image, cmap=cmap)
    axis.set_title(title, fontsize=10)
    axis.axis("off")

    figure.tight_layout()
    _save(figure, output_path)
    plt.close(figure)


def save_pipeline_figure(
    original: np.ndarray,
    smooth: np.ndarray,
    gradient: np.ndarray,
    merged_mask: np.ndarray,
    liver: np.ndarray,
    liver_filled: np.ndarray,
    output_path: Path | None = None,
) -> None:
    """Save the six main stages of the segmentation pipeline."""
    figure, axes = plt.subplots(
        2, 3, figsize=(15, 10)
    )

    images = [
        (original, "(a) Original CT"),
        (smooth, "(b) Gaussian Smoothing"),
        (gradient, "(c) Morphological Gradient"),
        (merged_mask, "(d) Region Merging"),
        (liver, "(e) Extracted Liver"),
        (liver_filled, "(f) Hole Filling"),
    ]

    for axis, (image, title) in zip(axes.ravel(), images):
        axis.imshow(image, cmap="gray")
        axis.set_title(title)
        axis.axis("off")

    figure.tight_layout()
    _save(figure, output_path)
    plt.close(figure)


def save_ground_truth_comparison(
    original: np.ndarray,
    ground_truth: np.ndarray,
    prediction: np.ndarray,
    output_path: Path | None = None,
) -> None:
    """Save original CT, ground truth and prediction side by side."""
    figure, axes = plt.subplots(
        1, 3, figsize=(18, 6)
    )

    axes[0].imshow(original, cmap="gray")
    axes[0].set_title("Original CT")

    axes[1].imshow(ground_truth, cmap="gray")
    axes[1].set_title("Ground Truth")

    axes[2].imshow(prediction, cmap="gray")
    axes[2].set_title("Proposed Method")

    for axis in axes:
        axis.axis("off")

    figure.tight_layout()
    _save(figure, output_path)
    plt.close(figure)


def save_boundary_overlay(
    image: np.ndarray,
    ground_truth: np.ndarray,
    prediction: np.ndarray,
    output_path: Path | None = None,
) -> None:
    """
    Save a boundary overlay.

    Ground truth is shown in red and prediction in green.
    """
    image = image.astype(float)

    image_range = image.max() - image.min()

    if image_range == 0:
        normalized = np.zeros_like(image)
    else:
        normalized = (image - image.min()) / image_range

    overlay = np.dstack(
        [normalized, normalized, normalized]
    )

    gt_boundary = find_boundaries(ground_truth)
    pred_boundary = find_boundaries(prediction)

    overlay[gt_boundary] = [1, 0, 0]
    overlay[pred_boundary] = [0, 1, 0]

    figure, axis = plt.subplots(figsize=(8, 8))

    axis.imshow(overlay)
    axis.set_title(
        "Red = Ground Truth | Green = Prediction"
    )
    axis.axis("off")

    figure.tight_layout()
    _save(figure, output_path)
    plt.close(figure)
