from setuptools import setup, find_packages

setup(
    name="scraper",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    py_modules=["scraper"],
    install_requires=[
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "scraper = cli:cli",
        ],
    },
)
