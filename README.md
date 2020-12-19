# geotiff

A noGDAL tool for reading and writing geotiff files

### What is noGDAL?

**noGDAL** is a philosophy for developing geospatial programs in python without using GDAL.

### Usage

Read a sections of a large tiff using a bounding box

```python
from geotiff.geotiff import read_box

bounding_box = [(138.387681, -32.310286), (138.414326, -32.344569)]
array = read_box(tiff_file, bounding_box)
```

This will detect and convert coordinates into WGS 84