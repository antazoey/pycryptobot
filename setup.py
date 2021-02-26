from os import path

from setuptools import find_packages
from setuptools import setup

here = path.abspath(path.dirname(__file__))

setup(
    name="pycryptobot",
    version="0.1.0",
    url="https://github.com/whittlem/pycryptobot/",
    project_urls={},
    description="",
    long_description_content_type="text/markdown",
    packages=find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">3, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4",
    install_requires=[
        "click>=7.1.1",
        "keyring==18.0.1",
        "pandas",
        "requests",
        "statsmodels",
        "matplotlib"
    ],
    extras_require={
        "dev": [
            "flake8==3.8.3",
            "pytest==4.6.11",
            "pytest-cov==2.10.0",
            "pytest-mock==2.0.0",
            "tox>=3.17.1",
        ]
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    entry_points={"console_scripts": ["pcb=pycryptobot.pycryptobot:cli"]},
)
