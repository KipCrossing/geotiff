from typing import Callable
import numpy as np  # type: ignore
import pytest
import os
from geotiff import GeoTiff
import zarr

@pytest.fixture(params=["dem.tif", "gda_94_sand.tif",  "sand_test.tif", "red.tif"])
def geotiff(request):
    filename = request.param 
    dir = dir = "./tests/inputs/"
    # TODO: test bands, and crs params
    return GeoTiff(os.path.join(dir, filename)) 


@pytest.fixture
def area_box():
    return ((138.632071411, -32.447310785), (138.644218874, -32.456979174))


def test_read(geotiff: GeoTiff):
    zarr_array = geotiff.read()
    print(zarr_array.info)
    assert isinstance(zarr_array, zarr.Array)
    print(zarr_array.chunks)

def test_read_box(area_box, geotiff: GeoTiff):
    print("testing read tiff")
    print(f"reading: {geotiff}")
    print(f"Using bBox: {area_box}")
    print(f"crs_code: {geotiff.crs_code}")
    print(f"as_crs: {geotiff.as_crs}")
    array = geotiff.read_box(area_box)
    print("Sample array:")
    print(array)
    print(array.shape)
    assert isinstance(array, np.ndarray)

def test_get_coord_arrays(geotiff: GeoTiff, area_box):
    array = geotiff.read_box(area_box)
    print(geotiff.tif_bBox_wgs_84)
    lon_array, lat_array = geotiff.get_coord_arrays(bBox=area_box)
    assert array.shape == lon_array.shape
    assert array.shape == lat_array.shape


def test_int_box(area_box, geotiff: GeoTiff):
    intBox = geotiff.get_int_box(area_box)
    assert isinstance(intBox, tuple)
    assert len(intBox) == 2
    assert isinstance(intBox[0], tuple)
    assert isinstance(intBox[1], tuple)
    intBox_outer = geotiff.get_int_box(area_box, outer_points=True)
    assert intBox[0][0] == intBox_outer[0][0]+1
    assert intBox[0][1] == intBox_outer[0][1]+1
    assert intBox[1][0] == intBox_outer[1][0]-1
    assert intBox[1][1] == intBox_outer[1][1]-1



def test_conversions(area_box, geotiff: GeoTiff):
    int_box = geotiff.get_int_box(area_box)
    i = int_box[0][0] + 5
    j = int_box[0][1] + 6
    geotiff.get_wgs_84_coords(i, j)
    bounding_box = geotiff.get_bBox_wgs_84(area_box)

    # * note: these tests will fail when the tiff it skewed
    # assert area_box[0][0] <= bounding_box[0][0]
    # assert area_box[0][1] >= bounding_box[0][1]
    # assert area_box[1][0] >= bounding_box[1][0]
    # assert area_box[1][1] <= bounding_box[1][1]

    bounding_box_outer = geotiff.get_bBox_wgs_84(area_box, outer_points=True)

    print(area_box)

    assert area_box[0][0] >= bounding_box_outer[0][0]
    assert area_box[0][1] <= bounding_box_outer[0][1]
    assert area_box[1][0] <= bounding_box_outer[1][0]
    assert area_box[1][1] >= bounding_box_outer[1][1]

    bounding_box_outer2 = geotiff.get_bBox_wgs_84(area_box, outer_points=2)

    assert bounding_box_outer[0][0] >= bounding_box_outer2[0][0]
    assert bounding_box_outer[0][1] <= bounding_box_outer2[0][1]
    assert bounding_box_outer[1][0] <= bounding_box_outer2[1][0]
    assert bounding_box_outer[1][1] >= bounding_box_outer2[1][1]
