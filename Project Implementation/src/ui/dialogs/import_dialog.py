"""
ImportDialog - Dialog for importing expense data from CSV files.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path
import csv

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING


class ImportDialog(tk.Toplevel):
    """
    Dialog for importing expenses from external CSV files.
    """

    def __init__(self, parent, main_window):
        """
        Initialize ImportDialog.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow
        """
        super().__init__(parent)
        self.main_window = main_window
        self.file_path = None
        self.headers = []
        self.preview_data = []
        self.column_mappings = {}

        self.title("Import Data")
        self.geometry("700x600")
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self.wait_window()

    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self, padding=PADDING['large'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Step 1: File selection
        file_frame = ttk.LabelFrame(main_frame, text="Step 1: Select CSV File")
        file_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        self.file_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_var, state='readonly')
        file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=PADDING['medium'], pady=PADDING['small'])

        browse_btn = ttk.Button(
            file_frame,
            text="Browse...",
            command=self._browse_file
        )
        browse_btn.pack(side=tk.RIGHT, padx=PADDING['medium'], pady=PADDING['small'])

        # Step 2: Column mapping
        mapping_frame = ttk.LabelFrame(main_frame, text="Step 2: Map Columns")
        mapping_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        self.mapping_content = ttk.Frame(mapping_frame)
        self.mapping_content.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(
            self.mapping_content,
            text="Select a file to configure column mappings",
            style='Muted.TLabel'
        ).pack()

        # Step 3: Preview
        preview_frame = ttk.LabelFrame(main_frame, text="Step 3: Preview Import")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, PADDING['medium']))

        # Preview treeview
        preview_container = ttk.Frame(preview_frame)
        preview_container.pack(fill=tk.BOTH, expand=True, padx=PADDING['small'], pady=PADDING['small'])

        self.preview_tree = ttk.Treeview(
            preview_container,
            columns=('date', 'amount', 'vendor', 'category'),
            show='headings',
            height=8
        )

        self.preview_tree.heading('date', text='Date')
        self.preview_tree.heading('amount', text='Amount')
        self.preview_tree.heading('vendor', text='Vendor')
        self.preview_tree.heading('category', text='Category')

        self.preview_tree.column('date', width=100)
        self.preview_tree.column('amount', width=100)
        self.preview_tree.column('vendor', width=150)
        self.preview_tree.column('category', width=150)

        scrollbar = ttk.Scrollbar(preview_container, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)

        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status
        self.status_var = tk.StringVar(value="Select a CSV file to begin")
        status_label = ttk.Label(
            preview_frame,
            textvariable=self.status_var,
            style='Muted.TLabel'
        )
        status_label.pack(anchor='w', padx=PADDING['medium'], pady=PADDING['small'])

        # Options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        self.skip_duplicates_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Skip duplicate entries",
            variable=self.skip_duplicates_var
        ).pack(anchor='w')

        self.validate_data_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Validate data before import",
            variable=self.validate_data_var
        ).pack(anchor='w')

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X)

        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy
        ).pack(side=tk.RIGHT)

        self.import_btn = ttk.Button(
            btn_frame,
            text="Import",
            command=self._import_data,
            style='Primary.TButton',
            state='disabled'
        )
        self.import_btn.pack(side=tk.RIGHT, padx=PADDING['small'])

        self.preview_btn = ttk.Button(
            btn_frame,
            text="Preview",
            command=self._preview_import,
            state='disabled'
        )
        self.preview_btn.pack(side=tk.RIGHT, padx=PADDING['small'])

    def _browse_file(self):
        """Browse for CSV file."""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            title="Select CSV File to Import"
        )

        if file_path:
            self.file_path = file_path
            self.file_var.set(file_path)
            self._load_file_headers()

    def _load_file_headers(self):
        """Load headers from CSV file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                self.headers = next(reader)

            self._create_mapping_ui()
            self.preview_btn.config(state='normal')
            self.status_var.set(f"Found {len(self.headers)} columns in file")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")

    def _create_mapping_ui(self):
        """Create column mapping UI."""
        # Clear existing
        for widget in self.mapping_content.winfo_children():
            widget.destroy()

        # Required fields
        required_fields = [
            ('amount', 'Amount *'),
            ('date', 'Date *'),
            ('vendor', 'Vendor *'),
            ('category', 'Category *')
        ]

        # Optional fields
        optional_fields = [
            ('subcategory', 'Subcategory'),
            ('payment_method', 'Payment Method'),
            ('description', 'Description'),
            ('tags', 'Tags')
        ]

        self.mapping_vars = {}

        # Create mapping dropdowns
        row = 0
        for field_key, field_label in required_fields + optional_fields:
            ttk.Label(
                self.mapping_content,
                text=field_label,
                width=15,
                anchor='w'
            ).grid(row=row, column=0, padx=PADDING['small'], pady=2)

            var = tk.StringVar(value='-- Select --')
            self.mapping_vars[field_key] = var

            # Try to auto-map based on header names
            for header in self.headers:
                if field_key.lower() in header.lower():
                    var.set(header)
                    break

            combo = ttk.Combobox(
                self.mapping_content,
                textvariable=var,
                values=['-- Select --'] + self.headers,
                state='readonly',
                width=25
            )
            combo.grid(row=row, column=1, padx=PADDING['small'], pady=2)

            row += 1

    def _preview_import(self):
        """Preview import data."""
        # Validate mappings
        required = ['amount', 'date', 'vendor', 'category']
        for field in required:
            if self.mapping_vars[field].get() == '-- Select --':
                messagebox.showerror("Error", f"Please map the {field} column")
                return

        try:
            # Clear preview
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)

            # Read data
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    if count >= 10:  # Preview first 10 rows
                        break

                    date_col = self.mapping_vars['date'].get()
                    amount_col = self.mapping_vars['amount'].get()
                    vendor_col = self.mapping_vars['vendor'].get()
                    category_col = self.mapping_vars['category'].get()

                    self.preview_tree.insert('', 'end', values=(
                        row.get(date_col, ''),
                        row.get(amount_col, ''),
                        row.get(vendor_col, ''),
                        row.get(category_col, '')
                    ))
                    count += 1

            # Count total rows
            with open(self.file_path, 'r', encoding='utf-8') as f:
                total = sum(1 for _ in f) - 1  # Subtract header

            self.status_var.set(f"Showing preview of first 10 rows ({total} total)")
            self.import_btn.config(state='normal')

        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview: {e}")

    def _import_data(self):
        """Import data from CSV."""
        # Validate mappings
        required = ['amount', 'date', 'vendor', 'category']
        for field in required:
            if self.mapping_vars[field].get() == '-- Select --':
                messagebox.showerror("Error", f"Please map the {field} column")
                return

        # Build column mapping
        column_mapping = {}
        for field, var in self.mapping_vars.items():
            if var.get() != '-- Select --':
                column_mapping[var.get()] = field

        try:
            result = self.main_window.data_manager.import_csv(
                self.file_path,
                column_mapping,
                skip_duplicates=self.skip_duplicates_var.get()
            )

            if result['success']:
                imported = result.get('imported', 0)
                skipped = result.get('skipped', 0)
                errors = result.get('errors', 0)

                message = f"Import completed!\n\nImported: {imported} expenses"
                if skipped > 0:
                    message += f"\nSkipped: {skipped} duplicates"
                if errors > 0:
                    message += f"\nErrors: {errors} rows"

                messagebox.showinfo("Import Complete", message)
                self.main_window.set_status(f"Imported {imported} expenses")
                self.destroy()
            else:
                messagebox.showerror("Import Failed", result.get('message', 'Unknown error'))

        except Exception as e:
            messagebox.showerror("Import Error", f"Failed to import: {e}")
