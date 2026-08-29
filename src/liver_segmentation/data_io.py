from pathlib import Path

import numpy as np
import pydicom


def load_dicom_volume(folder):
    """
    Load a 3D volume from a folder containing DICOM files.

    Parameters
    ----------
    folder : str or Path
        Directory containing the DICOM slices.

    Returns
    -------
    numpy.ndarray
        3D volume with shape:
        (number_of_slices, height, width)
    """

    folder = Path(folder)

    if not folder.exists():
        raise FileNotFoundError(
            f"DICOM folder not found: {folder}"
        )

    files = sorted(
        file for file in folder.iterdir()
        if file.is_file()
    )

    if not files:
        raise ValueError(
            f"No DICOM files found in: {folder}"
        )

    volume = []

    for file in files:

        dataset = pydicom.dcmread(file)

        if not hasattr(dataset, "pixel_array"):
            continue

        volume.append(
            dataset.pixel_array
        )

    if not volume:
        raise ValueError(
            f"No readable DICOM images found in: {folder}"
        )

    return np.asarray(volume)


def load_ct_volume(folder):
    """
    Load a CT volume from a DICOM directory.

    Parameters
    ----------
    folder : str or Path
        Directory containing CT DICOM slices.

    Returns
    -------
    numpy.ndarray
        3D CT volume.
    """

    return load_dicom_volume(folder)


def load_mask_volume(folder):
    """
    Load a ground-truth segmentation mask volume
    from a DICOM directory.

    Parameters
    ----------
    folder : str or Path
        Directory containing liver mask DICOM slices.

    Returns
    -------
    numpy.ndarray
        3D ground-truth mask volume.
    """

    return load_dicom_volume(folder)


def get_slice(volume, slice_id):
    """
    Extract one 2D slice from a 3D volume.

    Parameters
    ----------
    volume : numpy.ndarray
        3D image or mask volume.

    slice_id : int
        Index of the slice to extract.

    Returns
    -------
    numpy.ndarray
        Selected 2D slice.
    """

    if volume.ndim != 3:
        raise ValueError(
            "Expected a 3D volume."
        )

    if not 0 <= slice_id < volume.shape[0]:
        raise IndexError(
            f"Slice index {slice_id} is out of range "
            f"for volume with {volume.shape[0]} slices."
        )

    return volume[slice_id]


def binarize_mask(mask):
    """
    Convert a segmentation mask into a binary mask.

    All non-zero pixels are considered foreground.

    Parameters
    ----------
    mask : numpy.ndarray
        Input segmentation mask.

    Returns
    -------
    numpy.ndarray
        Boolean binary mask.
    """

    return mask > 0