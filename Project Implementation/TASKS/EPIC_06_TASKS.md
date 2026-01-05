# Epic 6: Visual Analytics & Dashboards - Implementation Tasks

**Phase:** 8 (Visualization)
**Priority:** Medium-Low
**Dependencies:** Epic 5 (Reporting)
**Estimated Tasks:** 30+

---

## Story 6.1: Visualizer Class

**Prerequisites:** Epic 1 (CategoryManager)

### Task 6.1.1: Create visualization package
- [ ] Create `visualization/__init__.py`:
```python
"""
Visualization components for Beauty Salon Expense Manager.
"""

from .visualizer import Visualizer

__all__ = ['Visualizer']
```

### Task 6.1.2: Create Visualizer class with constants
- [ ] Create `visualization/visualizer.py`:
```python
"""
Visualizer - Generates charts and visualizations for expense data.
"""

from typing import Dict, List, Optional, Tuple
import tkinter as tk

import matplotlib
matplotlib.use('TkAgg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd


class Visualizer:
    """Generates charts and visualizations for expense data."""

    # Category colors (matches CategoryManager)
    CATEGORY_COLORS = {
        'Supplies': '#FF6B9D',       # Pink
        'Equipment': '#9B59B6',      # Purple
        'Facilities': '#3498DB',     # Blue
        'Staff': '#2ECC71',          # Green
        'Marketing': '#F39C12',      # Orange
        'Administrative': '#95A5A6', # Gray
    }

    # Fallback palette for additional categories
    SALON_PALETTE = [
        '#E91E63',  # Pink
        '#9C27B0',  # Purple
        '#3F51B5',  # Indigo
        '#00BCD4',  # Cyan
        '#4CAF50',  # Green
        '#FF9800',  # Orange
        '#795548',  # Brown
        '#607D8B',  # Blue Grey
    ]

    # Status colors for budget indicators
    STATUS_COLORS = {
        'ok': '#4CAF50',      # Green
        'warning': '#FF9800',  # Orange
        'exceeded': '#F44336'  # Red
    }

    # Default figure sizes
    DEFAULT_FIGSIZE = (8, 6)
    SMALL_FIGSIZE = (6, 4)
    LARGE_FIGSIZE = (12, 8)

    def __init__(self):
        """Initialize with default settings."""
        # Set seaborn style
        sns.set_style("whitegrid")
        sns.set_palette(self.SALON_PALETTE)

        # Configure matplotlib defaults
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 12
        plt.rcParams['axes.labelsize'] = 10

    def _get_color(self, category: str) -> str:
        """Get color for a category."""
        return self.CATEGORY_COLORS.get(category, self.SALON_PALETTE[0])

    def _get_colors_for_categories(self, categories: List[str]) -> List[str]:
        """Get colors for a list of categories."""
        colors = []
        palette_idx = 0
        for cat in categories:
            if cat in self.CATEGORY_COLORS:
                colors.append(self.CATEGORY_COLORS[cat])
            else:
                colors.append(self.SALON_PALETTE[palette_idx % len(self.SALON_PALETTE)])
                palette_idx += 1
        return colors
```

### Task 6.1.3: Implement pie chart methods
- [ ] Add pie chart generation:
```python
    def create_category_pie_chart(
        self,
        data: pd.DataFrame,
        figsize: Tuple = None,
        title: str = "Expenses by Category"
    ) -> Figure:
        """Create pie chart of expenses by category."""
        fig, ax = plt.subplots(figsize=figsize or self.DEFAULT_FIGSIZE)

        if data.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title(title)
            return fig

        # Prepare data
        categories = data['category'].tolist()
        values = data['total'].tolist()
        colors = self._get_colors_for_categories(categories)

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=categories,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85
        )

        # Style
        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.setp(autotexts, size=9, weight='bold')

        # Equal aspect ratio ensures pie is circular
        ax.axis('equal')

        plt.tight_layout()
        return fig

    def create_payment_method_pie(
        self,
        data: pd.DataFrame,
        figsize: Tuple = None,
        title: str = "Expenses by Payment Method"
    ) -> Figure:
        """Create pie chart of expenses by payment method."""
        fig, ax = plt.subplots(figsize=figsize or self.DEFAULT_FIGSIZE)

        if data.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title(title)
            return fig

        methods = data['payment_method'].tolist()
        values = data['total'].tolist()

        wedges, texts, autotexts = ax.pie(
            values,
            labels=methods,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85
        )

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.axis('equal')

        plt.tight_layout()
        return fig
```

