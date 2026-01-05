"""
UI Module for Beauty Salon Expense Manager.

This module contains all user interface components including:
- Main application window
- Views for different sections
- Dialog windows
- Styling utilities
"""

from .styles import COLORS, FONTS, PADDING, DIMENSIONS, apply_theme
from .main_window import MainWindow

# Views
from .views import (
    DashboardView,
    ExpenseListView,
    ExpenseFormView,
    BudgetView,
    BudgetDialog,
    ReportsView,
    ChartsView,
    TemplatesView,
    TemplateDialog,
    SettingsView
)

# Dialogs
from .dialogs import ExportDialog, ImportDialog, AboutDialog

__all__ = [
    # Styling
    'COLORS',
    'FONTS',
    'PADDING',
    'DIMENSIONS',
    'apply_theme',

    # Main Window
    'MainWindow',

    # Views
    'DashboardView',
    'ExpenseListView',
    'ExpenseFormView',
    'BudgetView',
    'BudgetDialog',
    'ReportsView',
    'ChartsView',
    'TemplatesView',
    'TemplateDialog',
    'SettingsView',

    # Dialogs
    'ExportDialog',
    'ImportDialog',
    'AboutDialog'
]
