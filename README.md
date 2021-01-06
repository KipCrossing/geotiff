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

### Project Road Map

#### Core Features

- [x] read tiff files (including BigTiff)
- [] write tiff files (including BigTiff)
- [UNSTABLE] convert between coordinate systems
- [x] cut a section (bounding box) of the tiff file
- [x] convert the data to numpy arrays

#### Additional features

- [50%] Full test coverage
- [x] Typing with lint checking using mypy
- [x] Documentation: doc blocs and readthedocs
- [] Documentation: readthedocs