### Task 6.1.4: Implement bar chart methods
- [ ] Add bar chart generation:
```python
    def create_category_bar_chart(
        self,
        data: pd.DataFrame,
        figsize: Tuple = None,
        title: str = "Expenses by Category",
        horizontal: bool = True
    ) -> Figure:
        """Create bar chart of expenses by category."""
        fig, ax = plt.subplots(figsize=figsize or self.DEFAULT_FIGSIZE)

        if data.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title(title)
            return fig

        categories = data['category'].tolist()
        values = data['total'].tolist()
        colors = self._get_colors_for_categories(categories)

        if horizontal:
            bars = ax.barh(categories, values, color=colors)
            ax.set_xlabel('Amount (L)')
            ax.set_ylabel('Category')
            # Add value labels
            for bar, val in zip(bars, values):
                ax.text(val + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                       f'L {val:,.0f}', va='center', fontsize=9)
        else:
            bars = ax.bar(categories, values, color=colors)
            ax.set_ylabel('Amount (L)')
            ax.set_xlabel('Category')
            plt.xticks(rotation=45, ha='right')
            # Add value labels
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, val + max(values) * 0.01,
                       f'L {val:,.0f}', ha='center', fontsize=9)

        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig

    def create_vendor_bar_chart(
        self,
        data: pd.DataFrame,
        top_n: int = 10,
        figsize: Tuple = None,
        title: str = "Top Vendors"
    ) -> Figure:
        """Create horizontal bar chart of top vendors."""
        fig, ax = plt.subplots(figsize=figsize or self.DEFAULT_FIGSIZE)

        if data.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title(title)
            return fig

        # Take top N
        data = data.head(top_n)
        vendors = data['vendor'].tolist()
        values = data['total'].tolist()

        # Reverse for horizontal bar chart (top at top)
        vendors = vendors[::-1]
        values = values[::-1]

        bars = ax.barh(vendors, values, color=self.SALON_PALETTE[0])

        ax.set_xlabel('Amount (L)')
        ax.set_ylabel('Vendor')
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(val + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'L {val:,.0f}', va='center', fontsize=9)

        plt.tight_layout()
        return fig
```

### Task 6.1.5: Implement line/trend chart methods
- [ ] Add trend chart generation:
```python
    def create_monthly_trend_line(
        self,
        data: pd.DataFrame,
        figsize: Tuple = None,
        title: str = "Monthly Expense Trend"
    ) -> Figure:
        """Create line chart of monthly expenses."""
        fig, ax = plt.subplots(figsize=figsize or self.DEFAULT_FIGSIZE)

        if data.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title(title)
            return fig

        x = data['year_month'].tolist()
        y = data['total'].tolist()

        ax.plot(x, y, marker='o', linewidth=2, markersize=8, color=self.SALON_PALETTE[0])
        ax.fill_between(x, y, alpha=0.3, color=self.SALON_PALETTE[0])

        ax.set_xlabel('Month')
        ax.set_ylabel('Amount (L)')
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Rotate x labels
        plt.xticks(rotation=45, ha='right')

        # Add grid
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def create_yearly_trend_line(
        self,
        data: pd.DataFrame,
        figsize: Tuple = None,
        title: str = "Yearly Expense Trend"
    ) -> Figure:
        """Create line chart of yearly expenses."""
        fig, ax = plt.subplots(figsize=figsize or self.DEFAULT_FIGSIZE)

        if data.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title(title)
            return fig

        x = data['year'].tolist()
        y = data['total'].tolist()

        ax.plot(x, y, marker='o', linewidth=2, markersize=10, color=self.SALON_PALETTE[0])

        ax.set_xlabel('Year')
        ax.set_ylabel('Amount (L)')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)

        # Set x-axis to integers
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))

        plt.tight_layout()
        return fig

    def create_cumulative_area_chart(
        self,
        data: pd.DataFrame,
        figsize: Tuple = None,
        title: str = "Cumulative Spending"
    ) -> Figure:
        """Create area chart of cumulative spending over time."""
        fig, ax = plt.subplots(figsize=figsize or self.DEFAULT_FIGSIZE)

        if data.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title(title)
            return fig

        data = data.sort_values('date')
        data['cumulative'] = data['total'].cumsum()

        ax.fill_between(data['date'], data['cumulative'],
                       alpha=0.5, color=self.SALON_PALETTE[0])
        ax.plot(data['date'], data['cumulative'],
               linewidth=2, color=self.SALON_PALETTE[0])

        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Amount (L)')
        ax.set_title(title, fontsize=14, fontweight='bold')

        plt.xticks(rotation=45, ha='right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig
```

