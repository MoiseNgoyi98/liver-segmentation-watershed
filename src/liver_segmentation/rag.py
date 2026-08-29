import networkx as nx
import numpy as np

from skimage.measure import regionprops


def build_region_adjacency_graph(labels: np.ndarray) -> nx.Graph:
    """
    Build a Region Adjacency Graph.

    Two regions are connected when they touch horizontally or vertically.

    Parameters
    ----------
    labels : np.ndarray
        2D watershed label image.

    Returns
    -------
    nx.Graph
        Region Adjacency Graph.
    """

    if labels.ndim != 2:
        raise ValueError(
            "The label image must be a 2D array."
        )

    graph = nx.Graph()

    rows, cols = labels.shape

    for y in range(rows - 1):
        for x in range(cols - 1):

            current = labels[y, x]
            right = labels[y, x + 1]
            down = labels[y + 1, x]

            if current != right:
                graph.add_edge(current, right)

            if current != down:
                graph.add_edge(current, down)

    return graph


def compute_region_means(
    labels: np.ndarray,
    image: np.ndarray,
) -> dict[int, float]:
    """
    Compute mean CT intensity for each watershed region.

    Parameters
    ----------
    labels : np.ndarray
        2D watershed label image.

    image : np.ndarray
        2D CT image.

    Returns
    -------
    dict[int, float]
        Mapping between region labels and mean CT intensity.
    """

    if labels.ndim != 2:
        raise ValueError(
            "The label image must be a 2D array."
        )

    if image.ndim != 2:
        raise ValueError(
            "The CT image must be a 2D array."
        )

    if labels.shape != image.shape:
        raise ValueError(
            "Labels and image must have the same shape."
        )

    means = {}

    for region in regionprops(
        labels,
        intensity_image=image
    ):
        means[region.label] = float(
            region.intensity_mean   
        )

    return means


def recursive_region_merging(
    graph: nx.Graph,
    region_means: dict[int, float],
    seed_label: int,
    lower: float,
    upper: float,
) -> set[int]:
    """
    Expand from the seed region through adjacent regions whose
    mean intensity satisfies the similarity interval.

    Parameters
    ----------
    graph : nx.Graph
        Region Adjacency Graph.

    region_means : dict[int, float]
        Mean intensity associated with each watershed region.

    seed_label : int
        Label of the watershed region containing the seed point.

    lower : float
        Lower intensity threshold.

    upper : float
        Upper intensity threshold.

    Returns
    -------
    set[int]
        Labels of the selected regions.
    """

    if seed_label not in graph:
        raise ValueError(
            f"Seed label {seed_label} is not present in the RAG."
        )

    merged_labels: set[int] = set()

    stack = [seed_label]

    while stack:

        current = stack.pop()

        if current in merged_labels:
            continue

        if current not in region_means:
            continue

        mean_value = region_means[current]

        if lower <= mean_value <= upper:

            merged_labels.add(current)

            for neighbor in graph.neighbors(current):

                if neighbor not in merged_labels:
                    stack.append(neighbor)

    return merged_labels


def create_merged_mask(
    labels: np.ndarray,
    selected_regions: set[int],
) -> np.ndarray:
    """
    Convert selected watershed regions into a binary mask.

    Parameters
    ----------
    labels : np.ndarray
        Watershed label image.

    selected_regions : set[int]
        Labels selected during region merging.

    Returns
    -------
    np.ndarray
        Binary segmentation mask.
    """

    mask = np.zeros(
        labels.shape,
        dtype=np.uint8
    )

    for label_value in selected_regions:

        mask[labels == label_value] = 1

    return mask