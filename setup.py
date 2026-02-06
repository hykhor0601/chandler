from setuptools import setup, find_packages
from pathlib import Path

requirements = Path(__file__).parent.joinpath("requirements.txt").read_text().splitlines()
requirements = [r.strip() for r in requirements if r.strip() and not r.startswith("#")]

setup(
    name="chandler",
    version="1.0.0",
    description="Chandler - Personal AI Assistant",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "chandler=chandler.main:main",
        ],
    },
    package_data={
        "chandler": ["config.yaml", "data/*.json"],
    },
)
