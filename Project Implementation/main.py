#!/usr/bin/env python3
"""
Beauty Salon Expense Manager - Application Launcher

This is the main entry point for the application.
Run this script to start the expense manager.

Usage:
    python main.py
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

# Import and run main
from main import main

if __name__ == '__main__':
    main()
