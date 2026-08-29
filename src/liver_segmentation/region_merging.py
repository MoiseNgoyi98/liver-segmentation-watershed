import networkx as nx
import numpy as np
from skimage.measure import regionprops


def build_region_adjacency_graph(labels: np.ndarray) -> nx.Graph:
    """
    Build a Region Adjacency Graph.

    Two regions are connected when they touch horizontally or vertically.
    """
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
    """Compute mean CT intensity for each watershed region."""
    means = {}

    for region in regionprops(labels, intensity_image=image):
        means[region.label] = float(region.mean_intensity)

    return means


def recursive_region_merging(
    graph: nx.Graph,
    region_means: dict[int, float],
    seed_label: int,
    lower: float,
    upper: float,
) -> set[int]:
    """
    Expand from the seed region through adjacent regions whose mean
    intensity satisfies the similarity interval.
    """
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
    """Convert selected watershed labels into a binary mask."""
    mask = np.zeros(labels.shape, dtype=np.uint8)

    for label_value in selected_regions:
        mask[labels == label_value] = 1

    return mask
