import setuptools  # type: ignore
import os
import sys
from setuptools.command.install import install  # type: ignore

VERSION = "0.3a1"

# Send to pypi
# python3 setup.py sdist bdist_wheel
# twine upload dist/*

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setuptools.setup(
    name="geotiff",
    version=VERSION,
    author="Kipling Crossing",
    author_email="kip.crossing@gmail.com",
    description="A noGDAL tool for reading and writing geotiff files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Open-Source-Agriculture/geotiff",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "tifffile==2021.7.2",
        "numpy",
        "pyproj",
        "zarr",
    ],
    cmdclass={},
)
