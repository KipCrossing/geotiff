from typing import Dict, List, Tuple
import numpy as np # type: ignore
import os
from geotiff.utils.geotiff_logging import log # type: ignore
from geotiff.geotiff import read_box # type: ignore


filename = "dem.tif"
dir = "./tests/inputs/"
tiff_file = os.path.join(dir, filename)
# 138.632071411 -32.447310785 138.644218874 -32.456979174
bounding_box: List[Tuple[float, float]] = [(138.632071411, -32.447310785), (138.644218874, -32.456979174)]


log.info("testing read tiff")
log.debug(f"reading: {tiff_file}")
log.debug(f"Using bBox: {bounding_box}")
array = read_box(tiff_file, bounding_box)
log.debug("Sample array:")
log.debug(array)
log.debug(array.shape)
assert isinstance(array, np.ndarray)
print("Hello")
