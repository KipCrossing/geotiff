from typing import List, Optional, Tuple, Union
from tifffile import imread, TiffFile  # type: ignore
import numpy as np  # type: ignore
from pyproj import Transformer, CRS
import zarr  # type: ignore


BBox = Tuple[Tuple[float, float], Tuple[float, float]]
BBoxInt = Tuple[Tuple[int, int], Tuple[int, int]]


class GeographicTypeGeoKeyError(Exception):
    def __str__(_):
        return "Could not recognize the geo key\nPlease submit an issue: \
                https://github.com/Open-Source-Agriculture/geotiff/issues"


class UserDefinedGeoKeyError(Exception):
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
    def __init__(
        self,
        file: str,
        band: int = 0,
        as_crs: Optional[int] = 4326,
        crs_code: Optional[int] = None,
    ):
        """For representing a geotiff

        Args:
            file (str): Location of the geotiff file
            band (int): The band of the tiff file to use. Defaults to 0.
            as_crs (Optional[int]): The epsg crs code to read the data as.  Defaults to 4326 (WGS84).
            crs_code (Optional[int]): The epsg crs code of the tiff file. Include this if the crs code can't be detected.

        """
        self.file = file
        self._as_crs = crs_code if as_crs==None else as_crs
        tif = TiffFile(self.file)

        if not tif.is_geotiff:
            raise Exception("Not a geotiff file")

        store = tif.aszarr(key=band)
        self._z = zarr.open(store, mode="r")
        store.close()
        if isinstance(crs_code, int):
            self._crs_code: int = crs_code
        else:
            self._crs_code = self._get_crs_code(tif.geotiff_metadata)
        self._tif_shape: List[int] = self._z.shape
        scale: Tuple[float, float, float] = tif.geotiff_metadata["ModelPixelScale"]
        tilePoint: List[float] = tif.geotiff_metadata["ModelTiepoint"]
        self._tifTrans: TifTransformer = TifTransformer(
            self._tif_shape[0], self._tif_shape[1], scale, tilePoint
        )
        tif.close()

    @property
    def crs_code(self):
        return self._crs_code

    @property
    def as_crs(self):
        return self._as_crs

    @property
    def tif_shape(self):
        return self._tif_shape

    @property
    def tifTrans(self):
        return self._tifTrans

    @property
    def tif_bBox(self):
        return (
            self.tifTrans.get_xy(0, 0),
            self.tifTrans.get_xy(self.tif_shape[1], self.tif_shape[0]),
        )

    @property
    def tif_bBox_converted(self) -> BBox:
        right_top = self._convert_coords(self.crs_code, self.as_crs, self.tif_bBox[0])
        left_bottom = self._convert_coords(self.crs_code, self.as_crs, self.tif_bBox[1])
        return (right_top, left_bottom)

    @property
    def tif_bBox_wgs_84(self) -> BBox:
        right_top = self._convert_coords(self.crs_code, 4326, self.tif_bBox[0])
        left_bottom = self._convert_coords(self.crs_code, 4326, self.tif_bBox[1])
        return (right_top, left_bottom)

    def _get_crs_code(self, geotiff_metadata: dict) -> int:
        temp_crs_code: Optional[int] = None
        if geotiff_metadata["GTModelTypeGeoKey"].value == 1:
            temp_crs_code = geotiff_metadata["ProjectedCSTypeGeoKey"].value
            # TODO
            # if the ProjectedCSTypeGeoKey is user defined (32767)
            # use supplied keys to get the datum and define the CRS
        elif geotiff_metadata["GTModelTypeGeoKey"].value == 2:
            if isinstance(geotiff_metadata["GeographicTypeGeoKey"], int):
                temp_crs_code = geotiff_metadata["GeographicTypeGeoKey"]
            else:
                temp_crs_code = geotiff_metadata["GeographicTypeGeoKey"].value

        if temp_crs_code != 32767 and isinstance(temp_crs_code, int):
            return temp_crs_code
        elif temp_crs_code == 32767:
            raise UserDefinedGeoKeyError(
                "Can't detect the crs. Use as_crs to manually specify it."
            )
        else:
            raise GeographicTypeGeoKeyError()

    def _populate_2d_array(self, i_list: List[int], j_list: List[int]) -> np.ndarray:
        stack_em = lambda li, j: np.stack((np.array(li), np.ones(len(li)) * j), axis=-1)
        return np.array([stack_em(i_list, j) for j in j_list])

    def _convert_coords_array(
        self, from_crs_code: int, to_crs_code: int, i_list: List[int], j_list: List[int]
    ):
        ij_2d_array = self._populate_2d_array(i_list, j_list)
        # convert to x_vals and y_vals via tiffTransformer
        get_xy = lambda e: np.array(list(self.tifTrans.get_xy(e[0], e[1])))
        xy_2d_array = np.apply_along_axis(get_xy, -1, ij_2d_array)
        x_vals = xy_2d_array[:, :, 0]
        y_vals = xy_2d_array[:, :, 1]
        from_crs_proj4 = CRS.from_epsg(from_crs_code)
        to_crs_proj4 = CRS.from_epsg(to_crs_code)
        transformer = Transformer.from_crs(from_crs_proj4, to_crs_proj4, always_xy=True)
        return transformer.transform(x_vals, y_vals)

    def _convert_coords(
        self, from_crs_code: int, to_crs_code: int, xxyy: Tuple[float, float]
    ) -> Tuple[float, float]:
        xx, yy = xxyy
        from_crs_proj4 = CRS.from_epsg(from_crs_code)
        to_crs_proj4 = CRS.from_epsg(to_crs_code)
        transformer = Transformer.from_crs(from_crs_proj4, to_crs_proj4, always_xy=True)
        return transformer.transform(xx, yy)

    def _get_x_int(self, lon: float) -> int:
        x_range = self.tif_bBox[1][0] - self.tif_bBox[0][0]
        step_x: float = float(self.tif_shape[1] / x_range)
        return int(step_x * (lon - self.tif_bBox[0][0]))

    def _get_y_int(self, lat: float) -> int:
        y_range = self.tif_bBox[1][1] - self.tif_bBox[0][1]
        step_y: float = self.tif_shape[0] / y_range
        return int(step_y * (lat - self.tif_bBox[0][1]))

    def get_coords(self, i: int, j: int) -> Tuple[float, float]:
        """for a given i, j in the entire tiff array,
        returns the as_crs coordinates

        Args:
            i (int): col number of the array
            j (int): row number of the array

        Returns:
            Tuple[float, float]: lon, lat
        """
        x, y = self.tifTrans.get_xy(i, j)
        return self._convert_coords(self.crs_code, self.as_crs, (x, y))

    def get_wgs_84_coords(self, i: int, j: int) -> Tuple[float, float]:
        """for a given i, j in the entire tiff array,
        returns the wgs_84 coordinates

        Args:
            i (int): col number of the array
            j (int): row number of the array

        Returns:
            Tuple[float, float]: lon, lat
        """
        x, y = self.tifTrans.get_xy(i, j)
        return self._convert_coords(self.crs_code, 4326, (x, y))

    def _check_bound_in_tiff(self, shp_bBox, b_bBox):
        check = shp_bBox[0][0] >= b_bBox[0][0]
        check = check and (shp_bBox[1][0] <= b_bBox[1][0])
        check = check and (shp_bBox[0][1] <= b_bBox[0][1])
        check = check and (shp_bBox[1][1] >= b_bBox[1][1])
        if not check:
            raise BoundaryNotInTifError()

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

        # all 4 corners  of box
        left_top = bBox[0]
        right_bottom = bBox[1]
        left_bottom = (bBox[0][0], bBox[1][1])
        right_top = (bBox[1][0], bBox[0][1])

        left_top_c = self._convert_coords(self.as_crs, self.crs_code, left_top)
        right_bottom_c = self._convert_coords(self.as_crs, self.crs_code, right_bottom)
        left_bottom_c = self._convert_coords(self.as_crs, self.crs_code, left_bottom)
        right_top_c = self._convert_coords(self.as_crs, self.crs_code, right_top)

        all_x = [left_top_c[0], left_bottom_c[0], right_bottom_c[0], right_top_c[0]]
        all_y = [left_top_c[1], left_bottom_c[1], right_bottom_c[1], right_top_c[1]]

        # then get the outer ints based on the max and mins
        x_min = min(all_x)
        y_min = min(all_y)
        x_max = max(all_x)
        y_max = max(all_y)

        # convert to int
        i_bump = int(not self.tif_bBox[0][0] == x_min)
        i_min = self._get_x_int(x_min) + i_bump
        j_bump = int(not self.tif_bBox[0][1] == y_max)
        j_min = self._get_y_int(y_max) + j_bump
        i_max = self._get_x_int(x_max)
        j_max = self._get_y_int(y_min)

        if outer_points:
            i_min_out: int = i_min - int(outer_points)
            j_min_out: int = j_min - int(outer_points)
            i_max_out: int = i_max + int(outer_points)
            j_max_out: int = j_max + int(outer_points)
            height = self.tif_shape[0]
            width = self.tif_shape[1]
            if (
                i_min_out < 0
                or j_min_out < 0
                or i_max_out > width
                or j_max_out > height
            ):
                raise BoundaryNotInTifError(
                    "Your area_box is too close to the tif edge and cannot get the outer points"
                )
            return ((i_min_out, j_min_out), (i_max_out, j_max_out))

        shp_bBox = [
            self.tifTrans.get_xy(i_min, j_min),
            self.tifTrans.get_xy(i_max, j_max),
        ]
        self._check_bound_in_tiff(shp_bBox, ((x_min, y_max), (x_max, y_min)))
        return ((i_min, j_min), (i_max, j_max))

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

    def get_coord_arrays(
        self, bBox: Optional[BBox] = None, outer_points: int = 0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """gets the 2d x coordinates and the 2d y coordinates

        WARNING: this cannot handel big arrays (zarr), so use with caution

        Args:
            bBox (Optional[BBox], optional): The bounding box to git the coordinates within
            outer_points (int, optional): Takes an int (n) that gets extra n layers of points/pixels that directly surround the bBox.

        Returns:
            Tuple[np.ndarray, np.ndarray]: 2d x coordinates and the 2d y coordinates
        """
        if bBox == None:
            i_list = [i for i in range(self.tif_shape[1])]
            j_list = [i for i in range(self.tif_shape[0])]
            print(self.as_crs)
            return self._convert_coords_array(
                self.crs_code, self.as_crs, i_list, j_list
            )
        elif isinstance(bBox, tuple):
            ((x_min, y_min), (x_max, y_max)) = self.get_int_box(
                bBox, outer_points=outer_points
            )
            i_list = [i for i in range(x_min, x_max)]
            j_list = [i for i in range(y_min, y_max)]
            return self._convert_coords_array(
                self.crs_code, self.as_crs, i_list, j_list
            )
        raise TypeError(f"You must supply a valid bBox. You gave: {bBox}")

    def read(self) -> zarr.Array:
        """Reads the contents of the geotiff to a zarr array

        Returns:
            np.ndarray: zarr array of the geotiff file
        """
        return self._z

    def read_box(
        self, 
        bBox: BBox, 
        outer_points: Union[bool, int] = False,
        aszarr: bool = False,
    ) -> Union[np.ndarray, zarr.Array]:
        """Reads a boxed sections of the geotiff to a zarr/numpy array

        Args:
            bBox (BBox): A bounding box
            outer_points (Union[bool, int]): Takes an int (n) that gets extra n layers of points/pixels that directly surround the bBox. Defaults to False.
            safe (bool): If True, returns a zarr array. If False, forces a returns as a numpy array by putting the data into memory.  Defaults to False.

        

        Returns:
            np.ndarray: zarr array of the geotiff file
        """
        ((x_min, y_min), (x_max, y_max)) = self.get_int_box(
            bBox, outer_points=outer_points
        )
        tiff_array = self.read()
        boxed_array = tiff_array[y_min:y_max, x_min:x_max]
        if aszarr:
            return zarr.array(boxed_array)
        return np.array(boxed_array)
