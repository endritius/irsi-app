#!/usr/bin/env python3
"""
Beauty Salon Expense Manager - Main Entry Point

A comprehensive desktop application for tracking and analyzing
salon business expenses with budget management, reporting, and
data visualization capabilities.

Author: IRSI Project
Version: 1.0.0
"""

import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Ensure the src directory is in the path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))


def setup_logging():
    """Configure application logging."""
    logs_dir = src_dir / 'logs'
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

    return logging.getLogger(__name__)


def setup_data_directories():
    """Ensure required data directories exist."""
    data_dir = src_dir / 'data'
    data_dir.mkdir(exist_ok=True)

    # Create subdirectories
    (data_dir / 'backups').mkdir(exist_ok=True)

    return data_dir


def check_dependencies():
    """Check if required dependencies are available."""
    missing = []

    try:
        import tkinter
    except ImportError:
        missing.append('tkinter')

    try:
        import pandas
    except ImportError:
        missing.append('pandas')

    try:
        import numpy
    except ImportError:
        missing.append('numpy')

    try:
        import matplotlib
    except ImportError:
        missing.append('matplotlib')

    try:
        import seaborn
    except ImportError:
        missing.append('seaborn')

    if missing:
        print("Missing required dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print("\nPlease install dependencies with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)


def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Beauty Salon Expense Manager")

    # Check dependencies
    check_dependencies()

    # Setup data directories
    setup_data_directories()

    try:
        # Import UI components
        from ui.main_window import MainWindow
        from ui.styles import apply_theme
        import tkinter as tk

        # Create root window
        root = tk.Tk()

        # Apply theme
        apply_theme(root)

        # Create main window
        app = MainWindow(root)

        logger.info("Application initialized successfully")

        # Run the application
        root.mainloop()

        logger.info("Application closed normally")

    except Exception as e:
        logger.exception("Fatal error occurred")
        print(f"\nFatal error: {e}")
        print("Check logs for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()
