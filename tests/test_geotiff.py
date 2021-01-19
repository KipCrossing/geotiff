import numpy as np
import pytest
import os
from geotiff import GeoTiff

@pytest.fixture
def tiff_file():
    filename = "dem.tif"
    dir = dir = "./tests/inputs/"
    return(os.path.join(dir, filename))

@pytest.fixture
def bounding_box():
    return([(138.632071411, -32.447310785), (138.644218874, -32.456979174)])


@pytest.fixture
def geoTiff(tiff_file):
    return(GeoTiff(tiff_file))

def test_read(tiff_file, bounding_box, geoTiff: GeoTiff):
    print("testing read tiff")
    print(f"reading: {tiff_file}")
    print(f"Using bBox: {bounding_box}")
    array = geoTiff.read_box(bounding_box)
    print("Sample array:")
    print(array)
    print(array.shape)
    assert isinstance(array, np.ndarray)


def test_int_box(bounding_box, geoTiff: GeoTiff):
    intBox = geoTiff.get_int_box(bounding_box)
    assert isinstance(intBox, tuple)
    assert len(intBox) == 2
    assert isinstance(intBox[0], tuple)
    assert isinstance(intBox[1], tuple)
    assert ((125, 143), (169, 178)) == intBox