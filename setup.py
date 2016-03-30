from setuptools import setup
import styn

setup(
    name="styn",
    version=styn.__version__,
    author="Lenny Morayniss",
    author_email="ldmoray@gmail.com",
    url=styn.__contact__,
    packages=["styn"],
    entry_points={'console_scripts': ['styn=styn:main']},
    license="MIT License",
    description="Lightweight Python Build Tool.",
    long_description=open("README.rst").read() + "\n" + open("CHANGES.rst").read(),
    requires=['pytest']
)
