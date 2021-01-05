# geotiff

A noGDAL tool for reading and writing geotiff files

### What is noGDAL?

**noGDAL** is a philosophy for developing geospatial programs in python without using GDAL.

### Usage

Read a sections of a large tiff using a bounding box

```python
from geotiff import GeoTiff

bounding_box = [(138.632071411, -32.447310785), (138.644218874, -32.456979174)]
geoTiff = GeoTiff(tiff_file)
array = geoTiff.read_box(bounding_box)
```

This will detect and convert coordinates into WGS 84