### Task 6.1.6: Implement budget chart methods
- [ ] Add budget-specific charts:
```python
    def create_budget_vs_actual_bar(
        self,
        budget_data: List[Dict],
        figsize: Tuple = None,
        title: str = "Budget vs Actual"
    ) -> Figure:
        """Create grouped bar chart comparing budget vs actual spending."""
        fig, ax = plt.subplots(figsize=figsize or self.DEFAULT_FIGSIZE)

        if not budget_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center')
            ax.set_title(title)
            return fig

        categories = [d['category'] for d in budget_data]
        budgets = [d['budget'] for d in budget_data]
        actuals = [d['actual'] for d in budget_data]
        statuses = [d.get('status', 'ok') for d in budget_data]

        x = range(len(categories))
        width = 0.35

        # Budget bars (gray)
        ax.bar([i - width/2 for i in x], budgets, width,
              label='Budget', color='#BDBDBD')

        # Actual bars (colored by status)
        actual_colors = [self.STATUS_COLORS.get(s, '#4CAF50') for s in statuses]
        ax.bar([i + width/2 for i in x], actuals, width,
              label='Actual', color=actual_colors)

        ax.set_ylabel('Amount (L)')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()

        plt.tight_layout()
        return fig

    def create_budget_progress_gauge(
        self,
        percentage: float,
        figsize: Tuple = None,
        title: str = "Budget Usage"
    ) -> Figure:
        """Create gauge/donut chart showing budget progress."""
        fig, ax = plt.subplots(figsize=figsize or self.SMALL_FIGSIZE)

        # Determine color based on percentage
        if percentage > 100:
            color = self.STATUS_COLORS['exceeded']
        elif percentage >= 80:
            color = self.STATUS_COLORS['warning']
        else:
            color = self.STATUS_COLORS['ok']

        # Cap display at 100% for visual, but show actual value
        display_pct = min(percentage, 100)

        # Create donut chart
        sizes = [display_pct, 100 - display_pct]
        colors = [color, '#EEEEEE']

        wedges, _ = ax.pie(sizes, colors=colors, startangle=90,
                          wedgeprops=dict(width=0.3))

        # Add center text
        ax.text(0, 0, f'{percentage:.1f}%', ha='center', va='center',
               fontsize=20, fontweight='bold', color=color)

        ax.set_title(title, fontsize=14, fontweight='bold')

        plt.tight_layout()
        return fig
```

### Task 6.1.7: Implement Tkinter integration methods
- [ ] Add Tkinter embedding:
```python
    def embed_in_tkinter(self, figure: Figure, parent: tk.Widget) -> FigureCanvasTkAgg:
        """Embed a matplotlib figure in a Tkinter widget."""
        canvas = FigureCanvasTkAgg(figure, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return canvas

    def update_embedded_chart(self, canvas: FigureCanvasTkAgg, new_figure: Figure) -> None:
        """Update an embedded chart with new data."""
        # Clear old figure
        canvas.figure.clear()

        # Copy axes from new figure
        for ax in new_figure.axes:
            canvas.figure.add_axes(ax)

        canvas.draw()

    def save_chart(self, figure: Figure, filepath: str, dpi: int = 150) -> None:
        """Save a chart as an image file."""
        figure.savefig(filepath, dpi=dpi, bbox_inches='tight')

    def close_figure(self, figure: Figure) -> None:
        """Close a figure to free memory."""
        plt.close(figure)
```

### Task 6.1.8: Create Visualizer tests
- [ ] Create `tests/test_visualization/__init__.py`
- [ ] Create `tests/test_visualization/test_visualizer.py`

---

## Story 6.2: Dashboard View

**Prerequisites:** Story 6.1, Story 5.1, Story 4.1

### Task 6.2.1: Create dashboard package
- [ ] Create `ui/dashboard/__init__.py`
- [ ] Create `ui/dashboard/dashboard_view.py`:
  - Main dashboard frame
  - Period selector (month/year)
  - Refresh button
  - Navigation (Prev/Next)

### Task 6.2.2: Create KPI cards row
- [ ] Add KPI cards:
  - Total Spent (with % change)
  - Budget Usage (with progress bar)
  - Top Category (with amount and %)
  - Transaction Count
  - Average Expense
  - Recurring Due Count

