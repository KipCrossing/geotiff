from setuptools import find_packages, setup  # type: ignore
from setuptools.command.egg_info import egg_info  # type: ignore
from setuptools.command.install import install  # type: ignore

VERSION = "0.2.7"

# Send to pypi
# python3 setup.py sdist bdist_wheel
# twine upload dist/*

with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

requirements = []
with open("requirements.txt", encoding="utf-8") as fh:
    for dep in fh.readlines():
        requirements.append(dep)

dev_requirements = ["pytest"]

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
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={"dev": dev_requirements},
    license_files=("LICENSE",),
    zip_safe=False
    # cmdclass={"egg_info": egg_info_ex},
)
