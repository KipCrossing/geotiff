import os
from typing import Dict, List, Tuple

import numpy as np  # type: ignore

from geotiff import GeoTiff  # type: ignore

filename = "dem.tif"
# filename = "red.tif"
dir = "./tests/inputs/"
tiff_file = os.path.join(dir, filename)
area_box = ((138.632071411, -32.447310785), (138.644218874, -32.456979174))

if __name__ == "__main__":
    print("testing read tiff")
    print(f"reading: {tiff_file}")
    print(f"Using bBox: {area_box}")
    geo_tiff: GeoTiff = GeoTiff(tiff_file, crs_code=4326, as_crs=4326, band=0)

    print()
    print(geo_tiff.crs_code)
    print(geo_tiff.as_crs)
    print(geo_tiff.tif_shape)
    print(geo_tiff.tif_bBox)
    print(geo_tiff.tif_bBox_wgs_84)
    print(geo_tiff.tif_bBox_converted)
    i = 5
    j = 6
    print(geo_tiff.get_coords(i, j))
    print(geo_tiff.get_wgs_84_coords(i, j))
    zarr_array = geo_tiff.read()
    print(zarr_array)
    print(np.array(zarr_array))
    array = geo_tiff.read_box(area_box)
    small_zarr_array = geo_tiff.read_box(area_box, aszarr=True)
    int_box = geo_tiff.get_int_box(area_box)
    print(int_box)
    wgs_84_box = geo_tiff.get_bBox_wgs_84(area_box)
    print(wgs_84_box)

    int_box = geo_tiff.get_int_box(area_box, outer_points=2)
    print(int_box)
    wgs_84_box = geo_tiff.get_bBox_wgs_84(area_box, outer_points=2)
    print(wgs_84_box)
    i = int_box[0][0] + 5
    j = int_box[0][1] + 6
    print(geo_tiff.get_wgs_84_coords(i, j))
    lon_array, lat_array = geo_tiff.get_coord_arrays(area_box, outer_points=2)
    print(np.array(lon_array))
    print(np.array(lat_array))
    lon_array, lat_array = geo_tiff.get_coord_arrays()
    print(np.array(lon_array))
    print(np.array(lat_array))
