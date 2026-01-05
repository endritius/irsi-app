# Epic 10: Main Application & Integration - Implementation Tasks

**Phase:** 10 (Integration)
**Priority:** High
**Dependencies:** All other Epics
**Estimated Tasks:** 35+

---

## Story 10.1: Main Window

**Prerequisites:** All UI components from other Epics

### Task 10.1.1: Create main UI package structure
- [ ] Create `ui/__init__.py`:
```python
"""
UI components for Beauty Salon Expense Manager.
"""

from .main_window import MainWindow

__all__ = ['MainWindow']
```

### Task 10.1.2: Create MainWindow class
- [ ] Create `ui/main_window.py`:
```python
"""
MainWindow - Main application window with menu and tab navigation.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app import Application


class MainWindow:
    """Main application window with menu bar and tab navigation."""

    WINDOW_TITLE = "Beauty Salon Expense Manager"
    MIN_WIDTH = 1024
    MIN_HEIGHT = 768
    DEFAULT_WIDTH = 1280
    DEFAULT_HEIGHT = 800

    def __init__(self, root: tk.Tk, app: 'Application'):
        """
        Initialize with root window and Application instance.

        Args:
            root: The Tk root window (created in main.py)
            app: Application controller instance
        """
        self.root = root
        self.app = app

        self._setup_window()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_tab_navigation()
        self._create_status_bar()
        self._bind_shortcuts()

    def _setup_window(self) -> None:
        """Configure main window properties."""
        self.root.title(self.WINDOW_TITLE)
        self.root.geometry(f"{self.DEFAULT_WIDTH}x{self.DEFAULT_HEIGHT}")
        self.root.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.DEFAULT_WIDTH) // 2
        y = (self.root.winfo_screenheight() - self.DEFAULT_HEIGHT) // 2
        self.root.geometry(f"+{x}+{y}")

        # Window close handler
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)  # Main content area

    def _on_close(self) -> None:
        """Handle window close event."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.app.shutdown()
            self.root.destroy()
```

### Task 10.1.3: Implement menu bar
- [ ] Add menu bar creation:
```python
    def _create_menu_bar(self) -> None:
        """Create application menu bar."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New Expense", command=self._new_expense,
                                   accelerator="Ctrl+N")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Import from CSV...", command=self._import_csv)

        # Export submenu
        self.export_menu = tk.Menu(self.file_menu, tearoff=0)
        self.file_menu.add_cascade(label="Export", menu=self.export_menu)
        self.export_menu.add_command(label="To Excel...", command=self._export_excel)
        self.export_menu.add_command(label="To PDF...", command=self._export_pdf)

        self.file_menu.add_separator()
        self.file_menu.add_command(label="Create Backup...", command=self._create_backup)
        self.file_menu.add_command(label="Restore Backup...", command=self._restore_backup)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Settings...", command=self._show_settings)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._on_close,
                                   accelerator="Alt+F4")

        # Edit menu
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Edit Selected", command=self._edit_selected,
                                   accelerator="Ctrl+E")
        self.edit_menu.add_command(label="Delete Selected", command=self._delete_selected,
                                   accelerator="Delete")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Select All", command=self._select_all,
                                   accelerator="Ctrl+A")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Y")

        # View menu
        self.view_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Dashboard", command=lambda: self._switch_tab(0),
                                   accelerator="F1")
        self.view_menu.add_command(label="Expenses", command=lambda: self._switch_tab(1),
                                   accelerator="F2")
        self.view_menu.add_command(label="Budgets", command=lambda: self._switch_tab(2),
                                   accelerator="F3")
        self.view_menu.add_command(label="Reports", command=lambda: self._switch_tab(3),
                                   accelerator="F4")
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Deleted Items...", command=self._show_deleted)
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Refresh", command=self._refresh,
                                   accelerator="F5")

        # Reports menu
        self.reports_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Reports", menu=self.reports_menu)
        self.reports_menu.add_command(label="Summary Report...", command=self._summary_report)
        self.reports_menu.add_command(label="Category Analysis...", command=self._category_report)
        self.reports_menu.add_command(label="Trend Analysis...", command=self._trend_report)
        self.reports_menu.add_command(label="Vendor Analysis...", command=self._vendor_report)
        self.reports_menu.add_separator()
        self.reports_menu.add_command(label="Custom Report...", command=self._custom_report)
        self.reports_menu.add_separator()
        self.reports_menu.add_command(label="Export as PDF...", command=self._export_pdf)

        # Help menu
        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="User Guide", command=self._show_guide)
        self.help_menu.add_command(label="Keyboard Shortcuts", command=self._show_shortcuts)
        self.help_menu.add_separator()
        self.help_menu.add_command(label="About...", command=self._show_about)
```

