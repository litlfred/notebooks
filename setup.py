"""
Setup configuration for the Weierstrass Playground package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="weierstrass-playground",
    version="1.0.0",
    author="Weierstrass Playground Contributors",
    description="Interactive visualization of the Weierstrass ℘ function with trajectory integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/litlfred/notebooks",
    project_urls={
        "Bug Tracker": "https://github.com/litlfred/notebooks/issues",
        "Live Demo": "https://litlfred.github.io/notebooks/",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research", 
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
        ],
        "jupyter": [
            "ipywidgets>=7.6.0",
            "jupyter>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "weierstrass-demo=weierstrass_playground.browser:main",
        ],
    },
    keywords="weierstrass mathematics visualization elliptic-functions complex-analysis",
)