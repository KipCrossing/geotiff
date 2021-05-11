from typing import List, Optional, Tuple, Union
from shapely.geometry import Point, Polygon  # type: ignore
from tifffile import imread, TiffFile  # type: ignore
import numpy as np  # type: ignore
from pyproj import Transformer, CRS
import zarr  # type: ignore


BBox = Tuple[Tuple[float, float], Tuple[float, float]]
BBoxInt = Tuple[Tuple[int, int], Tuple[int, int]]


class GeographicTypeGeoKeyError(Exception):
    def __init__(_):
        pass

    def __str__(_):
        return "Could not recognize the geo key\nPlease submit an issue: \
                https://github.com/Open-Source-Agriculture/geotiff/issues"


class UserDefinedGeoKeyError(Exception):
    def __init__(_):
        pass

    def __str__(_):
        return "user-defined GeoKeys are not yet supported"


class BoundaryNotInTifError(Exception):
    pass


class FileTypeError(Exception):
    pass


class TifTransformer:
    def __init__(
        self,
        height: int,
        width: int,
        scale: Tuple[float, float, float],
        tiepoints: List[float],
    ):
        """for transforming the coordinates of the geotiff file

        Args:
            height (int): Hight (y) of the geotiff array/file
            width (int): Width of the geotiff array/file
            scale (Tuple[float, float, float]): (sx, sy, sz) from ModelPixelScaleTag
            tiepoints (List[float]): [description]
        """
        self.width: int = width
        self.height: int = height
        sx, sy, sz = scale  # ModelPixelScaleTag
        transforms: List[List[List[float]]] = []
        for tp in range(0, len(tiepoints), 6):
            i, j, k, x, y, z = tiepoints[tp : tp + 6]
            transforms.append(
                [
                    [sx, 0.0, 0.0, x - i * sx],
                    [0.0, -sy, 0.0, y + j * sy],
                    [0.0, 0.0, sz, z - k * sz],
                    [0.0, 0.0, 0.0, 1.0],
                ]
            )
        # if len(tiepoints) == 6:
        #     transforms = transforms[0]
        self.transforms: List[List[List[float]]] = transforms

    def get_x(self, i: int, j: int) -> float:
        """Gets the x or lon coordinate based on the array index

        Args:
            i (int): index in the x direction
            j (int): index in the y direction

        Returns:
            float: x or lon coordinate
        """
        transformed: List[float] = np.dot(self.transforms, [i, j, 0, 1]).tolist()[0]
        transformed_xy: List[float] = transformed[:2]
        return transformed_xy[0]

    def get_y(self, i: int, j: int) -> float:
        """Gets the y or lat coordinate based on the array index

        Args:
            i (int): index in the x direction
            j (int): index in the y direction

        Returns:
            float: y or lat coordinate
        """
        transformed: List[float] = np.dot(self.transforms, [i, j, 0, 1]).tolist()[0]
        transformed_xy: List[float] = transformed[:2]
        return transformed_xy[1]

    def get_xy(self, i: int, j: int) -> Tuple[float, float]:
        """Gets the (x or lon) and (y or lat) coordinates based on the array index

        Args:
            i (int): index in the x direction
            j (int): index in the y direction

        Returns:
            Tuple[float, float]: (x or lon) and (y or lat) coordinates
        """
        transformed: List[float] = np.dot(self.transforms, [i, j, 0, 1]).tolist()[0]
        transformed_xy: List[float] = transformed[:2]
        return (transformed_xy[0], transformed_xy[1])


