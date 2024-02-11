from setuptools import setup, find_packages

setup(
    name="draw",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",  # Add your project dependencies here
    ],
    entry_points={
        "console_scripts": [
            "draw=draw.main:main",  # "command=package.module:function"
        ],
    },
)
