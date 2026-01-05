"""
MainWindow - Primary application window with navigation and content panels.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import APP_NAME, APP_VERSION, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from ui.styles import apply_theme, COLORS, FONTS, PADDING, DIMENSIONS
from managers import (
    get_expense_manager, get_budget_manager,
    get_template_manager, get_filter_manager, get_undo_manager
)
from persistence import get_data_manager, get_settings_manager
from reports import get_report_generator
from visualization import get_visualizer
from exports import get_pdf_exporter, get_excel_exporter


class MainWindow:
    """
    Main application window with sidebar navigation and content panels.
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize MainWindow.

        Args:
            root: Root Tkinter window
        """
        self.root = root
        self._setup_window()
        self._init_managers()
        self._create_ui()
        self._setup_keyboard_shortcuts()
        self._load_initial_data()

    def _setup_window(self):
        """Configure main window properties."""
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry(f"{WINDOW_MIN_WIDTH}x{WINDOW_MIN_HEIGHT}")
        self.root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Apply theme
        apply_theme(self.root)

        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

        # Handle close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_managers(self):
        """Initialize manager instances."""
        self.expense_manager = get_expense_manager()
        self.budget_manager = get_budget_manager()
        self.template_manager = get_template_manager()
        self.filter_manager = get_filter_manager()
        self.undo_manager = get_undo_manager()
        self.data_manager = get_data_manager()
        self.settings_manager = get_settings_manager()
        self.report_generator = get_report_generator()
        self.visualizer = get_visualizer()

    def _create_ui(self):
        """Create main UI layout."""
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Create sidebar
        self._create_sidebar()

        # Create content area
        self._create_content_area()

        # Create status bar
        self._create_status_bar()

        # Show dashboard by default
        self._show_dashboard()

    def _create_sidebar(self):
        """Create navigation sidebar."""
        self.sidebar = tk.Frame(
            self.main_container,
            bg=COLORS['dark'],
            width=DIMENSIONS['sidebar_width']
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # App title
        title_frame = tk.Frame(self.sidebar, bg=COLORS['dark'])
        title_frame.pack(fill=tk.X, pady=20)

        title_label = tk.Label(
            title_frame,
            text=APP_NAME,
            font=FONTS['heading'],
            fg=COLORS['white'],
            bg=COLORS['dark']
        )
        title_label.pack()

        # Navigation buttons
        nav_items = [
            ("Dashboard", self._show_dashboard, "dashboard"),
            ("Expenses", self._show_expenses, "expenses"),
            ("Add Expense", self._show_add_expense, "add"),
            ("Budgets", self._show_budgets, "budgets"),
            ("Reports", self._show_reports, "reports"),
            ("Charts", self._show_charts, "charts"),
            ("Templates", self._show_templates, "templates"),
            ("Settings", self._show_settings, "settings"),
        ]

        self.nav_buttons = {}
        for text, command, key in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=FONTS['body'],
                fg=COLORS['white'],
                bg=COLORS['dark'],
                activebackground=COLORS['primary'],
                activeforeground=COLORS['white'],
                bd=0,
                padx=20,
                pady=12,
                anchor='w',
                cursor='hand2',
                command=command
            )
            btn.pack(fill=tk.X)
            btn.bind('<Enter>', lambda e, b=btn: b.config(bg=COLORS['primary']))
            btn.bind('<Leave>', lambda e, b=btn: self._reset_nav_button(b))
            self.nav_buttons[key] = btn

        # Bottom section - Quick actions
        bottom_frame = tk.Frame(self.sidebar, bg=COLORS['dark'])
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Export button
        export_btn = tk.Button(
            bottom_frame,
            text="Export Data",
            font=FONTS['small'],
            fg=COLORS['white'],
            bg=COLORS['gray'],
            activebackground=COLORS['primary'],
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._show_export_dialog
        )
        export_btn.pack(fill=tk.X, padx=10, pady=2)

        # Backup button
        backup_btn = tk.Button(
            bottom_frame,
            text="Backup",
            font=FONTS['small'],
            fg=COLORS['white'],
            bg=COLORS['gray'],
            activebackground=COLORS['primary'],
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._create_backup
        )
        backup_btn.pack(fill=tk.X, padx=10, pady=2)

        # Import button
        import_btn = tk.Button(
            bottom_frame,
            text="Import Data",
            font=FONTS['small'],
            fg=COLORS['white'],
            bg=COLORS['gray'],
            activebackground=COLORS['primary'],
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._show_import_dialog
        )
        import_btn.pack(fill=tk.X, padx=10, pady=2)

        # About button
        about_btn = tk.Button(
            bottom_frame,
            text="About",
            font=FONTS['small'],
            fg=COLORS['text_muted'],
            bg=COLORS['dark'],
            activebackground=COLORS['gray'],
            bd=0,
            padx=15,
            pady=5,
            cursor='hand2',
            command=self._show_about
        )
        about_btn.pack(fill=tk.X, padx=10, pady=(10, 2))

    def _reset_nav_button(self, button):
        """Reset nav button to default state."""
        if button != self._active_nav_button:
            button.config(bg=COLORS['dark'])

    def _set_active_nav(self, key):
        """Set active navigation button."""
        if hasattr(self, '_active_nav_button') and self._active_nav_button:
            self._active_nav_button.config(bg=COLORS['dark'])

        self._active_nav_button = self.nav_buttons.get(key)
        if self._active_nav_button:
            self._active_nav_button.config(bg=COLORS['primary'])

    def _create_content_area(self):
        """Create main content area."""
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Content header
        self.header_frame = ttk.Frame(self.content_frame)
        self.header_frame.pack(fill=tk.X, padx=PADDING['large'], pady=PADDING['medium'])

        self.header_title = ttk.Label(
            self.header_frame,
            text="Dashboard",
            style='Title.TLabel'
        )
        self.header_title.pack(side=tk.LEFT)

        # Header actions
        self.header_actions = ttk.Frame(self.header_frame)
        self.header_actions.pack(side=tk.RIGHT)

        # Content body (will be replaced by each view)
        self.content_body = ttk.Frame(self.content_frame)
        self.content_body.pack(fill=tk.BOTH, expand=True, padx=PADDING['large'])

    def _create_status_bar(self):
        """Create status bar at bottom."""
        self.status_bar = tk.Frame(self.root, bg=COLORS['gray_light'], height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            self.status_bar,
            text="Ready",
            font=FONTS['small'],
            bg=COLORS['gray_light'],
            fg=COLORS['text_muted'],
            anchor='w',
            padx=10
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Expense count
        self.expense_count_label = tk.Label(
            self.status_bar,
            text="0 expenses",
            font=FONTS['small'],
            bg=COLORS['gray_light'],
            fg=COLORS['text_muted'],
            padx=10
        )
        self.expense_count_label.pack(side=tk.RIGHT)

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.root.bind('<Control-n>', lambda e: self._show_add_expense())
        self.root.bind('<Control-e>', lambda e: self._show_expenses())
        self.root.bind('<Control-b>', lambda e: self._show_budgets())
        self.root.bind('<Control-r>', lambda e: self._show_reports())
        self.root.bind('<Control-z>', lambda e: self._undo())
        self.root.bind('<Control-y>', lambda e: self._redo())
        self.root.bind('<Control-s>', lambda e: self._save_data())
        self.root.bind('<F5>', lambda e: self._refresh())
        self.root.bind('<Escape>', lambda e: self._show_dashboard())

    def _load_initial_data(self):
        """Load initial data and update UI."""
        self._update_expense_count()

    def _clear_content(self):
        """Clear current content body."""
        for widget in self.content_body.winfo_children():
            widget.destroy()

        for widget in self.header_actions.winfo_children():
            widget.destroy()

    def _set_header(self, title: str):
        """Set header title."""
        self.header_title.config(text=title)

    def set_status(self, message: str):
        """Set status bar message."""
        self.status_label.config(text=message)
        self.root.after(5000, lambda: self.status_label.config(text="Ready"))

    def _update_expense_count(self):
        """Update expense count in status bar."""
        count = self.expense_manager.get_expense_count()
        self.expense_count_label.config(text=f"{count} expenses")

    # ===== VIEW METHODS =====

    def _show_dashboard(self):
        """Show dashboard view."""
        self._clear_content()
        self._set_header("Dashboard")
        self._set_active_nav("dashboard")

        from ui.views.dashboard_view import DashboardView
        self.current_view = DashboardView(self.content_body, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def _show_expenses(self):
        """Show expense list view."""
        self._clear_content()
        self._set_header("Expenses")
        self._set_active_nav("expenses")

        from ui.views.expense_list_view import ExpenseListView
        self.current_view = ExpenseListView(self.content_body, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def _show_add_expense(self):
        """Show add expense form."""
        self._clear_content()
        self._set_header("Add Expense")
        self._set_active_nav("add")

        from ui.views.expense_form_view import ExpenseFormView
        self.current_view = ExpenseFormView(self.content_body, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def _show_edit_expense(self, expense_id: str):
        """Show edit expense form."""
        self._clear_content()
        self._set_header("Edit Expense")

        from ui.views.expense_form_view import ExpenseFormView
        self.current_view = ExpenseFormView(
            self.content_body, self, expense_id=expense_id
        )
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def _show_budgets(self):
        """Show budget management view."""
        self._clear_content()
        self._set_header("Budgets")
        self._set_active_nav("budgets")

        from ui.views.budget_view import BudgetView
        self.current_view = BudgetView(self.content_body, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def _show_reports(self):
        """Show reports view."""
        self._clear_content()
        self._set_header("Reports")
        self._set_active_nav("reports")

        from ui.views.reports_view import ReportsView
        self.current_view = ReportsView(self.content_body, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def _show_charts(self):
        """Show charts/visualization view."""
        self._clear_content()
        self._set_header("Charts & Analytics")
        self._set_active_nav("charts")

        from ui.views.charts_view import ChartsView
        self.current_view = ChartsView(self.content_body, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def _show_templates(self):
        """Show templates management view."""
        self._clear_content()
        self._set_header("Expense Templates")
        self._set_active_nav("templates")

        from ui.views.templates_view import TemplatesView
        self.current_view = TemplatesView(self.content_body, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)

    def _show_settings(self):
        """Show settings view."""
        self._clear_content()
        self._set_header("Settings")
        self._set_active_nav("settings")

        from ui.views.settings_view import SettingsView
        self.current_view = SettingsView(self.content_body, self)
        self.current_view.pack(fill=tk.BOTH, expand=True)

    # ===== ACTION METHODS =====

    def _show_export_dialog(self):
        """Show export dialog."""
        from ui.dialogs.export_dialog import ExportDialog
        dialog = ExportDialog(self.root, self)

    def _show_import_dialog(self):
        """Show import dialog."""
        from ui.dialogs.import_dialog import ImportDialog
        dialog = ImportDialog(self.root, self)
        # Refresh current view after import
        if hasattr(self, 'current_view') and hasattr(self.current_view, 'refresh'):
            self.current_view.refresh()

    def _show_about(self):
        """Show about dialog."""
        from ui.dialogs.about_dialog import AboutDialog
        dialog = AboutDialog(self.root)

    def _create_backup(self):
        """Create data backup."""
        try:
            backup_path = self.data_manager.create_backup()
            messagebox.showinfo(
                "Backup Created",
                f"Backup saved to:\n{backup_path}"
            )
            self.set_status("Backup created successfully")
        except Exception as e:
            messagebox.showerror("Backup Error", str(e))

    def _undo(self):
        """Undo last action."""
        if self.undo_manager.can_undo():
            desc = self.undo_manager.get_undo_description()
            if self.undo_manager.undo():
                self.set_status(f"Undone: {desc}")
                self._refresh()
        else:
            self.set_status("Nothing to undo")

    def _redo(self):
        """Redo last undone action."""
        if self.undo_manager.can_redo():
            desc = self.undo_manager.get_redo_description()
            if self.undo_manager.redo():
                self.set_status(f"Redone: {desc}")
                self._refresh()
        else:
            self.set_status("Nothing to redo")

    def _save_data(self):
        """Force save all data."""
        try:
            self.expense_manager.save_expenses()
            self.budget_manager.save_budgets()
            self.template_manager.save_templates()
            self.set_status("All data saved")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _refresh(self):
        """Refresh current view."""
        self._update_expense_count()
        if hasattr(self, 'current_view') and hasattr(self.current_view, 'refresh'):
            self.current_view.refresh()
        self.set_status("Refreshed")

    def _on_close(self):
        """Handle window close."""
        if messagebox.askyesno("Confirm Exit", "Are you sure you want to exit?"):
            # Save any pending data
            try:
                self.expense_manager.save_expenses()
                self.budget_manager.save_budgets()
            except:
                pass

            self.visualizer.close_all_figures()
            self.root.destroy()

    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
