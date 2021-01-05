from typing import List, Optional, Tuple, Union
from shapely.geometry import Point, Polygon  # type: ignore
from tifffile import imread, TiffFile  # type: ignore
import numpy as np  # type: ignore
from tifffile.tifffile_geodb import Proj, GCSE, PCS, GCS, Ellipse, DatumE, Datum  # type: ignore
from difflib import SequenceMatcher
from pyproj import Transformer, CRS
import zarr  # type: ignore
from .utils.geotiff_logging import log  # type: ignore

BBox = Tuple[Tuple[float,float], Tuple[float,float]]

class GeographicTypeGeoKeyError(Exception):
    def __init__(_):
        log.error("We could not recognize the geo key\nPlease submit an issue: \
                https://github.com/Open-Source-Agriculture/geotiff/issues")

class BoundaryNotInTifError(Exception):
    pass


class TifTransformer():
    def __init__(self,  height: int, width: int, scale: Tuple[float, float, float], tiepoints: List[float]):
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

    def get_x(self, i: int, j: int) -> List[float]:
        return(list(np.dot(self.transforms, [i, j, 0, 1]))[0])

    def get_y(self, i: int, j: int) -> List[float]:
        return(list(np.dot(self.transforms, [i, j, 0, 1]))[1])

    def get_xy(self, i: int, j: int) -> Tuple[float, float]:
        transformed: List[float] = np.dot(
            self.transforms, [i, j, 0, 1]).tolist()[0]
        transformed_xy: List[float] = transformed[:2]
        log.debug("transformed_xy")
        log.debug(transformed_xy)
        return(transformed_xy[0], transformed_xy[1])




class GeoTiff():
    def __init__(self, file):
        self.file = file
        tif = TiffFile(self.file)

        if not tif.is_geotiff:
            raise Exception("Not a geotiff file")

        self.crs_code: int = self.get_crs_code(tif.geotiff_metadata)
        self.tifShape: List[int] = tif.asarray().shape
        scale: Tuple[float, float, float] = tif.geotiff_metadata['ModelPixelScale']
        tilePoint: List[float] = tif.geotiff_metadata['ModelTiepoint']
        self.tifTrans: TifTransformer = TifTransformer(self.tifShape[0], self.tifShape[1], scale, tilePoint)
        


    def get_crs_code(self, geotiff_metadata: dict, guess: bool = True) -> int:
        PreDict = List[Tuple[str, int]]
        projs: PreDict = [(name, member.value)
                        for name, member in Proj.__members__.items()]
        pcss: PreDict = [(name, member.value)
                        for name, member in PCS.__members__.items()]
        gcse: PreDict = [(name, member.value)
                        for name, member in GCSE.__members__.items()]
        gcs: PreDict = [(name, member.value)
                        for name, member in GCS.__members__.items()]
        # ! handel these!
        ellipse: PreDict = [(name, member.value)
                            for name, member in Ellipse.__members__.items()]
        datumE: PreDict = [(name, member.value)
                        for name, member in DatumE.__members__.items()]
        datum: PreDict = [(name, member.value)
                        for name, member in Datum.__members__.items()]
        all_crs = dict(projs + pcss + gcse + gcs)  # + ellipse + datumE + datum)
        temp_crs_code: int = 32767
        if geotiff_metadata["GTModelTypeGeoKey"].value == 1:
            log.info("PROJECTED")
            temp_crs_code = geotiff_metadata["ProjectedCSTypeGeoKey"].value
        elif geotiff_metadata["GTModelTypeGeoKey"].value == 2:
            log.info("GEO")
            temp_crs_code = geotiff_metadata["GeographicTypeGeoKey"].value

        log.info(temp_crs_code)
        if temp_crs_code == 32767 and guess:
            # takes a guess based on the GTCitationGeoKey
            info_str: str = str(geotiff_metadata["GTCitationGeoKey"])
            best_score: float = 0.0
            crs_key: str = ""
            for crs in all_crs.keys():
                score: float = SequenceMatcher(None, info_str, str(crs)).ratio()
                if score > best_score:
                    best_score = score
                    crs_key = crs
            if best_score < 0.4:
                raise GeographicTypeGeoKeyError()
            crs_code = all_crs[crs_key]
            return(crs_code)
        elif temp_crs_code in all_crs.values():
            crs_code = temp_crs_code
            return(crs_code)
        else:
            log.error(temp_crs_code)
            raise GeographicTypeGeoKeyError()


    def convert_to_wgs_84(self, crs_code: int, xxyy: Tuple[float, float]) -> Tuple[float, float]:
        xx: float = xxyy[0]
        yy: float = xxyy[1]
        crs_4326: CRS = CRS("WGS84")
        crs_proj: CRS = CRS.from_epsg(crs_code)
        transformer: Transformer = Transformer.from_crs(
            crs_proj, crs_4326, always_xy=True)
        return(transformer.transform(xx, yy))


    def convert_from_wgs_84(self, crs_code: int, xxyy: Tuple[float, float]) -> Tuple[float, float]:
        xx: float = xxyy[0]
        yy: float = xxyy[1]
        crs_4326: CRS = CRS("WGS84")
        crs_proj: CRS = CRS.from_epsg(crs_code)
        transformer: Transformer = Transformer.from_crs(
            crs_4326, crs_proj, always_xy=True)
        return(transformer.transform(xx, yy))


    def read_box(self, bBox: BBox) -> List[List[Union[int,float]]]:

        b_bBox: BBox = bBox
        tif_bBox: BBox = (self.tifTrans.get_xy(0, 0), self.tifTrans.get_xy(self.tifShape[1], self.tifShape[0]))
        b_bBox = (self.convert_from_wgs_84(self.crs_code, b_bBox[0]), self.convert_from_wgs_84(self.crs_code, b_bBox[1]))

        def get_x_int(lon) -> int:
            step_x: float = float(
                self.tifShape[1]/(tif_bBox[1][0] - tif_bBox[0][0]))
            return(int(step_x*(lon - tif_bBox[0][0])))

        def get_y_int(lat) -> int:
            step_y: float = self.tifShape[0]/(tif_bBox[1][1] - tif_bBox[0][1])
            return(int(step_y*(lat - tif_bBox[0][1])))

        x_min: int = get_x_int(b_bBox[0][0])
        x_max: int = get_x_int(b_bBox[1][0])
        y_min: int = get_y_int(b_bBox[0][1])
        y_max: int = get_y_int(b_bBox[1][1])
        # # TODO use this to make check
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
        tif_poly: Polygon = Polygon([(tif_bBox[0][0], tif_bBox[0][1]), (tif_bBox[0][0], tif_bBox[1][1]),
                            (tif_bBox[1][0], tif_bBox[1][1]), (tif_bBox[1][0], tif_bBox[0][1])])
        b_poly: Polygon = Polygon([(b_bBox[0][0], b_bBox[0][1]), (b_bBox[0][0], b_bBox[1][1]),
                        (b_bBox[1][0], b_bBox[1][1]), (b_bBox[1][0], b_bBox[0][1])])
        if not tif_poly.contains(b_poly):
            raise BoundaryNotInTifError()
        store = imread(self.file, aszarr=True)
        z = zarr.open(store, mode='r')

        cut_tif_array: List[List[Union[int,float]]] = z[y_min:y_max, x_min:x_max]

        store.close()

        return(cut_tif_array)
