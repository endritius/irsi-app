"""
SettingsView - Application settings management.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path
import json

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING
from config import (
    CATEGORIES, PAYMENT_METHODS, RECURRING_TYPES,
    DEFAULT_CURRENCY, CURRENCY_SYMBOL, DATE_FORMAT_DISPLAY
)


class SettingsView(ttk.Frame):
    """
    Settings view for application configuration.
    """

    def __init__(self, parent, main_window):
        """
        Initialize SettingsView.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow
        """
        super().__init__(parent)
        self.main_window = main_window
        self.settings = self._load_settings()
        self._create_widgets()

    def _load_settings(self):
        """Load current settings."""
        settings_path = Path(__file__).parent.parent.parent / 'data' / 'settings.json'
        default_settings = {
            'currency': DEFAULT_CURRENCY,
            'currency_symbol': CURRENCY_SYMBOL,
            'date_format': DATE_FORMAT_DISPLAY,
            'auto_backup': True,
            'backup_interval': 7,
            'default_payment_method': PAYMENT_METHODS[0],
            'budget_warning_threshold': 80,
            'budget_critical_threshold': 95,
            'show_notifications': True,
            'theme': 'light',
            'data_path': str(Path(__file__).parent.parent.parent / 'data'),
            'export_path': str(Path.home() / 'Documents'),
            'recent_vendors_count': 10,
            'recent_categories_count': 5
        }

        try:
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    saved_settings = json.load(f)
                    default_settings.update(saved_settings)
        except Exception:
            pass

        return default_settings

    def _create_widgets(self):
        """Create view widgets."""
        # Header
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, PADDING['medium']))

        ttk.Label(
            header,
            text="Application Settings",
            style='Title.TLabel'
        ).pack(side=tk.LEFT)

        save_btn = ttk.Button(
            header,
            text="Save Settings",
            command=self._save_settings,
            style='Primary.TButton'
        )
        save_btn.pack(side=tk.RIGHT)

        reset_btn = ttk.Button(
            header,
            text="Reset to Default",
            command=self._reset_settings
        )
        reset_btn.pack(side=tk.RIGHT, padx=PADDING['small'])

        # Scrollable content
        canvas = tk.Canvas(self, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=canvas.yview)

        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Settings sections
        self._create_general_section()
        self._create_display_section()
        self._create_budget_section()
        self._create_data_section()
        self._create_categories_section()

    def _create_general_section(self):
        """Create general settings section."""
        section = ttk.LabelFrame(self.scrollable_frame, text="General Settings")
        section.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['medium'])

        # Currency
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Currency:", width=20, anchor='w').pack(side=tk.LEFT)
        self.currency_var = tk.StringVar(value=self.settings.get('currency', 'ALL'))
        currency_entry = ttk.Entry(row, textvariable=self.currency_var, width=10)
        currency_entry.pack(side=tk.LEFT, padx=PADDING['small'])

        ttk.Label(row, text="Symbol:").pack(side=tk.LEFT, padx=(PADDING['medium'], 0))
        self.currency_symbol_var = tk.StringVar(value=self.settings.get('currency_symbol', 'L'))
        symbol_entry = ttk.Entry(row, textvariable=self.currency_symbol_var, width=5)
        symbol_entry.pack(side=tk.LEFT, padx=PADDING['small'])

        # Date format
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Date Format:", width=20, anchor='w').pack(side=tk.LEFT)
        self.date_format_var = tk.StringVar(value=self.settings.get('date_format', 'DD/MM/YYYY'))
        date_formats = ['DD/MM/YYYY', 'MM/DD/YYYY', 'YYYY-MM-DD']
        date_combo = ttk.Combobox(
            row,
            textvariable=self.date_format_var,
            values=date_formats,
            state='readonly',
            width=15
        )
        date_combo.pack(side=tk.LEFT, padx=PADDING['small'])

        # Default payment method
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Default Payment Method:", width=20, anchor='w').pack(side=tk.LEFT)
        self.default_payment_var = tk.StringVar(
            value=self.settings.get('default_payment_method', PAYMENT_METHODS[0])
        )
        payment_combo = ttk.Combobox(
            row,
            textvariable=self.default_payment_var,
            values=PAYMENT_METHODS,
            state='readonly',
            width=15
        )
        payment_combo.pack(side=tk.LEFT, padx=PADDING['small'])

    def _create_display_section(self):
        """Create display settings section."""
        section = ttk.LabelFrame(self.scrollable_frame, text="Display Settings")
        section.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['medium'])

        # Theme
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Theme:", width=20, anchor='w').pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.settings.get('theme', 'light'))
        themes = ['light', 'dark']
        theme_combo = ttk.Combobox(
            row,
            textvariable=self.theme_var,
            values=themes,
            state='readonly',
            width=15
        )
        theme_combo.pack(side=tk.LEFT, padx=PADDING['small'])

        # Show notifications
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        self.notifications_var = tk.BooleanVar(value=self.settings.get('show_notifications', True))
        ttk.Checkbutton(
            row,
            text="Show budget alerts and notifications",
            variable=self.notifications_var
        ).pack(anchor='w')

        # Recent items count
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Recent Vendors Count:", width=20, anchor='w').pack(side=tk.LEFT)
        self.recent_vendors_var = tk.StringVar(value=str(self.settings.get('recent_vendors_count', 10)))
        vendors_spin = ttk.Spinbox(
            row,
            textvariable=self.recent_vendors_var,
            from_=5,
            to=50,
            width=10
        )
        vendors_spin.pack(side=tk.LEFT, padx=PADDING['small'])

    def _create_budget_section(self):
        """Create budget settings section."""
        section = ttk.LabelFrame(self.scrollable_frame, text="Budget Settings")
        section.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['medium'])

        # Warning threshold
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Warning Threshold (%):", width=20, anchor='w').pack(side=tk.LEFT)
        self.warning_threshold_var = tk.StringVar(
            value=str(self.settings.get('budget_warning_threshold', 80))
        )
        warning_spin = ttk.Spinbox(
            row,
            textvariable=self.warning_threshold_var,
            from_=50,
            to=95,
            width=10
        )
        warning_spin.pack(side=tk.LEFT, padx=PADDING['small'])
        ttk.Label(row, text="(Show warning when budget usage exceeds this)").pack(side=tk.LEFT, padx=PADDING['small'])

        # Critical threshold
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Critical Threshold (%):", width=20, anchor='w').pack(side=tk.LEFT)
        self.critical_threshold_var = tk.StringVar(
            value=str(self.settings.get('budget_critical_threshold', 95))
        )
        critical_spin = ttk.Spinbox(
            row,
            textvariable=self.critical_threshold_var,
            from_=80,
            to=100,
            width=10
        )
        critical_spin.pack(side=tk.LEFT, padx=PADDING['small'])
        ttk.Label(row, text="(Show critical alert when budget usage exceeds this)").pack(side=tk.LEFT, padx=PADDING['small'])

    def _create_data_section(self):
        """Create data management settings section."""
        section = ttk.LabelFrame(self.scrollable_frame, text="Data Management")
        section.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['medium'])

        # Auto backup
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        self.auto_backup_var = tk.BooleanVar(value=self.settings.get('auto_backup', True))
        ttk.Checkbutton(
            row,
            text="Enable automatic backups",
            variable=self.auto_backup_var
        ).pack(anchor='w')

        # Backup interval
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Backup Interval (days):", width=20, anchor='w').pack(side=tk.LEFT)
        self.backup_interval_var = tk.StringVar(
            value=str(self.settings.get('backup_interval', 7))
        )
        interval_spin = ttk.Spinbox(
            row,
            textvariable=self.backup_interval_var,
            from_=1,
            to=30,
            width=10
        )
        interval_spin.pack(side=tk.LEFT, padx=PADDING['small'])

        # Data path
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Data Location:", width=20, anchor='w').pack(side=tk.LEFT)
        self.data_path_var = tk.StringVar(value=self.settings.get('data_path', ''))
        data_entry = ttk.Entry(row, textvariable=self.data_path_var, width=40)
        data_entry.pack(side=tk.LEFT, padx=PADDING['small'])
        ttk.Button(row, text="Browse", command=self._browse_data_path).pack(side=tk.LEFT)

        # Export path
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        ttk.Label(row, text="Default Export Location:", width=20, anchor='w').pack(side=tk.LEFT)
        self.export_path_var = tk.StringVar(value=self.settings.get('export_path', ''))
        export_entry = ttk.Entry(row, textvariable=self.export_path_var, width=40)
        export_entry.pack(side=tk.LEFT, padx=PADDING['small'])
        ttk.Button(row, text="Browse", command=self._browse_export_path).pack(side=tk.LEFT)

        # Manual backup button
        row = ttk.Frame(section)
        row.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['medium'])

        ttk.Button(
            row,
            text="Create Backup Now",
            command=self._create_backup
        ).pack(side=tk.LEFT)

        ttk.Button(
            row,
            text="Restore from Backup",
            command=self._restore_backup
        ).pack(side=tk.LEFT, padx=PADDING['small'])

    def _create_categories_section(self):
        """Create categories management section."""
        section = ttk.LabelFrame(self.scrollable_frame, text="Categories")
        section.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['medium'])

        info_label = ttk.Label(
            section,
            text="Current expense categories and subcategories:",
            style='Muted.TLabel'
        )
        info_label.pack(anchor='w', padx=PADDING['medium'], pady=PADDING['small'])

        # Categories display
        categories_frame = ttk.Frame(section)
        categories_frame.pack(fill=tk.X, padx=PADDING['medium'], pady=PADDING['small'])

        for category, cat_data in CATEGORIES.items():
            cat_frame = ttk.Frame(categories_frame)
            cat_frame.pack(fill=tk.X, pady=2)

            ttk.Label(
                cat_frame,
                text=f"{category}:",
                font=FONTS['body_bold'],
                width=15,
                anchor='w'
            ).pack(side=tk.LEFT)

            subcategories = cat_data.get('subcategories', []) if isinstance(cat_data, dict) else cat_data
            ttk.Label(
                cat_frame,
                text=", ".join(subcategories),
                style='Muted.TLabel'
            ).pack(side=tk.LEFT)

        # Note about custom categories
        note_label = ttk.Label(
            section,
            text="Note: Custom categories can be configured in config.py",
            style='Muted.TLabel',
            font=FONTS['small']
        )
        note_label.pack(anchor='w', padx=PADDING['medium'], pady=PADDING['small'])

    def _browse_data_path(self):
        """Browse for data path."""
        path = filedialog.askdirectory(
            initialdir=self.data_path_var.get(),
            title="Select Data Location"
        )
        if path:
            self.data_path_var.set(path)

    def _browse_export_path(self):
        """Browse for export path."""
        path = filedialog.askdirectory(
            initialdir=self.export_path_var.get(),
            title="Select Default Export Location"
        )
        if path:
            self.export_path_var.set(path)

    def _save_settings(self):
        """Save settings to file."""
        try:
            # Validate thresholds
            warning = int(self.warning_threshold_var.get())
            critical = int(self.critical_threshold_var.get())

            if warning >= critical:
                messagebox.showerror("Error", "Warning threshold must be less than critical threshold")
                return

            settings = {
                'currency': self.currency_var.get(),
                'currency_symbol': self.currency_symbol_var.get(),
                'date_format': self.date_format_var.get(),
                'default_payment_method': self.default_payment_var.get(),
                'theme': self.theme_var.get(),
                'show_notifications': self.notifications_var.get(),
                'recent_vendors_count': int(self.recent_vendors_var.get()),
                'budget_warning_threshold': warning,
                'budget_critical_threshold': critical,
                'auto_backup': self.auto_backup_var.get(),
                'backup_interval': int(self.backup_interval_var.get()),
                'data_path': self.data_path_var.get(),
                'export_path': self.export_path_var.get()
            }

            settings_path = Path(__file__).parent.parent.parent / 'data' / 'settings.json'
            settings_path.parent.mkdir(parents=True, exist_ok=True)

            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)

            self.settings = settings
            self.main_window.set_status("Settings saved")
            messagebox.showinfo("Success", "Settings saved successfully")

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid value: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def _reset_settings(self):
        """Reset settings to defaults."""
        if messagebox.askyesno("Confirm Reset", "Reset all settings to default values?"):
            self.settings = self._load_settings()

            # Update UI
            self.currency_var.set('ALL')
            self.currency_symbol_var.set('L')
            self.date_format_var.set('DD/MM/YYYY')
            self.default_payment_var.set(PAYMENT_METHODS[0])
            self.theme_var.set('light')
            self.notifications_var.set(True)
            self.recent_vendors_var.set('10')
            self.warning_threshold_var.set('80')
            self.critical_threshold_var.set('95')
            self.auto_backup_var.set(True)
            self.backup_interval_var.set('7')

            self.main_window.set_status("Settings reset to defaults")

    def _create_backup(self):
        """Create manual backup."""
        try:
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("ZIP files", "*.zip")],
                initialfile=f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            )

            if backup_path:
                self.main_window.data_manager.create_backup(backup_path)
                self.main_window.set_status(f"Backup created: {backup_path}")
                messagebox.showinfo("Success", f"Backup created successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create backup: {e}")

    def _restore_backup(self):
        """Restore from backup."""
        backup_path = filedialog.askopenfilename(
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
            title="Select Backup File"
        )

        if backup_path:
            if messagebox.askyesno(
                "Confirm Restore",
                "This will replace all current data. Are you sure?"
            ):
                try:
                    self.main_window.data_manager.restore_backup(backup_path)
                    self.main_window.set_status("Data restored from backup")
                    messagebox.showinfo("Success", "Data restored successfully. Please restart the application.")

                except Exception as e:
                    messagebox.showerror("Error", f"Failed to restore backup: {e}")

    def refresh(self):
        """Refresh settings view."""
        self.settings = self._load_settings()
