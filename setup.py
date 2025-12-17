"""
Setup script for RL Space Adventure package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="rl-space-adventure",
    version="1.0.0",
    author="RL Space Adventure Team",
    description="A reinforcement learning space adventure game built with Pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rl-space-adventure",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Games/Entertainment :: Arcade",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pygame>=2.0.0",
        "numpy>=1.19.0",
    ],
    extras_require={
        "dev": ["pytest>=6.0", "black", "flake8", "mypy"],
    },
    entry_points={
        "console_scripts": [
            "rl-space-adventure=rl_space_adventure.__main__:main_sync",
        ],
    },
)
