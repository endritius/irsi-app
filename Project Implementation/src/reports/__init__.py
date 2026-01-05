"""
Reporting and analytics for Beauty Salon Expense Manager.
"""

from .report_generator import ReportGenerator, ReportPeriod, get_report_generator

__all__ = [
    'ReportGenerator',
    'ReportPeriod',
    'get_report_generator'
]
