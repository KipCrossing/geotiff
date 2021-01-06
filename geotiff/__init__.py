from geotiff.utils.crs_code_guess import crs_code_gusser
from typing import List, Optional, Tuple, Union
from shapely.geometry import Point, Polygon  # type: ignore
from tifffile import imread, TiffFile  # type: ignore
import numpy as np  # type: ignore
from pyproj import Transformer, CRS
import zarr  # type: ignore
from .utils.geotiff_logging import log  # type: ignore

BBox = Tuple[Tuple[float,float], Tuple[float,float]]
BBoxInt = Tuple[Tuple[int,int], Tuple[int,int]]

class GeographicTypeGeoKeyError(Exception):
    def __init__(_):
        log.error("We could not recognize the geo key\nPlease submit an issue: \
                https://github.com/Open-Source-Agriculture/geotiff/issues")

class BoundaryNotInTifError(Exception):
    pass

class FileTypeError(Exception):
    pass

class TifTransformer():
    def __init__(self,  height: int, width: int, scale: Tuple[float, float, float], tiepoints: List[float]):
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
            i, j, k, x, y, z = tiepoints[tp:tp+6]
            transforms.append([
                [sx, 0.0, 0.0, x - i * sx],
                [0.0, -sy, 0.0, y + j * sy],
                [0.0, 0.0, sz, z - k * sz],
                [0.0, 0.0, 0.0, 1.0]])
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
        transformed: List[float] = np.dot(
            self.transforms, [i, j, 0, 1]).tolist()[0]
        transformed_xy: List[float] = transformed[:2]
        return(transformed_xy[0])

    def get_y(self, i: int, j: int) -> float:
        """Gets the y or lat coordinate based on the array index

        Args:
            i (int): index in the x direction
            j (int): index in the y direction

        Returns:
            float: y or lat coordinate
        """
        transformed: List[float] = np.dot(
            self.transforms, [i, j, 0, 1]).tolist()[0]
        transformed_xy: List[float] = transformed[:2]
        return(transformed_xy[1])

    def get_xy(self, i: int, j: int) -> Tuple[float, float]:
        """Gets the (x or lon) and (y or lat) coordinates based on the array index

        Args:
            i (int): index in the x direction
            j (int): index in the y direction

        Returns:
            Tuple[float, float]: (x or lon) and (y or lat) coordinates
        """
        transformed: List[float] = np.dot(
            self.transforms, [i, j, 0, 1]).tolist()[0]
        transformed_xy: List[float] = transformed[:2]
        return(transformed_xy[0], transformed_xy[1])