### Task 10.1.4: Implement toolbar
- [ ] Add toolbar creation:
```python
    def _create_toolbar(self) -> None:
        """Create toolbar with quick action buttons."""
        self.toolbar = ttk.Frame(self.root)
        self.toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        # Quick action buttons
        ttk.Button(self.toolbar, text="+ New Expense",
                  command=self._new_expense).pack(side=tk.LEFT, padx=2)

        ttk.Separator(self.toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Tab navigation buttons
        ttk.Button(self.toolbar, text="Dashboard",
                  command=lambda: self._switch_tab(0)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Expenses",
                  command=lambda: self._switch_tab(1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Budgets",
                  command=lambda: self._switch_tab(2)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.toolbar, text="Reports",
                  command=lambda: self._switch_tab(3)).pack(side=tk.LEFT, padx=2)

        # Search box on right
        self.search_var = tk.StringVar()
        ttk.Label(self.toolbar, text="Search:").pack(side=tk.RIGHT, padx=2)
        self.search_entry = ttk.Entry(self.toolbar, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.RIGHT, padx=2)
        self.search_entry.bind('<Return>', self._on_search)
```

### Task 10.1.5: Implement tab navigation
- [ ] Add tab navigation:
```python
    def _create_tab_navigation(self) -> None:
        """Create tab-based navigation."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        # Create tab frames
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.expenses_frame = ttk.Frame(self.notebook)
        self.budgets_frame = ttk.Frame(self.notebook)
        self.reports_frame = ttk.Frame(self.notebook)

        # Add tabs
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.expenses_frame, text="Expenses")
        self.notebook.add(self.budgets_frame, text="Budgets")
        self.notebook.add(self.reports_frame, text="Reports")

        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)

    def _switch_tab(self, index: int) -> None:
        """Switch to tab by index."""
        self.notebook.select(index)

    def _on_tab_changed(self, event):
        """Handle tab change event."""
        # Refresh current tab data
        selected = self.notebook.index(self.notebook.select())
        self._refresh_tab(selected)
```

### Task 10.1.6: Implement status bar
- [ ] Add status bar:
```python
    def _create_status_bar(self) -> None:
        """Create status bar at bottom."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.grid(row=3, column=0, sticky="ew")

        # Record count
        self.record_count_var = tk.StringVar(value="Records: 0")
        ttk.Label(self.status_bar, textvariable=self.record_count_var).pack(side=tk.LEFT, padx=10)

        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Filter indicator
        self.filter_var = tk.StringVar(value="Filtered: 0")
        ttk.Label(self.status_bar, textvariable=self.filter_var).pack(side=tk.LEFT, padx=10)

        ttk.Separator(self.status_bar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Last save time
        self.save_time_var = tk.StringVar(value="Last saved: --:--")
        ttk.Label(self.status_bar, textvariable=self.save_time_var).pack(side=tk.LEFT, padx=10)

        # Alert indicator (on right)
        self.alert_var = tk.StringVar(value="")
        self.alert_label = ttk.Label(self.status_bar, textvariable=self.alert_var,
                                     foreground="red")
        self.alert_label.pack(side=tk.RIGHT, padx=10)

    def set_status(self, message: str) -> None:
        """Update status bar message."""
        pass  # Status messages handled by specific variables

    def update_filter_indicator(self, active_count: int) -> None:
        """Update filter indicator in status bar."""
        self.filter_var.set(f"Filtered: {active_count}")

    def update_record_count(self, count: int) -> None:
        """Update record count in status bar."""
        self.record_count_var.set(f"Records: {count}")

    def update_save_time(self, time_str: str) -> None:
        """Update last save time in status bar."""
        self.save_time_var.set(f"Last saved: {time_str}")

    def update_alert_indicator(self, alert_count: int) -> None:
        """Update alert indicator in status bar."""
        if alert_count > 0:
            self.alert_var.set(f"[!] {alert_count} Budget Alert(s)")
        else:
            self.alert_var.set("")
```

