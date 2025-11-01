from setuptools import setup, find_packages

setup(
    name="ft-analyzer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",
        "pandas>=2.1.0",
        "pyarrow>=14.0.0",
        "pyyaml>=6.0",
        "anthropic>=0.18.0",
    ],
    entry_points={
        "console_scripts": [
            "ft-analyzer=ft_analyzer.cli:cli",
        ],
    },
    python_requires=">=3.10",
)
