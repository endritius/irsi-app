"""
ReportsView - Statistical reports and analytics display.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING
from utils.formatters import format_currency


class ReportsView(ttk.Frame):
    """
    Reports view with statistical summaries and export options.
    """

    def __init__(self, parent, main_window):
        """
        Initialize ReportsView.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow
        """
        super().__init__(parent)
        self.main_window = main_window
        self._create_widgets()
        self._generate_monthly_report()

    def _create_widgets(self):
        """Create view widgets."""
        # Report type selector
        selector_frame = ttk.Frame(self)
        selector_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        ttk.Label(selector_frame, text="Report Type:", style='Subheading.TLabel').pack(side=tk.LEFT)

        self.report_type = tk.StringVar(value='monthly')
        reports = [
            ('Monthly Summary', 'monthly'),
            ('Annual Summary', 'annual'),
            ('Category Analysis', 'category'),
            ('Vendor Analysis', 'vendor'),
            ('Trend Analysis', 'trend')
        ]

        for text, value in reports:
            rb = ttk.Radiobutton(
                selector_frame,
                text=text,
                variable=self.report_type,
                value=value,
                command=self._on_report_change
            )
            rb.pack(side=tk.LEFT, padx=PADDING['small'])

        # Export button
        export_btn = ttk.Button(
            selector_frame,
            text="Export Report",
            command=self._export_report
        )
        export_btn.pack(side=tk.RIGHT)

        # Period selector
        period_frame = ttk.Frame(self)
        period_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        ttk.Label(period_frame, text="Period:").pack(side=tk.LEFT)

        now = datetime.now()
        months = [(now.replace(month=i if i <= 12 else i-12, year=now.year if i <= 12 else now.year-1).strftime('%B %Y'), i)
                  for i in range(now.month, now.month-12, -1)]
        month_names = [m[0] for m in months]

        self.period_var = tk.StringVar(value=month_names[0])
        period_combo = ttk.Combobox(
            period_frame,
            textvariable=self.period_var,
            values=month_names,
            state='readonly',
            width=15
        )
        period_combo.pack(side=tk.LEFT, padx=PADDING['small'])
        period_combo.bind('<<ComboboxSelected>>', lambda e: self._on_report_change())

        # Report content area
        content_frame = ttk.Frame(self)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Create scrollable text area for report
        self.report_text = tk.Text(
            content_frame,
            font=FONTS['monospace'],
            wrap=tk.WORD,
            padx=PADDING['medium'],
            pady=PADDING['medium'],
            state='disabled'
        )

        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)

        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure text tags
        self.report_text.tag_configure('title', font=FONTS['heading'], foreground=COLORS['primary'])
        self.report_text.tag_configure('section', font=FONTS['subheading'], foreground=COLORS['text'])
        self.report_text.tag_configure('highlight', foreground=COLORS['primary'])
        self.report_text.tag_configure('warning', foreground=COLORS['warning'])
        self.report_text.tag_configure('danger', foreground=COLORS['danger'])

    def _on_report_change(self):
        """Handle report type change."""
        report_type = self.report_type.get()

        if report_type == 'monthly':
            self._generate_monthly_report()
        elif report_type == 'annual':
            self._generate_annual_report()
        elif report_type == 'category':
            self._generate_category_report()
        elif report_type == 'vendor':
            self._generate_vendor_report()
        elif report_type == 'trend':
            self._generate_trend_report()

    def _clear_report(self):
        """Clear report content."""
        self.report_text.config(state='normal')
        self.report_text.delete('1.0', tk.END)

    def _add_text(self, text, tag=None):
        """Add text to report."""
        self.report_text.insert(tk.END, text, tag)

    def _finalize_report(self):
        """Finalize report (make read-only)."""
        self.report_text.config(state='disabled')

    def _generate_monthly_report(self):
        """Generate monthly summary report."""
        self._clear_report()

        expenses = self.main_window.expense_manager.get_all_expenses()
        budgets = self.main_window.budget_manager.get_active_budgets()

        report = self.main_window.report_generator.generate_monthly_report(
            expenses, budgets
        )

        # Title
        period = report.get('period', {})
        self._add_text(f"Monthly Report - {period.get('month', 'Unknown')}\n", 'title')
        self._add_text("=" * 50 + "\n\n")

        # Summary
        summary = report.get('summary', {})
        self._add_text("SUMMARY\n", 'section')
        self._add_text("-" * 30 + "\n")
        self._add_text(f"Total Expenses:      {format_currency(summary.get('total_amount', 0))}\n")
        self._add_text(f"Number of Expenses:  {summary.get('expense_count', 0)}\n")
        self._add_text(f"Average Expense:     {format_currency(summary.get('average_amount', 0))}\n")
        self._add_text(f"Highest Expense:     {format_currency(summary.get('max_amount', 0))}\n")
        self._add_text(f"Lowest Expense:      {format_currency(summary.get('min_amount', 0))}\n\n")

        # Category breakdown
        self._add_text("BY CATEGORY\n", 'section')
        self._add_text("-" * 30 + "\n")
        for cat in report.get('by_category', []):
            pct = cat.get('percentage', 0)
            self._add_text(f"{cat.get('category', ''):20} {format_currency(cat.get('amount', 0)):>12} ({pct:5.1f}%)\n")
        self._add_text("\n")

        # Top vendors
        self._add_text("TOP VENDORS\n", 'section')
        self._add_text("-" * 30 + "\n")
        for vendor in report.get('by_vendor', [])[:10]:
            self._add_text(f"{vendor.get('vendor', ''):20} {format_currency(vendor.get('amount', 0)):>12}\n")
        self._add_text("\n")

        # Budget status
        if report.get('budget_status'):
            self._add_text("BUDGET STATUS\n", 'section')
            self._add_text("-" * 30 + "\n")
            for b in report.get('budget_status', []):
                pct = b.get('used_percentage', 0)
                status_tag = 'danger' if pct >= 100 else 'warning' if pct >= 80 else None
                self._add_text(f"{b.get('category', ''):15} ", None)
                self._add_text(f"{pct:5.1f}% used\n", status_tag)

        self._finalize_report()

    def _generate_annual_report(self):
        """Generate annual summary report."""
        self._clear_report()

        expenses = self.main_window.expense_manager.get_all_expenses()
        budgets = self.main_window.budget_manager.get_all_budgets()

        report = self.main_window.report_generator.generate_annual_report(
            expenses, budgets
        )

        # Title
        period = report.get('period', {})
        self._add_text(f"Annual Report - {period.get('year', datetime.now().year)}\n", 'title')
        self._add_text("=" * 50 + "\n\n")

        # Summary
        summary = report.get('summary', {})
        self._add_text("ANNUAL SUMMARY\n", 'section')
        self._add_text("-" * 30 + "\n")
        self._add_text(f"Total Expenses:      {format_currency(summary.get('total_amount', 0))}\n")
        self._add_text(f"Number of Expenses:  {summary.get('expense_count', 0)}\n")
        self._add_text(f"Monthly Average:     {format_currency(summary.get('total_amount', 0) / 12)}\n")
        self._add_text(f"Est. Monthly Recurring: {format_currency(report.get('estimated_monthly_recurring', 0))}\n\n")

        # Monthly trend
        self._add_text("MONTHLY TREND\n", 'section')
        self._add_text("-" * 30 + "\n")
        for m in report.get('monthly_trend', []):
            month_name = m.get('month_name', m.get('month', ''))[:10]
            self._add_text(f"{month_name:12} {format_currency(m.get('amount', 0)):>12}\n")

        self._finalize_report()

    def _generate_category_report(self):
        """Generate category analysis report."""
        self._clear_report()

        expenses = self.main_window.expense_manager.get_all_expenses()

        categories = self.main_window.report_generator.get_category_breakdown(expenses)
        subcategories = self.main_window.report_generator.get_subcategory_breakdown(expenses)

        self._add_text("Category Analysis Report\n", 'title')
        self._add_text("=" * 50 + "\n\n")

        self._add_text("BY CATEGORY\n", 'section')
        self._add_text("-" * 40 + "\n")
        self._add_text(f"{'Category':<20} {'Amount':>12} {'Count':>8} {'%':>8}\n")
        self._add_text("-" * 40 + "\n")

        for cat in categories:
            self._add_text(
                f"{cat.get('category', ''):<20} "
                f"{format_currency(cat.get('amount', 0)):>12} "
                f"{cat.get('count', 0):>8} "
                f"{cat.get('percentage', 0):>7.1f}%\n"
            )

        self._add_text("\n")
        self._add_text("BY SUBCATEGORY\n", 'section')
        self._add_text("-" * 50 + "\n")

        for sub in subcategories[:20]:
            self._add_text(
                f"{sub.get('category', ''):<15} / {sub.get('subcategory', ''):<15} "
                f"{format_currency(sub.get('amount', 0)):>12}\n"
            )

        self._finalize_report()

    def _generate_vendor_report(self):
        """Generate vendor analysis report."""
        self._clear_report()

        expenses = self.main_window.expense_manager.get_all_expenses()
        vendors = self.main_window.report_generator.get_top_vendors(expenses, 25)

        self._add_text("Vendor Analysis Report\n", 'title')
        self._add_text("=" * 50 + "\n\n")

        self._add_text("TOP 25 VENDORS\n", 'section')
        self._add_text("-" * 50 + "\n")
        self._add_text(f"{'Vendor':<25} {'Amount':>12} {'Count':>8} {'Avg':>10}\n")
        self._add_text("-" * 50 + "\n")

        for v in vendors:
            self._add_text(
                f"{v.get('vendor', '')[:25]:<25} "
                f"{format_currency(v.get('amount', 0)):>12} "
                f"{v.get('count', 0):>8} "
                f"{format_currency(v.get('average', 0)):>10}\n"
            )

        self._finalize_report()

    def _generate_trend_report(self):
        """Generate trend analysis report."""
        self._clear_report()

        expenses = self.main_window.expense_manager.get_all_expenses()

        monthly = self.main_window.report_generator.get_monthly_trend(expenses, 12)
        day_of_week = self.main_window.report_generator.get_day_of_week_analysis(expenses)

        self._add_text("Trend Analysis Report\n", 'title')
        self._add_text("=" * 50 + "\n\n")

        self._add_text("MONTHLY TREND (Last 12 Months)\n", 'section')
        self._add_text("-" * 40 + "\n")

        for m in monthly:
            month = m.get('month_name', m.get('month', ''))
            amount = m.get('amount', 0)
            bar_len = int(amount / max(1, max(x.get('amount', 0) for x in monthly)) * 20)
            bar = "█" * bar_len

            self._add_text(f"{month[:12]:12} {format_currency(amount):>12} {bar}\n")

        self._add_text("\n")
        self._add_text("BY DAY OF WEEK\n", 'section')
        self._add_text("-" * 40 + "\n")

        for d in day_of_week:
            day = d.get('day_name', '')
            amount = d.get('amount', 0)
            count = d.get('count', 0)
            self._add_text(f"{day:<12} {format_currency(amount):>12} ({count} expenses)\n")

        self._finalize_report()

    def _export_report(self):
        """Export current report to file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[
                ("PDF files", "*.pdf"),
                ("Excel files", "*.xlsx"),
                ("Text files", "*.txt")
            ]
        )

        if not filepath:
            return

        expenses = self.main_window.expense_manager.get_all_expenses()
        budgets = self.main_window.budget_manager.get_active_budgets()

        report_type = self.report_type.get()

        if filepath.endswith('.pdf'):
            from exports import get_pdf_exporter
            exporter = get_pdf_exporter()

            if report_type == 'monthly':
                report = self.main_window.report_generator.generate_monthly_report(expenses, budgets)
                exporter.export_monthly_report(report, filepath)
            elif report_type == 'annual':
                report = self.main_window.report_generator.generate_annual_report(expenses, budgets)
                exporter.export_annual_report(report, filepath)
            else:
                # Export expense list for other report types
                expense_dicts = [e.to_dict() for e in expenses]
                exporter.export_expense_list(expense_dicts, filepath, f"{report_type.title()} Report")

        elif filepath.endswith('.xlsx'):
            from exports import get_excel_exporter
            if report_type == 'monthly':
                report = self.main_window.report_generator.generate_monthly_report(expenses, budgets)
                get_excel_exporter().export_monthly_report(report, filepath)
            elif report_type == 'annual':
                report = self.main_window.report_generator.generate_annual_report(expenses, budgets)
                get_excel_exporter().export_annual_report(report, filepath)
            else:
                expense_dicts = [e.to_dict() for e in expenses]
                get_excel_exporter().export_expenses(expense_dicts, filepath)

        else:
            # Text export
            with open(filepath, 'w') as f:
                f.write(self.report_text.get('1.0', tk.END))

        self.main_window.set_status(f"Report exported to {filepath}")

    def refresh(self):
        """Refresh current report."""
        self._on_report_change()
