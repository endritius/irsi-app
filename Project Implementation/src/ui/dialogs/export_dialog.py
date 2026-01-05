"""
ExportDialog - Dialog for exporting expense data.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING
from config import CATEGORIES


class ExportDialog(tk.Toplevel):
    """
    Dialog for exporting expenses to various formats.
    """

    def __init__(self, parent, main_window):
        """
        Initialize ExportDialog.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow
        """
        super().__init__(parent)
        self.main_window = main_window
        self.result = None

        self.title("Export Data")
        self.geometry("500x650")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self.wait_window()

    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self, padding=PADDING['large'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Export type
        type_frame = ttk.LabelFrame(main_frame, text="Export Type")
        type_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        self.export_type = tk.StringVar(value='expenses')

        types = [
            ('All Expenses', 'expenses'),
            ('Monthly Report', 'monthly'),
            ('Annual Report', 'annual'),
            ('Category Summary', 'category'),
            ('Budget Report', 'budget'),
            ('Charts Only', 'charts')
        ]

        for text, value in types:
            rb = ttk.Radiobutton(
                type_frame,
                text=text,
                variable=self.export_type,
                value=value,
                command=self._on_type_change
            )
            rb.pack(anchor='w', padx=PADDING['medium'], pady=2)

        # Date range
        date_frame = ttk.LabelFrame(main_frame, text="Date Range")
        date_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        self.date_range = tk.StringVar(value='all')

        ranges = [
            ('All Time', 'all'),
            ('This Month', 'month'),
            ('This Year', 'year'),
            ('Custom Range', 'custom')
        ]

        for text, value in ranges:
            rb = ttk.Radiobutton(
                date_frame,
                text=text,
                variable=self.date_range,
                value=value,
                command=self._on_range_change
            )
            rb.pack(anchor='w', padx=PADDING['medium'], pady=2)

        # Custom date inputs
        self.custom_frame = ttk.Frame(date_frame)
        self.custom_frame.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(self.custom_frame, text="From:").pack(side=tk.LEFT)
        self.start_date_var = tk.StringVar(value=datetime.now().replace(day=1).strftime('%d/%m/%Y'))
        self.start_entry = ttk.Entry(self.custom_frame, textvariable=self.start_date_var, width=12)
        self.start_entry.pack(side=tk.LEFT, padx=PADDING['small'])

        ttk.Label(self.custom_frame, text="To:").pack(side=tk.LEFT, padx=(PADDING['medium'], 0))
        self.end_date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.end_entry = ttk.Entry(self.custom_frame, textvariable=self.end_date_var, width=12)
        self.end_entry.pack(side=tk.LEFT, padx=PADDING['small'])

        self.custom_frame.pack_forget()  # Initially hidden

        # Category filter
        category_frame = ttk.LabelFrame(main_frame, text="Filter by Category")
        category_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        self.all_categories_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            category_frame,
            text="Include all categories",
            variable=self.all_categories_var,
            command=self._toggle_categories
        ).pack(anchor='w', padx=PADDING['medium'], pady=PADDING['small'])

        self.categories_frame = ttk.Frame(category_frame)
        self.categories_frame.pack(fill=tk.X, padx=PADDING['medium'])

        self.category_vars = {}
        for i, category in enumerate(CATEGORIES.keys()):
            var = tk.BooleanVar(value=True)
            self.category_vars[category] = var
            cb = ttk.Checkbutton(
                self.categories_frame,
                text=category,
                variable=var
            )
            cb.grid(row=i // 2, column=i % 2, sticky='w', padx=PADDING['small'])

        self.categories_frame.pack_forget()  # Initially hidden

        # Export format
        format_frame = ttk.LabelFrame(main_frame, text="Export Format")
        format_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        self.export_format = tk.StringVar(value='pdf')

        formats = [
            ('PDF Document', 'pdf'),
            ('Excel Spreadsheet', 'xlsx'),
            ('CSV File', 'csv'),
            ('Image (PNG)', 'png')
        ]

        format_row = ttk.Frame(format_frame)
        format_row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        for text, value in formats:
            rb = ttk.Radiobutton(
                format_row,
                text=text,
                variable=self.export_format,
                value=value
            )
            rb.pack(side=tk.LEFT, padx=PADDING['small'])

        # Options
        options_frame = ttk.LabelFrame(main_frame, text="Options")
        options_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        self.include_charts_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Include charts and visualizations",
            variable=self.include_charts_var
        ).pack(anchor='w', padx=PADDING['medium'], pady=2)

        self.include_summary_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Include summary statistics",
            variable=self.include_summary_var
        ).pack(anchor='w', padx=PADDING['medium'], pady=2)

        self.group_by_category_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Group expenses by category",
            variable=self.group_by_category_var
        ).pack(anchor='w', padx=PADDING['medium'], pady=2)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=PADDING['medium'])

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side=tk.RIGHT)

        ttk.Button(
            btn_frame,
            text="Export",
            command=self._export,
            style='Primary.TButton'
        ).pack(side=tk.RIGHT, padx=PADDING['small'])

    def _on_type_change(self):
        """Handle export type change."""
        export_type = self.export_type.get()

        # Update format options based on type
        if export_type == 'charts':
            self.export_format.set('png')
        elif export_type in ('monthly', 'annual', 'budget'):
            if self.export_format.get() == 'csv':
                self.export_format.set('pdf')

    def _on_range_change(self):
        """Handle date range change."""
        if self.date_range.get() == 'custom':
            self.custom_frame.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])
        else:
            self.custom_frame.pack_forget()

    def _toggle_categories(self):
        """Toggle category selection visibility."""
        if self.all_categories_var.get():
            self.categories_frame.pack_forget()
            for var in self.category_vars.values():
                var.set(True)
        else:
            self.categories_frame.pack(fill=tk.X, padx=PADDING['medium'])

    def _get_date_range(self):
        """Get selected date range."""
        range_type = self.date_range.get()
        now = datetime.now()

        if range_type == 'all':
            return None, None
        elif range_type == 'month':
            start = now.replace(day=1)
            return start, now
        elif range_type == 'year':
            start = now.replace(month=1, day=1)
            return start, now
        else:
            try:
                start = datetime.strptime(self.start_date_var.get(), '%d/%m/%Y')
                end = datetime.strptime(self.end_date_var.get(), '%d/%m/%Y')
                return start, end
            except ValueError:
                raise ValueError("Invalid date format. Use DD/MM/YYYY")

    def _get_selected_categories(self):
        """Get list of selected categories."""
        if self.all_categories_var.get():
            return None
        return [cat for cat, var in self.category_vars.items() if var.get()]

    def _export(self):
        """Perform export."""
        try:
            export_type = self.export_type.get()
            export_format = self.export_format.get()

            # Get file extension
            extensions = {
                'pdf': '.pdf',
                'xlsx': '.xlsx',
                'csv': '.csv',
                'png': '.png'
            }

            # Ask for save location
            filepath = filedialog.asksaveasfilename(
                defaultextension=extensions[export_format],
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("Excel files", "*.xlsx"),
                    ("CSV files", "*.csv"),
                    ("PNG files", "*.png")
                ],
                initialfile=f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extensions[export_format]}"
            )

            if not filepath:
                return

            # Get date range
            start_date, end_date = self._get_date_range()

            # Get categories
            categories = self._get_selected_categories()

            # Get expenses
            expenses = self.main_window.expense_manager.get_all_expenses()

            # Filter by date
            if start_date:
                expenses = [e for e in expenses if e.date >= start_date]
            if end_date:
                expenses = [e for e in expenses if e.date <= end_date]

            # Filter by category
            if categories:
                expenses = [e for e in expenses if e.category in categories]

            # Export based on type and format
            if export_format == 'pdf':
                self._export_pdf(filepath, export_type, expenses)
            elif export_format == 'xlsx':
                self._export_excel(filepath, export_type, expenses)
            elif export_format == 'csv':
                self._export_csv(filepath, expenses)
            elif export_format == 'png':
                self._export_image(filepath, export_type, expenses)

            self.main_window.set_status(f"Exported to {filepath}")
            messagebox.showinfo("Success", f"Data exported successfully to:\n{filepath}")
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")

    def _export_pdf(self, filepath, export_type, expenses):
        """Export to PDF."""
        from exports import get_pdf_exporter
        exporter = get_pdf_exporter()

        budgets = self.main_window.budget_manager.get_active_budgets()

        if export_type == 'expenses':
            expense_dicts = [e.to_dict() for e in expenses]
            exporter.export_expense_list(expense_dicts, filepath, "Expense Report")
        elif export_type == 'monthly':
            report = self.main_window.report_generator.generate_monthly_report(expenses, budgets)
            exporter.export_monthly_report(report, filepath)
        elif export_type == 'annual':
            report = self.main_window.report_generator.generate_annual_report(expenses, budgets)
            exporter.export_annual_report(report, filepath)
        elif export_type == 'budget':
            budget_data = [b.to_dict() for b in budgets]
            exporter.export_budget_report(budget_data, filepath)
        else:
            expense_dicts = [e.to_dict() for e in expenses]
            exporter.export_expense_list(expense_dicts, filepath, f"{export_type.title()} Report")

    def _export_excel(self, filepath, export_type, expenses):
        """Export to Excel."""
        from exports import get_excel_exporter
        exporter = get_excel_exporter()

        budgets = self.main_window.budget_manager.get_active_budgets()

        if export_type == 'expenses':
            expense_dicts = [e.to_dict() for e in expenses]
            exporter.export_expenses(expense_dicts, filepath)
        elif export_type == 'monthly':
            report = self.main_window.report_generator.generate_monthly_report(expenses, budgets)
            exporter.export_monthly_report(report, filepath)
        elif export_type == 'annual':
            report = self.main_window.report_generator.generate_annual_report(expenses, budgets)
            exporter.export_annual_report(report, filepath)
        else:
            expense_dicts = [e.to_dict() for e in expenses]
            exporter.export_expenses(expense_dicts, filepath)

    def _export_csv(self, filepath, expenses):
        """Export to CSV."""
        import csv

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Date', 'Amount', 'Category', 'Subcategory', 'Vendor',
                'Payment Method', 'Description', 'Tags', 'Is Recurring'
            ])

            # Data
            for expense in expenses:
                writer.writerow([
                    expense.date.strftime('%d/%m/%Y'),
                    expense.amount,
                    expense.category,
                    expense.subcategory,
                    expense.vendor,
                    expense.payment_method,
                    expense.description,
                    ', '.join(expense.tags) if expense.tags else '',
                    'Yes' if expense.is_recurring else 'No'
                ])

    def _export_image(self, filepath, export_type, expenses):
        """Export charts to image."""
        from exports import get_image_exporter
        exporter = get_image_exporter()

        budgets = self.main_window.budget_manager.get_active_budgets()

        if export_type == 'charts':
            # Export all chart types
            base_path = Path(filepath)
            output_dir = base_path.parent / base_path.stem
            exporter.export_all_charts(
                expenses,
                [b.to_dict() for b in budgets],
                str(output_dir)
            )
        else:
            # Export category pie chart
            category_data = self.main_window.report_generator.get_category_breakdown(expenses)
            exporter.export_category_pie_chart(category_data, filepath)
