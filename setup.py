"""
Setup script for EvalNE-GUI. You can install the library globally using:

python3 setup.py install

Or for a single user with:

python3 setup.py install --user

Run the library using:

evalne_gui
"""

from setuptools import setup, find_packages

setup(
    name="evalne_gui",
    version='0.1.0',
    url="https://github.com/Dru-Mara/EvalNE-GUI",
    license="MIT License",
    author="Alexandru Mara",
    author_email='alexandru.mara@ugent.be',
    description="Plotly Dash based GUI for EvalNE",
    long_description=open("./README.md").read(),
    long_description_content_type="text/markdown",
    keywords='dashboard visualization evaluation monitoring evalne',
    packages=find_packages(),
    python_requires='>3.6',
    zip_safe=False,
    tests_require=["pytest", "pytest-cov"],
    include_package_data=True,
    install_requires=[
        'numpy',
        'plotly',
        'dash-daq',
        'dash_bootstrap_components',
        'dash',
        'fa2',
        'psutil'
    ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    entry_points={'console_scripts': ['evalne_gui = evalne_gui.__main__:main']},
)
