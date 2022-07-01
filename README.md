# geotiff

A noGDAL tool for reading geotiff files

WARNING this package is under development and some features are unstable. Use with caution.

Please support this project be giving it a [star on GitHub](https://github.com/Open-Source-Agriculture/geotiff)!

### What is noGDAL?

**[noGDAL](https://kipling.medium.com/nogdal-e5b60b114a1c)** is a philosophy for developing geospatial programs in python without using GDAL.

### Installation

Installing this package is as easy as:

```
pip install geotiff
```

There is also an Anaconda-based package available, published on [conda-forge](https://conda-forge.org/):

```
conda install -c conda-forge python-geotiff
```

For local development from sources, you can install geotiff with its development requirements using:

```
git clone git@github.com:KipCrossing/geotiff.git
cd geotiff
pip install -e .[dev]
```

### Usage

#### Making the GeoTiff object

```python
from geotiff import GeoTiff

geo_tiff = GeoTiff(tiff_file)
```

This will detect the crs code. If it's 'user defined' and you know what it should be, you may supply a crs code:

```python
geo_tiff = GeoTiff(tiff_file, crs_code=4326)
```

By default, the coordinates will be in WGS 84, however they can be specified by using the `as_crs` param:

```python
geo_tiff = GeoTiff(tiff_file, as_crs=7844)
```

Or you can use the original crs by setting `as_crs` to `None`:

```python
geo_tiff = GeoTiff(tiff_file, as_crs=None)
```


If the geotiff file has multiple bands, you can specify which band to use:

```python
geo_tiff = GeoTiff(tiff_file, band=1)
```

The default band is 0


Get information (properties) about the geotiff:

```python
# the original crs code
geo_tiff.crs_code
# the current crs code
geo_tiff.as_crs
# the shape of the tiff
geo_tiff.tif_shape
# the bounding box in the as_crs CRS
geo_tiff.tif_bBox
# the bounding box as WGS 84
geo_tiff.tif_bBox_wgs_84
# the bounding box in the as_crs converted coordinates
geo_tiff.tif_bBox_converted
```

Get coordinates of a point/pixel:

```python
i=5
j=6
# in the as_crs coords
geo_tiff.get_coords(i, j)
# in WGS 84 coords
geo_tiff.get_wgs_84_coords(i, j)
```

#### Read the data

To read the data, use the `.read()` method. This will return a [zarr](https://zarr.readthedocs.io/en/stable/api/core.html) array as often geotiff files cannot fit into memory.

```python
zarr_array = geo_tiff.read()
```

If you are confident that the data will fit into memory, you can convert it to a numpy array:

```python
import numpy as np

array = np.array(zarr_array)
```

#### Read a section of a large tiff

In many cases, you are only interested in a section of the tiff. For convenience, you can use the `.read_box()` method. This will return a numpy array.

WARNING: This will fail if the box you are using is too large and the data cannot fit into memory.

```python
from geotiff import GeoTiff

# in WGS 84
area_box = [(138.632071411, -32.447310785), (138.644218874, -32.456979174)]
geo_tiff = GeoTiff(tiff_file)
array = geo_tiff.read_box(area_box)
```

*Note:* For the `area_box`, use the same crs as `as_crs`.

In some cases, you may want some extra points/pixels around the outside of your `area_box`. This may be useful if you want to interpolate to points near the area_box boundary. To achieve this, use the `outer_points` param:

array = geo_tiff.read_box(area_box, outer_points=2)

This will get 2 extra perimeters of points around the outside of the the `area_box`.

#### Getting bounding box information

There are also some helper methods to get the bounding box of the resulting cut array:

```python
# col and row indexes of the cut area
int_box = geo_tiff.get_int_box(area_box)
# lon and lat coords of the cut points/pixels
wgs_84_box = geo_tiff.get_bBox_wgs_84(area_box)
```

Again, you can also get bounding box for an extra n layers of points/pixels that directly surround the `area_box`:

```python
# col and row indexes of the cut area
int_box = geo_tiff.get_int_box(area_box, outer_points = 2)
# lon and lat coords of the cut points/pixels
wgs_84_box = geo_tiff.get_bBox_wgs_84(area_box, outer_points = 2)
```

#### Get coordinates of a point/pixel

You may want to get the coordinates of a value in your array:

```python
i=int_box[0][0] + 5
j=int_box[0][1] + 6
geo_tiff.get_wgs_84_coords(i, j)
```

#### Get coordinates of an array

You may want to simply get all the coordinates in the array:

```python
array = geo_tiff.read_box(area_box, outer_points=2)
lon_array, lat_array = geo_tiff.get_coord_arrays(area_box, outer_points=2)
```

This will return two arrays that are in the same shape as the array from the `read_box()` method. The output coords will be in the `as_crs` crs.

If your tiff file is small and can fit into memory, simply:

```python
lon_array, lat_array = geo_tiff.get_coord_arrays()
```

### Contributing

If you would like to contribute to this project, please fork this repo and make a PR with your patches.

You can join the conversation by saying hi in the [project discussion board](https://github.com/KipCrossing/geotiff/discussions).

To help users and other contributes, be sure to:
- make doc blocs if appropriate
- use typing wherever possible
- format with black

*Note:* The continuous integration has lint checking with **mypy**, so be sure to check it yourself before making a PR.

### Project Road Map

#### Core Features

- [x] read tiff files (including BigTiff)
- [ ] write tiff files (including BigTiff)
- [x] convert between epsg coordinate systems
- [ ] read a user defined CRS `32767` from tiff file
- [x] cut a section (bounding box) of the tiff file
- [x] convert the data to numpy arrays

#### Additional features

- [x] **(50%)** Full test coverage
- [x] Typing with lint checking using mypy
- [x] Formatted with black
- [x] Documentation: doc blocs
- [ ] Documentation: readthedocs
