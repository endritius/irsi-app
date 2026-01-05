"""
ExpenseFormView - Form for adding and editing expenses.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
from typing import Optional

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING
from models import Expense
from config import CATEGORIES, PAYMENT_METHODS, RECURRING_TYPES, get_subcategories
from utils.validators import validate_expense
from utils.formatters import format_currency


class ExpenseFormView(ttk.Frame):
    """
    Form for adding or editing expenses.
    """

    def __init__(self, parent, main_window, expense_id: str = None):
        """
        Initialize ExpenseFormView.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow
            expense_id: Expense ID for editing (None for new)
        """
        super().__init__(parent)
        self.main_window = main_window
        self.expense_id = expense_id
        self.is_edit = expense_id is not None

        self._create_widgets()

        if self.is_edit:
            self._load_expense()

    def _create_widgets(self):
        """Create form widgets."""
        # Main form container
        form_container = ttk.Frame(self)
        form_container.pack(fill=tk.BOTH, expand=True, padx=PADDING['large'])

        # Left column - Main details
        left_frame = ttk.LabelFrame(form_container, text="Expense Details")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['medium']))

        self._create_main_fields(left_frame)

        # Right column - Additional options
        right_frame = ttk.LabelFrame(form_container, text="Additional Options")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._create_additional_fields(right_frame)

        # Bottom - Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, pady=PADDING['large'])

        self._create_buttons(button_frame)

    def _create_main_fields(self, parent):
        """Create main form fields."""
        # Amount
        self._create_field(parent, "Amount *", "amount")
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(
            parent,
            textvariable=self.amount_var,
            font=FONTS['input']
        )
        self.amount_entry.pack(fill=tk.X, padx=PADDING['medium'], pady=(0, PADDING['medium']))
        self.amount_entry.focus()

        # Date
        self._create_field(parent, "Date *", "date")
        date_frame = ttk.Frame(parent)
        date_frame.pack(fill=tk.X, padx=PADDING['medium'], pady=(0, PADDING['medium']))

        self.date_var = tk.StringVar(value=datetime.now().strftime('%d/%m/%Y'))
        self.date_entry = ttk.Entry(date_frame, textvariable=self.date_var, width=15)
        self.date_picker = None

        try:
            from tkcalendar import DateEntry
            self.date_picker = DateEntry(
                date_frame,
                date_pattern='dd/mm/yyyy',
                width=15,
                background='darkblue',
                foreground='white',
                borderwidth=2
            )
            self.date_picker.set_date(datetime.now())
            self.date_picker.pack(side=tk.LEFT)
            # Update StringVar when date changes
            self.date_picker.bind('<<DateEntrySelected>>', self._on_date_selected)
        except ImportError:
            # Calendar not available, use manual entry
            self.date_entry.pack(side=tk.LEFT)
            ttk.Label(date_frame, text="(DD/MM/YYYY)", style='Muted.TLabel').pack(side=tk.LEFT, padx=5)

        # Vendor
        self._create_field(parent, "Vendor *", "vendor")
        self.vendor_var = tk.StringVar()

        # Autocomplete combobox
        vendors = self.main_window.expense_manager.get_unique_vendors()
        self.vendor_combo = ttk.Combobox(
            parent,
            textvariable=self.vendor_var,
            values=vendors
        )
        self.vendor_combo.pack(fill=tk.X, padx=PADDING['medium'], pady=(0, PADDING['medium']))

        # Category
        self._create_field(parent, "Category *", "category")
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            parent,
            textvariable=self.category_var,
            values=list(CATEGORIES.keys()),
            state='readonly'
        )
        self.category_combo.pack(fill=tk.X, padx=PADDING['medium'], pady=(0, PADDING['medium']))
        self.category_combo.bind('<<ComboboxSelected>>', self._on_category_change)

        # Subcategory
        self._create_field(parent, "Subcategory", "subcategory")
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(
            parent,
            textvariable=self.subcategory_var,
            state='readonly'
        )
        self.subcategory_combo.pack(fill=tk.X, padx=PADDING['medium'], pady=(0, PADDING['medium']))

        # Payment Method
        self._create_field(parent, "Payment Method", "payment")
        self.payment_var = tk.StringVar(value=PAYMENT_METHODS[0])
        self.payment_combo = ttk.Combobox(
            parent,
            textvariable=self.payment_var,
            values=PAYMENT_METHODS,
            state='readonly'
        )
        self.payment_combo.pack(fill=tk.X, padx=PADDING['medium'], pady=(0, PADDING['medium']))

        # Description
        self._create_field(parent, "Description", "description")
        self.description_text = tk.Text(parent, height=3, font=FONTS['input'])
        self.description_text.pack(fill=tk.X, padx=PADDING['medium'], pady=(0, PADDING['medium']))

    def _create_additional_fields(self, parent):
        """Create additional option fields."""
        # Initialize tags_var for internal use (not displayed)
        self.tags_var = tk.StringVar()

        # Recurring expense
        recurring_frame = ttk.LabelFrame(parent, text="Recurring Expense")
        recurring_frame.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['medium'])

        self.is_recurring_var = tk.BooleanVar(value=False)
        recurring_check = ttk.Checkbutton(
            recurring_frame,
            text="This is a recurring expense",
            variable=self.is_recurring_var,
            command=self._toggle_recurring
        )
        recurring_check.pack(anchor='w', padx=PADDING['small'], pady=PADDING['small'])

        # Recurring options frame
        self.recurring_options = ttk.Frame(recurring_frame)
        self.recurring_options.pack(fill=tk.X, padx=PADDING['small'], pady=PADDING['small'])

        ttk.Label(self.recurring_options, text="Frequency:").pack(side=tk.LEFT)
        self.frequency_var = tk.StringVar(value="monthly")
        freq_combo = ttk.Combobox(
            self.recurring_options,
            textvariable=self.frequency_var,
            values=RECURRING_TYPES,
            state='readonly',
            width=12
        )
        freq_combo.pack(side=tk.LEFT, padx=PADDING['small'])

        # Initially hide recurring options
        self.recurring_options.pack_forget()

        # Duplicate warning area
        self.warning_frame = ttk.Frame(parent)
        self.warning_frame.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['medium'])

    def _create_field(self, parent, label: str, name: str):
        """Create a form field label."""
        ttk.Label(parent, text=label, style='Card.TLabel').pack(
            anchor='w', padx=PADDING['medium'], pady=(PADDING['small'], 2)
        )

    def _create_buttons(self, parent):
        """Create form action buttons."""
        # Cancel button
        cancel_btn = ttk.Button(
            parent,
            text="Cancel",
            command=self._cancel
        )
        cancel_btn.pack(side=tk.RIGHT, padx=PADDING['small'])

        # Save button
        save_text = "Update Expense" if self.is_edit else "Save Expense"
        save_btn = ttk.Button(
            parent,
            text=save_text,
            command=self._save,
            style='Primary.TButton'
        )
        save_btn.pack(side=tk.RIGHT)

        if not self.is_edit:
            # Save and add another
            save_another_btn = ttk.Button(
                parent,
                text="Save & Add Another",
                command=self._save_and_clear
            )
            save_another_btn.pack(side=tk.RIGHT, padx=PADDING['small'])

    def _toggle_recurring(self):
        """Toggle recurring options visibility."""
        if self.is_recurring_var.get():
            self.recurring_options.pack(fill=tk.X, padx=PADDING['small'], pady=PADDING['small'])
        else:
            self.recurring_options.pack_forget()

    def _on_date_selected(self, event=None):
        """Handle date selection from date picker."""
        if self.date_picker:
            selected_date = self.date_picker.get_date()
            self.date_var.set(selected_date.strftime('%d/%m/%Y'))

    def _on_category_change(self, event):
        """Handle category selection change."""
        category = self.category_var.get()
        subcategories = get_subcategories(category)
        self.subcategory_combo['values'] = subcategories
        if subcategories:
            self.subcategory_combo.set(subcategories[0])
        else:
            self.subcategory_combo.set('')

    def _apply_template(self, template):
        """Apply template values to form."""
        self.vendor_var.set(template.vendor)
        self.category_var.set(template.category)
        self._on_category_change(None)
        self.subcategory_var.set(template.subcategory)
        self.payment_var.set(template.payment_method)

        if template.typical_amount:
            self.amount_var.set(str(template.typical_amount))

        if template.description:
            self.description_text.delete('1.0', tk.END)
            self.description_text.insert('1.0', template.description)

        if template.tags:
            self.tags_var.set(', '.join(template.tags))

    def _load_expense(self):
        """Load expense data for editing."""
        expense = self.main_window.expense_manager.get_expense(self.expense_id)
        if not expense:
            messagebox.showerror("Error", "Expense not found")
            self._cancel()
            return

        self.amount_var.set(str(expense.amount))
        self.date_var.set(expense.date.strftime('%d/%m/%Y'))
        if self.date_picker:
            self.date_picker.set_date(expense.date)
        self.vendor_var.set(expense.vendor)
        self.category_var.set(expense.category)
        self._on_category_change(None)
        self.subcategory_var.set(expense.subcategory)
        self.payment_var.set(expense.payment_method)

        if expense.description:
            self.description_text.insert('1.0', expense.description)

        if expense.tags:
            self.tags_var.set(', '.join(expense.tags))

        self.is_recurring_var.set(expense.is_recurring)
        if expense.is_recurring:
            self._toggle_recurring()
            self.frequency_var.set(expense.recurring_type or 'monthly')

    def _validate_form(self) -> Optional[Expense]:
        """Validate form and create expense object."""
        errors = []

        # Amount
        try:
            amount = float(self.amount_var.get().replace(',', '').strip())
            if amount <= 0:
                errors.append("Amount must be positive")
        except ValueError:
            errors.append("Invalid amount")
            amount = 0

        # Date
        try:
            if self.date_picker:
                date = datetime.combine(self.date_picker.get_date(), datetime.min.time())
            else:
                date_str = self.date_var.get()
                date = datetime.strptime(date_str, '%d/%m/%Y')
        except (ValueError, Exception):
            errors.append("Invalid date format (use DD/MM/YYYY)")
            date = datetime.now()

        # Vendor
        vendor = self.vendor_var.get().strip()
        if not vendor:
            errors.append("Vendor is required")

        # Category
        category = self.category_var.get()
        if not category:
            errors.append("Category is required")

        if errors:
            messagebox.showerror("Validation Error", "\n".join(errors))
            return None

        # Create expense object
        description = self.description_text.get('1.0', tk.END).strip()
        tags_str = self.tags_var.get().strip()
        tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []

        expense = Expense(
            amount=amount,
            date=date,
            category=category,
            subcategory=self.subcategory_var.get(),
            vendor=vendor,
            payment_method=self.payment_var.get(),
            description=description,
            tags=tags,
            is_recurring=self.is_recurring_var.get(),
            recurring_type=self.frequency_var.get() if self.is_recurring_var.get() else None
        )

        if self.is_edit:
            expense.expense_id = self.expense_id

        return expense

    def _check_duplicates(self, expense: Expense):
        """Check for potential duplicates."""
        duplicates = self.main_window.expense_manager.find_duplicates(expense)

        if duplicates:
            # Clear previous warnings
            for widget in self.warning_frame.winfo_children():
                widget.destroy()

            warning = tk.Label(
                self.warning_frame,
                text=f"Warning: Found {len(duplicates)} similar expense(s)",
                font=FONTS['small_bold'],
                fg=COLORS['warning'],
                bg=COLORS['background']
            )
            warning.pack()

    def _save(self):
        """Save expense."""
        expense = self._validate_form()
        if not expense:
            return

        try:
            if self.is_edit:
                # Update existing
                updates = expense.to_dict()
                del updates['expense_id']
                del updates['created_at']

                self.main_window.expense_manager.update_expense(
                    self.expense_id, updates
                )
                self.main_window.set_status("Expense updated")
            else:
                # Add new
                self.main_window.expense_manager.add_expense(expense)
                self.main_window.set_status("Expense added")

            self.main_window._update_expense_count()
            self.main_window._show_expenses()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _save_and_clear(self):
        """Save and clear form for another entry."""
        expense = self._validate_form()
        if not expense:
            return

        try:
            self.main_window.expense_manager.add_expense(expense)
            self.main_window.set_status("Expense added - ready for another")
            self.main_window._update_expense_count()
            self._clear_form()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _clear_form(self):
        """Clear form for new entry."""
        self.amount_var.set('')
        self.date_var.set(datetime.now().strftime('%d/%m/%Y'))
        self.vendor_var.set('')
        self.category_var.set('')
        self.subcategory_var.set('')
        self.payment_var.set(PAYMENT_METHODS[0])
        self.description_text.delete('1.0', tk.END)
        self.tags_var.set('')
        self.is_recurring_var.set(False)
        self._toggle_recurring()

        self.amount_entry.focus()

    def _cancel(self):
        """Cancel and return to expense list."""
        self.main_window._show_expenses()
