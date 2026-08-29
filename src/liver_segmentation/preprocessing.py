import numpy as np

from scipy.ndimage import gaussian_filter

from skimage.morphology import disk
from skimage.morphology import dilation
from skimage.morphology import erosion


def gaussian_smoothing(
    image,
    sigma=1.0
):
    """
    Apply Gaussian smoothing to a CT image.

    Gaussian filtering reduces high-frequency noise and produces
    a smoother image for the subsequent morphological processing.

    Parameters
    ----------
    image : numpy.ndarray
        2D CT image.

    sigma : float, optional
        Standard deviation of the Gaussian kernel.
        Default is 1.0.

    Returns
    -------
    numpy.ndarray
        Gaussian-smoothed image.
    """

    return gaussian_filter(
        image,
        sigma=sigma
    )


def multi_scale_gradient(
    image,
    scales=None
):
    """
    Compute a multi-scale morphological gradient.

    The morphological gradient is computed as the difference
    between morphological dilation and erosion. The operation
    is repeated at several structuring-element scales and the
    resulting gradients are averaged.

    Parameters
    ----------
    image : numpy.ndarray
        2D input image.

    scales : list[int], optional
        Radii of the disk-shaped structuring elements.
        Default is [1, 2, 3].

    Returns
    -------
    numpy.ndarray
        Multi-scale morphological gradient.
    """

    if scales is None:
        scales = [1, 2, 3]

    gradient = np.zeros(
        image.shape,
        dtype=np.float64
    )

    for scale in scales:

        # Create a disk-shaped structuring element
        structuring_element = disk(scale)

        # Morphological dilation
        dilated = dilation(
            image,
            structuring_element
        )

        # Morphological erosion
        eroded = erosion(
            image,
            structuring_element
        )

        # Morphological gradient at the current scale
        gradient += (
            dilated - eroded
        )

    # Average the gradients obtained at all scales
    gradient /= len(scales)

    return gradient