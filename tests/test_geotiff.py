import numpy as np  # type: ignore
import pytest
import os
from geotiff import GeoTiff


@pytest.fixture
def tiff_file():
    filename = "dem.tif"
    dir = dir = "./tests/inputs/"
    return os.path.join(dir, filename)


@pytest.fixture
def area_box():
    return [(138.632071411, -32.447310785), (138.644218874, -32.456979174)]


@pytest.fixture
def geoTiff(tiff_file):
    return GeoTiff(tiff_file)


def test_read(tiff_file, area_box, geoTiff: GeoTiff):
    print("testing read tiff")
    print(f"reading: {tiff_file}")
    print(f"Using bBox: {area_box}")
    array = geoTiff.read_box(area_box)
    print("Sample array:")
    print(array)
    print(array.shape)
    assert isinstance(array, np.ndarray)


def test_int_box(area_box, geoTiff: GeoTiff):
    intBox = geoTiff.get_int_box(area_box)
    assert isinstance(intBox, tuple)
    assert len(intBox) == 2
    assert isinstance(intBox[0], tuple)
    assert isinstance(intBox[1], tuple)
    assert ((126, 144), (169, 178)) == intBox


def test_int_box_outer(area_box, geoTiff: GeoTiff):
    intBox = geoTiff.get_int_box(area_box, outer_points=True)
    assert isinstance(intBox, tuple)
    assert len(intBox) == 2
    assert isinstance(intBox[0], tuple)
    assert isinstance(intBox[1], tuple)
    assert ((125, 143), (170, 179)) == intBox


def test_conversions(area_box, geoTiff: GeoTiff):
    int_box = geoTiff.get_int_box(area_box)
    i = int_box[0][0] + 5
    j = int_box[0][1] + 6
    geoTiff.get_wgs_84_coords(i, j)
    bounding_box = geoTiff.get_bBox_wgs_84(area_box)
    assert area_box[0][0] <= bounding_box[0][0]
    assert area_box[0][1] >= bounding_box[0][1]
    assert area_box[1][0] >= bounding_box[1][0]
    assert area_box[1][1] <= bounding_box[1][1]

    assert geoTiff.read_box(area_box).shape == (34, 43)
    assert geoTiff.get_bBox_wgs_84(area_box) == (
        (138.63222222222188, -32.44749999999997),
        (138.64416666666634, -32.45694444444442),
    )
    assert geoTiff.read_box(area_box, outer_points=True).shape == (36, 45)

    bounding_box_outer = geoTiff.get_bBox_wgs_84(area_box, outer_points=True)

    print(area_box)

    assert area_box[0][0] >= bounding_box_outer[0][0]
    assert area_box[0][1] <= bounding_box_outer[0][1]
    assert area_box[1][0] <= bounding_box_outer[1][0]
    assert area_box[1][1] >= bounding_box_outer[1][1]

    bounding_box_outer2 = geoTiff.get_bBox_wgs_84(area_box, outer_points=2)

    assert bounding_box_outer[0][0] >= bounding_box_outer2[0][0]
    assert bounding_box_outer[0][1] <= bounding_box_outer2[0][1]
    assert bounding_box_outer[1][0] <= bounding_box_outer2[1][0]
    assert bounding_box_outer[1][1] >= bounding_box_outer2[1][1]


    assert geoTiff.get_bBox_wgs_84(area_box, outer_points=True) == (
        (138.63194444444412, -32.447222222222194),
        (138.6444444444441, -32.45722222222219),
    )

    assert geoTiff.tif_bBox_wgs_84 == (
        (138.5972222222219, -32.40749999999997),
        (138.69055555555522, -32.49138888888886),
    )