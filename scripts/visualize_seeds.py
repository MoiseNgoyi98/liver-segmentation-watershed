from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from src.liver_segmentation.config import SegmentationConfig
from src.liver_segmentation.data_io import (
    get_slice,
    load_ct_volume,
)
from src.liver_segmentation.seed_detection import detect_seed


SLICE_IDS = [40, 50, 60, 70, 80]


def load_liver_mask(
    mask_folder: Path,
    slice_id: int,
) -> np.ndarray:
    """
    Load the liver mask corresponding to a CT slice.

    The mask is converted to a binary image.
    """

    from src.liver_segmentation.data_io import load_dicom_volume

    mask_volume = load_dicom_volume(mask_folder)

    mask = get_slice(
        mask_volume,
        slice_id,
    )

    return mask > 0


def visualize_seed(
    image: np.ndarray,
    mask: np.ndarray,
    manual_seed: tuple[int, int],
    automatic_seed: tuple[int, int],
    slice_id: int,
    output_path: Path,
) -> None:
    """
    Generate a visualization comparing manual and automatic seeds.
    """

    fig, ax = plt.subplots(
        figsize=(8, 8)
    )

    ax.imshow(
        image,
        cmap="gray",
    )

    # Ground-truth liver contour
    ax.contour(
        mask,
        levels=[0.5],
        linewidths=1.5,
    )

    # Manual seed
    manual_x, manual_y = manual_seed

    ax.scatter(
        manual_x,
        manual_y,
        marker="x",
        s=120,
        linewidths=3,
        label="Manual seed",
    )

    # Automatic seed
    automatic_x, automatic_y = automatic_seed

    ax.scatter(
        automatic_x,
        automatic_y,
        marker="o",
        s=100,
        facecolors="none",
        linewidths=2.5,
        label="Automatic seed",
    )

    ax.set_title(
        f"Slice {slice_id} — Seed comparison"
    )

    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    ax.legend()

    ax.set_axis_off()

    fig.tight_layout()

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)


def main() -> None:
    """
    Visualize manual and automatic seeds for several CT slices.
    """

    config = SegmentationConfig()

    output_dir = (
        config.output_dir
        / "evaluation"
        / "seeds"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    volume = load_ct_volume(
        config.ct_folder
    )

    manual_seed = (
        config.seed_x,
        config.seed_y,
    )

    print("=" * 60)
    print("SEED VISUALIZATION")
    print("=" * 60)

    for slice_id in SLICE_IDS:

        print(
            f"Visualizing slice {slice_id}..."
        )

        image = get_slice(
            volume,
            slice_id,
        )

        automatic_seed = detect_seed(
            image=image,
            mode="automatic",
            block_size=config.block_size,
            grid_size=config.seed_grid_size,
            margin_ratio=config.seed_margin_ratio,
        )

        mask = load_liver_mask(
            config.mask_folder,
            slice_id,
        )

        output_path = (
            output_dir
            / f"slice_{slice_id}_seed.png"
        )

        visualize_seed(
            image=image,
            mask=mask,
            manual_seed=manual_seed,
            automatic_seed=automatic_seed,
            slice_id=slice_id,
            output_path=output_path,
        )

        print(
            f"  Manual seed    : {manual_seed}"
        )

        print(
            f"  Automatic seed : {automatic_seed}"
        )

        print(
            f"  Saved to       : {output_path}"
        )

    print("=" * 60)
    print("SEED VISUALIZATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()