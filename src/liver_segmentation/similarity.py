import numpy as np


def weighted_similarity_criterion(
    img,
    seed_x,
    seed_y,
    block_size=3,
    sigma_factor=3.0
):
    """
    Compute a weighted statistical similarity criterion
    around a selected seed point.

    The method estimates a weighted mean and standard deviation
    from local neighborhoods around the seed point.

    The resulting statistical interval is then used during
    region merging to determine whether neighboring regions
    have similar intensity characteristics.

    Parameters
    ----------
    img : numpy.ndarray
        2D CT image.

    seed_x : int
        X-coordinate of the seed point.

    seed_y : int
        Y-coordinate of the seed point.

    block_size : int, optional
        Distance between neighboring block centers.
        Default is 3.

    sigma_factor : float, optional
        Multiplication factor used to define the similarity
        interval. Default is 3.0.

    Returns
    -------
    tuple
        (mean, standard_deviation, lower_threshold, upper_threshold)
    """

    # --------------------------------------------------------
    # Gaussian-like spatial weighting kernel
    # --------------------------------------------------------

    weights = np.array([
        [0.0625, 0.125, 0.0625],
        [0.1250, 0.250, 0.1250],
        [0.0625, 0.125, 0.0625]
    ])

    # --------------------------------------------------------
    # Store weighted local statistics
    # --------------------------------------------------------

    weighted_means = []
    weighted_variances = []

    # --------------------------------------------------------
    # Analyze the 3x3 neighborhood of blocks
    # around the seed point
    # --------------------------------------------------------

    idx = 0

    for j in [-1, 0, 1]:

        for i in [-1, 0, 1]:

            # Coordinates of the current block center
            x = seed_x + i * block_size
            y = seed_y + j * block_size

            # Extract local 3x3 pixel block
            block = img[
                y - 1:y + 2,
                x - 1:x + 2
            ]

            # Safety check for image boundaries
            if block.size == 0:
                continue

            # Local mean
            local_mean = np.mean(block)

            # Local variance
            local_variance = np.var(block)

            # Spatial weighting
            weight = weights.flat[idx]

            weighted_means.append(
                local_mean * weight
            )

            weighted_variances.append(
                local_variance * weight
            )

            idx += 1

    # --------------------------------------------------------
    # Global weighted statistics
    # --------------------------------------------------------

    mean = np.sum(weighted_means)

    standard_deviation = np.sqrt(
        np.sum(weighted_variances)
    )

    # --------------------------------------------------------
    # Statistical similarity interval
    # --------------------------------------------------------

    lower_threshold = (
        mean - sigma_factor * standard_deviation
    )

    upper_threshold = (
        mean + sigma_factor * standard_deviation
    )

    return (
        mean,
        standard_deviation,
        lower_threshold,
        upper_threshold
    )