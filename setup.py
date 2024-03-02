from setuptools import setup, find_packages

setup(
    name="frameit",
    version="0.1.0",
    packages=find_packages(),
    package_data={"frameit": ["data/*.pkl"]},
    install_requires=[
        "requests",  # Add your project dependencies here
        "spacy",
        "scikit-learn",
    ],
    entry_points={
        "console_scripts": [
            "frameit=frameit.frameit:main",  # "command=package.module:function"
        ],
    },
)
