# geotiff

A noGDAL tool for reading geotiff files

WARNING this package is under development and some features are unstable. Use with caution. 

Please support this project be giving it a [star on GitHub](https://github.com/Open-Source-Agriculture/geotiff)!

### What is noGDAL?

**[noGDAL](https://kipcrossing.github.io/2021-01-03-noGDAL/)** is a philosophy for developing geospatial programs in python without using GDAL.

### Instillation

Installing this package is as easy as:

```
pip install geotiff
```

### Usage

#### Read the GeoTiff to an array

```python
from geotiff import GeoTiff

geoTiff = GeoTiff(tiff_file)
array = geoTiff.read()
```

This will detect the crs code. If it's 'user defined' and you know what it should be, you may supply a crs code:

```python
geoTiff = GeoTiff(tiff_file, crs_code=4236)
```

Get bounding box info about the tiff

```python
# in the original CRS
geotiff.tif_bBox
# as WGS 84
geotiff.tif_bBox_wgs_84
```

Get coordinates of a point/pixel

```python
i=5
j=6
geoTiff.get_wgs_84_coords(i, j)
```

Get the original crs code

```python
geotiff.crs_code
```

#### Read a sections of a large tiff using a WGS 84 area

```python
from geotiff import GeoTiff

# in WGS 84
area_box = [(138.632071411, -32.447310785), (138.644218874, -32.456979174)]
geotiff = GeoTiff(tiff_file)
array = geotiff.read_box(area_box)
```

#### Getting bounding box information

You can either get the points/pixels that are within a given area_box:

```python
# col and row indexes of the cut area
int_box = geoTiff.get_int_box(area_box)
# lon and lat coords of the cut points/pixels
geoTiff.get_bBox_wgs_84(area_box)
```

You can also get extra n layers of points/pixels that directly surround the area_box

```python
# col and row indexes of the cut area
int_box = geoTiff.get_int_box(area_box, outer_points = 1)
# lon and lat coords of the cut points/pixels
geoTiff.get_bBox_wgs_84(area_box, outer_points = 1)
```

This may be useful of you want to interpolate to points near the area_box boundary.

#### Get coordinates of a point/pixel

```python
i=int_box[0][0] + 5
j=int_box[0][1] + 6
geoTiff.get_wgs_84_coords(i, j)
```

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
- [x] **(UNSTABLE/LIMITED)** convert between coordinate systems
- [ ] read a user defined CRS
- [x] cut a section (bounding box) of the tiff file
- [x] convert the data to numpy arrays

#### Additional features

- [ ] **(50%)** Full test coverage
- [x] Typing with lint checking using mypy
- [x] Documentation: doc blocs
- [ ] Documentation: readthedocs
