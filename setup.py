'''
from setuptools import setup, find_packages

setup(
    name="MetaboConverter",
    version="0.1.0",
    author="Yuxuan Mao",
    author_email="ymao4@uw.edu",
    description="A Python package to view and analyze Excel sheets via a GUI.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/JaydenMao102/MetaboConverter",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.19.0",
        "scipy>=1.5.0",
        "tkinter"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
'''
