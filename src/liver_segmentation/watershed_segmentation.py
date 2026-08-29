import numpy as np

from skimage.segmentation import watershed


def apply_watershed(
    gradient: np.ndarray,
    markers: np.ndarray | None = None
) -> np.ndarray:
    """
    Apply watershed segmentation to a gradient image.

    The gradient image is interpreted as a topographic surface.
    Low-gradient areas correspond to basins, while high-gradient
    areas represent potential boundaries between regions.

    Parameters
    ----------
    gradient : np.ndarray
        2D morphological gradient image used as the topographic
        surface for watershed segmentation.

    markers : np.ndarray, optional
        Marker image defining the starting regions for watershed.
        If None, watershed is applied without explicitly defined
        markers.

    Returns
    -------
    np.ndarray
        2D labeled image in which each segmented region is
        represented by a unique integer label.

    Raises
    ------
    ValueError
        If the gradient image is not a 2D array.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if gradient.ndim != 2:
        raise ValueError(
            "The gradient image must be a 2D array."
        )

    # --------------------------------------------------------
    # Apply watershed segmentation
    # --------------------------------------------------------

    labels = watershed(
        gradient,
        markers=markers
    )

    return labels