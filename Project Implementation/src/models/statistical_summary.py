"""
StatisticalSummary dataclass - Summary statistics for expense reports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Any, Optional


@dataclass
class StatisticalSummary:
    """
    Statistical summary for expense analysis.

    Attributes:
        period_start: Start of analysis period
        period_end: End of analysis period
        total_amount: Total expenses
        expense_count: Number of expenses
        average_amount: Average expense amount
        median_amount: Median expense amount
        min_amount: Minimum expense
        max_amount: Maximum expense
        std_deviation: Standard deviation
        by_category: Breakdown by category
        by_subcategory: Breakdown by subcategory
        by_vendor: Top vendors by spend
        by_payment_method: Breakdown by payment method
        by_month: Monthly totals
        by_day_of_week: Day of week distribution
        trend_data: Time series for trend analysis
        comparison_data: Comparison with previous period
        top_expenses: Top N expenses by amount
        recurring_total: Total recurring expenses
        budget_status: Budget tracking info
    """

    # Period info
    period_start: datetime
    period_end: datetime

    # Basic statistics
    total_amount: float = 0.0
    expense_count: int = 0
    average_amount: float = 0.0
    median_amount: float = 0.0
    min_amount: float = 0.0
    max_amount: float = 0.0
    std_deviation: float = 0.0

    # Breakdowns
    by_category: Dict[str, float] = field(default_factory=dict)
    by_subcategory: Dict[str, Dict[str, float]] = field(default_factory=dict)
    by_vendor: Dict[str, float] = field(default_factory=dict)
    by_payment_method: Dict[str, float] = field(default_factory=dict)
    by_month: Dict[str, float] = field(default_factory=dict)
    by_day_of_week: Dict[str, float] = field(default_factory=dict)

    # Trend data (list of (date, amount) tuples)
    trend_data: List[Dict[str, Any]] = field(default_factory=list)

    # Comparison with previous period
    comparison_data: Dict[str, Any] = field(default_factory=dict)

    # Top expenses
    top_expenses: List[Dict[str, Any]] = field(default_factory=list)

    # Recurring expenses total
    recurring_total: float = 0.0
    recurring_count: int = 0

    # Budget info
    budget_status: Dict[str, Any] = field(default_factory=dict)

    @property
    def period_days(self) -> int:
        """Get number of days in the period."""
        return (self.period_end - self.period_start).days + 1

    @property
    def daily_average(self) -> float:
        """Get daily average spending."""
        days = self.period_days
        return self.total_amount / days if days > 0 else 0.0

    @property
    def category_percentages(self) -> Dict[str, float]:
        """Get category breakdown as percentages."""
        if self.total_amount == 0:
            return {}
        return {
            cat: (amount / self.total_amount * 100)
            for cat, amount in self.by_category.items()
        }

    @property
    def top_category(self) -> Optional[str]:
        """Get category with highest spending."""
        if not self.by_category:
            return None
        return max(self.by_category, key=self.by_category.get)

    @property
    def top_vendor(self) -> Optional[str]:
        """Get vendor with highest spending."""
        if not self.by_vendor:
            return None
        return max(self.by_vendor, key=self.by_vendor.get)

    def get_category_total(self, category: str) -> float:
        """Get total for a specific category."""
        return self.by_category.get(category, 0.0)

    def get_vendor_total(self, vendor: str) -> float:
        """Get total for a specific vendor."""
        return self.by_vendor.get(vendor, 0.0)

    def get_period_comparison(self) -> Dict[str, Any]:
        """Get comparison with previous period."""
        if not self.comparison_data:
            return {
                'previous_total': 0,
                'change_amount': 0,
                'change_percent': 0,
                'trend': 'stable'
            }
        return self.comparison_data

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'period_start': self.period_start.strftime('%Y-%m-%d'),
            'period_end': self.period_end.strftime('%Y-%m-%d'),
            'total_amount': self.total_amount,
            'expense_count': self.expense_count,
            'average_amount': self.average_amount,
            'median_amount': self.median_amount,
            'min_amount': self.min_amount,
            'max_amount': self.max_amount,
            'std_deviation': self.std_deviation,
            'daily_average': self.daily_average,
            'by_category': self.by_category.copy(),
            'by_subcategory': {k: v.copy() for k, v in self.by_subcategory.items()},
            'by_vendor': self.by_vendor.copy(),
            'by_payment_method': self.by_payment_method.copy(),
            'by_month': self.by_month.copy(),
            'by_day_of_week': self.by_day_of_week.copy(),
            'trend_data': self.trend_data.copy(),
            'comparison_data': self.comparison_data.copy(),
            'top_expenses': self.top_expenses.copy(),
            'recurring_total': self.recurring_total,
            'recurring_count': self.recurring_count,
            'budget_status': self.budget_status.copy(),
            'category_percentages': self.category_percentages,
            'top_category': self.top_category,
            'top_vendor': self.top_vendor
        }

    def get_summary_text(self) -> str:
        """Get human-readable summary text."""
        lines = [
            f"Period: {self.period_start.strftime('%d/%m/%Y')} - {self.period_end.strftime('%d/%m/%Y')}",
            f"Total Expenses: L {self.total_amount:,.2f}",
            f"Number of Expenses: {self.expense_count}",
            f"Average: L {self.average_amount:,.2f}",
            f"Daily Average: L {self.daily_average:,.2f}",
        ]

        if self.top_category:
            cat_amount = self.by_category.get(self.top_category, 0)
            lines.append(f"Top Category: {self.top_category} (L {cat_amount:,.2f})")

        if self.top_vendor:
            vendor_amount = self.by_vendor.get(self.top_vendor, 0)
            lines.append(f"Top Vendor: {self.top_vendor} (L {vendor_amount:,.2f})")

        return "\n".join(lines)

    @classmethod
    def empty(cls, start: datetime, end: datetime) -> 'StatisticalSummary':
        """Create an empty summary for a period with no expenses."""
        return cls(
            period_start=start,
            period_end=end,
            total_amount=0.0,
            expense_count=0,
            average_amount=0.0,
            median_amount=0.0,
            min_amount=0.0,
            max_amount=0.0,
            std_deviation=0.0
        )
