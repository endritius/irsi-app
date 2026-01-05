# Epic 5: Advanced Reporting & Analytics - Implementation Tasks

**Phase:** 7 (Reporting)
**Priority:** Medium
**Dependencies:** Epic 2, Epic 3
**Estimated Tasks:** 35+

---

## Story 5.1: ReportGenerator Class

**Prerequisites:** Epic 2 (ExpenseManager), Epic 3 (FilterManager)

### Task 5.1.1: Create reports package
- [ ] Create `reports/__init__.py`:
```python
"""
Reports and analytics for Beauty Salon Expense Manager.
"""

from .report_generator import ReportGenerator, StatisticalSummary

__all__ = [
    'ReportGenerator',
    'StatisticalSummary'
]
```

### Task 5.1.2: Create StatisticalSummary dataclass
- [ ] Create `reports/report_generator.py`:
```python
"""
ReportGenerator - Generates statistical reports and analytics.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from managers.expense_manager import ExpenseManager
from managers.filter_manager import FilterManager


@dataclass
class StatisticalSummary:
    """Statistical summary of expenses."""
    total: float
    average: float
    median: float
    minimum: float
    maximum: float
    std_deviation: float
    count: int
    date_range: Tuple[datetime, datetime]

    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'total': self.total,
            'average': self.average,
            'median': self.median,
            'minimum': self.minimum,
            'maximum': self.maximum,
            'std_deviation': self.std_deviation,
            'count': self.count,
            'date_from': self.date_range[0],
            'date_to': self.date_range[1]
        }
```

### Task 5.1.3: Create ReportGenerator class
- [ ] Add ReportGenerator class:
```python
class ReportGenerator:
    """Generates statistical reports and analytics for expenses."""

    def __init__(self, expense_manager: ExpenseManager, filter_manager: FilterManager):
        """Initialize with managers."""
        self.expense_manager = expense_manager
        self.filter_manager = filter_manager

    def _get_dataframe(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Get DataFrame, using provided or fetching from manager."""
        if df is not None:
            return df
        return self.expense_manager.get_expenses_dataframe()

    def get_statistical_summary(self, df: pd.DataFrame = None) -> StatisticalSummary:
        """Calculate statistical summary using NumPy."""
        df = self._get_dataframe(df)

        if df.empty:
            return StatisticalSummary(
                total=0, average=0, median=0, minimum=0, maximum=0,
                std_deviation=0, count=0,
                date_range=(datetime.now(), datetime.now())
            )

        amounts = df['amount'].values

        return StatisticalSummary(
            total=float(np.sum(amounts)),
            average=float(np.mean(amounts)),
            median=float(np.median(amounts)),
            minimum=float(np.min(amounts)),
            maximum=float(np.max(amounts)),
            std_deviation=float(np.std(amounts)),
            count=len(amounts),
            date_range=(
                pd.to_datetime(df['date']).min().to_pydatetime(),
                pd.to_datetime(df['date']).max().to_pydatetime()
            )
        )
```

### Task 5.1.4: Implement category analysis methods
- [ ] Add category analysis:
```python
    def get_category_summary(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Get category breakdown with statistics."""
        df = self._get_dataframe(df)

        if df.empty:
            return pd.DataFrame(columns=[
                'category', 'total', 'percentage', 'count',
                'average', 'min_amount', 'max_amount'
            ])

        total_amount = df['amount'].sum()

        summary = df.groupby('category').agg({
            'amount': ['sum', 'count', 'mean', 'min', 'max']
        }).reset_index()

        summary.columns = ['category', 'total', 'count', 'average', 'min_amount', 'max_amount']
        summary['percentage'] = (summary['total'] / total_amount * 100).round(1)

        return summary.sort_values('total', ascending=False)

    def get_subcategory_summary(self, category: str, df: pd.DataFrame = None) -> pd.DataFrame:
        """Get subcategory breakdown for a specific category."""
        df = self._get_dataframe(df)

        if df.empty:
            return pd.DataFrame(columns=[
                'subcategory', 'total', 'percentage', 'count', 'average'
            ])

        category_df = df[df['category'] == category]
        if category_df.empty:
            return pd.DataFrame(columns=[
                'subcategory', 'total', 'percentage', 'count', 'average'
            ])

        total_amount = category_df['amount'].sum()

        summary = category_df.groupby('subcategory').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()

        summary.columns = ['subcategory', 'total', 'count', 'average']
        summary['percentage'] = (summary['total'] / total_amount * 100).round(1)

        return summary.sort_values('total', ascending=False)
```

