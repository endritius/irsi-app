"""
ExpenseListView - Displays list of expenses with filtering and sorting.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING
from utils.formatters import format_currency, format_date
from models import FilterCriteria
from config import CATEGORIES, PAYMENT_METHODS


class ExpenseListView(ttk.Frame):
    """
    Expense list view with filtering, sorting, and CRUD operations.
    """

    def __init__(self, parent, main_window):
        """
        Initialize ExpenseListView.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow
        """
        super().__init__(parent)
        self.main_window = main_window
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        """Create view widgets."""
        # Filter bar
        self._create_filter_bar()

        # Action buttons
        self._create_action_bar()

        # Expense list
        self._create_expense_list()

        # Summary bar
        self._create_summary_bar()

    def _create_filter_bar(self):
        """Create filter controls."""
        filter_frame = ttk.LabelFrame(self, text="Filters")
        filter_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        # Row 1: Date range and quick filters
        row1 = ttk.Frame(filter_frame)
        row1.pack(fill=tk.X, padx=PADDING['small'], pady=PADDING['small'])

        # Quick filter buttons
        ttk.Label(row1, text="Quick:").pack(side=tk.LEFT, padx=(0, 5))

        quick_filters = [
            ("Today", "today"),
            ("This Week", "this_week"),
            ("This Month", "this_month"),
            ("Last Month", "last_month"),
            ("All", "all")
        ]

        for text, key in quick_filters:
            btn = ttk.Button(
                row1,
                text=text,
                command=lambda k=key: self._apply_quick_filter(k)
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Row 2: Category and search
        row2 = ttk.Frame(filter_frame)
        row2.pack(fill=tk.X, padx=PADDING['small'], pady=PADDING['small'])

        # Category filter
        ttk.Label(row2, text="Category:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(
            row2,
            textvariable=self.category_var,
            values=["All"] + list(CATEGORIES.keys()),
            width=15,
            state='readonly'
        )
        category_combo.pack(side=tk.LEFT, padx=(0, 15))
        category_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_filters())

        # Payment method filter
        ttk.Label(row2, text="Payment:").pack(side=tk.LEFT, padx=(0, 5))
        self.payment_var = tk.StringVar(value="All")
        payment_combo = ttk.Combobox(
            row2,
            textvariable=self.payment_var,
            values=["All"] + PAYMENT_METHODS,
            width=12,
            state='readonly'
        )
        payment_combo.pack(side=tk.LEFT, padx=(0, 15))
        payment_combo.bind('<<ComboboxSelected>>', lambda e: self._apply_filters())

        # Search box
        ttk.Label(row2, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(row2, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT)
        search_entry.bind('<Return>', lambda e: self._apply_filters())

        search_btn = ttk.Button(row2, text="Search", command=self._apply_filters)
        search_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(row2, text="Clear", command=self._clear_filters)
        clear_btn.pack(side=tk.LEFT)

    def _create_action_bar(self):
        """Create action buttons bar."""
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, pady=(0, PADDING['small']))

        # Add button
        add_btn = ttk.Button(
            action_frame,
            text="+ Add Expense",
            command=self.main_window._show_add_expense,
            style='Primary.TButton'
        )
        add_btn.pack(side=tk.LEFT)

        # Delete button
        self.delete_btn = ttk.Button(
            action_frame,
            text="Delete Selected",
            command=self._delete_selected,
            style='Danger.TButton'
        )
        self.delete_btn.pack(side=tk.LEFT, padx=PADDING['small'])

        # Export button
        export_btn = ttk.Button(
            action_frame,
            text="Export",
            command=self._export_current
        )
        export_btn.pack(side=tk.RIGHT)

        # Refresh button
        refresh_btn = ttk.Button(
            action_frame,
            text="Refresh",
            command=self.refresh
        )
        refresh_btn.pack(side=tk.RIGHT, padx=PADDING['small'])

    def _create_expense_list(self):
        """Create expense treeview list."""
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview
        columns = ('date', 'vendor', 'category', 'subcategory', 'description', 'amount', 'payment')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            selectmode='extended'
        )

        # Column headings
        headings = {
            'date': ('Date', 90),
            'vendor': ('Vendor', 150),
            'category': ('Category', 100),
            'subcategory': ('Subcategory', 100),
            'description': ('Description', 200),
            'amount': ('Amount', 100),
            'payment': ('Payment', 100)
        }

        for col, (text, width) in headings.items():
            self.tree.heading(col, text=text, command=lambda c=col: self._sort_by(c))
            anchor = 'e' if col == 'amount' else 'w'
            self.tree.column(col, width=width, anchor=anchor)

        # Scrollbars
        v_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        # Bindings
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Delete>', lambda e: self._delete_selected())
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_change)

        # Context menu
        self._create_context_menu()

        # Sort state
        self._sort_column = 'date'
        self._sort_reverse = True

    def _create_context_menu(self):
        """Create right-click context menu."""
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self._edit_selected)
        self.context_menu.add_command(label="Duplicate", command=self._duplicate_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Create Template", command=self._create_template)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self._delete_selected)

        self.tree.bind('<Button-3>', self._show_context_menu)

    def _create_summary_bar(self):
        """Create summary bar at bottom."""
        summary_frame = tk.Frame(self, bg=COLORS['light'], height=35)
        summary_frame.pack(fill=tk.X, pady=(PADDING['small'], 0))

        self.summary_label = tk.Label(
            summary_frame,
            text="",
            font=FONTS['body_bold'],
            bg=COLORS['light'],
            fg=COLORS['text']
        )
        self.summary_label.pack(side=tk.LEFT, padx=PADDING['medium'], pady=5)

        self.total_label = tk.Label(
            summary_frame,
            text="",
            font=FONTS['body_bold'],
            bg=COLORS['light'],
            fg=COLORS['primary']
        )
        self.total_label.pack(side=tk.RIGHT, padx=PADDING['medium'], pady=5)

    def refresh(self):
        """Refresh expense list."""
        self._apply_filters()

    def _apply_filters(self):
        """Apply current filters and refresh list."""
        # Build filter criteria
        criteria = FilterCriteria()

        # Category
        if self.category_var.get() != "All":
            criteria.categories = [self.category_var.get()]

        # Payment method
        if self.payment_var.get() != "All":
            criteria.payment_methods = [self.payment_var.get()]

        # Search text
        if self.search_var.get():
            criteria.search_text = self.search_var.get()

        # Get expenses and filter
        df = self.main_window.expense_manager.get_expenses_dataframe()
        filtered_df = self.main_window.filter_manager.apply_filter(df, criteria)

        # Sort
        if self._sort_column:
            filtered_df = self.main_window.filter_manager.sort_dataframe(
                filtered_df, self._sort_column, not self._sort_reverse
            )

        # Update tree
        self._populate_tree(filtered_df)

    def _apply_quick_filter(self, filter_name: str):
        """Apply a quick date filter."""
        if filter_name == "all":
            self._clear_filters()
            return

        criteria = self.main_window.filter_manager.get_quick_filter(filter_name)

        # Get and filter expenses
        df = self.main_window.expense_manager.get_expenses_dataframe()
        filtered_df = self.main_window.filter_manager.apply_filter(df, criteria)

        # Sort
        filtered_df = self.main_window.filter_manager.sort_dataframe(
            filtered_df, 'date', ascending=False
        )

        self._populate_tree(filtered_df)

    def _clear_filters(self):
        """Clear all filters."""
        self.category_var.set("All")
        self.payment_var.set("All")
        self.search_var.set("")
        self._apply_filters()

    def _populate_tree(self, df):
        """Populate tree with expense data."""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add rows
        total = 0
        for _, row in df.iterrows():
            date_val = row.get('date', '')
            if hasattr(date_val, 'strftime'):
                date_str = date_val.strftime('%d/%m/%Y')
            else:
                date_str = str(date_val)

            amount = float(row.get('amount', 0))
            total += amount

            self.tree.insert('', 'end', iid=row.get('expense_id', ''), values=(
                date_str,
                row.get('vendor', ''),
                row.get('category', ''),
                row.get('subcategory', ''),
                row.get('description', '') or '-',
                format_currency(amount),
                row.get('payment_method', '')
            ))

        # Update summary
        count = len(df)
        self.summary_label.config(text=f"{count} expense(s)")
        self.total_label.config(text=f"Total: {format_currency(total)}")

    def _sort_by(self, column: str):
        """Sort list by column."""
        if self._sort_column == column:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_column = column
            self._sort_reverse = False

        self._apply_filters()

    def _on_double_click(self, event):
        """Handle double-click to edit."""
        self._edit_selected()

    def _on_selection_change(self, event):
        """Handle selection change."""
        selection = self.tree.selection()
        # Could enable/disable buttons based on selection

    def _show_context_menu(self, event):
        """Show context menu on right-click."""
        # Select item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _edit_selected(self):
        """Edit selected expense."""
        selection = self.tree.selection()
        if selection:
            expense_id = selection[0]
            self.main_window._show_edit_expense(expense_id)

    def _delete_selected(self):
        """Delete selected expenses."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select expenses to delete.")
            return

        count = len(selection)
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete {count} expense(s)?"
        ):
            return

        for expense_id in selection:
            self.main_window.expense_manager.delete_expense(expense_id)

        self.main_window.set_status(f"Deleted {count} expense(s)")
        self.main_window._update_expense_count()
        self.refresh()

    def _duplicate_selected(self):
        """Duplicate selected expense."""
        selection = self.tree.selection()
        if not selection:
            return

        expense_id = selection[0]
        copied = self.main_window.expense_manager.copy_expense(expense_id)
        if copied:
            self.main_window.expense_manager.add_expense(copied)
            self.main_window.set_status("Expense duplicated")
            self.refresh()

    def _create_template(self):
        """Create template from selected expense."""
        selection = self.tree.selection()
        if not selection:
            return

        expense_id = selection[0]
        expense = self.main_window.expense_manager.get_expense(expense_id)

        if expense:
            # Simple dialog for template name
            from tkinter import simpledialog
            name = simpledialog.askstring(
                "Template Name",
                "Enter a name for this template:",
                parent=self
            )

            if name:
                template = self.main_window.template_manager.create_from_expense(expense, name)
                self.main_window.set_status(f"Template '{name}' created")

    def _export_current(self):
        """Export currently displayed expenses."""
        # Get current filtered data
        df = self.main_window.expense_manager.get_expenses_dataframe()
        criteria = FilterCriteria()

        if self.category_var.get() != "All":
            criteria.categories = [self.category_var.get()]
        if self.payment_var.get() != "All":
            criteria.payment_methods = [self.payment_var.get()]
        if self.search_var.get():
            criteria.search_text = self.search_var.get()

        filtered_df = self.main_window.filter_manager.apply_filter(df, criteria)

        # Show export dialog
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("PDF files", "*.pdf")
            ]
        )

        if filepath:
            expenses_list = filtered_df.to_dict('records')

            if filepath.endswith('.xlsx'):
                from exports import get_excel_exporter
                get_excel_exporter().export_expenses(expenses_list, filepath)
            elif filepath.endswith('.pdf'):
                from exports import get_pdf_exporter
                get_pdf_exporter().export_expense_list(expenses_list, filepath)
            else:
                filtered_df.to_csv(filepath, index=False)

            self.main_window.set_status(f"Exported to {filepath}")
