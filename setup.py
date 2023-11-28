"""Setup for TechnoVE in Pypi."""
from setuptools import setup

setup(
    name="pytechnove",
    version="0.1.0",
    description="TechnoVE local station API library",
    url="https://github.com/moustachauve/pytechnove",
    author="Christophe Gagnier",
    license="GNU General Public License v3 (GPLv3)",
    packages=["pytechnove"],
    install_requires=["httpx"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT license ",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries",
    ],
)
