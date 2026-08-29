from src.liver_segmentation.config import SegmentationConfig
from src.liver_segmentation.data_io import (
    binarize_mask,
    get_slice,
    load_mask_volume,
)
from src.liver_segmentation.evaluation import (
    dice_score,
    hausdorff_distance,
    iou_score,
    sensitivity,
    specificity,
)
from src.liver_segmentation.pipeline import run_pipeline


def main() -> None:
    """
    Run liver segmentation and evaluate the result
    against the corresponding ground-truth mask.
    """

    # ========================================================
    # 1. Load segmentation configuration
    # ========================================================

    config = SegmentationConfig()

    # ========================================================
    # 2. Run segmentation pipeline
    # ========================================================

    result = run_pipeline(config)

    # ========================================================
    # 3. Load ground-truth mask volume
    # ========================================================

    ground_truth_volume = load_mask_volume(
        config.mask_folder
    )

    # ========================================================
    # 4. Extract ground-truth slice
    # ========================================================

    ground_truth = get_slice(
        ground_truth_volume,
        config.slice_id,
    )

    # Convert the mask to binary format
    ground_truth = binarize_mask(
        ground_truth
    )

    # ========================================================
    # 5. Get predicted liver mask
    # ========================================================

    prediction = result.liver_mask

    # ========================================================
    # 6. Compute evaluation metrics
    # ========================================================

    dice = dice_score(
        ground_truth,
        prediction,
    )

    iou = iou_score(
        ground_truth,
        prediction,
    )

    sens = sensitivity(
        ground_truth,
        prediction,
    )

    spec = specificity(
        ground_truth,
        prediction,
    )

    hausdorff = hausdorff_distance(
        ground_truth,
        prediction,
    )

    # ========================================================
    # 7. Display results
    # ========================================================

    print()
    print("=" * 60)
    print("LIVER SEGMENTATION EVALUATION")
    print("=" * 60)

    print(f"Slice ID           : {config.slice_id}")
    print(f"Dice Score         : {dice:.4f}")
    print(f"IoU Score          : {iou:.4f}")
    print(f"Sensitivity        : {sens:.4f}")
    print(f"Specificity        : {spec:.4f}")
    print(f"Hausdorff Distance : {hausdorff:.4f} pixels")

    print("=" * 60)


if __name__ == "__main__":
    main()