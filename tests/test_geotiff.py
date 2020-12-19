import numpy as np
import pytest
import os
from geotiff.utils.geotiff_logging import log
from geotiff.geotiff import read_box

@pytest.fixture
def tiff_file():
    filename = "dem.tif"
    dir = "/home/kipling/Documents/fsm_sample_data"
    return(os.path.join(dir, filename))

@pytest.fixture
def bounding_box():
    return([(138.387681, -32.310286), (138.414326, -32.344569)])

def test_read(tiff_file, bounding_box):
    log.info("testing read tiff")
    log.debug(f"reading: {tiff_file}")
    log.debug(f"Using bBox: {bounding_box}")
    array = read_box(tiff_file, bounding_box)
    log.debug("Sample array:")
    log.debug(array)
    log.debug(array.shape)
    assert isinstance(array, np.ndarray)
