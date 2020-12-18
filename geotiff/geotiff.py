from typing import Optional, Tuple
from shapely.geometry import Point, Polygon
from tifffile import imread, TiffFile
import numpy as np
from tifffile.tifffile_geodb import Proj, GCSE, PCS, GCS, Ellipse, DatumE, Datum
from difflib import SequenceMatcher
from pyproj import Transformer, CRS
import zarr
from .utils.geotiff_logging import log

class GeographicTypeGeoKeyError(Exception):
    pass

class BoundaryNotInTifError(Exception):
    pass

class TifStats():
    def __init__(self,  height, width, scale, tiepoints):
        self.width = width
        self.height = height
        sx, sy, sz = scale  # ModelPixelScaleTag
        transforms = []
        for tp in range(0, len(tiepoints), 6):
            i, j, k, x, y, z = tiepoints[tp:tp+6]
            transforms.append([
                [sx, 0.0, 0.0, x - i * sx],
                [0.0, -sy, 0.0, y + j * sy],
                [0.0, 0.0, sz, z - k * sz],
                [0.0, 0.0, 0.0, 1.0]])
        if len(tiepoints) == 6:
            transforms = transforms[0]
        self.transforms = transforms
        
    def get_x(self, i,j):
        return(list(np.dot(self.transforms,[i,j,0,1]))[0])

    def get_y(self, i,j):
        return(list(np.dot(self.transforms,[i,j,0,1]))[1])

    def get_xy(self, i,j):
        return(tuple(list(np.dot(self.transforms,[i,j,0,1]))[:2]))

def get_crs_code(geotiff_metadata, guess=True):
    projs = [(name, member.value) for name, member in Proj.__members__.items()]
    pcss = [(name, member.value) for name, member in PCS.__members__.items()]
    gcse = [(name, member.value) for name, member in GCSE.__members__.items()]
    gcs = [(name, member.value) for name, member in GCS.__members__.items()]
    # ! handel these!
    ellipse = [(name, member.value) for name, member in Ellipse.__members__.items()]
    datumE = [(name, member.value) for name, member in DatumE.__members__.items()]
    datum = [(name, member.value) for name, member in Datum.__members__.items()]
    all_crs = dict(projs + pcss + gcse + gcs) # + ellipse + datumE + datum)
    temp_crs_code = 32767
    if geotiff_metadata["GTModelTypeGeoKey"].value == 1:
        log.info("PROJECTED")
        temp_crs_code = geotiff_metadata["ProjectedCSTypeGeoKey"].value
    elif geotiff_metadata["GTModelTypeGeoKey"].value == 2:
        log.info("GEO")
        temp_crs_code = geotiff_metadata["GeographicTypeGeoKey"].value

    log.info(temp_crs_code)
    if temp_crs_code == 32767 and guess:
        info_str = str(geotiff_metadata["GTCitationGeoKey"])
        best_score = 0.0
        crs_key = ""
        for crs in all_crs.keys():
            score = SequenceMatcher(None, info_str, str(crs)).ratio()
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


def convert_to_wgs_84(crs_code: int, xxyy: Tuple[float,float])-> Tuple[float, float]:
    xx = xxyy[0]
    yy = xxyy[1]
    crs_4326 =  CRS("WGS84")
    crs_proj = CRS.from_epsg(crs_code)
    transformer = Transformer.from_crs(crs_proj, crs_4326, always_xy=True)
    return(transformer.transform(xx, yy))

def convert_from_wgs_84(crs_code: int, xxyy: Tuple[float,float])-> Tuple[float, float]:
    xx = xxyy[0]
    yy = xxyy[1]
    crs_4326 =  CRS("WGS84")
    crs_proj = CRS.from_epsg(crs_code)
    transformer = Transformer.from_crs(crs_4326, crs_proj, always_xy=True)
    return(transformer.transform(xx, yy))



def read_box(input_file: str, uid: str, bBox: list):
    tif = TiffFile(input_file)
    def get_x_int(lon):
        step_x = tifShape[1]/(tif_bBox[1][0] - tif_bBox[0][0])
        return(int(step_x*(lon - tif_bBox[0][0])))
    def get_y_int(lat):
        step_y = tifShape[0]/(tif_bBox[1][1] - tif_bBox[0][1])
        return(int(step_y*(lat - tif_bBox[0][1])))
    if tif.is_geotiff:
        crs_code = get_crs_code(tif.geotiff_metadata)
        tifShape = tif.asarray().shape
        scale = tif.geotiff_metadata['ModelPixelScale']
        tilePoint = tif.geotiff_metadata['ModelTiepoint']
        stats = TifStats(tifShape[0], tifShape[1], scale, tilePoint)
        b_bBox = [(bBox[0], bBox[3]), (bBox[2], bBox[1])]
        log.warning(b_bBox)
        tif_bBox = [stats.get_xy(0,0), stats.get_xy(tifShape[1],tifShape[0])]
        b_bBox = [convert_from_wgs_84(crs_code,c) for c in b_bBox]
        x_min = get_x_int(b_bBox[0][0])
        x_max = get_x_int(b_bBox[1][0])
        y_min = get_y_int(b_bBox[0][1])
        y_max = get_y_int(b_bBox[1][1])
        # # TODO use this to make check 
        # shp_bBox = [stats.get_xy(x_min,y_min),  stats.get_xy(x_max+1,y_max+1)]
        # print(shp_bBox)
        # print(b_bBox)
        # print(shp_bBox[0][0] < b_bBox[0][0])
        # print(shp_bBox[1][0] > b_bBox[1][0])
        # print(shp_bBox[0][1] > b_bBox[0][1])
        # print(shp_bBox[1][1] < b_bBox[1][1])
        tif_poly = Polygon([(tif_bBox[0][0],tif_bBox[0][1]),(tif_bBox[0][0],tif_bBox[1][1]), (tif_bBox[1][0],tif_bBox[1][1]),(tif_bBox[1][0],tif_bBox[0][1])])
        b_poly = Polygon([(b_bBox[0][0],b_bBox[0][1]),(b_bBox[0][0],b_bBox[1][1]), (b_bBox[1][0],b_bBox[1][1]),(b_bBox[1][0],b_bBox[0][1])])
        if not tif_poly.contains(b_poly):
            raise BoundaryNotInTifError()
        store = imread(input_file, aszarr=True)
        z = zarr.open(store, mode='r')
        log.warning([y_min,y_max, x_min,x_max])

        cut_tif_array = z[y_min:y_max, x_min:x_max] 
        log.info(cut_tif_array)

        store.close()

        return(cut_tif_array)

