from typing import Dict, List, Tuple
import numpy as np # type: ignore
import os
from geotiff import GeoTiff # type: ignore


filename = "dem.tif"
dir = "./tests/inputs/"
tiff_file = os.path.join(dir, filename)
# 138.632071411 -32.447310785 138.644218874 -32.456979174
bounding_box: List[Tuple[float, float]] = [(138.632071411, -32.447310785), (138.644218874, -32.456979174)]


print("testing read tiff")
print(f"reading: {tiff_file}")
print(f"Using bBox: {bounding_box}")
array = GeoTiff(tiff_file).read_box(bounding_box)
print("Sample array:")
print(array)
print(array.shape)
assert isinstance(array, np.ndarray)
print("end")
