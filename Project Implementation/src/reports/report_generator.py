"""
ReportGenerator - Generates statistical reports and analytics for expenses.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import Expense, Budget, StatisticalSummary
from utils.error_handler import log_info, log_error
from config import CATEGORIES


class ReportPeriod(Enum):
    """Report period types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReportGenerator:
    """
    Generates statistical reports and analytics for expenses.
    Provides aggregations, trends, and comparisons.
    """

    def __init__(self):
        """Initialize ReportGenerator."""
        pass

    # ===== BASIC STATISTICS =====

    def calculate_basic_stats(
        self,
        expenses: List[Expense]
    ) -> StatisticalSummary:
        """
        Calculate basic statistical summary.

        Args:
            expenses: List of expenses to analyze

        Returns:
            StatisticalSummary object
        """
        if not expenses:
            return StatisticalSummary(
                total_amount=0.0,
                average_amount=0.0,
                min_amount=0.0,
                max_amount=0.0,
                expense_count=0,
                category_totals={},
                payment_method_totals={},
                date_from=None,
                date_to=None
            )

        amounts = [e.amount for e in expenses]
        dates = [e.date for e in expenses]

        # Category totals
        category_totals = defaultdict(float)
        for expense in expenses:
            category_totals[expense.category] += expense.amount

        # Payment method totals
        payment_totals = defaultdict(float)
        for expense in expenses:
            payment_totals[expense.payment_method] += expense.amount

        return StatisticalSummary(
            total_amount=sum(amounts),
            average_amount=np.mean(amounts) if amounts else 0.0,
            min_amount=min(amounts) if amounts else 0.0,
            max_amount=max(amounts) if amounts else 0.0,
            expense_count=len(expenses),
            category_totals=dict(category_totals),
            payment_method_totals=dict(payment_totals),
            date_from=min(dates) if dates else None,
            date_to=max(dates) if dates else None,
            median_amount=float(np.median(amounts)) if amounts else 0.0,
            std_deviation=float(np.std(amounts)) if len(amounts) > 1 else 0.0
        )

    def calculate_percentiles(
        self,
        expenses: List[Expense],
        percentiles: List[float] = [25, 50, 75, 90, 95]
    ) -> Dict[float, float]:
        """
        Calculate expense amount percentiles.

        Args:
            expenses: List of expenses
            percentiles: List of percentile values

        Returns:
            Dictionary mapping percentile to value
        """
        if not expenses:
            return {p: 0.0 for p in percentiles}

        amounts = [e.amount for e in expenses]
        return {p: float(np.percentile(amounts, p)) for p in percentiles}

    # ===== CATEGORY ANALYSIS =====

    def get_category_breakdown(
        self,
        expenses: List[Expense]
    ) -> List[Dict]:
        """
        Get expense breakdown by category.

        Args:
            expenses: List of expenses

        Returns:
            List of category summaries with totals and percentages
        """
        if not expenses:
            return []

        category_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})
        total_amount = 0.0

        for expense in expenses:
            category_data[expense.category]['amount'] += expense.amount
            category_data[expense.category]['count'] += 1
            total_amount += expense.amount

        result = []
        for category, data in category_data.items():
            percentage = (data['amount'] / total_amount * 100) if total_amount > 0 else 0
            result.append({
                'category': category,
                'amount': data['amount'],
                'count': data['count'],
                'percentage': percentage,
                'average': data['amount'] / data['count'] if data['count'] > 0 else 0
            })

        # Sort by amount descending
        result.sort(key=lambda x: x['amount'], reverse=True)
        return result

    def get_subcategory_breakdown(
        self,
        expenses: List[Expense],
        category: str = None
    ) -> List[Dict]:
        """
        Get expense breakdown by subcategory.

        Args:
            expenses: List of expenses
            category: Optional category filter

        Returns:
            List of subcategory summaries
        """
        if not expenses:
            return []

        filtered = expenses
        if category:
            filtered = [e for e in expenses if e.category == category]

        subcategory_data = defaultdict(lambda: {'amount': 0.0, 'count': 0, 'category': ''})
        total_amount = sum(e.amount for e in filtered)

        for expense in filtered:
            key = (expense.category, expense.subcategory)
            subcategory_data[key]['amount'] += expense.amount
            subcategory_data[key]['count'] += 1
            subcategory_data[key]['category'] = expense.category

        result = []
        for (cat, subcat), data in subcategory_data.items():
            percentage = (data['amount'] / total_amount * 100) if total_amount > 0 else 0
            result.append({
                'category': cat,
                'subcategory': subcat,
                'amount': data['amount'],
                'count': data['count'],
                'percentage': percentage
            })

        result.sort(key=lambda x: x['amount'], reverse=True)
        return result

    # ===== TIME-BASED ANALYSIS =====

    def get_monthly_trend(
        self,
        expenses: List[Expense],
        months: int = 12
    ) -> List[Dict]:
        """
        Get monthly expense trend.

        Args:
            expenses: List of expenses
            months: Number of months to include

        Returns:
            List of monthly summaries
        """
        if not expenses:
            return []

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        # Filter to date range
        filtered = [e for e in expenses if e.date >= start_date]

        # Group by month
        monthly_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})

        for expense in filtered:
            month_key = expense.date.strftime('%Y-%m')
            monthly_data[month_key]['amount'] += expense.amount
            monthly_data[month_key]['count'] += 1

        # Generate all months in range
        result = []
        current = start_date.replace(day=1)
        while current <= end_date:
            month_key = current.strftime('%Y-%m')
            data = monthly_data.get(month_key, {'amount': 0.0, 'count': 0})
            result.append({
                'month': month_key,
                'month_name': current.strftime('%B %Y'),
                'amount': data['amount'],
                'count': data['count']
            })
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)

        return result

    def get_weekly_trend(
        self,
        expenses: List[Expense],
        weeks: int = 12
    ) -> List[Dict]:
        """
        Get weekly expense trend.

        Args:
            expenses: List of expenses
            weeks: Number of weeks to include

        Returns:
            List of weekly summaries
        """
        if not expenses:
            return []

        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)

        filtered = [e for e in expenses if e.date >= start_date]

        # Group by week
        weekly_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})

        for expense in filtered:
            # Get ISO week
            week_key = expense.date.strftime('%Y-W%W')
            weekly_data[week_key]['amount'] += expense.amount
            weekly_data[week_key]['count'] += 1

        result = []
        for week_key in sorted(weekly_data.keys()):
            data = weekly_data[week_key]
            result.append({
                'week': week_key,
                'amount': data['amount'],
                'count': data['count']
            })

        return result

    def get_daily_trend(
        self,
        expenses: List[Expense],
        days: int = 30
    ) -> List[Dict]:
        """
        Get daily expense trend.

        Args:
            expenses: List of expenses
            days: Number of days to include

        Returns:
            List of daily summaries
        """
        if not expenses:
            return []

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        filtered = [e for e in expenses if e.date >= start_date]

        # Group by day
        daily_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})

        for expense in filtered:
            day_key = expense.date.strftime('%Y-%m-%d')
            daily_data[day_key]['amount'] += expense.amount
            daily_data[day_key]['count'] += 1

        # Generate all days in range
        result = []
        current = start_date
        while current <= end_date:
            day_key = current.strftime('%Y-%m-%d')
            data = daily_data.get(day_key, {'amount': 0.0, 'count': 0})
            result.append({
                'date': day_key,
                'day_name': current.strftime('%A'),
                'amount': data['amount'],
                'count': data['count']
            })
            current += timedelta(days=1)

        return result

    def get_day_of_week_analysis(
        self,
        expenses: List[Expense]
    ) -> List[Dict]:
        """
        Analyze expenses by day of week.

        Args:
            expenses: List of expenses

        Returns:
            List of day-of-week summaries
        """
        if not expenses:
            return []

        day_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for expense in expenses:
            day_num = expense.date.weekday()
            day_data[day_num]['amount'] += expense.amount
            day_data[day_num]['count'] += 1

        result = []
        for i, day_name in enumerate(day_names):
            data = day_data.get(i, {'amount': 0.0, 'count': 0})
            result.append({
                'day_number': i,
                'day_name': day_name,
                'amount': data['amount'],
                'count': data['count'],
                'average': data['amount'] / data['count'] if data['count'] > 0 else 0
            })

        return result

    # ===== VENDOR ANALYSIS =====

    def get_top_vendors(
        self,
        expenses: List[Expense],
        n: int = 10
    ) -> List[Dict]:
        """
        Get top vendors by spending.

        Args:
            expenses: List of expenses
            n: Number of vendors to return

        Returns:
            List of vendor summaries
        """
        if not expenses:
            return []

        vendor_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})
        total_amount = sum(e.amount for e in expenses)

        for expense in expenses:
            vendor_data[expense.vendor]['amount'] += expense.amount
            vendor_data[expense.vendor]['count'] += 1

        result = []
        for vendor, data in vendor_data.items():
            percentage = (data['amount'] / total_amount * 100) if total_amount > 0 else 0
            result.append({
                'vendor': vendor,
                'amount': data['amount'],
                'count': data['count'],
                'percentage': percentage,
                'average': data['amount'] / data['count'] if data['count'] > 0 else 0
            })

        result.sort(key=lambda x: x['amount'], reverse=True)
        return result[:n]

    def get_vendor_trend(
        self,
        expenses: List[Expense],
        vendor: str,
        months: int = 6
    ) -> List[Dict]:
        """
        Get spending trend for a specific vendor.

        Args:
            expenses: List of expenses
            vendor: Vendor name
            months: Number of months

        Returns:
            List of monthly vendor spending
        """
        vendor_expenses = [e for e in expenses if e.vendor.lower() == vendor.lower()]
        return self.get_monthly_trend(vendor_expenses, months)

    # ===== PAYMENT METHOD ANALYSIS =====

    def get_payment_method_breakdown(
        self,
        expenses: List[Expense]
    ) -> List[Dict]:
        """
        Get expense breakdown by payment method.

        Args:
            expenses: List of expenses

        Returns:
            List of payment method summaries
        """
        if not expenses:
            return []

        method_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})
        total_amount = sum(e.amount for e in expenses)

        for expense in expenses:
            method_data[expense.payment_method]['amount'] += expense.amount
            method_data[expense.payment_method]['count'] += 1

        result = []
        for method, data in method_data.items():
            percentage = (data['amount'] / total_amount * 100) if total_amount > 0 else 0
            result.append({
                'payment_method': method,
                'amount': data['amount'],
                'count': data['count'],
                'percentage': percentage
            })

        result.sort(key=lambda x: x['amount'], reverse=True)
        return result

    # ===== COMPARISON REPORTS =====

    def compare_periods(
        self,
        expenses: List[Expense],
        period1_start: datetime,
        period1_end: datetime,
        period2_start: datetime,
        period2_end: datetime
    ) -> Dict:
        """
        Compare two time periods.

        Args:
            expenses: List of expenses
            period1_start: First period start
            period1_end: First period end
            period2_start: Second period start
            period2_end: Second period end

        Returns:
            Comparison dictionary
        """
        # Filter expenses for each period
        period1_expenses = [
            e for e in expenses
            if period1_start <= e.date <= period1_end
        ]
        period2_expenses = [
            e for e in expenses
            if period2_start <= e.date <= period2_end
        ]

        # Calculate stats for each period
        stats1 = self.calculate_basic_stats(period1_expenses)
        stats2 = self.calculate_basic_stats(period2_expenses)

        # Calculate changes
        amount_change = stats2.total_amount - stats1.total_amount
        amount_change_pct = (
            (amount_change / stats1.total_amount * 100)
            if stats1.total_amount > 0 else 0
        )

        count_change = stats2.expense_count - stats1.expense_count
        count_change_pct = (
            (count_change / stats1.expense_count * 100)
            if stats1.expense_count > 0 else 0
        )

        avg_change = stats2.average_amount - stats1.average_amount
        avg_change_pct = (
            (avg_change / stats1.average_amount * 100)
            if stats1.average_amount > 0 else 0
        )

        return {
            'period1': {
                'start': period1_start,
                'end': period1_end,
                'total': stats1.total_amount,
                'count': stats1.expense_count,
                'average': stats1.average_amount
            },
            'period2': {
                'start': period2_start,
                'end': period2_end,
                'total': stats2.total_amount,
                'count': stats2.expense_count,
                'average': stats2.average_amount
            },
            'changes': {
                'amount': amount_change,
                'amount_percentage': amount_change_pct,
                'count': count_change,
                'count_percentage': count_change_pct,
                'average': avg_change,
                'average_percentage': avg_change_pct
            }
        }

    def compare_months(
        self,
        expenses: List[Expense],
        month1: datetime,
        month2: datetime
    ) -> Dict:
        """
        Compare two months.

        Args:
            expenses: List of expenses
            month1: First month (any date in that month)
            month2: Second month (any date in that month)

        Returns:
            Comparison dictionary
        """
        from dateutil.relativedelta import relativedelta

        # Get month boundaries
        p1_start = month1.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        p1_end = (p1_start + relativedelta(months=1)) - timedelta(seconds=1)

        p2_start = month2.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        p2_end = (p2_start + relativedelta(months=1)) - timedelta(seconds=1)

        return self.compare_periods(expenses, p1_start, p1_end, p2_start, p2_end)

    def get_year_over_year(
        self,
        expenses: List[Expense]
    ) -> Dict:
        """
        Compare current year to previous year.

        Args:
            expenses: List of expenses

        Returns:
            Year-over-year comparison
        """
        now = datetime.now()

        # Current year
        current_year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        current_year_end = now

        # Previous year same period
        prev_year_start = current_year_start.replace(year=current_year_start.year - 1)
        prev_year_end = now.replace(year=now.year - 1)

        return self.compare_periods(
            expenses,
            prev_year_start, prev_year_end,
            current_year_start, current_year_end
        )

    # ===== BUDGET REPORTS =====

    def get_budget_vs_actual(
        self,
        expenses: List[Expense],
        budgets: List[Budget]
    ) -> List[Dict]:
        """
        Compare budgets vs actual spending.

        Args:
            expenses: List of expenses
            budgets: List of budgets

        Returns:
            List of budget vs actual comparisons
        """
        result = []

        for budget in budgets:
            # Get expenses for this budget period and category
            budget_expenses = [
                e for e in expenses
                if (e.category == budget.category and
                    budget.period_start <= e.date <= budget.period_end and
                    not e.is_deleted)
            ]

            actual = sum(e.amount for e in budget_expenses)
            variance = budget.amount - actual
            variance_pct = (variance / budget.amount * 100) if budget.amount > 0 else 0
            used_pct = (actual / budget.amount * 100) if budget.amount > 0 else 0

            result.append({
                'category': budget.category,
                'budget': budget.amount,
                'actual': actual,
                'variance': variance,
                'variance_percentage': variance_pct,
                'used_percentage': used_pct,
                'status': 'over' if actual > budget.amount else 'under',
                'period_start': budget.period_start,
                'period_end': budget.period_end
            })

        return result

    # ===== RECURRING EXPENSE REPORTS =====

    def get_recurring_expense_summary(
        self,
        expenses: List[Expense]
    ) -> Dict:
        """
        Summarize recurring expenses.

        Args:
            expenses: List of expenses

        Returns:
            Recurring expense summary
        """
        recurring = [e for e in expenses if e.is_recurring and not e.is_deleted]
        non_recurring = [e for e in expenses if not e.is_recurring and not e.is_deleted]

        recurring_total = sum(e.amount for e in recurring)
        non_recurring_total = sum(e.amount for e in non_recurring)
        total = recurring_total + non_recurring_total

        return {
            'recurring': {
                'count': len(recurring),
                'total': recurring_total,
                'percentage': (recurring_total / total * 100) if total > 0 else 0
            },
            'non_recurring': {
                'count': len(non_recurring),
                'total': non_recurring_total,
                'percentage': (non_recurring_total / total * 100) if total > 0 else 0
            },
            'total': total
        }

    def estimate_monthly_recurring(
        self,
        expenses: List[Expense]
    ) -> float:
        """
        Estimate monthly recurring expense total.

        Args:
            expenses: List of expenses

        Returns:
            Estimated monthly recurring amount
        """
        monthly_estimate = 0.0

        recurring = [e for e in expenses if e.is_recurring and not e.is_deleted]

        for expense in recurring:
            freq = expense.recurring_frequency
            if freq == 'daily':
                monthly_estimate += expense.amount * 30
            elif freq == 'weekly':
                monthly_estimate += expense.amount * 4
            elif freq == 'biweekly':
                monthly_estimate += expense.amount * 2
            elif freq == 'monthly':
                monthly_estimate += expense.amount
            elif freq == 'quarterly':
                monthly_estimate += expense.amount / 3
            elif freq == 'annually':
                monthly_estimate += expense.amount / 12

        return monthly_estimate

    # ===== TAG ANALYSIS =====

    def get_tag_breakdown(
        self,
        expenses: List[Expense]
    ) -> List[Dict]:
        """
        Analyze expenses by tags.

        Args:
            expenses: List of expenses

        Returns:
            List of tag summaries
        """
        if not expenses:
            return []

        tag_data = defaultdict(lambda: {'amount': 0.0, 'count': 0})

        for expense in expenses:
            if expense.tags:
                for tag in expense.tags:
                    tag_data[tag]['amount'] += expense.amount
                    tag_data[tag]['count'] += 1

        total_amount = sum(e.amount for e in expenses if e.tags)

        result = []
        for tag, data in tag_data.items():
            percentage = (data['amount'] / total_amount * 100) if total_amount > 0 else 0
            result.append({
                'tag': tag,
                'amount': data['amount'],
                'count': data['count'],
                'percentage': percentage
            })

        result.sort(key=lambda x: x['amount'], reverse=True)
        return result

    # ===== FULL REPORTS =====

    def generate_monthly_report(
        self,
        expenses: List[Expense],
        budgets: List[Budget],
        month: datetime = None
    ) -> Dict:
        """
        Generate comprehensive monthly report.

        Args:
            expenses: List of all expenses
            budgets: List of budgets
            month: Month to report on (default: current)

        Returns:
            Complete monthly report dictionary
        """
        from dateutil.relativedelta import relativedelta

        if month is None:
            month = datetime.now()

        # Get month boundaries
        month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + relativedelta(months=1)) - timedelta(seconds=1)

        # Filter expenses for month
        month_expenses = [
            e for e in expenses
            if month_start <= e.date <= month_end and not e.is_deleted
        ]

        # Generate report sections
        report = {
            'period': {
                'month': month.strftime('%B %Y'),
                'start': month_start,
                'end': month_end
            },
            'summary': self.calculate_basic_stats(month_expenses).__dict__,
            'by_category': self.get_category_breakdown(month_expenses),
            'by_vendor': self.get_top_vendors(month_expenses, 10),
            'by_payment_method': self.get_payment_method_breakdown(month_expenses),
            'by_day': self.get_daily_trend(month_expenses, 31),
            'recurring': self.get_recurring_expense_summary(month_expenses),
            'budget_status': self.get_budget_vs_actual(month_expenses, budgets),
            'generated_at': datetime.now()
        }

        # Add comparison to previous month
        prev_month = month_start - relativedelta(months=1)
        report['vs_previous_month'] = self.compare_months(expenses, prev_month, month_start)

        return report

    def generate_annual_report(
        self,
        expenses: List[Expense],
        budgets: List[Budget],
        year: int = None
    ) -> Dict:
        """
        Generate comprehensive annual report.

        Args:
            expenses: List of all expenses
            budgets: List of budgets
            year: Year to report on (default: current)

        Returns:
            Complete annual report dictionary
        """
        if year is None:
            year = datetime.now().year

        # Get year boundaries
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)

        # Filter expenses for year
        year_expenses = [
            e for e in expenses
            if year_start <= e.date <= year_end and not e.is_deleted
        ]

        # Generate report sections
        report = {
            'period': {
                'year': year,
                'start': year_start,
                'end': year_end
            },
            'summary': self.calculate_basic_stats(year_expenses).__dict__,
            'by_category': self.get_category_breakdown(year_expenses),
            'by_subcategory': self.get_subcategory_breakdown(year_expenses),
            'monthly_trend': self.get_monthly_trend(year_expenses, 12),
            'by_vendor': self.get_top_vendors(year_expenses, 20),
            'by_payment_method': self.get_payment_method_breakdown(year_expenses),
            'by_day_of_week': self.get_day_of_week_analysis(year_expenses),
            'recurring': self.get_recurring_expense_summary(year_expenses),
            'estimated_monthly_recurring': self.estimate_monthly_recurring(year_expenses),
            'by_tags': self.get_tag_breakdown(year_expenses),
            'generated_at': datetime.now()
        }

        # Add year over year if previous year data exists
        prev_year_expenses = [
            e for e in expenses
            if datetime(year-1, 1, 1) <= e.date <= datetime(year-1, 12, 31, 23, 59, 59)
            and not e.is_deleted
        ]
        if prev_year_expenses:
            report['vs_previous_year'] = self.get_year_over_year(expenses)

        return report


# Singleton instance
_report_generator: Optional[ReportGenerator] = None


def get_report_generator() -> ReportGenerator:
    """Get or create global ReportGenerator instance."""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator
