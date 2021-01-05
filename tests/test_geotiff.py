import numpy as np
import pytest
import os
from geotiff.utils.geotiff_logging import log
from geotiff import read_box

@pytest.fixture
def tiff_file():
    filename = "dem.tif"
    dir = dir = "./tests/inputs/"
    return(os.path.join(dir, filename))

@pytest.fixture
def bounding_box():
    return([(138.632071411, -32.447310785), (138.644218874, -32.456979174)])

def test_read(tiff_file, bounding_box):
    log.info("testing read tiff")
    log.debug(f"reading: {tiff_file}")
    log.debug(f"Using bBox: {bounding_box}")
    array = read_box(tiff_file, bounding_box)
    log.debug("Sample array:")
    log.debug(array)
    log.debug(array.shape)
    assert isinstance(array, np.ndarray)
