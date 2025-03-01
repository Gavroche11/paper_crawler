#!/usr/bin/env python
"""
Script to run the Paper Crawler from the command line.

This is a convenience script that allows running the crawler directly
without having to use the module syntax.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to sys.path to allow imports
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from paper_crawler.cli import run_crawler


if __name__ == "__main__":
    # Print banner
    print("=" * 80)
    print("PAPER CRAWLER".center(80))
    print("=" * 80)
    
    # Run the crawler function from the CLI module
    run_crawler()