### Task 5.1.5: Implement trend analysis methods
- [ ] Add trend methods:
```python
    def get_monthly_trend(self, months: int = 12) -> pd.DataFrame:
        """Get monthly expense totals for trend analysis."""
        df = self._get_dataframe()

        if df.empty:
            return pd.DataFrame(columns=['year_month', 'year', 'month', 'total', 'count', 'average'])

        df['date'] = pd.to_datetime(df['date'])
        df['year_month'] = df['date'].dt.to_period('M')

        # Filter to last N months
        cutoff = datetime.now() - timedelta(days=months * 31)
        df = df[df['date'] >= cutoff]

        if df.empty:
            return pd.DataFrame(columns=['year_month', 'year', 'month', 'total', 'count', 'average'])

        summary = df.groupby('year_month').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()

        summary.columns = ['year_month', 'total', 'count', 'average']
        summary['year'] = summary['year_month'].dt.year
        summary['month'] = summary['year_month'].dt.month
        summary['year_month'] = summary['year_month'].astype(str)

        return summary.sort_values(['year', 'month'])

    def get_quarterly_summary(self, year: int) -> pd.DataFrame:
        """Get quarterly breakdown for a specific year."""
        df = self._get_dataframe()

        if df.empty:
            return pd.DataFrame(columns=['quarter', 'total', 'count', 'average'])

        df['date'] = pd.to_datetime(df['date'])
        df = df[df['date'].dt.year == year]

        if df.empty:
            return pd.DataFrame(columns=['quarter', 'total', 'count', 'average'])

        df['quarter'] = df['date'].dt.quarter

        summary = df.groupby('quarter').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()

        summary.columns = ['quarter', 'total', 'count', 'average']
        return summary

    def get_yearly_trend(self, years: int = 3) -> pd.DataFrame:
        """Get yearly expense totals for long-term trend."""
        df = self._get_dataframe()

        if df.empty:
            return pd.DataFrame(columns=['year', 'total', 'count', 'average'])

        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year

        # Filter to last N years
        current_year = datetime.now().year
        df = df[df['year'] >= (current_year - years + 1)]

        if df.empty:
            return pd.DataFrame(columns=['year', 'total', 'count', 'average'])

        summary = df.groupby('year').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()

        summary.columns = ['year', 'total', 'count', 'average']
        return summary.sort_values('year')
```

### Task 5.1.6: Implement vendor analysis methods
- [ ] Add vendor analysis:
```python
    def get_vendor_analysis(self, top_n: int = 10, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyze spending by vendor."""
        df = self._get_dataframe(df)

        if df.empty:
            return pd.DataFrame(columns=[
                'vendor', 'total', 'count', 'average', 'last_transaction', 'percentage'
            ])

        df['date'] = pd.to_datetime(df['date'])
        total_amount = df['amount'].sum()

        summary = df.groupby('vendor').agg({
            'amount': ['sum', 'count', 'mean'],
            'date': 'max'
        }).reset_index()

        summary.columns = ['vendor', 'total', 'count', 'average', 'last_transaction']
        summary['percentage'] = (summary['total'] / total_amount * 100).round(1)

        summary = summary.sort_values('total', ascending=False)
        return summary.head(top_n)

    def get_top_expenses(self, n: int = 10, df: pd.DataFrame = None) -> pd.DataFrame:
        """Get the N largest individual expenses."""
        df = self._get_dataframe(df)

        if df.empty:
            return df

        return df.nlargest(n, 'amount')
```