### Task 10.1.7: Implement keyboard shortcuts
- [ ] Add keyboard bindings:
```python
    def _bind_shortcuts(self) -> None:
        """Bind keyboard shortcuts."""
        # Global shortcuts
        self.root.bind('<Control-n>', lambda e: self._new_expense())
        self.root.bind('<Control-e>', lambda e: self._edit_selected())
        self.root.bind('<Delete>', lambda e: self._delete_selected())
        self.root.bind('<Control-f>', lambda e: self.search_entry.focus())
        self.root.bind('<F5>', lambda e: self._refresh())
        self.root.bind('<Control-s>', lambda e: self._force_save())
        self.root.bind('<Control-z>', lambda e: self._undo())
        self.root.bind('<Control-y>', lambda e: self._redo())
        self.root.bind('<Escape>', lambda e: self._clear_selection())
        self.root.bind('<Control-q>', lambda e: self._on_close())

        # Navigation shortcuts
        self.root.bind('<F1>', lambda e: self._switch_tab(0))
        self.root.bind('<F2>', lambda e: self._switch_tab(1))
        self.root.bind('<F3>', lambda e: self._switch_tab(2))
        self.root.bind('<F4>', lambda e: self._switch_tab(3))

        self.root.bind('<Control-Key-1>', lambda e: self._switch_tab(0))
        self.root.bind('<Control-Key-2>', lambda e: self._switch_tab(1))
        self.root.bind('<Control-Key-3>', lambda e: self._switch_tab(2))
        self.root.bind('<Control-Key-4>', lambda e: self._switch_tab(3))
```

### Task 10.1.8: Implement placeholder menu handlers
- [ ] Add stub methods for menu actions (to be connected later):
```python
    def _new_expense(self):
        """Open new expense form."""
        pass  # TODO: Connect to expense form

    def _edit_selected(self):
        """Edit selected expense."""
        pass

    def _delete_selected(self):
        """Delete selected expense."""
        pass

    def _select_all(self):
        """Select all items in current view."""
        pass

    def _undo(self):
        """Undo last action."""
        pass

    def _redo(self):
        """Redo last undone action."""
        pass

    def _import_csv(self):
        """Import expenses from CSV."""
        pass

    def _export_excel(self):
        """Export to Excel."""
        pass

    def _export_pdf(self):
        """Export to PDF."""
        pass

    def _create_backup(self):
        """Create backup."""
        pass

    def _restore_backup(self):
        """Restore from backup."""
        pass

    def _show_settings(self):
        """Show settings dialog."""
        pass

    def _show_deleted(self):
        """Show deleted items view."""
        pass

    def _refresh(self):
        """Refresh current view."""
        pass

    def _refresh_tab(self, tab_index: int):
        """Refresh specific tab."""
        pass

    def _summary_report(self):
        """Show summary report."""
        pass

    def _category_report(self):
        """Show category report."""
        pass

    def _trend_report(self):
        """Show trend report."""
        pass

    def _vendor_report(self):
        """Show vendor report."""
        pass

    def _custom_report(self):
        """Show custom report builder."""
        pass

    def _show_guide(self):
        """Show user guide."""
        pass

    def _show_shortcuts(self):
        """Show keyboard shortcuts dialog."""
        pass

    def _show_about(self):
        """Show about dialog."""
        pass

    def _on_search(self, event):
        """Handle search."""
        pass

    def _clear_selection(self):
        """Clear current selection."""
        pass

    def _force_save(self):
        """Force save all data."""
        pass

    def run(self) -> None:
        """Start the main event loop."""
        self.root.mainloop()
```

---

## Story 10.2: Application Startup

**Prerequisites:** Story 10.1, Story 7.1, Story 9.1

