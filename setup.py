from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="paper_crawler",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
        "xml-python>=0.4.3",
    ],
    entry_points={
        "console_scripts": [
            "paper_crawler=paper_crawler.cli:main",
        ],
    },
    scripts=["scripts/run_crawler.py"],
    author="Inhyeok Taylor Baek",
    author_email="bih011122@gmail.com",
    description="A tool to search research papers from medical journals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="pubmed, research, academic journals, papers, search",
    url="https://github.com/yourusername/paper_crawler",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
    ],
    python_requires=">=3.6",
)