### Task 5.1.7: Implement payment and comparison methods
- [ ] Add payment method and comparison:
```python
    def get_payment_method_distribution(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Get expense distribution by payment method."""
        df = self._get_dataframe(df)

        if df.empty:
            return pd.DataFrame(columns=['payment_method', 'total', 'count', 'percentage'])

        total_amount = df['amount'].sum()

        summary = df.groupby('payment_method').agg({
            'amount': ['sum', 'count']
        }).reset_index()

        summary.columns = ['payment_method', 'total', 'count']
        summary['percentage'] = (summary['total'] / total_amount * 100).round(1)

        return summary.sort_values('total', ascending=False)

    def get_recurring_vs_onetime(self, df: pd.DataFrame = None) -> Dict:
        """Compare recurring vs one-time expenses."""
        df = self._get_dataframe(df)

        if df.empty:
            return {
                'recurring_total': 0, 'recurring_count': 0,
                'onetime_total': 0, 'onetime_count': 0,
                'recurring_percentage': 0
            }

        recurring = df[df['is_recurring'] == True]
        onetime = df[df['is_recurring'] != True]

        recurring_total = recurring['amount'].sum() if not recurring.empty else 0
        onetime_total = onetime['amount'].sum() if not onetime.empty else 0
        total = recurring_total + onetime_total

        return {
            'recurring_total': recurring_total,
            'recurring_count': len(recurring),
            'onetime_total': onetime_total,
            'onetime_count': len(onetime),
            'recurring_percentage': (recurring_total / total * 100) if total > 0 else 0
        }

    def compare_periods(
        self,
        period1: Tuple[datetime, datetime],
        period2: Tuple[datetime, datetime]
    ) -> Dict:
        """Compare spending between two time periods."""
        df = self._get_dataframe()

        if df.empty:
            return {
                'period1_total': 0, 'period2_total': 0,
                'difference': 0, 'percentage_change': 0
            }

        df['date'] = pd.to_datetime(df['date'])

        p1_df = df[(df['date'] >= period1[0]) & (df['date'] <= period1[1])]
        p2_df = df[(df['date'] >= period2[0]) & (df['date'] <= period2[1])]

        p1_total = p1_df['amount'].sum() if not p1_df.empty else 0
        p2_total = p2_df['amount'].sum() if not p2_df.empty else 0

        difference = p2_total - p1_total
        pct_change = ((p2_total - p1_total) / p1_total * 100) if p1_total > 0 else 0

        return {
            'period1_total': p1_total,
            'period1_count': len(p1_df),
            'period2_total': p2_total,
            'period2_count': len(p2_df),
            'difference': difference,
            'percentage_change': pct_change
        }
```

### Task 5.1.8: Implement tag and pattern analysis
- [ ] Add tag and seasonal analysis:
```python
    def get_tag_analysis(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyze expenses by tags."""
        df = self._get_dataframe(df)

        if df.empty:
            return pd.DataFrame(columns=['tag', 'total', 'count', 'average'])

        # Explode tags into separate rows
        tag_data = []
        for _, row in df.iterrows():
            tags_str = row.get('tags', '')
            if pd.notna(tags_str) and tags_str:
                tags = [t.strip() for t in str(tags_str).split(',')]
                for tag in tags:
                    if tag:
                        tag_data.append({'tag': tag, 'amount': row['amount']})

        if not tag_data:
            return pd.DataFrame(columns=['tag', 'total', 'count', 'average'])

        tag_df = pd.DataFrame(tag_data)
        summary = tag_df.groupby('tag').agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()

        summary.columns = ['tag', 'total', 'count', 'average']
        return summary.sort_values('total', ascending=False)

    def identify_seasonal_patterns(self, df: pd.DataFrame = None) -> Dict:
        """Identify high/low spending months."""
        df = self._get_dataframe(df)

        if df.empty:
            return {'high_months': [], 'low_months': [], 'average': 0}

        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month

        monthly = df.groupby('month')['amount'].sum()
        avg = monthly.mean()
        std = monthly.std()

        high_months = monthly[monthly > avg + std].index.tolist()
        low_months = monthly[monthly < avg - std].index.tolist()

        return {
            'high_months': high_months,
            'low_months': low_months,
            'average': avg,
            'monthly_totals': monthly.to_dict()
        }
```

