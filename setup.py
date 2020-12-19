import setuptools
import os
import sys
from setuptools.command.install import install

VERSION = "0.0.1"

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
    url="https://github.com/KipCrossing/geotiff",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU LESSER GENERAL PUBLIC LICENSE",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    cmdclass={
        'verify': VerifyVersionCommand,
    }
)