class GeoTiff:
    def __init__(self, file: str, crs_code: Optional[int] = None):
        """For representing a geotiff

        Args:
            file (str): Location of the geoTiff file
            crs_code (Optional[int]): the crs code of the tiff file

        Raises:
            FileTypeError: [description]
        """
        self.file = file
        tif = TiffFile(self.file)

        if not tif.is_geotiff:
            raise Exception("Not a geotiff file")

        store = imread(self.file, aszarr=True)
        self.z = zarr.open(store, mode="r")
        store.close()
        if isinstance(crs_code, int):
            self.crs_code: int = crs_code
        else:
            self.crs_code = self._get_crs_code(tif.geotiff_metadata)
        self.tifShape: List[int] = self.z.shape
        scale: Tuple[float, float, float] = tif.geotiff_metadata["ModelPixelScale"]
        tilePoint: List[float] = tif.geotiff_metadata["ModelTiepoint"]
        self.tifTrans: TifTransformer = TifTransformer(
            self.tifShape[0], self.tifShape[1], scale, tilePoint
        )
        self.tif_bBox: BBox = (
            self.tifTrans.get_xy(0, 0),
            self.tifTrans.get_xy(self.tifShape[1], self.tifShape[0]),
        )
        tif.close()

    def _get_crs_code(self, geotiff_metadata: dict, guess: bool = True) -> int:
        temp_crs_code: Optional[int] = None
        if geotiff_metadata["GTModelTypeGeoKey"].value == 1:
            temp_crs_code = geotiff_metadata["ProjectedCSTypeGeoKey"].value
            # TODO
            # if the ProjectedCSTypeGeoKey is user defined (32767)
            # use supplied keys to get the datum and define the CRS
        elif geotiff_metadata["GTModelTypeGeoKey"].value == 2:
            temp_crs_code = geotiff_metadata["GeographicTypeGeoKey"].value

        if temp_crs_code != 32767 and isinstance(temp_crs_code, int):
            return temp_crs_code
        elif temp_crs_code == 32767:
            raise UserDefinedGeoKeyError()
        else:
            raise GeographicTypeGeoKeyError()

    def _convert_to_wgs_84(
        self, crs_code: int, xxyy: Tuple[float, float]
    ) -> Tuple[float, float]:
        xx: float = xxyy[0]
        yy: float = xxyy[1]
        crs_4326: CRS = CRS("WGS84")
        crs_proj: CRS = CRS.from_epsg(crs_code)
        transformer: Transformer = Transformer.from_crs(
            crs_proj, crs_4326, always_xy=True
        )
        return transformer.transform(xx, yy)

    def _convert_from_wgs_84(
        self, crs_code: int, xxyy: Tuple[float, float]
    ) -> Tuple[float, float]:
        xx: float = xxyy[0]
        yy: float = xxyy[1]
        crs_4326: CRS = CRS("WGS84")
        crs_proj: CRS = CRS.from_epsg(crs_code)
        transformer: Transformer = Transformer.from_crs(
            crs_4326, crs_proj, always_xy=True
        )
        return transformer.transform(xx, yy)

    def _get_x_int(self, lon) -> int:
        step_x: float = float(
            self.tifShape[1] / (self.tif_bBox[1][0] - self.tif_bBox[0][0])
        )
        return int(step_x * (lon - self.tif_bBox[0][0]))

    def _get_y_int(self, lat) -> int:
        step_y: float = self.tifShape[0] / (self.tif_bBox[1][1] - self.tif_bBox[0][1])
        return int(step_y * (lat - self.tif_bBox[0][1]))

    def get_wgs_84_coords(self, i: int, j) -> Tuple[float, float]:
        """for a given i, j in the entire tiff array,
        returns the wgs_84 coordinates

        Args:
            i (int): col number of the array
            j (int): row number of the array

        Returns:
            Tuple[float, float]: lon, lat
        """
        x, y = self.tifTrans.get_xy(i, j)
        return self._convert_to_wgs_84(self.crs_code, (x, y))

    @property
    def tif_bBox_wgs_84(self) -> BBox:
        right_top = self._convert_to_wgs_84(self.crs_code, self.tif_bBox[0])
        left_bottom = self._convert_to_wgs_84(self.crs_code, self.tif_bBox[1])
        return (right_top, left_bottom)

    def _check_bound_in_tiff(self, shp_bBox, b_bBox):
        check = shp_bBox[0][0] >= b_bBox[0][0]
        check = check and (shp_bBox[1][0] <= b_bBox[1][0])
        check = check and (shp_bBox[0][1] <= b_bBox[0][1])
        check = check and (shp_bBox[1][1] >= b_bBox[1][1])
        if not check:
            raise BoundaryNotInTifError()

        tif_poly: Polygon = Polygon(
            [
                (self.tif_bBox[0][0], self.tif_bBox[0][1]),
                (self.tif_bBox[0][0], self.tif_bBox[1][1]),
                (self.tif_bBox[1][0], self.tif_bBox[1][1]),
                (self.tif_bBox[1][0], self.tif_bBox[0][1]),
            ]
        )
        b_poly: Polygon = Polygon(
            [
                (b_bBox[0][0], b_bBox[0][1]),
                (b_bBox[0][0], b_bBox[1][1]),
                (b_bBox[1][0], b_bBox[1][1]),
                (b_bBox[1][0], b_bBox[0][1]),
            ]
        )
        if not tif_poly.contains(b_poly):
            raise BoundaryNotInTifError()

    def _get_outer_ints(self, b_bBox):
        x_min: int = self._get_x_int(b_bBox[0][0]) + int(
            not self.tif_bBox[0][0] == b_bBox[0][0]
        )
        y_min: int = self._get_y_int(b_bBox[0][1]) + int(
            not self.tif_bBox[0][1] == b_bBox[0][1]
        )
        x_max: int = self._get_x_int(b_bBox[1][0])
        y_max: int = self._get_y_int(b_bBox[1][1])
        return (x_min, y_min, x_max, y_max)

    def get_int_box(
        self, bBox: BBox, outer_points: Union[bool, int] = False
    ) -> BBoxInt:
        """Gets the intiger array index values based on a bounding box

        Args:
            bBox (BBox): A bounding box
            outer_points (Union[bool, int]): Takes an int (n) that gets extra n layers of points/pixels that directly surround the bBox. Defaults to False.

        Raises:
            BoundaryNotInTifError: If the boundary is not enclosed withing the
                                    outer cooridinated of the tiff

        Returns:
            BBoxInt: array index values
        """
        b_bBox_0 = self._convert_from_wgs_84(self.crs_code, bBox[0])
        b_bBox_1 = self._convert_from_wgs_84(self.crs_code, bBox[1])
        b_bBox = (b_bBox_0, b_bBox_1)
        x_min, y_min, x_max, y_max = self._get_outer_ints(b_bBox)

        if outer_points:
            x_min_out: int = x_min - int(outer_points)
            y_min_out: int = y_min - int(outer_points)
            x_max_out: int = x_max + int(outer_points)
            y_max_out: int = y_max + int(outer_points)
            height = self.tifShape[0]
            width = self.tifShape[1]
            if (
                x_min_out < 0
                or y_min_out < 0
                or x_max_out > width
                or y_max_out > height
            ):
                raise BoundaryNotInTifError(
                    "Your area_box is too close to the tif edge and cannot get the outer points"
                )
            return ((x_min_out, y_min_out), (x_max_out, y_max_out))

        shp_bBox = [
            self.tifTrans.get_xy(x_min, y_min),
            self.tifTrans.get_xy(x_max, y_max),
        ]
        self._check_bound_in_tiff(shp_bBox, b_bBox)
        return ((x_min, y_min), (x_max, y_max))

    def get_bBox_wgs_84(
        self, bBox: BBox, outer_points: Union[bool, int] = False
    ) -> BBox:
        """takes a bounding area gets the coordinates of the extremities
        as if they were clipped by that bounding area

        Args:
            bBox (BBox): bounding box area to clip within (wgs_84)
            outer_points (Union[bool, int]): Takes an int (n) that gets extra n layers of points/pixels that directly surround the bBox. Defaults to False.

        Returns:
            BBox: in wgs_84
        """
        b = self.get_int_box(bBox, outer_points=outer_points)
        left_top = self.get_wgs_84_coords(b[0][0], b[0][1])
        right_bottom = self.get_wgs_84_coords(b[1][0], b[1][1])
        return (left_top, right_bottom)

    def read(self) -> np.ndarray:
        """Reade the contents of the geotiff to a zarr array

        Returns:
            np.ndarray: zarr array of the geotiff file
        """
        return self.z

    def read_box(
        self, bBox: BBox, outer_points: Union[bool, int] = False
    ) -> np.ndarray:
        """[summary]

        Args:
            bBox (BBox): A bounding box
            outer_points (Union[bool, int]): Takes an int (n) that gets extra n layers of points/pixels that directly surround the bBox. Defaults to False.

        Returns:
            np.ndarray: zarr array of the geotiff file
        """
        ((x_min, y_min), (x_max, y_max)) = self.get_int_box(
            bBox, outer_points=outer_points
        )
        tiff_array = self.read()
        cut_tif_array: np.ndarray = tiff_array[y_min:y_max, x_min:x_max]
        return cut_tif_array