### Task 5.1.9: Implement cash flow methods
- [ ] Add cash flow analysis (Story 5.7):
```python
    def get_daily_cash_flow(self, days: int = 30) -> pd.DataFrame:
        """Get daily expense totals for cash flow analysis."""
        df = self._get_dataframe()

        if df.empty:
            return pd.DataFrame(columns=['date', 'total', 'count'])

        df['date'] = pd.to_datetime(df['date']).dt.date
        cutoff = (datetime.now() - timedelta(days=days)).date()
        df = df[df['date'] >= cutoff]

        if df.empty:
            return pd.DataFrame(columns=['date', 'total', 'count'])

        summary = df.groupby('date').agg({
            'amount': ['sum', 'count']
        }).reset_index()

        summary.columns = ['date', 'total', 'count']
        return summary.sort_values('date')

    def get_weekly_cash_flow(self, weeks: int = 12) -> pd.DataFrame:
        """Get weekly expense totals."""
        df = self._get_dataframe()

        if df.empty:
            return pd.DataFrame(columns=['week', 'total', 'count', 'average'])

        df['date'] = pd.to_datetime(df['date'])
        cutoff = datetime.now() - timedelta(weeks=weeks)
        df = df[df['date'] >= cutoff]

        if df.empty:
            return pd.DataFrame(columns=['week', 'total', 'count', 'average'])

        df['week'] = df['date'].dt.isocalendar().week
        df['year'] = df['date'].dt.year

        summary = df.groupby(['year', 'week']).agg({
            'amount': ['sum', 'count', 'mean']
        }).reset_index()

        summary.columns = ['year', 'week', 'total', 'count', 'average']
        return summary.sort_values(['year', 'week'])

    def get_peak_spending_analysis(self, df: pd.DataFrame = None) -> Dict:
        """Identify peak spending days (day of week, day of month)."""
        df = self._get_dataframe(df)

        if df.empty:
            return {
                'by_day_of_week': {},
                'by_day_of_month': {},
                'peak_day_of_week': None,
                'peak_day_of_month': None
            }

        df['date'] = pd.to_datetime(df['date'])
        df['day_of_week'] = df['date'].dt.dayofweek
        df['day_of_month'] = df['date'].dt.day

        by_dow = df.groupby('day_of_week')['amount'].sum().to_dict()
        by_dom = df.groupby('day_of_month')['amount'].sum().to_dict()

        peak_dow = max(by_dow, key=by_dow.get) if by_dow else None
        peak_dom = max(by_dom, key=by_dom.get) if by_dom else None

        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        return {
            'by_day_of_week': {day_names[k]: v for k, v in by_dow.items()},
            'by_day_of_month': by_dom,
            'peak_day_of_week': day_names[peak_dow] if peak_dow is not None else None,
            'peak_day_of_month': peak_dom
        }

    def get_recurring_ratio(self, df: pd.DataFrame = None) -> Dict:
        """Calculate recurring vs one-time expense ratio."""
        return self.get_recurring_vs_onetime(df)
```

### Task 5.1.10: Create ReportGenerator tests
- [ ] Create `tests/test_reports/__init__.py`
- [ ] Create `tests/test_reports/test_report_generator.py`

---

## Story 5.2: Summary Statistics View

**Prerequisites:** Story 5.1

### Task 5.2.1: Create summary statistics view
- [ ] Create `ui/reports/__init__.py`
- [ ] Create `ui/reports/summary_statistics.py`:
  - KPI cards row (Total, Count, Average)
  - Statistical details table
  - Period selector (This Month, Last Month, Quarter, Year, Custom)
  - Compare with previous period button

### Task 5.2.2: Create KPI card component
- [ ] Create `ui/components/kpi_card.py`:
  - Value display with formatting
  - Label text
  - Optional change indicator (+/-%)
  - Color coding for positive/negative

### Task 5.2.3: Implement period comparison
- [ ] Add comparison dialog showing:
  - Period 1 vs Period 2 totals
  - Difference amount
  - Percentage change
  - Category breakdown comparison

---

## Story 5.3: Category Analysis Report

**Prerequisites:** Story 5.1

