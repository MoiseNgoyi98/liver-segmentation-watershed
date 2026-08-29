from pathlib import Path

import pandas as pd

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


# ============================================================
# Evaluation settings
# ============================================================

SLICE_IDS = [40, 50, 60, 70, 80]

OUTPUT_DIR = Path("outputs/evaluation")

RESULTS_FILE = (
    OUTPUT_DIR / "metrics_per_slice.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR / "metrics_summary.csv"
)


def evaluate_slice(
    config: SegmentationConfig,
    ground_truth_volume,
    slice_id: int,
) -> dict:
    """
    Run segmentation and evaluation for one CT slice.

    Parameters
    ----------
    config : SegmentationConfig
        Segmentation configuration.

    ground_truth_volume : np.ndarray
        Complete ground-truth mask volume.

    slice_id : int
        Index of the CT slice to evaluate.

    Returns
    -------
    dict
        Evaluation metrics for the selected slice.
    """

    # ========================================================
    # 1. Run segmentation
    # ========================================================

    result = run_pipeline(
        config,
        slice_id=slice_id,
    )

    # ========================================================
    # 2. Extract corresponding ground truth
    # ========================================================

    ground_truth = get_slice(
        ground_truth_volume,
        slice_id,
    )

    ground_truth = binarize_mask(
        ground_truth
    )

    # ========================================================
    # 3. Predicted segmentation
    # ========================================================

    prediction = result.liver_mask

    # ========================================================
    # 4. Compute metrics
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
    # 5. Return results
    # ========================================================

    return {
        "slice_id": slice_id,
        "dice": dice,
        "iou": iou,
        "sensitivity": sens,
        "specificity": spec,
        "hausdorff": hausdorff,
    }


def main() -> None:
    """
    Evaluate the liver segmentation method on multiple CT slices.
    """

    # ========================================================
    # 1. Load configuration
    # ========================================================

    config = SegmentationConfig()

    # ========================================================
    # 2. Create output directory
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================================
    # 3. Load ground-truth volume once
    # ========================================================

    ground_truth_volume = load_mask_volume(
        config.mask_folder
    )

    # ========================================================
    # 4. Evaluate all selected slices
    # ========================================================

    results = []

    print()
    print("=" * 60)
    print("MULTI-SLICE LIVER SEGMENTATION EVALUATION")
    print("=" * 60)

    for slice_id in SLICE_IDS:

        print(
            f"\nEvaluating slice {slice_id}..."
        )

        metrics = evaluate_slice(
            config,
            ground_truth_volume,
            slice_id,
        )

        results.append(metrics)

        print(
            f"  Dice        : {metrics['dice']:.4f}"
        )

        print(
            f"  IoU         : {metrics['iou']:.4f}"
        )

        print(
            f"  Sensitivity : {metrics['sensitivity']:.4f}"
        )

        print(
            f"  Specificity : {metrics['specificity']:.4f}"
        )

        print(
            f"  Hausdorff   : {metrics['hausdorff']:.4f}"
        )

    # ========================================================
    # 5. Create results DataFrame
    # ========================================================

    dataframe = pd.DataFrame(
        results
    )

    # ========================================================
    # 6. Save per-slice results
    # ========================================================

    dataframe.to_csv(
        RESULTS_FILE,
        index=False,
    )

    # ========================================================
    # 7. Compute mean and standard deviation
    # ========================================================

    metric_columns = [
        "dice",
        "iou",
        "sensitivity",
        "specificity",
        "hausdorff",
    ]

    summary = pd.DataFrame({
        "metric": metric_columns,
        "mean": [
            dataframe[column].mean()
            for column in metric_columns
        ],
        "std": [
            dataframe[column].std()
            for column in metric_columns
        ],
    })

    # ========================================================
    # 8. Save summary
    # ========================================================

    summary.to_csv(
        SUMMARY_FILE,
        index=False,
    )

    # ========================================================
    # 9. Display summary
    # ========================================================

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for _, row in summary.iterrows():

        print(
            f"{row['metric']:15s} : "
            f"{row['mean']:.4f} ± "
            f"{row['std']:.4f}"
        )

    print("=" * 60)

    print(
        f"\nPer-slice results saved to:"
        f"\n{RESULTS_FILE}"
    )

    print(
        f"\nSummary saved to:"
        f"\n{SUMMARY_FILE}"
    )


if __name__ == "__main__":
    main()