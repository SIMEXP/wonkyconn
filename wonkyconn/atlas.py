from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
import nibabel as nib
import numpy as np
from numpy import typing as npt
import scipy

from .logger import gc_log


@dataclass
class Atlas(ABC):
    seg: str
    image: nib.nifti1.Nifti1Image

    structure: npt.NDArray[np.bool_] = field(
        default_factory=lambda: np.ones((3, 3, 3), dtype=bool)
    )

    @abstractmethod
    def get_centroid_points(self) -> npt.NDArray[np.float64]:
        raise NotImplementedError

    def get_centroids(self) -> npt.NDArray[np.float64]:
        centroid_points = self.get_centroid_points()
        centroid_coordinates = nib.affines.apply_affine(
            self.image.affine, centroid_points
        )
        return centroid_coordinates

    def get_distance_matrix(self) -> npt.NDArray[np.float64]:
        centroids = self.get_centroids()
        return scipy.spatial.distance.squareform(
            scipy.spatial.distance.pdist(centroids)
        )

    @staticmethod
    def create(seg: str, path: Path) -> "Atlas":
        image = nib.nifti1.load(path)

        if image.ndim <= 3 or image.shape[3] == 1:
            return DsegAtlas(seg, nib.funcs.squeeze_image(image))
        else:
            return ProbsegAtlas(seg, image)


@dataclass
class DsegAtlas(Atlas):
    def get_array(self) -> npt.NDArray[np.int64]:
        return np.asarray(self.image.dataobj, dtype=np.int64)

    def check_single_connected_component(self, array: npt.NDArray[np.int64]) -> None:
        for i in range(1, array.max() + 1):
            mask = array == i
            _, num_features = scipy.ndimage.label(mask, structure=self.structure)
            if num_features > 1:
                gc_log.warning(
                    f'Atlas "{self.seg}" region {i} has more than a single connected component'
                )

    def get_centroid_points(self) -> npt.NDArray[np.float64]:
        array = self.get_array()
        self.check_single_connected_component(array)
        return np.asarray(
            scipy.ndimage.center_of_mass(
                input=array > 0, labels=array, index=np.arange(1, array.max() + 1)
            )
        )


@dataclass
class ProbsegAtlas(Atlas):
    epsilon: float = 1e-6

    def get_centroid_point(
        self, i: int, array: npt.NDArray[np.float64]
    ) -> tuple[float, ...]:
        mask = array > self.epsilon
        _, num_features = scipy.ndimage.label(mask, structure=self.structure)
        if num_features > 1:
            gc_log.warning(
                f'Atlas "{self.seg}" region {i} has more than a single connected component'
            )
        return scipy.ndimage.center_of_mass(array)

    def get_centroid_points(self) -> npt.NDArray[np.float64]:
        return np.asarray(
            [
                self.get_centroid_point(i, image.get_fdata())
                for i, image in enumerate(nib.funcs.four_to_three(self.image))
            ]
        )