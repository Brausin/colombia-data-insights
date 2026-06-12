from setuptools import setup, find_packages

setup(
    name="colombia-data-insights",
    version="0.2.0",
    author="Brausin",
    author_email="juansvargasb@gmail.com",
    description="Análisis de datos públicos colombianos — inflación, economía, demografía",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Brausin/colombia-data-insights",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Natural Language :: Spanish",
    ],
)
