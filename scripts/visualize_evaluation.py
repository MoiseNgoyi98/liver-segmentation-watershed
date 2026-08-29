from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage.segmentation import find_boundaries

from src.liver_segmentation.config import SegmentationConfig
from src.liver_segmentation.data_io import load_dicom_volume, get_slice
from src.liver_segmentation.pipeline import run_pipeline


# ============================================================
# Project paths
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "evaluation"
    / "visualizations"
)


# ============================================================
# Evaluation slices
# ============================================================

SLICE_IDS = [40, 50, 60, 70, 80]


# ============================================================
# Helper functions
# ============================================================

def create_boundary_overlay(
    image: np.ndarray,
    ground_truth: np.ndarray,
    prediction: np.ndarray,
) -> np.ndarray:
    """
    Create an RGB overlay showing ground-truth and predicted boundaries.

    Ground-truth boundaries are displayed in red.
    Predicted boundaries are displayed in green.
    """

    # Normalize CT image to [0, 1]
    image = image.astype(np.float32)

    image_min = image.min()
    image_max = image.max()

    if image_max > image_min:
        normalized = (
            image - image_min
        ) / (
            image_max - image_min
        )
    else:
        normalized = np.zeros_like(image)

    # Convert grayscale image to RGB
    overlay = np.dstack([
        normalized,
        normalized,
        normalized,
    ])

    # Extract boundaries
    gt_boundary = find_boundaries(
        ground_truth
    )

    pred_boundary = find_boundaries(
        prediction
    )

    # Ground Truth = red
    overlay[gt_boundary] = [1.0, 0.0, 0.0]

    # Prediction = green
    overlay[pred_boundary] = [0.0, 1.0, 0.0]

    return overlay


def save_slice_comparison(
    slice_id: int,
    result,
    ground_truth: np.ndarray,
) -> None:
    """
    Create and save a six-panel comparison figure
    for one CT slice.
    """

    output_path = (
        OUTPUT_DIR
        / f"slice_{slice_id}_comparison.png"
    )

    # --------------------------------------------------------
    # Create boundary overlay
    # --------------------------------------------------------

    overlay = create_boundary_overlay(
        result.image,
        ground_truth,
        result.liver_mask,
    )

    # --------------------------------------------------------
    # Create figure
    # --------------------------------------------------------

    fig, axes = plt.subplots(
        2,
        3,
        figsize=(15, 10),
    )

    # --------------------------------------------------------
    # (a) Original CT
    # --------------------------------------------------------

    axes[0, 0].imshow(
        result.image,
        cmap="gray",
    )

    axes[0, 0].set_title(
        "(a) Original CT"
    )

    # --------------------------------------------------------
    # (b) Ground Truth
    # --------------------------------------------------------

    axes[0, 1].imshow(
        ground_truth,
        cmap="gray",
    )

    axes[0, 1].set_title(
        "(b) Ground Truth"
    )

    # --------------------------------------------------------
    # (c) Watershed
    # --------------------------------------------------------

    axes[0, 2].imshow(
        result.watershed_labels,
        cmap="nipy_spectral",
    )

    axes[0, 2].set_title(
        "(c) Watershed Segmentation"
    )

    # --------------------------------------------------------
    # (d) Region Merging
    # --------------------------------------------------------

    axes[1, 0].imshow(
        result.merged_mask,
        cmap="gray",
    )

    axes[1, 0].set_title(
        "(d) Region Merging"
    )

    # --------------------------------------------------------
    # (e) Final Liver
    # --------------------------------------------------------

    axes[1, 1].imshow(
        result.liver_mask,
        cmap="gray",
    )

    axes[1, 1].set_title(
        "(e) Final Liver Segmentation"
    )

    # --------------------------------------------------------
    # (f) Boundary comparison
    # --------------------------------------------------------

    axes[1, 2].imshow(
        overlay
    )

    axes[1, 2].set_title(
        "(f) Ground Truth vs Prediction"
    )

    # --------------------------------------------------------
    # Remove axes
    # --------------------------------------------------------

    for axis in axes.ravel():
        axis.axis("off")

    # --------------------------------------------------------
    # Figure title
    # --------------------------------------------------------

    fig.suptitle(
        f"Liver Segmentation Evaluation - Slice {slice_id}",
        fontsize=14,
    )

    # --------------------------------------------------------
    # Layout
    # --------------------------------------------------------

    plt.tight_layout()

    # --------------------------------------------------------
    # Save figure
    # --------------------------------------------------------

    fig.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0.05,
    )

    plt.close(fig)

    print(
        f"Saved visualization: {output_path}"
    )


# ============================================================
# Main
# ============================================================

def main() -> None:
    """
    Generate visual evaluation figures for multiple CT slices.
    """

    print("=" * 60)
    print("LIVER SEGMENTATION VISUAL EVALUATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Load configuration
    # --------------------------------------------------------

    config = SegmentationConfig()

    # --------------------------------------------------------
    # Load CT volume
    # --------------------------------------------------------

    ct_volume = load_dicom_volume(
        config.ct_folder
    )

    # --------------------------------------------------------
    # Load Ground Truth volume
    # --------------------------------------------------------

    gt_volume = load_dicom_volume(
        config.mask_folder
    )

    # --------------------------------------------------------
    # Process each selected slice
    # --------------------------------------------------------

    for slice_id in SLICE_IDS:

        print()
        print(
            f"Processing slice {slice_id}..."
        )

        # ----------------------------------------------------
        # Extract Ground Truth slice
        # ----------------------------------------------------

        ground_truth = get_slice(
            gt_volume,
            slice_id,
        )

        ground_truth = (
            ground_truth > 0
        )

        # ----------------------------------------------------
        # Create slice-specific configuration
        # ----------------------------------------------------

        slice_config = SegmentationConfig(
            ct_folder=config.ct_folder,
            mask_folder=config.mask_folder,
            slice_id=slice_id,
            seed_x=config.seed_x,
            seed_y=config.seed_y,
            block_size=config.block_size,
            gaussian_sigma=config.gaussian_sigma,
            gradient_scales=config.gradient_scales,
        )

        # ----------------------------------------------------
        # Run segmentation pipeline
        # ----------------------------------------------------

        result = run_pipeline(
            slice_config
        )

        # ----------------------------------------------------
        # Save comparison figure
        # ----------------------------------------------------

        save_slice_comparison(
            slice_id=slice_id,
            result=result,
            ground_truth=ground_truth,
        )

    print()
    print("=" * 60)
    print("VISUALIZATION COMPLETE")
    print("=" * 60)
    print(
        f"Figures saved to: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()