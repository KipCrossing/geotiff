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


class VerifyVersionCommand(install):
    """Custom command to verify that the git tag matches our version"""

    description = "verify that the git tag matches our version"

    def run(self):
        tag = os.getenv("CIRCLE_TAG")

        if tag == None:
            info = "No new version to upload"
            print(info)
        elif tag != VERSION:
            info = "Git tag: {0} does not match the version of this app: {1}".format(
                tag, VERSION
            )
            sys.exit(info)


class egg_info_ex(egg_info):
    """Includes license file into `.egg-info` folder."""

    def run(self):
        # don't duplicate license into `.egg-info` when building a distribution
        if not self.distribution.have_run.get("install", True):
            # `install` command is in progress, copy license
            self.mkpath(self.egg_info)
            self.copy_file("LICENSE.txt", self.egg_info)


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
    license_files=("LICENSE.txt",),
    cmdclass={"verify": VerifyVersionCommand, "egg_info": egg_info_ex},
)
