from setuptools import setup, find_packages

setup(
    name="meriweather",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    author="Zachary Mays",
    author_email="zachary.a.mays@gmail.com",
    description="A package for retrieving historical weather data from the National Weather Service API",
    keywords="weather, nws, api, climate",
    url="https://github.com/zamays/Meriweather",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)