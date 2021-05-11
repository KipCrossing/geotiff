import setuptools
import os
import sys
from setuptools.command.install import install

VERSION = "0.1.8"

# Send to pypi
# python3 setup.py sdist bdist_wheel
# twine upload dist/*

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""
    description = 'verify that the git tag matches our version'

    def run(self):
        tag = os.getenv('CIRCLE_TAG')

        if tag == None:
            info = "No new version to upload"
            print(info)
        elif tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)

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
    python_requires='>=3.7',
    install_requires=[
        'shapely',
        'tifffile',
        'numpy',
        'pyproj',
        'zarr',
        'pycrs',
    ],
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)