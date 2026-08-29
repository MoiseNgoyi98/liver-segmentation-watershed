"""
Run the liver segmentation pipeline.

This script is the main entry point for executing the complete
liver segmentation workflow from the command line.
"""

from pathlib import Path
import sys

import matplotlib.pyplot as plt


# ============================================================
# Project root
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# Project imports
# ============================================================

from src.liver_segmentation.config import SegmentationConfig
from src.liver_segmentation.pipeline import run_pipeline


# ============================================================
# Output directory
# ============================================================

OUTPUT_DIR = PROJECT_ROOT / "outputs"


# ============================================================
# Main
# ============================================================

def main() -> None:
    """
    Execute the complete liver segmentation pipeline.
    """

    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Load configuration
    # --------------------------------------------------------

    config = SegmentationConfig()

    # --------------------------------------------------------
    # Run segmentation pipeline
    # --------------------------------------------------------

    result = run_pipeline(config)

    # --------------------------------------------------------
    # Display processing information
    # --------------------------------------------------------

    print("=" * 60)
    print("LIVER SEGMENTATION")
    print("=" * 60)

    print(f"CT slice shape      : {result.image.shape}")
    print(f"Seed label          : {result.seed_label}")
    print(f"Selected regions    : {len(result.selected_regions)}")
    print(f"Final liver pixels  : {result.liver_mask.sum()}")

    print("-" * 60)

    print(f"Mean intensity      : {result.mean:.4f}")
    print(f"Standard deviation  : {result.std:.4f}")
    print(f"Lower threshold     : {result.lower:.4f}")
    print(f"Upper threshold     : {result.upper:.4f}")

    print("=" * 60)

    # --------------------------------------------------------
    # Create visualization
    # --------------------------------------------------------

    fig, axes = plt.subplots(
        2,
        3,
        figsize=(12, 8)
    )

    # Original CT
    axes[0, 0].imshow(
        result.image,
        cmap="gray"
    )
    axes[0, 0].set_title(
        "Original CT"
    )

    # Gaussian smoothing
    axes[0, 1].imshow(
        result.smooth,
        cmap="gray"
    )
    axes[0, 1].set_title(
        "Gaussian Smoothing"
    )

    # Morphological gradient
    axes[0, 2].imshow(
        result.gradient,
        cmap="gray"
    )
    axes[0, 2].set_title(
        "Morphological Gradient"
    )

    # Watershed
    axes[1, 0].imshow(
        result.watershed_labels
    )
    axes[1, 0].set_title(
        "Watershed Segmentation"
    )

    # Region merging
    axes[1, 1].imshow(
        result.merged_mask,
        cmap="gray"
    )
    axes[1, 1].set_title(
        "Region Merging"
    )

    # Final liver
    axes[1, 2].imshow(
        result.liver_mask,
        cmap="gray"
    )
    axes[1, 2].set_title(
        "Final Liver Mask"
    )

    # Remove axes
    for axis in axes.ravel():
        axis.axis("off")

    # Optimize layout
    plt.tight_layout()

    # --------------------------------------------------------
    # Save result
    # --------------------------------------------------------

    output_path = (
        OUTPUT_DIR
        / "segmentation_pipeline.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
        pad_inches=0
    )

    plt.show()

    print(
        f"Pipeline figure saved to: {output_path}"
    )


# ============================================================
# Script entry point
# ============================================================

if __name__ == "__main__":
    main()