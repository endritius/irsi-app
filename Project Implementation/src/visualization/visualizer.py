"""
Visualizer - Creates charts and graphs using Matplotlib and Seaborn.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
from io import BytesIO

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CURRENCY_SYMBOL


class Visualizer:
    """
    Creates charts and graphs for expense data visualization.
    Uses Matplotlib and Seaborn for professional-looking charts.
    """

    def __init__(self):
        """Initialize Visualizer with default style settings."""
        # Set style
        sns.set_theme(style="whitegrid")
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['font.size'] = 10

        # Color palette
        self.colors = sns.color_palette("husl", 12)
        self.category_colors = {
            'Supplies': '#3498db',
            'Equipment': '#e74c3c',
            'Facilities': '#2ecc71',
            'Staff': '#9b59b6',
            'Marketing': '#f39c12',
            'Administrative': '#1abc9c'
        }

    def _format_currency(self, value: float) -> str:
        """Format value as currency."""
        return f"{value:,.0f} {CURRENCY_SYMBOL}"

    def _get_category_color(self, category: str) -> str:
        """Get color for category."""
        return self.category_colors.get(category, '#7f8c8d')

    # ===== PIE CHARTS =====

    def create_category_pie_chart(
        self,
        category_data: List[Dict],
        figsize: Tuple[int, int] = (8, 8),
        title: str = "Expenses by Category"
    ) -> Figure:
        """
        Create pie chart of expenses by category.

        Args:
            category_data: List of dicts with 'category' and 'amount'
            figsize: Figure size tuple
            title: Chart title

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if not category_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        labels = [d['category'] for d in category_data]
        values = [d['amount'] for d in category_data]
        colors = [self._get_category_color(cat) for cat in labels]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            pctdistance=0.75,
            startangle=90,
            explode=[0.02] * len(values)
        )

        # Style autopct
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Add legend with amounts
        legend_labels = [f"{cat}: {self._format_currency(amt)}"
                        for cat, amt in zip(labels, values)]
        ax.legend(wedges, legend_labels, title="Categories",
                 loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

        plt.tight_layout()
        return fig

    def create_payment_method_pie_chart(
        self,
        payment_data: List[Dict],
        figsize: Tuple[int, int] = (8, 8),
        title: str = "Expenses by Payment Method"
    ) -> Figure:
        """
        Create pie chart of expenses by payment method.

        Args:
            payment_data: List of dicts with 'payment_method' and 'amount'
            figsize: Figure size tuple
            title: Chart title

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if not payment_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        labels = [d['payment_method'] for d in payment_data]
        values = [d['amount'] for d in payment_data]

        # Payment method colors
        payment_colors = {
            'Cash': '#27ae60',
            'Debit Card': '#3498db',
            'Credit Card': '#9b59b6',
            'Bank Transfer': '#f39c12'
        }
        colors = [payment_colors.get(pm, '#95a5a6') for pm in labels]

        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            pctdistance=0.75,
            startangle=90
        )

        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        return fig

    # ===== BAR CHARTS =====

    def create_category_bar_chart(
        self,
        category_data: List[Dict],
        figsize: Tuple[int, int] = (10, 6),
        title: str = "Expenses by Category",
        horizontal: bool = True
    ) -> Figure:
        """
        Create bar chart of expenses by category.

        Args:
            category_data: List of dicts with 'category' and 'amount'
            figsize: Figure size tuple
            title: Chart title
            horizontal: If True, create horizontal bar chart

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if not category_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        categories = [d['category'] for d in category_data]
        amounts = [d['amount'] for d in category_data]
        colors = [self._get_category_color(cat) for cat in categories]

        if horizontal:
            bars = ax.barh(categories, amounts, color=colors)
            ax.set_xlabel(f'Amount ({CURRENCY_SYMBOL})')
            ax.set_ylabel('Category')

            # Add value labels
            for bar, amount in zip(bars, amounts):
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2,
                       self._format_currency(amount),
                       ha='left', va='center', fontsize=9)
        else:
            bars = ax.bar(categories, amounts, color=colors)
            ax.set_ylabel(f'Amount ({CURRENCY_SYMBOL})')
            ax.set_xlabel('Category')
            plt.xticks(rotation=45, ha='right')

            # Add value labels
            for bar, amount in zip(bars, amounts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, height,
                       self._format_currency(amount),
                       ha='center', va='bottom', fontsize=9)

        ax.set_title(title, fontsize=14, fontweight='bold')
        plt.tight_layout()
        return fig

    def create_vendor_bar_chart(
        self,
        vendor_data: List[Dict],
        figsize: Tuple[int, int] = (10, 6),
        title: str = "Top Vendors by Spending"
    ) -> Figure:
        """
        Create horizontal bar chart of top vendors.

        Args:
            vendor_data: List of dicts with 'vendor' and 'amount'
            figsize: Figure size tuple
            title: Chart title

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if not vendor_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        vendors = [d['vendor'] for d in vendor_data]
        amounts = [d['amount'] for d in vendor_data]

        # Create gradient colors
        colors = sns.color_palette("Blues_r", len(vendors))

        bars = ax.barh(vendors, amounts, color=colors)
        ax.set_xlabel(f'Amount ({CURRENCY_SYMBOL})')
        ax.set_ylabel('Vendor')

        # Add value labels
        for bar, amount in zip(bars, amounts):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2,
                   self._format_currency(amount),
                   ha='left', va='center', fontsize=9)

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.invert_yaxis()  # Top vendors at top
        plt.tight_layout()
        return fig

    # ===== LINE CHARTS =====

    def create_monthly_trend_chart(
        self,
        monthly_data: List[Dict],
        figsize: Tuple[int, int] = (12, 6),
        title: str = "Monthly Expense Trend"
    ) -> Figure:
        """
        Create line chart of monthly expense trend.

        Args:
            monthly_data: List of dicts with 'month' and 'amount'
            figsize: Figure size tuple
            title: Chart title

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if not monthly_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        months = [d.get('month_name', d['month']) for d in monthly_data]
        amounts = [d['amount'] for d in monthly_data]

        # Create line plot
        ax.plot(range(len(months)), amounts, marker='o', linewidth=2,
               markersize=8, color='#3498db')

        # Fill area under line
        ax.fill_between(range(len(months)), amounts, alpha=0.3, color='#3498db')

        # Add value labels
        for i, (month, amount) in enumerate(zip(months, amounts)):
            ax.annotate(self._format_currency(amount),
                       (i, amount), textcoords="offset points",
                       xytext=(0, 10), ha='center', fontsize=8)

        ax.set_xticks(range(len(months)))
        ax.set_xticklabels(months, rotation=45, ha='right')
        ax.set_ylabel(f'Amount ({CURRENCY_SYMBOL})')
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add grid
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    def create_daily_trend_chart(
        self,
        daily_data: List[Dict],
        figsize: Tuple[int, int] = (12, 6),
        title: str = "Daily Expense Trend"
    ) -> Figure:
        """
        Create line chart of daily expense trend.

        Args:
            daily_data: List of dicts with 'date' and 'amount'
            figsize: Figure size tuple
            title: Chart title

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if not daily_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in daily_data]
        amounts = [d['amount'] for d in daily_data]

        ax.plot(dates, amounts, marker='.', linewidth=1.5,
               markersize=4, color='#2ecc71')
        ax.fill_between(dates, amounts, alpha=0.2, color='#2ecc71')

        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.xticks(rotation=45)

        ax.set_ylabel(f'Amount ({CURRENCY_SYMBOL})')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        return fig

    # ===== STACKED/GROUPED CHARTS =====

    def create_category_trend_chart(
        self,
        expenses_df: pd.DataFrame,
        figsize: Tuple[int, int] = (12, 6),
        title: str = "Category Trend Over Time"
    ) -> Figure:
        """
        Create stacked area chart of categories over time.

        Args:
            expenses_df: DataFrame with expense data
            figsize: Figure size tuple
            title: Chart title

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if expenses_df.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        # Pivot data
        df = expenses_df.copy()
        df['month'] = pd.to_datetime(df['date']).dt.to_period('M')
        pivot = df.pivot_table(
            values='amount',
            index='month',
            columns='category',
            aggfunc='sum',
            fill_value=0
        )

        # Create stacked area chart
        colors = [self._get_category_color(cat) for cat in pivot.columns]
        pivot.plot.area(ax=ax, stacked=True, alpha=0.7, color=colors)

        ax.set_ylabel(f'Amount ({CURRENCY_SYMBOL})')
        ax.set_xlabel('Month')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(title='Category', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        return fig

    # ===== BUDGET CHARTS =====

    def create_budget_comparison_chart(
        self,
        budget_data: List[Dict],
        figsize: Tuple[int, int] = (12, 6),
        title: str = "Budget vs Actual"
    ) -> Figure:
        """
        Create grouped bar chart comparing budget to actual spending.

        Args:
            budget_data: List of dicts with 'category', 'budget', and 'actual'
            figsize: Figure size tuple
            title: Chart title

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if not budget_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        categories = [d['category'] for d in budget_data]
        budgets = [d['budget'] for d in budget_data]
        actuals = [d['actual'] for d in budget_data]

        x = np.arange(len(categories))
        width = 0.35

        bars1 = ax.bar(x - width/2, budgets, width, label='Budget',
                      color='#3498db', alpha=0.8)
        bars2 = ax.bar(x + width/2, actuals, width, label='Actual',
                      color='#e74c3c', alpha=0.8)

        ax.set_ylabel(f'Amount ({CURRENCY_SYMBOL})')
        ax.set_xlabel('Category')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()

        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax.annotate(f'{height:,.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=8)

        for bar in bars2:
            height = bar.get_height()
            ax.annotate(f'{height:,.0f}',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=8)

        ax.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()
        return fig

    def create_budget_gauge_chart(
        self,
        budget: Dict,
        figsize: Tuple[int, int] = (6, 4),
        title: str = None
    ) -> Figure:
        """
        Create a gauge-style chart for single budget.

        Args:
            budget: Dict with 'category', 'budget', 'spent', 'percentage'
            figsize: Figure size tuple
            title: Chart title (default: category name)

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if not budget:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            return fig

        percentage = min(budget.get('percentage', 0), 100)
        spent = budget.get('spent', 0)
        total = budget.get('budget', budget.get('amount', 0))

        # Create horizontal progress bar
        ax.barh([0], [100], color='#ecf0f1', height=0.5)

        # Color based on percentage
        if percentage >= 100:
            color = '#e74c3c'  # Red - over budget
        elif percentage >= 80:
            color = '#f39c12'  # Orange - warning
        else:
            color = '#2ecc71'  # Green - under budget

        ax.barh([0], [percentage], color=color, height=0.5)

        # Add percentage text
        ax.text(50, 0, f'{percentage:.1f}%', ha='center', va='center',
               fontsize=16, fontweight='bold', color='black')

        ax.set_xlim(0, 100)
        ax.set_ylim(-0.5, 0.5)
        ax.axis('off')

        chart_title = title or budget.get('category', 'Budget')
        ax.set_title(f"{chart_title}\n{self._format_currency(spent)} / {self._format_currency(total)}",
                    fontsize=12, fontweight='bold')

        plt.tight_layout()
        return fig

    # ===== DAY OF WEEK CHARTS =====

    def create_day_of_week_chart(
        self,
        day_data: List[Dict],
        figsize: Tuple[int, int] = (10, 6),
        title: str = "Expenses by Day of Week"
    ) -> Figure:
        """
        Create bar chart of expenses by day of week.

        Args:
            day_data: List of dicts with 'day_name' and 'amount'
            figsize: Figure size tuple
            title: Chart title

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if not day_data:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        days = [d['day_name'] for d in day_data]
        amounts = [d['amount'] for d in day_data]

        # Color weekends differently
        colors = ['#3498db' if i < 5 else '#e74c3c' for i in range(len(days))]

        bars = ax.bar(days, amounts, color=colors)

        ax.set_ylabel(f'Amount ({CURRENCY_SYMBOL})')
        ax.set_xlabel('Day of Week')
        ax.set_title(title, fontsize=14, fontweight='bold')

        # Add value labels
        for bar, amount in zip(bars, amounts):
            height = bar.get_height()
            ax.annotate(self._format_currency(amount),
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3), textcoords="offset points",
                       ha='center', va='bottom', fontsize=9)

        ax.grid(True, axis='y', alpha=0.3)
        plt.tight_layout()
        return fig

    # ===== HEATMAP =====

    def create_expense_heatmap(
        self,
        expenses_df: pd.DataFrame,
        figsize: Tuple[int, int] = (12, 8),
        title: str = "Expense Heatmap"
    ) -> Figure:
        """
        Create heatmap of expenses by category and month.

        Args:
            expenses_df: DataFrame with expense data
            figsize: Figure size tuple
            title: Chart title

        Returns:
            Matplotlib Figure
        """
        fig, ax = plt.subplots(figsize=figsize)

        if expenses_df.empty:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center',
                   fontsize=14, color='gray')
            ax.set_title(title)
            return fig

        df = expenses_df.copy()
        df['month'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m')

        # Pivot for heatmap
        pivot = df.pivot_table(
            values='amount',
            index='category',
            columns='month',
            aggfunc='sum',
            fill_value=0
        )

        # Create heatmap
        sns.heatmap(pivot, annot=True, fmt=',.0f', cmap='YlOrRd',
                   ax=ax, cbar_kws={'label': f'Amount ({CURRENCY_SYMBOL})'})

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Category')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        return fig

    # ===== DASHBOARD SUMMARY =====

    def create_dashboard_summary(
        self,
        summary_data: Dict,
        figsize: Tuple[int, int] = (14, 10)
    ) -> Figure:
        """
        Create multi-panel dashboard summary.

        Args:
            summary_data: Dict with 'category_breakdown', 'monthly_trend',
                         'budget_status', 'top_vendors'
            figsize: Figure size tuple

        Returns:
            Matplotlib Figure with multiple subplots
        """
        fig = plt.figure(figsize=figsize)

        # Create 2x2 grid
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Category pie chart (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        category_data = summary_data.get('category_breakdown', [])
        if category_data:
            labels = [d['category'] for d in category_data]
            values = [d['amount'] for d in category_data]
            colors = [self._get_category_color(cat) for cat in labels]
            ax1.pie(values, labels=labels, colors=colors, autopct='%1.1f%%')
        ax1.set_title('Expenses by Category', fontweight='bold')

        # Monthly trend (top right)
        ax2 = fig.add_subplot(gs[0, 1])
        monthly_data = summary_data.get('monthly_trend', [])
        if monthly_data:
            months = [d.get('month_name', d.get('month', ''))[:3] for d in monthly_data]
            amounts = [d['amount'] for d in monthly_data]
            ax2.plot(range(len(months)), amounts, marker='o', color='#3498db')
            ax2.fill_between(range(len(months)), amounts, alpha=0.3, color='#3498db')
            ax2.set_xticks(range(len(months)))
            ax2.set_xticklabels(months, rotation=45)
        ax2.set_title('Monthly Trend', fontweight='bold')
        ax2.grid(True, alpha=0.3)

        # Budget status (bottom left)
        ax3 = fig.add_subplot(gs[1, 0])
        budget_data = summary_data.get('budget_status', [])
        if budget_data:
            categories = [d['category'] for d in budget_data]
            percentages = [min(d.get('used_percentage', 0), 100) for d in budget_data]
            colors = ['#e74c3c' if p >= 100 else '#f39c12' if p >= 80 else '#2ecc71'
                     for p in percentages]
            ax3.barh(categories, percentages, color=colors)
            ax3.axvline(x=100, color='red', linestyle='--', alpha=0.5)
            ax3.set_xlim(0, 120)
        ax3.set_title('Budget Status (%)', fontweight='bold')

        # Top vendors (bottom right)
        ax4 = fig.add_subplot(gs[1, 1])
        vendor_data = summary_data.get('top_vendors', [])[:5]
        if vendor_data:
            vendors = [d['vendor'][:15] for d in vendor_data]
            amounts = [d['amount'] for d in vendor_data]
            ax4.barh(vendors, amounts, color=sns.color_palette("Blues_r", len(vendors)))
            ax4.invert_yaxis()
        ax4.set_title('Top Vendors', fontweight='bold')

        fig.suptitle('Expense Dashboard', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        return fig

    # ===== UTILITY METHODS =====

    def save_figure(
        self,
        fig: Figure,
        filepath: str,
        dpi: int = 150,
        format: str = None
    ) -> bool:
        """
        Save figure to file.

        Args:
            fig: Matplotlib Figure
            filepath: Output file path
            dpi: Resolution
            format: Output format (auto-detect from extension if None)

        Returns:
            True on success
        """
        try:
            fig.savefig(filepath, dpi=dpi, format=format,
                       bbox_inches='tight', facecolor='white')
            return True
        except Exception as e:
            print(f"Error saving figure: {e}")
            return False

    def figure_to_bytes(
        self,
        fig: Figure,
        format: str = 'png',
        dpi: int = 150
    ) -> bytes:
        """
        Convert figure to bytes.

        Args:
            fig: Matplotlib Figure
            format: Output format
            dpi: Resolution

        Returns:
            Image bytes
        """
        buf = BytesIO()
        fig.savefig(buf, format=format, dpi=dpi,
                   bbox_inches='tight', facecolor='white')
        buf.seek(0)
        return buf.getvalue()

    def embed_in_tk(
        self,
        fig: Figure,
        master
    ) -> FigureCanvasTkAgg:
        """
        Embed matplotlib figure in Tkinter widget.

        Args:
            fig: Matplotlib Figure
            master: Tkinter parent widget

        Returns:
            FigureCanvasTkAgg instance
        """
        canvas = FigureCanvasTkAgg(fig, master=master)
        canvas.draw()
        return canvas

    def close_figure(self, fig: Figure) -> None:
        """Close figure to free memory."""
        plt.close(fig)

    def close_all_figures(self) -> None:
        """Close all open figures."""
        plt.close('all')


# Singleton instance
_visualizer: Optional[Visualizer] = None


def get_visualizer() -> Visualizer:
    """Get or create global Visualizer instance."""
    global _visualizer
    if _visualizer is None:
        _visualizer = Visualizer()
    return _visualizer
