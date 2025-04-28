from setuptools import setup, find_packages

# NOTE: Dependencies are managed via requirements/base.txt, dev.txt, and test.txt.
# See the README for installation instructions for users, developers, and testers.
# This setup.py is provided for editable/development installs (pip install -e .)

setup(
    name="power_aware_hpc_benchmarking",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="Power-aware HPC benchmarking framework",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Power-aware-HPC-benchmarking",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering",
    ],
) 