### Task 6.2.3: Create charts grid
- [ ] Implement 2x2 chart grid:
  - Category Distribution (Pie Chart)
  - Monthly Trend (Line Chart)
  - Budget vs Actual (Bar Chart)
  - Top Vendors (Horizontal Bars)

### Task 6.2.4: Create alerts section
- [ ] Add alerts panel at bottom:
  - Show active budget alerts
  - Color-coded by severity
  - Click handler to view details
  - View All link

### Task 6.2.5: Implement quick actions
- [ ] Add quick action buttons:
  - [+ Add Expense]
  - [View Reports]
  - [Manage Budgets]
  - [Trend Analysis]

### Task 6.2.6: Implement data refresh
- [ ] Period change handler
- [ ] Refresh button handler
- [ ] Cache chart data for performance

---

## Story 6.3: Category Charts

**Prerequisites:** Story 6.1

### Task 6.3.1: Create category charts view
- [ ] Create `ui/charts/__init__.py`
- [ ] Create `ui/charts/category_charts.py`:
  - Chart type selector (Pie, Bar horizontal, Bar vertical, Donut)
  - Period selector
  - Main chart display area

### Task 6.3.2: Implement chart switching
- [ ] Pie chart option
- [ ] Horizontal bar chart option
- [ ] Vertical bar chart option
- [ ] Donut chart option

### Task 6.3.3: Implement subcategory drill-down
- [ ] Click segment/bar to drill into subcategories
- [ ] Back button to return to main view
- [ ] Breadcrumb navigation

### Task 6.3.4: Add context menu
- [ ] Right-click menu:
  - Save as PNG/JPG
  - Copy to clipboard
  - View data table
  - Export data

### Task 6.3.5: Create chart options dialog
- [ ] Chart type selection
- [ ] Display options (values, legend, percentages)
- [ ] Color scheme selection

---

## Story 6.4: Trend Charts

**Prerequisites:** Story 6.1

### Task 6.4.1: Create trend charts view
- [ ] Create `ui/charts/trend_charts.py`:
  - Trend type selector (Monthly, Quarterly, Yearly, Cumulative)
  - Category filter dropdown
  - Main chart area

### Task 6.4.2: Implement trend types
- [ ] Monthly trend (last 12 months)
- [ ] Quarterly trend (last 8 quarters)
- [ ] Yearly trend (last 5 years)
- [ ] Cumulative (area chart)

### Task 6.4.3: Implement category filtering
- [ ] All categories option
- [ ] Single category filter
- [ ] Multi-category comparison (multiple lines)

### Task 6.4.4: Add summary statistics panel
- [ ] Average per period
- [ ] Overall trend direction
- [ ] Peak period
- [ ] Lowest period

---

## Story 6.5: Budget Charts

**Prerequisites:** Story 6.1, Story 4.1

### Task 6.5.1: Create budget charts view
- [ ] Create `ui/charts/budget_charts.py`:
  - Period selector (month picker)
  - Overall progress gauge
  - Category comparison chart

### Task 6.5.2: Implement overall progress gauge
- [ ] Donut/gauge chart showing total budget usage
- [ ] Percentage in center
- [ ] Color based on status
- [ ] Amounts and days remaining text

### Task 6.5.3: Implement category comparison chart
- [ ] Grouped bar chart
- [ ] Budget bars (gray)
- [ ] Actual bars (status colored)
- [ ] Percentage labels

### Task 6.5.4: Add historical comparison table
- [ ] Month, Budget, Actual, Variance, Status columns
- [ ] Sortable
- [ ] Export option

---

## Completion Checklist

### Story 6.1: Visualizer
- [ ] Visualizer class created
- [ ] Color constants defined
- [ ] Pie chart methods working
- [ ] Bar chart methods working
- [ ] Line chart methods working
- [ ] Budget chart methods working
- [ ] Tkinter embedding working
- [ ] Save chart working
- [ ] Tests passing

### Story 6.2: Dashboard
- [ ] Dashboard view created
- [ ] KPI cards working
- [ ] Charts grid working
- [ ] Alerts section working
- [ ] Period navigation working
- [ ] Quick actions working

### Story 6.3-6.5: Chart Views
- [ ] Category charts view created
- [ ] Trend charts view created
- [ ] Budget charts view created
- [ ] Drill-down working
- [ ] All chart types working
- [ ] Context menus working

---

## Next Steps

After completing Epic 6, proceed to:
- **Epic 8: Export Capabilities** - Uses charts for report export
