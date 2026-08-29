import numpy as np

from scipy.spatial.distance import directed_hausdorff


def dice_score(
    ground_truth: np.ndarray,
    prediction: np.ndarray,
) -> float:
    """
    Compute the Dice Similarity Coefficient (DSC).

    Parameters
    ----------
    ground_truth : np.ndarray
        Binary reference mask.

    prediction : np.ndarray
        Binary predicted mask.

    Returns
    -------
    float
        Dice score in the range [0, 1].
    """

    ground_truth = ground_truth.astype(bool)
    prediction = prediction.astype(bool)

    intersection = np.logical_and(
        ground_truth,
        prediction,
    ).sum()

    denominator = (
        ground_truth.sum()
        + prediction.sum()
    )

    if denominator == 0:
        return 1.0

    return (
        2.0 * intersection
    ) / denominator


def iou_score(
    ground_truth: np.ndarray,
    prediction: np.ndarray,
) -> float:
    """
    Compute the Intersection over Union (IoU).

    Parameters
    ----------
    ground_truth : np.ndarray
        Binary reference mask.

    prediction : np.ndarray
        Binary predicted mask.

    Returns
    -------
    float
        IoU score in the range [0, 1].
    """

    ground_truth = ground_truth.astype(bool)
    prediction = prediction.astype(bool)

    intersection = np.logical_and(
        ground_truth,
        prediction,
    ).sum()

    union = np.logical_or(
        ground_truth,
        prediction,
    ).sum()

    if union == 0:
        return 1.0

    return intersection / union


def sensitivity(
    ground_truth: np.ndarray,
    prediction: np.ndarray,
) -> float:
    """
    Compute Sensitivity (Recall).

    Sensitivity measures the proportion of actual
    positive pixels correctly detected by the prediction.
    """

    ground_truth = ground_truth.astype(bool)
    prediction = prediction.astype(bool)

    true_positive = np.logical_and(
        ground_truth,
        prediction,
    ).sum()

    false_negative = np.logical_and(
        ground_truth,
        np.logical_not(prediction),
    ).sum()

    denominator = true_positive + false_negative

    if denominator == 0:
        return 1.0

    return true_positive / denominator


def specificity(
    ground_truth: np.ndarray,
    prediction: np.ndarray,
) -> float:
    """
    Compute Specificity.

    Specificity measures the proportion of actual
    background pixels correctly identified as background.
    """

    ground_truth = ground_truth.astype(bool)
    prediction = prediction.astype(bool)

    true_negative = np.logical_and(
        np.logical_not(ground_truth),
        np.logical_not(prediction),
    ).sum()

    false_positive = np.logical_and(
        np.logical_not(ground_truth),
        prediction,
    ).sum()

    denominator = true_negative + false_positive

    if denominator == 0:
        return 1.0

    return true_negative / denominator


def hausdorff_distance(
    ground_truth: np.ndarray,
    prediction: np.ndarray,
) -> float:
    """
    Compute the symmetric Hausdorff distance between two binary masks.

    Parameters
    ----------
    ground_truth : np.ndarray
        Binary reference mask.

    prediction : np.ndarray
        Binary predicted mask.

    Returns
    -------
    float
        Symmetric Hausdorff distance in pixels.
    """

    ground_truth = ground_truth.astype(bool)
    prediction = prediction.astype(bool)

    ground_truth_points = np.argwhere(
        ground_truth
    )

    prediction_points = np.argwhere(
        prediction
    )

    if (
        len(ground_truth_points) == 0
        and len(prediction_points) == 0
    ):
        return 0.0

    if (
        len(ground_truth_points) == 0
        or len(prediction_points) == 0
    ):
        return float("inf")

    distance_gt_to_prediction = directed_hausdorff(
        ground_truth_points,
        prediction_points,
    )[0]

    distance_prediction_to_gt = directed_hausdorff(
        prediction_points,
        ground_truth_points,
    )[0]

    return max(
        distance_gt_to_prediction,
        distance_prediction_to_gt,
    )