### Task 5.3.1: Create category analysis view
- [ ] Create `ui/reports/category_analysis.py`:
  - Category summary table with columns
  - Color indicators per category
  - Sortable columns
  - Drill-down buttons

### Task 5.3.2: Implement subcategory drill-down
- [ ] Back button navigation
- [ ] Subcategory table for selected category
- [ ] Breadcrumb navigation

### Task 5.3.3: Add export functionality
- [ ] Export category report to PDF
- [ ] Export category data to CSV

---

## Story 5.4: Trend Analysis Report

**Prerequisites:** Story 5.1

### Task 5.4.1: Create trend analysis view
- [ ] Create `ui/reports/trend_analysis.py`:
  - Trend type selector (Monthly, Quarterly, Yearly)
  - Data table with columns
  - Pattern identification panel
  - Insights section

### Task 5.4.2: Implement category-specific trends
- [ ] Category dropdown filter
  - Multi-category comparison option
  - Legend for multiple lines

### Task 5.4.3: Add trend insights
- [ ] Calculate overall trend direction
- [ ] Identify peak/lowest periods
- [ ] Display average values

---

## Story 5.5: Vendor Analysis Report

**Prerequisites:** Story 5.1

### Task 5.5.1: Create vendor analysis view
- [ ] Create `ui/reports/vendor_analysis.py`:
  - Vendor search/filter
  - Top N vendors table
  - Click to expand transactions

### Task 5.5.2: Implement vendor detail view
- [ ] Expandable transaction list per vendor
- [ ] Summary statistics per vendor
- [ ] Transaction history

### Task 5.5.3: Add export options
- [ ] Export to CSV
- [ ] Export to PDF

---

## Story 5.6: Custom Report Builder

**Prerequisites:** Story 5.1, Epic 6 (Visualizer), Epic 8 (Exporters)

### Task 5.6.1: Create custom report builder dialog
- [ ] Create `ui/reports/custom_report_builder.py`:
  - Report name field
  - Date range picker
  - Category checkboxes (Select/Clear All)
  - Group by radio buttons
  - Metrics checkboxes
  - Chart options checkboxes

### Task 5.6.2: Implement report preview
- [ ] Generate preview panel
- [ ] Show tables and charts
- [ ] Edit report button

### Task 5.6.3: Implement export actions
- [ ] Generate PDF button
- [ ] Generate Excel button
- [ ] Save report configuration (optional)

---

## Story 5.7: Cash Flow Analysis

**Prerequisites:** Story 5.1

### Task 5.7.1: Create cash flow analysis view
- [ ] Create `ui/reports/cash_flow_analysis.py`:
  - View toggle (Daily, Weekly, Monthly)
  - Period selector
  - Cash outflow summary panel

### Task 5.7.2: Implement payment method breakdown
- [ ] Payment method distribution panel
- [ ] Pie chart integration

### Task 5.7.3: Implement recurring vs one-time comparison
- [ ] Recurring expenses panel
- [ ] One-time expenses panel
- [ ] Ratio display with pie chart

### Task 5.7.4: Implement peak spending analysis
- [ ] Day of week analysis
- [ ] Day of month analysis
- [ ] Pattern insights text

---

## Completion Checklist

### Story 5.1: ReportGenerator
- [ ] StatisticalSummary dataclass created
- [ ] ReportGenerator class created
- [ ] Statistical summary working
- [ ] Category analysis working
- [ ] Trend analysis working
- [ ] Vendor analysis working
- [ ] Payment method distribution working
- [ ] Period comparison working
- [ ] Tag analysis working
- [ ] Cash flow methods working
- [ ] Tests passing

### Story 5.2-5.5: Report Views
- [ ] Summary statistics view created
- [ ] Category analysis view created
- [ ] Trend analysis view created
- [ ] Vendor analysis view created
- [ ] All drill-downs working
- [ ] Export options working

### Story 5.6-5.7: Advanced Reports
- [ ] Custom report builder created
- [ ] Cash flow analysis created
- [ ] All charts integrated
- [ ] Export working

---

## Next Steps

After completing Epic 5, proceed to:
- **Epic 6: Visualization & Dashboards** - Chart generation for reports