class GeoTiff():
    def __init__(self, file: str):
        """For representing a geotiff

        Args:
            file (str): Location of the geoTiff file

        Raises:
            FileTypeError: [description]
        """
        self.file = file
        tif = TiffFile(self.file)

        if not tif.is_geotiff:
            raise Exception("Not a geotiff file")

        self.crs_code: int = self._get_crs_code(tif.geotiff_metadata)
        self.tifShape: List[int] = tif.asarray().shape
        scale: Tuple[float, float, float] = tif.geotiff_metadata['ModelPixelScale']
        tilePoint: List[float] = tif.geotiff_metadata['ModelTiepoint']
        self.tifTrans: TifTransformer = TifTransformer(self.tifShape[0], self.tifShape[1], scale, tilePoint)
        self.tif_bBox: BBox = (self.tifTrans.get_xy(0, 0), self.tifTrans.get_xy(self.tifShape[1], self.tifShape[0]))
        


    def _get_crs_code(self, geotiff_metadata: dict, guess: bool = True) -> int:
        temp_crs_code: int = 32767
        if geotiff_metadata["GTModelTypeGeoKey"].value == 1:
            log.info("PROJECTED")
            temp_crs_code = geotiff_metadata["ProjectedCSTypeGeoKey"].value
        elif geotiff_metadata["GTModelTypeGeoKey"].value == 2:
            log.info("GEO")
            temp_crs_code = geotiff_metadata["GeographicTypeGeoKey"].value

        log.info(temp_crs_code)
        if temp_crs_code == 32767 and guess:
            GTCitationGeo: str = str(geotiff_metadata["GTCitationGeoKey"])
            crs_code, score = crs_code_gusser(GTCitationGeo)

            if score < 0.4:
                raise GeographicTypeGeoKeyError()
        else:
            crs_code = temp_crs_code
            return(crs_code)

        if crs_code != 32767:
            return(crs_code)
        else:
            log.error(temp_crs_code)
            raise GeographicTypeGeoKeyError()


    def _convert_to_wgs_84(self, crs_code: int, xxyy: Tuple[float, float]) -> Tuple[float, float]:
        xx: float = xxyy[0]
        yy: float = xxyy[1]
        crs_4326: CRS = CRS("WGS84")
        crs_proj: CRS = CRS.from_epsg(crs_code)
        transformer: Transformer = Transformer.from_crs(
            crs_proj, crs_4326, always_xy=True)
        return(transformer.transform(xx, yy))


    def _convert_from_wgs_84(self, crs_code: int, xxyy: Tuple[float, float]) -> Tuple[float, float]:
        xx: float = xxyy[0]
        yy: float = xxyy[1]
        crs_4326: CRS = CRS("WGS84")
        crs_proj: CRS = CRS.from_epsg(crs_code)
        transformer: Transformer = Transformer.from_crs(
            crs_4326, crs_proj, always_xy=True)
        return(transformer.transform(xx, yy))

    def _get_x_int(self, lon) -> int:
        step_x: float = float(
            self.tifShape[1]/(self.tif_bBox[1][0] - self.tif_bBox[0][0]))
        return(int(step_x*(lon - self.tif_bBox[0][0])))

    def _get_y_int(self, lat) -> int:
        step_y: float = self.tifShape[0]/(self.tif_bBox[1][1] - self.tif_bBox[0][1])
        return(int(step_y*(lat - self.tif_bBox[0][1])))

    def get_int_box(self, bBox: BBox) -> BBoxInt:
        """Gets the intiger array index values based on a bounding box

        Args:
            bBox (BBox): A bounding box

        Raises:
            BoundaryNotInTifError: If the boundary is not enclosed withing the 
                                    outer cooridinated of the tiff

        Returns:
            BBoxInt: array index values
        """
        b_bBox = (self._convert_from_wgs_84(self.crs_code, bBox[0]), self._convert_from_wgs_84(self.crs_code, bBox[1]))
        x_min: int = self._get_x_int(b_bBox[0][0])
        y_min: int = self._get_y_int(b_bBox[0][1])
        x_max: int = self._get_x_int(b_bBox[1][0])
        y_max: int = self._get_y_int(b_bBox[1][1])

        shp_bBox = [self.tifTrans.get_xy(x_min,y_min),  self.tifTrans.get_xy(x_max+1,y_max+1)]
        log.debug(shp_bBox)
        log.debug(b_bBox)
        check = (shp_bBox[0][0] < b_bBox[0][0])
        check = check and (shp_bBox[1][0] > b_bBox[1][0])
        check = check and (shp_bBox[0][1] > b_bBox[0][1])
        check = check and (shp_bBox[1][1] < b_bBox[1][1])

        if not check:
            raise BoundaryNotInTifError()
        else:
            log.info("Boundary is in tiff")
        tif_poly: Polygon = Polygon([(self.tif_bBox[0][0], self.tif_bBox[0][1]), (self.tif_bBox[0][0], self.tif_bBox[1][1]),
                            (self.tif_bBox[1][0], self.tif_bBox[1][1]), (self.tif_bBox[1][0], self.tif_bBox[0][1])])
        b_poly: Polygon = Polygon([(b_bBox[0][0], b_bBox[0][1]), (b_bBox[0][0], b_bBox[1][1]),
                        (b_bBox[1][0], b_bBox[1][1]), (b_bBox[1][0], b_bBox[0][1])])
        if not tif_poly.contains(b_poly):
            raise BoundaryNotInTifError()
        
        return(((x_min,y_min),(x_max,y_max)))


    def read(self) -> np.asarray:
        """Reade the contents of the geotiff to a zarr array

        Returns:
            List[List[Union[int,float]]]: zarr array of the geotiff file
        """
        store = imread(self.file, aszarr=True)
        z = zarr.open(store, mode='r')
        store.close()
        return(z)

    def read_box(self, bBox: BBox) -> List[List[Union[int,float]]]:
        ((x_min,y_min),(x_max,y_max)) = self.get_int_box(bBox)
        tiff_array = self.read()
        cut_tif_array: List[List[Union[int,float]]] = tiff_array[y_min:y_max, x_min:x_max]
        return(cut_tif_array)