### Task 10.2.1: Create Application class
- [ ] Create `app.py`:
```python
"""
Application - Central application controller.
"""

from datetime import datetime
from typing import Callable, Dict, Optional

from persistence.data_manager import DataManager
from managers.expense_manager import ExpenseManager
from managers.budget_manager import BudgetManager
from managers.filter_manager import FilterManager
from managers.template_manager import TemplateManager
from managers.recurring_handler import RecurringHandler
from reports.report_generator import ReportGenerator
from visualization.visualizer import Visualizer
from utils.error_handler import get_error_handler


class Application:
    """Central application controller coordinating all managers."""

    VERSION = "1.0.0"
    APP_NAME = "Beauty Salon Expense Manager"

    def __init__(self):
        """Initialize manager references."""
        self.error_handler = get_error_handler()

        # Manager instances (initialized during startup)
        self.data_manager: Optional[DataManager] = None
        self.expense_manager: Optional[ExpenseManager] = None
        self.budget_manager: Optional[BudgetManager] = None
        self.filter_manager: Optional[FilterManager] = None
        self.template_manager: Optional[TemplateManager] = None
        self.recurring_handler: Optional[RecurringHandler] = None
        self.report_generator: Optional[ReportGenerator] = None
        self.visualizer: Optional[Visualizer] = None

        # Startup state
        self._startup_issues: list = []
        self._startup_time: Optional[datetime] = None

    def initialize(self, progress_callback: Callable[[str, int], None] = None) -> bool:
        """
        Initialize all components with progress callback.

        Args:
            progress_callback: Function(message, percentage) for progress updates

        Returns:
            True if initialization successful
        """
        def update(msg: str, pct: int):
            if progress_callback:
                progress_callback(msg, pct)

        try:
            update("Initializing error handler...", 5)
            # Error handler already initialized in __init__

            update("Initializing data manager...", 10)
            self.data_manager = DataManager()

            update("Loading settings...", 15)
            self.data_manager.load_settings()

            update("Loading expenses...", 25)
            self.expense_manager = ExpenseManager(self.data_manager)

            update("Loading budgets...", 40)
            self.budget_manager = BudgetManager(
                self.data_manager,
                self.expense_manager
            )

            update("Loading templates...", 50)
            self.template_manager = TemplateManager(self.data_manager)

            update("Initializing filter manager...", 60)
            self.filter_manager = FilterManager()

            update("Initializing recurring handler...", 70)
            self.recurring_handler = RecurringHandler(self.expense_manager)

            update("Initializing report generator...", 80)
            self.report_generator = ReportGenerator(
                self.expense_manager,
                self.filter_manager
            )

            update("Initializing visualizer...", 85)
            self.visualizer = Visualizer()

            update("Checking for budget alerts...", 90)
            self._check_budget_alerts()

            update("Processing recurring expenses...", 95)
            self._process_recurring()

            update("Startup complete!", 100)
            self._startup_time = datetime.now()

            return True

        except Exception as e:
            self.error_handler.log_error(f"Startup failed: {e}")
            self._startup_issues.append(str(e))
            return False

    def _check_budget_alerts(self) -> None:
        """Check for budget alerts on startup."""
        if self.budget_manager:
            alerts = self.budget_manager.get_all_alerts()
            if alerts:
                self._startup_issues.extend([
                    f"Budget alert: {a['message']}" for a in alerts
                ])

    def _process_recurring(self) -> None:
        """Process recurring expenses on startup."""
        if self.recurring_handler:
            auto_generate, reminders = self.recurring_handler.check_due_expenses()

            # Auto-generate expenses
            if auto_generate:
                generated = self.recurring_handler.process_auto_generate(auto_generate)
                if generated:
                    self._startup_issues.append(
                        f"Auto-generated {len(generated)} recurring expense(s)"
                    )

            # Add reminders to issues
            for exp in reminders:
                self._startup_issues.append(
                    f"Recurring due: {exp.vendor} - L {exp.amount:,.2f}"
                )

    def shutdown(self) -> None:
        """Clean shutdown with final save."""
        self.error_handler.log_info("Application shutting down...")

        try:
            if self.expense_manager:
                self.expense_manager.save_expenses()
            if self.budget_manager:
                self.budget_manager.save_budgets()
            if self.template_manager:
                self.template_manager.save_templates()
            if self.data_manager:
                self.data_manager.save_settings()
        except Exception as e:
            self.error_handler.log_error(f"Error during shutdown: {e}")

        self.error_handler.log_info("Shutdown complete")

    def get_startup_summary(self) -> Dict:
        """Get summary of startup results."""
        return {
            'success': len(self._startup_issues) == 0 or
                      all('alert' in i.lower() or 'recurring' in i.lower()
                          for i in self._startup_issues),
            'expense_count': len(self.expense_manager.get_all_expenses())
                            if self.expense_manager else 0,
            'budget_count': len(self.budget_manager.get_all_budgets())
                           if self.budget_manager else 0,
            'issues': self._startup_issues,
            'startup_time': self._startup_time
        }
```

### Task 10.2.2: Create main entry point
- [ ] Create `main.py`:
```python
"""
Main entry point for Beauty Salon Expense Manager.
"""

import sys
import tkinter as tk

from app import Application
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen


def main():
    """Main application entry point."""
    # Create root window (hidden initially)
    root = tk.Tk()
    root.withdraw()

    # Show splash screen
    splash = SplashScreen(root)

    # Create application
    app = Application()

    # Initialize with progress updates
    success = app.initialize(progress_callback=splash.update_progress)

    # Close splash
    splash.close()

    if not success:
        from tkinter import messagebox
        messagebox.showerror(
            "Startup Error",
            "Failed to initialize application. Check logs for details."
        )
        sys.exit(1)

    # Show main window
    root.deiconify()
    main_window = MainWindow(root, app)

    # Show startup summary if there are issues
    summary = app.get_startup_summary()
    if summary['issues']:
        # Show startup alerts dialog
        from ui.dialogs.startup_alerts import show_startup_alerts
        show_startup_alerts(root, summary['issues'])

    # Run main loop
    main_window.run()


if __name__ == "__main__":
    main()
```

