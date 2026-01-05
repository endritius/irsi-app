"""
ChartsView - Visualization and charts display.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class ChartsView(ttk.Frame):
    """
    Charts view with various expense visualizations.
    """

    def __init__(self, parent, main_window):
        """
        Initialize ChartsView.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow
        """
        super().__init__(parent)
        self.main_window = main_window
        self.current_figure = None
        self.canvas = None
        self._create_widgets()
        self._show_category_pie()

    def _create_widgets(self):
        """Create view widgets."""
        # Chart type selector
        selector_frame = ttk.Frame(self)
        selector_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        ttk.Label(selector_frame, text="Chart Type:", style='Subheading.TLabel').pack(side=tk.LEFT)

        self.chart_type = tk.StringVar(value='category_pie')

        charts = [
            ('Category Pie', 'category_pie'),
            ('Category Bar', 'category_bar'),
            ('Monthly Trend', 'monthly_trend'),
            ('Budget Status', 'budget_status'),
            ('Top Vendors', 'vendors'),
            ('Day of Week', 'day_of_week'),
            ('Dashboard', 'dashboard')
        ]

        for text, value in charts:
            rb = ttk.Radiobutton(
                selector_frame,
                text=text,
                variable=self.chart_type,
                value=value,
                command=self._on_chart_change
            )
            rb.pack(side=tk.LEFT, padx=PADDING['small'])

        # Save button
        save_btn = ttk.Button(
            selector_frame,
            text="Save Image",
            command=self._save_chart
        )
        save_btn.pack(side=tk.RIGHT)

        # Chart container
        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill=tk.BOTH, expand=True)

    def _clear_chart(self):
        """Clear current chart."""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None

        if self.current_figure:
            self.main_window.visualizer.close_figure(self.current_figure)
            self.current_figure = None

    def _show_chart(self, fig):
        """Display a matplotlib figure."""
        self._clear_chart()

        self.current_figure = fig
        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _on_chart_change(self):
        """Handle chart type change."""
        chart_type = self.chart_type.get()

        if chart_type == 'category_pie':
            self._show_category_pie()
        elif chart_type == 'category_bar':
            self._show_category_bar()
        elif chart_type == 'monthly_trend':
            self._show_monthly_trend()
        elif chart_type == 'budget_status':
            self._show_budget_status()
        elif chart_type == 'vendors':
            self._show_top_vendors()
        elif chart_type == 'day_of_week':
            self._show_day_of_week()
        elif chart_type == 'dashboard':
            self._show_dashboard()

    def _show_category_pie(self):
        """Show category pie chart."""
        expenses = self.main_window.expense_manager.get_all_expenses()
        category_data = self.main_window.report_generator.get_category_breakdown(expenses)

        fig = self.main_window.visualizer.create_category_pie_chart(
            category_data,
            title="Expenses by Category"
        )
        self._show_chart(fig)

    def _show_category_bar(self):
        """Show category bar chart."""
        expenses = self.main_window.expense_manager.get_all_expenses()
        category_data = self.main_window.report_generator.get_category_breakdown(expenses)

        fig = self.main_window.visualizer.create_category_bar_chart(
            category_data,
            title="Expenses by Category",
            horizontal=True
        )
        self._show_chart(fig)

    def _show_monthly_trend(self):
        """Show monthly trend chart."""
        expenses = self.main_window.expense_manager.get_all_expenses()
        monthly_data = self.main_window.report_generator.get_monthly_trend(expenses, 12)

        fig = self.main_window.visualizer.create_monthly_trend_chart(
            monthly_data,
            title="Monthly Expense Trend"
        )
        self._show_chart(fig)

    def _show_budget_status(self):
        """Show budget comparison chart."""
        expenses = self.main_window.expense_manager.get_all_expenses()
        budgets = self.main_window.budget_manager.get_active_budgets()

        # Update spent amounts
        self.main_window.budget_manager.update_all_budgets_spent(expenses)

        budget_data = []
        for budget in budgets:
            budget_data.append({
                'category': budget.category,
                'budget': budget.amount,
                'actual': budget.spent
            })

        if budget_data:
            fig = self.main_window.visualizer.create_budget_comparison_chart(
                budget_data,
                title="Budget vs Actual Spending"
            )
            self._show_chart(fig)
        else:
            self._show_no_data_message("No active budgets to display")

    def _show_top_vendors(self):
        """Show top vendors chart."""
        expenses = self.main_window.expense_manager.get_all_expenses()
        vendor_data = self.main_window.report_generator.get_top_vendors(expenses, 10)

        if vendor_data:
            fig = self.main_window.visualizer.create_vendor_bar_chart(
                vendor_data,
                title="Top 10 Vendors by Spending"
            )
            self._show_chart(fig)
        else:
            self._show_no_data_message("No vendor data to display")

    def _show_day_of_week(self):
        """Show day of week analysis chart."""
        expenses = self.main_window.expense_manager.get_all_expenses()
        day_data = self.main_window.report_generator.get_day_of_week_analysis(expenses)

        if day_data:
            fig = self.main_window.visualizer.create_day_of_week_chart(
                day_data,
                title="Expenses by Day of Week"
            )
            self._show_chart(fig)
        else:
            self._show_no_data_message("No data to display")

    def _show_dashboard(self):
        """Show full dashboard summary."""
        expenses = self.main_window.expense_manager.get_all_expenses()
        budgets = self.main_window.budget_manager.get_active_budgets()

        # Update budget spent amounts
        self.main_window.budget_manager.update_all_budgets_spent(expenses)

        summary_data = {
            'category_breakdown': self.main_window.report_generator.get_category_breakdown(expenses),
            'monthly_trend': self.main_window.report_generator.get_monthly_trend(expenses, 6),
            'budget_status': [
                {'category': b.category, 'budget': b.amount, 'actual': b.spent,
                 'used_percentage': b.get_used_percentage()}
                for b in budgets
            ],
            'top_vendors': self.main_window.report_generator.get_top_vendors(expenses, 5)
        }

        fig = self.main_window.visualizer.create_dashboard_summary(summary_data)
        self._show_chart(fig)

    def _show_no_data_message(self, message):
        """Show no data message."""
        self._clear_chart()

        label = ttk.Label(
            self.chart_frame,
            text=message,
            style='Muted.TLabel',
            font=FONTS['heading']
        )
        label.pack(expand=True)

    def _save_chart(self):
        """Save current chart to file."""
        if not self.current_figure:
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("PDF files", "*.pdf"),
                ("SVG files", "*.svg")
            ]
        )

        if filepath:
            self.main_window.visualizer.save_figure(
                self.current_figure,
                filepath,
                dpi=150
            )
            self.main_window.set_status(f"Chart saved to {filepath}")

    def refresh(self):
        """Refresh current chart."""
        self._on_chart_change()

    def destroy(self):
        """Clean up before destroying."""
        self._clear_chart()
        super().destroy()
