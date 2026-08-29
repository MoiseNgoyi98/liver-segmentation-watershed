from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SegmentationConfig:
    """
    Configuration parameters for the liver segmentation pipeline.
    """

    # ========================================================
    # Project paths
    # ========================================================

    project_root: Path = field(
        default_factory=lambda: Path(__file__).resolve().parents[2]
    )

    # ========================================================
    # Dataset
    # ========================================================

    ct_folder: Path | None = None
    mask_folder: Path | None = None

    # ========================================================
    # Slice and seed
    # ========================================================
    
    slice_id: int = 60

    seed_mode: str = "automatic"

    seed_x: int = 200
    seed_y: int = 250

    seed_grid_size: int = 5
    seed_margin_ratio: float = 0.20

    # ========================================================
    # Similarity criterion
    # ========================================================

    block_size: int = 3
    sigma_factor: float = 3.0

    # ========================================================
    # Preprocessing
    # ========================================================

    gaussian_sigma: float = 1.0

    gradient_scales: list[int] = field(
        default_factory=lambda: [1, 2, 3]
    )

    # ========================================================
    # Output directories
    # ========================================================

    output_dir: Path | None = None
    figure_dir: Path | None = None
    result_dir: Path | None = None

    def __post_init__(self):
        """
        Build default project paths after initialization.
        """

        # ----------------------------------------------------
        # Dataset directory
        # ----------------------------------------------------

        data_dir = self.project_root / "data"

        # ----------------------------------------------------
        # CT volume
        # ----------------------------------------------------

        if self.ct_folder is None:
            self.ct_folder = (
                data_dir
                / "3Dircadb1"
                / "3Dircadb1.4"
                / "PATIENT_DICOM"
            )

        # ----------------------------------------------------
        # Liver Ground Truth
        # ----------------------------------------------------

        if self.mask_folder is None:
            self.mask_folder = (
                data_dir
                / "3Dircadb1"
                / "3Dircadb1.4"
                / "MASKS_DICOM"
                / "liver"
            )

        if self.seed_mode not in {"manual", "automatic"}:
            raise ValueError(
                "seed_mode must be either 'manual' or 'automatic'."
            )

        # ----------------------------------------------------
        # Main output directory
        # ----------------------------------------------------

        if self.output_dir is None:
            self.output_dir = (
                self.project_root / "outputs"
            )

        # ----------------------------------------------------
        # Figure directory
        # ----------------------------------------------------

        if self.figure_dir is None:
            self.figure_dir = (
                self.output_dir / "figures"
            )

        # ----------------------------------------------------
        # Result directory
        # ----------------------------------------------------

        if self.result_dir is None:
            self.result_dir = (
                self.output_dir / "results"
            )

    def create_output_directories(self):
        """
        Create directories required to store experiment outputs.
        """

        self.figure_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.result_dir.mkdir(
            parents=True,
            exist_ok=True
        )