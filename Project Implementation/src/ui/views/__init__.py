"""
UI Views for Beauty Salon Expense Manager.
"""

from .dashboard_view import DashboardView
from .expense_list_view import ExpenseListView
from .expense_form_view import ExpenseFormView
from .budget_view import BudgetView, BudgetDialog
from .reports_view import ReportsView
from .charts_view import ChartsView
from .templates_view import TemplatesView, TemplateDialog
from .settings_view import SettingsView

__all__ = [
    'DashboardView',
    'ExpenseListView',
    'ExpenseFormView',
    'BudgetView',
    'BudgetDialog',
    'ReportsView',
    'ChartsView',
    'TemplatesView',
    'TemplateDialog',
    'SettingsView'
]
