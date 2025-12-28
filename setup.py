from setuptools import setup

setup(
    name="commish",
    version="0.1.0",
    description="Fantasy league management for RuPaul's Drag Race",
    author="Ryan Z Friedman",
    packages=["commish"],
    install_requires=["pandas", "numpy", "matplotlib", "tabulate", "pyyaml"],
    python_requires=">=3.7",
)
