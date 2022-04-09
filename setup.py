import sys
from importlib.util import spec_from_file_location, module_from_spec
from pathlib import Path

from setuptools import find_packages, setup


def _load_module_from_src(mod_name, mod_fname, pkg_dir=""):
    cwd = Path.cwd()
    pkg_path = Path.joinpath(cwd, pkg_dir)
    mod_spec = spec_from_file_location(mod_name, f"{str(pkg_path)}/{mod_fname}.py")
    mod = module_from_spec(mod_spec)
    sys.modules[mod_name] = mod
    mod_spec.loader.exec_module(mod)
    return mod


about = _load_module_from_src("about", "__about__", "pixel_artist")
install_requires = [
    "Pillow==9.0.1",
    "colormath==3.0.0"
]

test_requires = []

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pixel-artist",
    version=about.__version__,
    author=about.__author__,
    author_email=about.__author_email__,
    description=about.__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=about.__url__,
    license=about.__license__,
    packages=find_packages(where=".", exclude=["tests", "venv*"]),
    entry_points={
        'console_scripts': [
            'pixel-artist = pixel_artist.__main__:main',
        ],
    },
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=install_requires,
    test_requires=test_requires,
    keywords=["python", "command-line", "console", "cmd", "pixel-art", "pixel", "image-processing"],
    project_urls={
        "Source": about.__url__,
        "Documentation": about.__docs__,
        "Bug Tracker": about.__issues__,
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Terminals",
        "Topic :: Utilities"
    ],
)
