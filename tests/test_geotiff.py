from typing import Callable
import numpy as np  # type: ignore
import pytest
import os
from geotiff import GeoTiff
import zarr  # type: ignore

@pytest.fixture(params=["dem.tif", "gda_94_sand.tif",  "sand_test.tif", "red.tif"])
def geo_tiff(request):
    filename = request.param 
    dir = dir = "./tests/inputs/"
    # TODO: test bands, and crs params
    return GeoTiff(os.path.join(dir, filename)) 


@pytest.fixture
def area_box():
    return ((138.632071411, -32.447310785), (138.644218874, -32.456979174))


def test_read(geo_tiff: GeoTiff):
    zarr_array = geo_tiff.read()
    print(zarr_array.info)
    assert isinstance(zarr_array, zarr.Array)
    print(zarr_array.chunks)

def test_read_box(area_box, geo_tiff: GeoTiff):
    print("testing read tiff")
    print(f"reading: {geo_tiff}")
    print(f"Using bBox: {area_box}")
    print(f"crs_code: {geo_tiff.crs_code}")
    print(f"as_crs: {geo_tiff.as_crs}")
    array = geo_tiff.read_box(area_box)
    assert isinstance(array, np.ndarray)
    print("Sample array:")
    print(array)
    print(array.shape)
    assert isinstance(array, np.ndarray)
    zarr_array = geo_tiff.read_box(area_box, aszarr=True)
    print(type(zarr_array))
    assert isinstance(zarr_array, zarr.Array)


def test_get_coord_arrays(geo_tiff: GeoTiff, area_box):
    array = geo_tiff.read_box(area_box)
    print(geo_tiff.tif_bBox_wgs_84)
    lon_array, lat_array = geo_tiff.get_coord_arrays(bBox=area_box)
    assert array.shape == lon_array.shape
    assert array.shape == lat_array.shape


def test_int_box(area_box, geo_tiff: GeoTiff):
    intBox = geo_tiff.get_int_box(area_box)
    assert isinstance(intBox, tuple)
    assert len(intBox) == 2
    assert isinstance(intBox[0], tuple)
    assert isinstance(intBox[1], tuple)
    intBox_outer = geo_tiff.get_int_box(area_box, outer_points=True)
    assert intBox[0][0] == intBox_outer[0][0]+1
    assert intBox[0][1] == intBox_outer[0][1]+1
    assert intBox[1][0] == intBox_outer[1][0]-1
    assert intBox[1][1] == intBox_outer[1][1]-1



def test_conversions(area_box, geo_tiff: GeoTiff):
    int_box = geo_tiff.get_int_box(area_box)
    i = int_box[0][0] + 5
    j = int_box[0][1] + 6
    geo_tiff.get_wgs_84_coords(i, j)
    bounding_box = geo_tiff.get_bBox_wgs_84(area_box)

    # * note: these tests will fail when the tiff it skewed
    # assert area_box[0][0] <= bounding_box[0][0]
    # assert area_box[0][1] >= bounding_box[0][1]
    # assert area_box[1][0] >= bounding_box[1][0]
    # assert area_box[1][1] <= bounding_box[1][1]

    bounding_box_outer = geo_tiff.get_bBox_wgs_84(area_box, outer_points=True)

    print(area_box)

    assert area_box[0][0] >= bounding_box_outer[0][0]
    assert area_box[0][1] <= bounding_box_outer[0][1]
    assert area_box[1][0] <= bounding_box_outer[1][0]
    assert area_box[1][1] >= bounding_box_outer[1][1]

    bounding_box_outer2 = geo_tiff.get_bBox_wgs_84(area_box, outer_points=2)

    assert bounding_box_outer[0][0] >= bounding_box_outer2[0][0]
    assert bounding_box_outer[0][1] <= bounding_box_outer2[0][1]
    assert bounding_box_outer[1][0] <= bounding_box_outer2[1][0]
    assert bounding_box_outer[1][1] >= bounding_box_outer2[1][1]
