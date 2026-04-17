#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="datamatrix-quality-scanner",
    version="1.0.0",
    description="Data Matrix Quality Scanner по ГОСТ Р 57302-2016",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "opencv-python>=4.8.0",
        "pylibdmtx>=0.1.10",
        "Pillow>=10.0.0",
        "numpy>=1.24.0",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "datamatrix-scanner=main:main",
        ],
    },
)