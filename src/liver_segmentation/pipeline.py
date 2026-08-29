from dataclasses import dataclass

import numpy as np

from .config import SegmentationConfig
from .data_io import get_slice, load_ct_volume
from .preprocessing import (
    gaussian_smoothing,
    multi_scale_gradient,
)
from .rag import (
    build_region_adjacency_graph,
    compute_region_means,
    create_merged_mask,
    recursive_region_merging,
)
from .similarity import weighted_similarity_criterion
from .postprocessing import (
    fill_holes,
    keep_largest_component,
)
from .watershed_segmentation import apply_watershed
from .seed_detection import detect_seed


@dataclass
class SegmentationResult:
    """
    Container for the intermediate and final results
    produced by the liver segmentation pipeline.
    """

    image: np.ndarray
    smooth: np.ndarray
    gradient: np.ndarray
    watershed_labels: np.ndarray
    merged_mask: np.ndarray
    liver_mask: np.ndarray

    seed_label: int

    mean: float
    std: float
    lower: float
    upper: float

    selected_regions: set[int]


def run_pipeline(
    config: SegmentationConfig,
    slice_id: int | None = None,
) -> SegmentationResult:
    """
    Run the complete liver segmentation pipeline.

    The pipeline follows the methodology implemented in the
    original notebook:

        DICOM volume
            ↓
        CT slice extraction
            ↓
        Weighted similarity criterion
            ↓
        Gaussian smoothing
            ↓
        Multi-scale morphological gradient
            ↓
        Watershed segmentation
            ↓
        Region Adjacency Graph
            ↓
        Region mean intensities
            ↓
        Region merging
            ↓
        Binary merged mask
            ↓
        Largest connected component
            ↓
        Hole filling
            ↓
        Final liver mask

    Parameters
    ----------
    config : SegmentationConfig
        Configuration object containing dataset paths and
        segmentation parameters.

    Returns
    -------
    SegmentationResult
        Object containing the intermediate processing results
        and the final liver segmentation mask.
    """

    # ========================================================
    # 1. Load CT volume
    # ========================================================

    volume = load_ct_volume(
        config.ct_folder
    )

    # ========================================================
    # 2. Extract selected CT slice
    # ========================================================

    # Use the provided slice ID when specified.
    # Otherwise, use the default slice ID from the configuration.
    selected_slice_id = (
        config.slice_id
        if slice_id is None
        else slice_id
    )

    image = get_slice(
        volume,
        selected_slice_id,
    )
    
    seed_x, seed_y = detect_seed(
    image=image,
    mode=config.seed_mode,
    seed_x=config.seed_x,
    seed_y=config.seed_y,
    block_size=config.block_size,
    grid_size=config.seed_grid_size,
    margin_ratio=config.seed_margin_ratio,
)

    # ========================================================
    # 3. Compute weighted similarity criterion
    # ========================================================

    mean, std, lower, upper = weighted_similarity_criterion(
    img=image,
    seed_x=seed_x,
    seed_y=seed_y,
    block_size=config.block_size,
)

    # ========================================================
    # 4. Gaussian smoothing
    # ========================================================

    smooth = gaussian_smoothing(
        image,
        sigma=config.gaussian_sigma,
    )

    # ========================================================
    # 5. Multi-scale morphological gradient
    # ========================================================

    gradient = multi_scale_gradient(
        smooth,
        scales=config.gradient_scales,
    )

    # ========================================================
    # 6. Watershed segmentation
    # ========================================================

    watershed_labels = apply_watershed(
        gradient
    )

    # ========================================================
    # 7. Build Region Adjacency Graph
    # ========================================================

    graph = build_region_adjacency_graph(
        watershed_labels
    )

    # ========================================================
    # 8. Compute mean intensity of each region
    # ========================================================

    region_means = compute_region_means(
        watershed_labels,
        image,
    )

    # ========================================================
    # 9. Identify seed region
    # ========================================================

    seed_label = int(
    watershed_labels[
        seed_y,
        seed_x,
    ]
    )

    # ========================================================
    # 10. Region merging
    # ========================================================

    selected_regions = recursive_region_merging(
        graph=graph,
        region_means=region_means,
        seed_label=seed_label,
        lower=lower,
        upper=upper,
    )

    # ========================================================
    # 11. Create binary merged mask
    # ========================================================

    merged_mask = create_merged_mask(
        watershed_labels,
        selected_regions,
    )

    # ========================================================
    # 12. Keep largest connected component
    # ========================================================

    liver_mask = keep_largest_component(
        merged_mask
    )

    # ========================================================
    # 13. Fill holes
    # ========================================================

    liver_mask = fill_holes(
        liver_mask
    )

    # ========================================================
    # 14. Return complete result
    # ========================================================

    return SegmentationResult(
        image=image,
        smooth=smooth,
        gradient=gradient,
        watershed_labels=watershed_labels,
        merged_mask=merged_mask,
        liver_mask=liver_mask,
        seed_label=seed_label,
        mean=mean,
        std=std,
        lower=lower,
        upper=upper,
        selected_regions=selected_regions,
    )