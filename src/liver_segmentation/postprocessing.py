import numpy as np

from scipy.ndimage import binary_fill_holes
from skimage.measure import label
from skimage.measure import regionprops


def keep_largest_component(
    mask: np.ndarray,
) -> np.ndarray:
    """
    Keep only the largest connected component of a binary mask.

    This operation removes smaller disconnected regions that may
    correspond to false positive regions after region merging.

    Parameters
    ----------
    mask : np.ndarray
        2D binary segmentation mask.

    Returns
    -------
    np.ndarray
        Binary mask containing only the largest connected component.

    Raises
    ------
    ValueError
        If the input mask is not a 2D array.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if mask.ndim != 2:
        raise ValueError(
            "The input mask must be a 2D array."
        )

    # --------------------------------------------------------
    # Label connected components
    # --------------------------------------------------------

    labeled_mask = label(mask)

    # Extract properties of each connected component
    regions = regionprops(labeled_mask)

    # Handle the case where the mask is empty
    if not regions:
        return np.zeros_like(
            mask,
            dtype=bool
        )

    # --------------------------------------------------------
    # Find largest connected component
    # --------------------------------------------------------

    largest_region = max(
        regions,
        key=lambda region: region.area
    )

    # --------------------------------------------------------
    # Create binary mask
    # --------------------------------------------------------

    largest_component = (
        labeled_mask == largest_region.label
    )

    return largest_component


def fill_holes(
    mask: np.ndarray,
) -> np.ndarray:
    """
    Fill internal holes in a binary segmentation mask.

    This operation improves the anatomical continuity of the
    segmented liver region by filling enclosed background areas.

    Parameters
    ----------
    mask : np.ndarray
        2D binary segmentation mask.

    Returns
    -------
    np.ndarray
        Binary mask after hole filling.

    Raises
    ------
    ValueError
        If the input mask is not a 2D array.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if mask.ndim != 2:
        raise ValueError(
            "The input mask must be a 2D array."
        )

    # --------------------------------------------------------
    # Fill internal holes
    # --------------------------------------------------------

    filled_mask = binary_fill_holes(mask)

    return filled_mask