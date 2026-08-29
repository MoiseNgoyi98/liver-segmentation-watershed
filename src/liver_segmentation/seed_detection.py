
from __future__ import annotations

import numpy as np


def validate_seed(
    image: np.ndarray,
    seed_x: int,
    seed_y: int,
) -> tuple[int, int]:
    """
    Validate that a seed point lies inside a 2D image.

    Parameters
    ----------
    image : np.ndarray
        2D CT image.

    seed_x : int
        Horizontal coordinate of the seed.

    seed_y : int
        Vertical coordinate of the seed.

    Returns
    -------
    tuple[int, int]
        Validated seed coordinates as (x, y).

    Raises
    ------
    ValueError
        If the image is not 2D or the coordinates are outside
        the image boundaries.
    """

    if image.ndim != 2:
        raise ValueError(
            "Seed detection requires a 2D image."
        )

    height, width = image.shape

    if not (0 <= seed_x < width):
        raise ValueError(
            f"seed_x={seed_x} is outside image width={width}."
        )

    if not (0 <= seed_y < height):
        raise ValueError(
            f"seed_y={seed_y} is outside image height={height}."
        )

    return int(seed_x), int(seed_y)


def get_manual_seed(
    image: np.ndarray,
    seed_x: int,
    seed_y: int,
) -> tuple[int, int]:
    """
    Return a validated manually selected seed.
    """

    return validate_seed(
        image=image,
        seed_x=seed_x,
        seed_y=seed_y,
    )


def generate_seed_candidates(
    image: np.ndarray,
    grid_size: int = 5,
    margin_ratio: float = 0.20,
) -> list[tuple[int, int]]:
    """
    Generate candidate seed points inside a central region.

    The outer part of the image is excluded to reduce the probability
    of selecting anatomically implausible points near the image borders.

    Parameters
    ----------
    image : np.ndarray
        2D CT image.

    grid_size : int, default=5
        Number of candidate positions along each dimension.

    margin_ratio : float, default=0.20
        Fraction of the image excluded from each border.

    Returns
    -------
    list[tuple[int, int]]
        Candidate coordinates represented as (x, y).
    """

    if image.ndim != 2:
        raise ValueError(
            "Seed candidate generation requires a 2D image."
        )

    if not 0.0 <= margin_ratio < 0.5:
        raise ValueError(
            "margin_ratio must be between 0.0 and 0.5."
        )

    if grid_size < 2:
        raise ValueError(
            "grid_size must be at least 2."
        )

    height, width = image.shape

    x_min = int(width * margin_ratio)
    x_max = int(width * (1.0 - margin_ratio))

    y_min = int(height * margin_ratio)
    y_max = int(height * (1.0 - margin_ratio))

    x_positions = np.linspace(
        x_min,
        x_max,
        grid_size,
        dtype=int,
    )

    y_positions = np.linspace(
        y_min,
        y_max,
        grid_size,
        dtype=int,
    )

    return [
        (int(x), int(y))
        for y in y_positions
        for x in x_positions
    ]


def score_seed_candidate(
    image: np.ndarray,
    x: int,
    y: int,
    block_size: int = 3,
) -> float:
    """
    Compute a local homogeneity score for a seed candidate.

    The score is defined as the negative local standard deviation.
    Therefore, a higher score corresponds to a more homogeneous
    neighborhood.

    Parameters
    ----------
    image : np.ndarray
        2D CT image.

    x : int
        Candidate horizontal coordinate.

    y : int
        Candidate vertical coordinate.

    block_size : int, default=3
        Size of the local neighborhood.

    Returns
    -------
    float
        Local homogeneity score.
    """

    if image.ndim != 2:
        raise ValueError(
            "Seed scoring requires a 2D image."
        )

    if block_size < 1:
        raise ValueError(
            "block_size must be greater than zero."
        )

    if block_size % 2 == 0:
        raise ValueError(
            "block_size must be an odd number."
        )

    validate_seed(
        image=image,
        seed_x=x,
        seed_y=y,
    )

    half = block_size // 2

    y_min = max(0, y - half)
    y_max = min(image.shape[0], y + half + 1)

    x_min = max(0, x - half)
    x_max = min(image.shape[1], x + half + 1)

    block = image[
        y_min:y_max,
        x_min:x_max,
    ]

    if block.size == 0:
        return float("-inf")

    return -float(np.std(block))


def select_best_seed(
    image: np.ndarray,
    candidates: list[tuple[int, int]],
    block_size: int = 3,
) -> tuple[int, int]:
    """
    Select the most homogeneous candidate seed.

    The candidate with the highest homogeneity score
    (lowest local standard deviation) is selected.

    Parameters
    ----------
    image : np.ndarray
        2D CT image.

    candidates : list[tuple[int, int]]
        Candidate seed coordinates.

    block_size : int, default=3
        Size of the local neighborhood used for scoring.

    Returns
    -------
    tuple[int, int]
        Selected seed coordinates.

    Raises
    ------
    ValueError
        If no candidates are provided.
    """

    if not candidates:
        raise ValueError(
            "At least one seed candidate is required."
        )

    best_seed = max(
        candidates,
        key=lambda seed: score_seed_candidate(
            image=image,
            x=seed[0],
            y=seed[1],
            block_size=block_size,
        ),
    )

    return best_seed


def detect_seed(
    image: np.ndarray,
    mode: str = "manual",
    seed_x: int | None = None,
    seed_y: int | None = None,
    block_size: int = 3,
    grid_size: int = 5,
    margin_ratio: float = 0.20,
) -> tuple[int, int]:
    """
    Determine the seed used by the segmentation pipeline.

    Parameters
    ----------
    image : np.ndarray
        2D CT image.

    mode : str, default="manual"
        Seed detection mode.

        "manual"
            Use the specified seed coordinates.

        "automatic"
            Generate candidates inside the central region and
            select the most homogeneous candidate.

    seed_x : int, optional
        Manual horizontal seed coordinate.

    seed_y : int, optional
        Manual vertical seed coordinate.

    block_size : int, default=3
        Local neighborhood size used by the automatic scoring.

    grid_size : int, default=5
        Number of candidate positions per dimension.

    margin_ratio : float, default=0.20
        Fraction excluded from each image border.

    Returns
    -------
    tuple[int, int]
        Seed coordinates as (x, y).

    Raises
    ------
    ValueError
        If an unsupported mode is provided or manual coordinates
        are missing.
    """

    if image.ndim != 2:
        raise ValueError(
            "Seed detection requires a 2D image."
        )

    if mode == "manual":

        if seed_x is None or seed_y is None:
            raise ValueError(
                "seed_x and seed_y are required in manual mode."
            )

        return get_manual_seed(
            image=image,
            seed_x=seed_x,
            seed_y=seed_y,
        )

    if mode == "automatic":

        candidates = generate_seed_candidates(
            image=image,
            grid_size=grid_size,
            margin_ratio=margin_ratio,
        )

        return select_best_seed(
            image=image,
            candidates=candidates,
            block_size=block_size,
        )

    raise ValueError(
        f"Unsupported seed mode: {mode!r}. "
        "Expected 'manual' or 'automatic'."
    )
