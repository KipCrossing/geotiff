import os
import sys
from setuptools.command.install import install  # type: ignore
from setuptools import setup, find_packages  # type: ignore
from setuptools.command.egg_info import egg_info  # type: ignore


VERSION = "0.2.4"

# Send to pypi
# python3 setup.py sdist bdist_wheel
# twine upload dist/*

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="geotiff",
    version=VERSION,
    author="Kipling Crossing",
    author_email="kip.crossing@gmail.com",
    description="A noGDAL tool for reading and writing geotiff files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Open-Source-Agriculture/geotiff",
    packages=find_packages(),
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
    license_files=("LICENSE",),
    # cmdclass={"egg_info": egg_info_ex},
)
