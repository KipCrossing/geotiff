from typing import Dict, List, Tuple
import numpy as np # type: ignore
import os
from geotiff import GeoTiff # type: ignore


filename = "dem.tif"
filename = "red.tif"
dir = "./tests/inputs/"
tiff_file = os.path.join(dir, filename)
# tiff_file = "/home/kipling/Programs/pylandsat_sandbox/data/gamma/Radmap2019-grid-k_conc-Filtered-AWAGS_RAD_2019.tif"
# 138.632071411 -32.447310785 138.644218874 -32.456979174
bounding_box: List[Tuple[float, float]] = [(138.632071411, -32.447310785), (138.644218874, -32.456979174)]

if __name__ == '__main__':
    print("testing read tiff")
    print(f"reading: {tiff_file}")
    print(f"Using bBox: {bounding_box}")
    geotiff: GeoTiff = GeoTiff(tiff_file)
    print(geotiff.tif_bBox)
    print(geotiff.crs_code)
    array = geotiff.read_box(bounding_box)
    print("Sample array:")
    print(array)
    print(array.shape)
    assert isinstance(array, np.ndarray)
    print(geotiff.tif_bBox_wgs_84)
    print("end")