### Task 10.2.3: Create SplashScreen
- [ ] Create `ui/splash_screen.py`:
```python
"""
SplashScreen - Shown during application startup.
"""

import tkinter as tk
from tkinter import ttk


class SplashScreen:
    """Splash screen shown during application startup."""

    def __init__(self, parent):
        """Create splash window."""
        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)

        # Size and center
        width, height = 400, 200
        x = (self.window.winfo_screenwidth() - width) // 2
        y = (self.window.winfo_screenheight() - height) // 2
        self.window.geometry(f"{width}x{height}+{x}+{y}")

        # Content frame
        frame = ttk.Frame(self.window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(frame, text="Beauty Salon Expense Manager",
                 font=('Helvetica', 16, 'bold')).pack(pady=10)
        ttk.Label(frame, text="Version 1.0.0",
                 font=('Helvetica', 10)).pack()

        # Progress bar
        self.progress = ttk.Progressbar(frame, length=300, mode='determinate')
        self.progress.pack(pady=20)

        # Status message
        self.status_var = tk.StringVar(value="Starting...")
        ttk.Label(frame, textvariable=self.status_var).pack()

        self.window.update()

    def update_progress(self, message: str, percentage: int) -> None:
        """Update progress display."""
        self.status_var.set(message)
        self.progress['value'] = percentage
        self.window.update()

    def close(self) -> None:
        """Close splash screen."""
        self.window.destroy()
```

---

## Story 10.3: Recurring Expense Handler

**Prerequisites:** Story 2.1

### Task 10.3.1: Create RecurringHandler class
- [ ] Create `managers/recurring_handler.py`:
```python
"""
RecurringHandler - Handles recurring expense generation and reminders.
"""

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import List, Optional, Tuple
import uuid

from models.expense import Expense
from managers.expense_manager import ExpenseManager


class RecurringHandler:
    """Handles recurring expense generation and reminders."""

    def __init__(self, expense_manager: ExpenseManager):
        """Initialize with ExpenseManager."""
        self.expense_manager = expense_manager

    def check_due_expenses(self) -> Tuple[List[Expense], List[Expense]]:
        """
        Check for due recurring expenses.

        Returns:
            Tuple of (auto_generate list, reminder list)
        """
        today = datetime.now().date()
        auto_generate = []
        reminders = []

        for expense in self.expense_manager.get_recurring_expenses():
            if not expense.next_due_date:
                continue

            due_date = expense.next_due_date.date()
            if due_date <= today:
                if expense.recurring_action == 'auto_generate':
                    auto_generate.append(expense)
                else:  # reminder
                    reminders.append(expense)

        return auto_generate, reminders

    def process_auto_generate(self, due_expenses: List[Expense]) -> List[str]:
        """
        Auto-generate expenses.

        Returns:
            List of generated expense IDs
        """
        generated_ids = []

        for original in due_expenses:
            # Create new expense from template
            new_expense = self._create_from_recurring(original, original.next_due_date)

            # Add the new expense
            expense_id = self.expense_manager.add_expense(new_expense)
            generated_ids.append(expense_id)

            # Update the original's next due date
            next_date = self._calculate_next_due_date(original)
            self.expense_manager.update_expense(original.expense_id, {
                'last_recurring_date': original.next_due_date,
                'next_due_date': next_date
            })

        return generated_ids

    def _calculate_next_due_date(self, expense: Expense) -> Optional[datetime]:
        """Calculate next due date based on frequency."""
        if not expense.next_due_date:
            return None

        current = expense.next_due_date
        frequency = expense.recurring_type

        if frequency == 'daily':
            return current + timedelta(days=1)
        elif frequency == 'weekly':
            return current + timedelta(weeks=1)
        elif frequency == 'biweekly':
            return current + timedelta(weeks=2)
        elif frequency == 'monthly':
            return current + relativedelta(months=1)
        elif frequency == 'quarterly':
            return current + relativedelta(months=3)
        elif frequency == 'annually':
            return current + relativedelta(years=1)

        return None

    def _create_from_recurring(self, original: Expense, due_date: datetime) -> Expense:
        """Create new expense from recurring template."""
        return Expense(
            expense_id=str(uuid.uuid4()),
            amount=original.amount,
            date=due_date,
            category=original.category,
            subcategory=original.subcategory,
            vendor=original.vendor,
            payment_method=original.payment_method,
            description=f"{original.description} (auto-generated)",
            tags=original.tags.copy(),
            is_recurring=False,  # Generated expense is not recurring
            recurring_parent_id=original.expense_id
        )
```

