# geotiff

A noGDAL tool for reading and writing geotiff files

WARNING this package is under development and some features are unstable. Use with caution. 

### What is noGDAL?

**[noGDAL](https://kipcrossing.github.io/2021-01-03-noGDAL/)** is a philosophy for developing geospatial programs in python without using GDAL.

### Instillation

Installing this package is as easy as:

```
pip install geotiff
```

### Usage

Read the GeoTiff to an array

```python
from geotiff import GeoTiff

geoTiff = GeoTiff(tiff_file)
array = geoTiff.read()
```

Read a sections of a large tiff using a bounding box

```python
from geotiff import GeoTiff

bounding_box = [(138.632071411, -32.447310785), (138.644218874, -32.456979174)]
geoTiff = GeoTiff(tiff_file)
array = geoTiff.read_box(bounding_box)
```

This will detect and convert coordinates into WGS 84

### Contributing

If you would like to contribute to this project, please fork it and make a PR with you patches.

You can join the conversation by saying hi in the [project discussion board](https://github.com/Open-Source-Agriculture/geotiff/discussions).

To help users and and other contributes, be sure to:
- make doc blocs if appropriate
- use typing wherever possible. 

*Note:* The continuous integration has lint checking with **mypy**, so be sure to check it yourself before making a PR.

### Project Road Map

#### Core Features

- [x] read tiff files (including BigTiff)
- [ ] write tiff files (including BigTiff)
- [ ] **(UNSTABLE/LIMITED)** convert between coordinate systems
- [x] cut a section (bounding box) of the tiff file
- [x] convert the data to numpy arrays

#### Additional features

- [ ] **(50%)** Full test coverage
- [x] Typing with lint checking using mypy
- [x] Documentation: doc blocs
- [ ] Documentation: readthedocs
