from setuptools import setup

setup(
    name="haystack-sonic",
    version="0.1",
    description="Sonic backend for Haystack",
    packages=["haystack_sonic"],
    install_requires=["haystack", "sonic-client"],
)