### Task 10.3.2: Create recurring reminder dialog
- [ ] Create `ui/dialogs/recurring_reminder.py`:
  - List of due recurring expenses
  - Checkboxes for selection
  - Generate Selected / Add Manually / Dismiss buttons
  - "Don't show today" checkbox

---

## Story 10.4: Settings Dialog

**Prerequisites:** Story 10.1, Story 7.1

### Task 10.4.1: Create SettingsDialog class
- [ ] Create `ui/dialogs/settings_dialog.py`:
```python
"""
SettingsDialog - Application settings configuration.
"""

import tkinter as tk
from tkinter import ttk, filedialog


class SettingsDialog:
    """Settings dialog with tabbed interface."""

    def __init__(self, parent, data_manager):
        """Create settings dialog."""
        self.data_manager = data_manager
        self.settings = data_manager.get_settings().copy()
        self.result = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.dialog)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self._create_general_tab()
        self._create_backup_tab()
        self._create_alerts_tab()
        self._create_display_tab()

        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self._cancel).pack(side=tk.RIGHT)

    def _create_general_tab(self):
        """Create general settings tab."""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="General")

        # Salon Information
        ttk.Label(tab, text="Salon Information", font=('', 10, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Label(tab, text="Salon Name:").grid(row=1, column=0, sticky=tk.W)
        self.salon_name = ttk.Entry(tab, width=40)
        self.salon_name.insert(0, self.settings.get('salon_name', ''))
        self.salon_name.grid(row=1, column=1, sticky=tk.W, pady=2)

        ttk.Label(tab, text="Address:").grid(row=2, column=0, sticky=tk.W)
        self.salon_address = ttk.Entry(tab, width=40)
        self.salon_address.insert(0, self.settings.get('salon_address', ''))
        self.salon_address.grid(row=2, column=1, sticky=tk.W, pady=2)

        ttk.Label(tab, text="Contact:").grid(row=3, column=0, sticky=tk.W)
        self.salon_contact = ttk.Entry(tab, width=40)
        self.salon_contact.insert(0, self.settings.get('salon_contact', ''))
        self.salon_contact.grid(row=3, column=1, sticky=tk.W, pady=2)

        # Data Options
        ttk.Label(tab, text="Data Options", font=('', 10, 'bold')).grid(
            row=4, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))

        self.auto_save_var = tk.BooleanVar(value=self.settings.get('auto_save', True))
        ttk.Checkbutton(tab, text="Auto-save after each change",
                       variable=self.auto_save_var).grid(row=5, column=0, columnspan=2, sticky=tk.W)

        self.check_duplicates_var = tk.BooleanVar(value=self.settings.get('check_duplicates', True))
        ttk.Checkbutton(tab, text="Check for duplicate expenses",
                       variable=self.check_duplicates_var).grid(row=6, column=0, columnspan=2, sticky=tk.W)

        self.validate_startup_var = tk.BooleanVar(value=self.settings.get('validate_on_startup', True))
        ttk.Checkbutton(tab, text="Validate data on startup",
                       variable=self.validate_startup_var).grid(row=7, column=0, columnspan=2, sticky=tk.W)

    def _create_backup_tab(self):
        """Create backup settings tab."""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Backup")

        self.auto_backup_var = tk.BooleanVar(value=self.settings.get('auto_backup', False))
        ttk.Checkbutton(tab, text="Enable automatic backup",
                       variable=self.auto_backup_var).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        ttk.Label(tab, text="Backup frequency:").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.backup_freq = ttk.Combobox(tab, values=['Daily', 'Weekly', 'Monthly'], state='readonly')
        self.backup_freq.set(self.settings.get('backup_frequency', 'Weekly'))
        self.backup_freq.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(tab, text="Backup location:").grid(row=2, column=0, sticky=tk.W)
        backup_frame = ttk.Frame(tab)
        backup_frame.grid(row=2, column=1, sticky=tk.W)
        self.backup_path = ttk.Entry(backup_frame, width=30)
        self.backup_path.insert(0, self.settings.get('backup_path', 'backups/'))
        self.backup_path.pack(side=tk.LEFT)
        ttk.Button(backup_frame, text="Browse",
                  command=self._browse_backup_path).pack(side=tk.LEFT, padx=5)

        ttk.Label(tab, text="Keep backups for (days):").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.backup_days = ttk.Spinbox(tab, from_=7, to=365, width=10)
        self.backup_days.set(self.settings.get('backup_retention_days', 30))
        self.backup_days.grid(row=3, column=1, sticky=tk.W)

        ttk.Button(tab, text="Create Backup Now").grid(row=5, column=0, pady=20)
        ttk.Button(tab, text="Restore from Backup").grid(row=5, column=1, pady=20, sticky=tk.W)

    def _create_alerts_tab(self):
        """Create alerts settings tab."""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Alerts")

        self.enable_alerts_var = tk.BooleanVar(value=self.settings.get('enable_budget_alerts', True))
        ttk.Checkbutton(tab, text="Enable budget alerts",
                       variable=self.enable_alerts_var).grid(row=0, column=0, columnspan=2, sticky=tk.W)

        ttk.Label(tab, text="Warning threshold (%):").grid(row=1, column=0, sticky=tk.W, pady=10)
        self.warning_threshold = ttk.Spinbox(tab, from_=50, to=100, width=10)
        self.warning_threshold.set(self.settings.get('warning_threshold', 80))
        self.warning_threshold.grid(row=1, column=1, sticky=tk.W)

        self.alerts_on_startup_var = tk.BooleanVar(value=self.settings.get('show_alerts_on_startup', True))
        ttk.Checkbutton(tab, text="Show alerts on startup",
                       variable=self.alerts_on_startup_var).grid(row=2, column=0, columnspan=2, sticky=tk.W)

        self.alert_before_exceed_var = tk.BooleanVar(value=self.settings.get('alert_before_exceed', True))
        ttk.Checkbutton(tab, text="Show alert before exceeding budget",
                       variable=self.alert_before_exceed_var).grid(row=3, column=0, columnspan=2, sticky=tk.W)

        self.recurring_reminders_var = tk.BooleanVar(value=self.settings.get('recurring_reminders', True))
        ttk.Checkbutton(tab, text="Show recurring expense reminders",
                       variable=self.recurring_reminders_var).grid(row=4, column=0, columnspan=2, sticky=tk.W)

    def _create_display_tab(self):
        """Create display settings tab."""
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Display")

        ttk.Label(tab, text="Default view on startup:").grid(row=0, column=0, sticky=tk.W)
        self.default_view = ttk.Combobox(tab, values=['Dashboard', 'Expenses', 'Budgets', 'Reports'],
                                         state='readonly')
        self.default_view.set(self.settings.get('default_view', 'Dashboard'))
        self.default_view.grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Label(tab, text="Rows per page:").grid(row=1, column=0, sticky=tk.W)
        self.rows_per_page = ttk.Combobox(tab, values=['25', '50', '100', '200'], state='readonly')
        self.rows_per_page.set(str(self.settings.get('rows_per_page', 50)))
        self.rows_per_page.grid(row=1, column=1, sticky=tk.W, pady=5)

        self.alt_row_colors_var = tk.BooleanVar(value=self.settings.get('alternating_row_colors', True))
        ttk.Checkbutton(tab, text="Alternating row colors",
                       variable=self.alt_row_colors_var).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        self.show_chart_labels_var = tk.BooleanVar(value=self.settings.get('show_chart_labels', True))
        ttk.Checkbutton(tab, text="Show data labels on charts",
                       variable=self.show_chart_labels_var).grid(row=3, column=0, columnspan=2, sticky=tk.W)

    def _browse_backup_path(self):
        """Browse for backup directory."""
        path = filedialog.askdirectory()
        if path:
            self.backup_path.delete(0, tk.END)
            self.backup_path.insert(0, path)

    def _save(self):
        """Save settings."""
        self.settings.update({
            'salon_name': self.salon_name.get(),
            'salon_address': self.salon_address.get(),
            'salon_contact': self.salon_contact.get(),
            'auto_save': self.auto_save_var.get(),
            'check_duplicates': self.check_duplicates_var.get(),
            'validate_on_startup': self.validate_startup_var.get(),
            'auto_backup': self.auto_backup_var.get(),
            'backup_frequency': self.backup_freq.get(),
            'backup_path': self.backup_path.get(),
            'backup_retention_days': int(self.backup_days.get()),
            'enable_budget_alerts': self.enable_alerts_var.get(),
            'warning_threshold': int(self.warning_threshold.get()),
            'show_alerts_on_startup': self.alerts_on_startup_var.get(),
            'alert_before_exceed': self.alert_before_exceed_var.get(),
            'recurring_reminders': self.recurring_reminders_var.get(),
            'default_view': self.default_view.get(),
            'rows_per_page': int(self.rows_per_page.get()),
            'alternating_row_colors': self.alt_row_colors_var.get(),
            'show_chart_labels': self.show_chart_labels_var.get(),
        })

        self.data_manager.update_settings(self.settings)
        self.result = self.settings
        self.dialog.destroy()

    def _cancel(self):
        """Cancel without saving."""
        self.dialog.destroy()
```

---

## Story 10.5: Data Load Summary

**Prerequisites:** Story 10.2, Story 9.5

### Task 10.5.1: Create DataSummaryDialog
- [ ] Create `ui/dialogs/data_summary_dialog.py`:
  - Loaded counts display
  - Issues found table
  - Export Issues button
  - OK button
  - "Don't show if no issues" checkbox

### Task 10.5.2: Create startup alerts dialog
- [ ] Create `ui/dialogs/startup_alerts.py`:
```python
"""
StartupAlertsDialog - Shows alerts and reminders on startup.
"""

import tkinter as tk
from tkinter import ttk
from typing import List


def show_startup_alerts(parent: tk.Widget, issues: List[str]) -> None:
    """
    Show startup alerts dialog.

    Args:
        parent: Parent widget
        issues: List of alert messages to display
    """
    if not issues:
        return

    dialog = StartupAlertsDialog(parent, issues)
    dialog.dialog.wait_window()


class StartupAlertsDialog:
    """Dialog showing startup alerts and reminders."""

    def __init__(self, parent: tk.Widget, issues: List[str]):
        """Create startup alerts dialog."""
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Startup Notifications")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        self._create_widgets(issues)

    def _create_widgets(self, issues: List[str]) -> None:
        """Create dialog widgets."""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Header
        ttk.Label(frame, text="Startup Notifications",
                 font=('Helvetica', 12, 'bold')).pack(anchor=tk.W)
        ttk.Label(frame, text=f"{len(issues)} item(s) require your attention"
                 ).pack(anchor=tk.W, pady=(0, 10))

        # Alerts list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                  font=('Helvetica', 10))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # Categorize issues
        budget_alerts = [i for i in issues if 'budget' in i.lower()]
        recurring_alerts = [i for i in issues if 'recurring' in i.lower()]
        other_alerts = [i for i in issues if i not in budget_alerts and i not in recurring_alerts]

        if budget_alerts:
            self.listbox.insert(tk.END, "--- Budget Alerts ---")
            for alert in budget_alerts:
                self.listbox.insert(tk.END, f"  • {alert}")

        if recurring_alerts:
            self.listbox.insert(tk.END, "--- Recurring Expenses ---")
            for alert in recurring_alerts:
                self.listbox.insert(tk.END, f"  • {alert}")

        if other_alerts:
            self.listbox.insert(tk.END, "--- Other ---")
            for alert in other_alerts:
                self.listbox.insert(tk.END, f"  • {alert}")

        # Buttons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(btn_frame, text="Dismiss",
                  command=self.dialog.destroy).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="View Details",
                  command=self._view_details).pack(side=tk.RIGHT, padx=5)

    def _view_details(self) -> None:
        """View details of selected alert."""
        selection = self.listbox.curselection()
        if selection:
            # Navigate to relevant section based on alert type
            pass  # TODO: Implement navigation
```

---

## Completion Checklist

### Story 10.1: Main Window
- [ ] MainWindow class created
- [ ] Menu bar working
- [ ] Toolbar working
- [ ] Tab navigation working
- [ ] Status bar working
- [ ] Keyboard shortcuts working

### Story 10.2: Application Startup
- [ ] Application class created
- [ ] main.py entry point created
- [ ] SplashScreen working
- [ ] All managers initialized
- [ ] Startup alerts shown

### Story 10.3: Recurring Handler
- [ ] RecurringHandler class created
- [ ] Auto-generate working
- [ ] Reminders working
- [ ] Next due date calculation working
- [ ] Reminder dialog created

### Story 10.4-10.5: Settings and Summary
- [ ] Settings dialog created
- [ ] All settings tabs working
- [ ] Data summary dialog created
- [ ] Startup alerts dialog created

---

## Next Steps

After completing Epic 10, proceed to:
- **Epic 11: Enhancements** - Optional improvements
