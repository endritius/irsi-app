# Epic 11: Optional Enhancements - Implementation Tasks

**Phase:** 11 (Optional)
**Priority:** Low
**Dependencies:** All Core Epics
**Estimated Tasks:** 30+

These tasks are optional enhancements that can be implemented after the core functionality is complete.

---

## Story 11.1: Undo/Redo System

**Prerequisites:** Story 2.1 (ExpenseManager), Story 4.1 (BudgetManager)

### Task 11.1.1: Create UndoAction dataclass
- [ ] Create `managers/undo_manager.py`:
```python
"""
UndoManager - Manages undo/redo stack for expense operations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional
import copy


class ActionType(Enum):
    """Types of undoable actions."""
    ADD_EXPENSE = "add_expense"
    EDIT_EXPENSE = "edit_expense"
    DELETE_EXPENSE = "delete_expense"
    ADD_BUDGET = "add_budget"
    EDIT_BUDGET = "edit_budget"
    DELETE_BUDGET = "delete_budget"


@dataclass
class UndoAction:
    """Represents an undoable action."""
    action_type: ActionType
    entity_id: str
    data_before: Dict
    data_after: Dict
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""

    def get_undo_description(self) -> str:
        """Get description for undo menu."""
        return f"Undo: {self.description or self.action_type.value}"

    def get_redo_description(self) -> str:
        """Get description for redo menu."""
        return f"Redo: {self.description or self.action_type.value}"
```

### Task 11.1.2: Create UndoManager class
- [ ] Add UndoManager class:
```python
class UndoManager:
    """Manages undo/redo stack for expense operations."""

    MAX_UNDO_HISTORY = 10

    def __init__(self):
        """Initialize empty stacks and callbacks dict."""
        self._undo_stack: List[UndoAction] = []
        self._redo_stack: List[UndoAction] = []
        self._callbacks: Dict[str, Callable] = {}
        self._state_change_callback: Optional[Callable] = None

    def register_callback(self, name: str, callback: Callable) -> None:
        """Register callback for undo/redo operations."""
        self._callbacks[name] = callback

    def set_state_change_callback(self, callback: Callable) -> None:
        """Set callback to be called when undo/redo state changes."""
        self._state_change_callback = callback

    def _notify_state_change(self) -> None:
        """Notify listeners that undo/redo state changed."""
        if self._state_change_callback:
            self._state_change_callback()

    def record_action(
        self,
        action_type: ActionType,
        entity_id: str,
        data_before: Dict,
        data_after: Dict,
        description: str = ""
    ) -> None:
        """Record an action for potential undo."""
        action = UndoAction(
            action_type=action_type,
            entity_id=entity_id,
            data_before=copy.deepcopy(data_before) if data_before else {},
            data_after=copy.deepcopy(data_after) if data_after else {},
            description=description
        )

        self._undo_stack.append(action)

        # Limit stack size
        if len(self._undo_stack) > self.MAX_UNDO_HISTORY:
            self._undo_stack.pop(0)

        # Clear redo stack on new action
        self._redo_stack.clear()

        self._notify_state_change()

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    def undo(self) -> Optional[UndoAction]:
        """Undo the last action."""
        if not self.can_undo():
            return None

        action = self._undo_stack.pop()
        self._redo_stack.append(action)

        # Execute undo callback
        callback_name = f"undo_{action.action_type.value}"
        if callback_name in self._callbacks:
            self._callbacks[callback_name](action)

        self._notify_state_change()
        return action

    def redo(self) -> Optional[UndoAction]:
        """Redo the last undone action."""
        if not self.can_redo():
            return None

        action = self._redo_stack.pop()
        self._undo_stack.append(action)

        # Execute redo callback
        callback_name = f"redo_{action.action_type.value}"
        if callback_name in self._callbacks:
            self._callbacks[callback_name](action)

        self._notify_state_change()
        return action

    def get_undo_description(self) -> Optional[str]:
        """Get description of next undo action."""
        if not self.can_undo():
            return None
        return self._undo_stack[-1].get_undo_description()

    def get_redo_description(self) -> Optional[str]:
        """Get description of next redo action."""
        if not self.can_redo():
            return None
        return self._redo_stack[-1].get_redo_description()

    def clear_history(self) -> None:
        """Clear all undo/redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        self._notify_state_change()
```

### Task 11.1.3: Integrate with ExpenseManager
- [ ] Add undo recording to ExpenseManager CRUD operations
- [ ] Register undo/redo callbacks

### Task 11.1.4: Update Edit menu
- [ ] Update Undo menu item with description
- [ ] Update Redo menu item with description
- [ ] Enable/disable based on availability

### Task 11.1.5: Create UndoManager tests
- [ ] Create `tests/test_managers/test_undo_manager.py`

---

## Story 11.2: Keyboard Navigation

**Prerequisites:** Story 10.1 (MainWindow)

### Task 11.2.1: Create keyboard shortcuts dialog
- [ ] Create `ui/dialogs/shortcuts_dialog.py`:
```python
"""
KeyboardShortcutsDialog - Shows available keyboard shortcuts.
"""

import tkinter as tk
from tkinter import ttk


class KeyboardShortcutsDialog:
    """Dialog showing all keyboard shortcuts."""

    SHORTCUTS = {
        'General': [
            ('Ctrl+N', 'New expense'),
            ('Ctrl+E', 'Edit selected'),
            ('Delete', 'Delete selected'),
            ('Ctrl+F', 'Focus search'),
            ('F5', 'Refresh'),
            ('Ctrl+S', 'Save'),
            ('Ctrl+Z', 'Undo'),
            ('Ctrl+Y', 'Redo'),
            ('Escape', 'Close/Clear'),
            ('Ctrl+Q', 'Exit'),
        ],
        'Navigation': [
            ('Ctrl+1', 'Dashboard'),
            ('Ctrl+2', 'Expenses'),
            ('Ctrl+3', 'Budgets'),
            ('Ctrl+4', 'Reports'),
            ('Tab', 'Next field'),
            ('Shift+Tab', 'Previous field'),
        ],
        'List Navigation': [
            ('Up/Down', 'Select item'),
            ('Enter', 'Open item'),
            ('Home/End', 'First/Last item'),
            ('Space', 'Toggle selection'),
        ],
    }

    def __init__(self, parent):
        """Create shortcuts dialog."""
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Keyboard Shortcuts")
        self.dialog.geometry("400x500")
        self.dialog.transient(parent)

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Scrollable frame
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add shortcuts by category
        for category, shortcuts in self.SHORTCUTS.items():
            ttk.Label(scrollable_frame, text=category,
                     font=('', 11, 'bold')).pack(anchor=tk.W, pady=(10, 5))

            for shortcut, description in shortcuts:
                row = ttk.Frame(scrollable_frame)
                row.pack(fill=tk.X, pady=2)
                ttk.Label(row, text=shortcut, width=15,
                         font=('Courier', 10)).pack(side=tk.LEFT)
                ttk.Label(row, text=description).pack(side=tk.LEFT, padx=10)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Close button
        ttk.Button(self.dialog, text="Close",
                  command=self.dialog.destroy).pack(pady=10)
```

### Task 11.2.2: Implement list navigation
- [ ] Add Up/Down arrow key handlers to expense list
- [ ] Add Home/End key handlers
- [ ] Add Space for toggle selection
- [ ] Add Enter to open selected item

### Task 11.2.3: Implement form navigation
- [ ] Tab moves to next field
- [ ] Shift+Tab moves to previous field
- [ ] Enter submits form (where appropriate)
- [ ] Escape cancels/closes

---

## Story 11.3: Enhanced Data Validation Summary

**Prerequisites:** Story 9.5 (DataIntegrityValidator), Story 10.5

### Task 11.3.1: Enhance validation summary dialog
- [ ] Add severity column (Warning/Error)
- [ ] Add sortable table columns
- [ ] Add "View All" button for detailed list
- [ ] Highlight critical issues separately

### Task 11.3.2: Add user preferences
- [ ] "Don't show for auto-corrected issues" checkbox
- [ ] Add setting to enable/disable on startup
- [ ] Option to show only errors (hide warnings)

---

## Story 11.4: Enhanced Template Manager UI

**Prerequisites:** Story 2.10 (Templates), Story 10.1

### Task 11.4.1: Create enhanced template manager dialog
- [ ] Create `ui/dialogs/template_manager_dialog.py`:
```python
"""
TemplateManagerDialog - Enhanced template management interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox


class TemplateManagerDialog:
    """Enhanced template management dialog."""

    def __init__(self, parent, template_manager):
        """Create template manager dialog."""
        self.template_manager = template_manager
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Expense Templates")
        self.dialog.geometry("700x500")
        self.dialog.transient(parent)

        self._create_widgets()
        self._load_templates()

    def _create_widgets(self):
        """Create dialog widgets."""
        # Quick add section
        quick_frame = ttk.LabelFrame(self.dialog, text="Quick Add", padding=10)
        quick_frame.pack(fill=tk.X, padx=10, pady=10)

        self.quick_buttons_frame = ttk.Frame(quick_frame)
        self.quick_buttons_frame.pack(fill=tk.X)

        # Search and filter
        filter_frame = ttk.Frame(self.dialog)
        filter_frame.pack(fill=tk.X, padx=10)

        ttk.Label(filter_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search)
        ttk.Entry(filter_frame, textvariable=self.search_var,
                 width=30).pack(side=tk.LEFT, padx=5)

        ttk.Label(filter_frame, text="Sort by:").pack(side=tk.LEFT, padx=(20, 5))
        self.sort_var = tk.StringVar(value="Most Used")
        sort_combo = ttk.Combobox(filter_frame, textvariable=self.sort_var,
                                  values=['Most Used', 'Name', 'Category', 'Last Used'],
                                  state='readonly', width=15)
        sort_combo.pack(side=tk.LEFT)
        sort_combo.bind('<<ComboboxSelected>>', self._on_sort_change)

        # Template list
        list_frame = ttk.Frame(self.dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        columns = ('name', 'category', 'amount', 'uses', 'last_used')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings')

        self.tree.heading('name', text='Name')
        self.tree.heading('category', text='Category')
        self.tree.heading('amount', text='Amount')
        self.tree.heading('uses', text='Uses')
        self.tree.heading('last_used', text='Last Used')

        self.tree.column('name', width=150)
        self.tree.column('category', width=100)
        self.tree.column('amount', width=100)
        self.tree.column('uses', width=60)
        self.tree.column('last_used', width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                  command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Context menu
        self.tree.bind('<Button-3>', self._show_context_menu)
        self.tree.bind('<Double-1>', self._on_use_template)

        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Button(btn_frame, text="New Template",
                  command=self._new_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Edit",
                  command=self._edit_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Delete",
                  command=self._delete_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Use Template",
                  command=self._on_use_template).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Close",
                  command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _load_templates(self):
        """Load templates into tree."""
        self.tree.delete(*self.tree.get_children())

        templates = self.template_manager.get_all_templates()

        # Apply sort
        sort_key = self.sort_var.get()
        if sort_key == 'Most Used':
            templates.sort(key=lambda t: t.use_count, reverse=True)
        elif sort_key == 'Name':
            templates.sort(key=lambda t: t.name.lower())
        elif sort_key == 'Category':
            templates.sort(key=lambda t: t.category)
        elif sort_key == 'Last Used':
            templates.sort(key=lambda t: t.last_used or datetime.min, reverse=True)

        # Apply search filter
        search = self.search_var.get().lower()
        if search:
            templates = [t for t in templates if
                        search in t.name.lower() or
                        search in t.category.lower() or
                        search in t.vendor.lower()]

        # Populate tree
        for template in templates:
            last_used = template.last_used.strftime('%d/%m/%Y') if template.last_used else 'Never'
            self.tree.insert('', tk.END, values=(
                template.name,
                template.category,
                f"L {template.typical_amount:,.2f}",
                template.use_count,
                last_used
            ), tags=(template.template_id,))

        # Update quick add buttons
        self._update_quick_buttons(templates[:5])

    def _update_quick_buttons(self, top_templates):
        """Update quick add buttons."""
        for widget in self.quick_buttons_frame.winfo_children():
            widget.destroy()

        for template in top_templates:
            btn = ttk.Button(self.quick_buttons_frame, text=template.name,
                           command=lambda t=template: self._use_template(t))
            btn.pack(side=tk.LEFT, padx=2)

        ttk.Button(self.quick_buttons_frame, text="+ New",
                  command=self._new_template).pack(side=tk.LEFT, padx=10)

    def _on_search(self, *args):
        """Handle search change."""
        self._load_templates()

    def _on_sort_change(self, event):
        """Handle sort change."""
        self._load_templates()

    def _show_context_menu(self, event):
        """Show context menu."""
        pass  # TODO: Implement context menu

    def _on_use_template(self, event=None):
        """Use selected template."""
        selection = self.tree.selection()
        if selection:
            template_id = self.tree.item(selection[0])['tags'][0]
            template = self.template_manager.get_template(template_id)
            if template:
                self._use_template(template)

    def _use_template(self, template):
        """Use a template to create expense."""
        pass  # TODO: Open expense form with template data

    def _new_template(self):
        """Create new template."""
        pass  # TODO: Open template edit dialog

    def _edit_template(self):
        """Edit selected template."""
        pass  # TODO: Open template edit dialog

    def _delete_template(self):
        """Delete selected template."""
        selection = self.tree.selection()
        if not selection:
            return

        if messagebox.askyesno("Delete Template",
                              "Are you sure you want to delete this template?"):
            template_id = self.tree.item(selection[0])['tags'][0]
            self.template_manager.delete_template(template_id)
            self._load_templates()
```

### Task 11.4.2: Implement template editing
- [ ] Create template edit dialog
- [ ] Connect to expense form

---

## Story 11.5: Print Support

**Prerequisites:** Story 8.1 (PDF Export)

### Task 11.5.1: Create print preview dialog
- [ ] Create `ui/dialogs/print_preview.py`:
  - Print preview canvas
  - Page navigation
  - Zoom controls
  - Print button

### Task 11.5.2: Implement page setup
- [ ] Paper size selection
- [ ] Orientation selection
- [ ] Margin settings
- [ ] Header/footer options

### Task 11.5.3: Implement print action
- [ ] System print dialog integration
- [ ] Print to PDF option
- [ ] Save as PDF option

---

## Story 11.6: Auto-Export Scheduling

**Prerequisites:** Story 8.1 (PDF), Story 8.2 (Excel), Story 10.2

### Task 11.6.1: Create AutoExportConfig dataclass
- [ ] Create `exports/auto_export.py`:
```python
"""
AutoExporter - Handles scheduled automatic report exports.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class ExportSchedule(Enum):
    """Export schedule options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


@dataclass
class AutoExportConfig:
    """Configuration for automatic exports."""
    enabled: bool = False
    schedule: ExportSchedule = ExportSchedule.MONTHLY
    day_of_month: int = 1
    custom_days: int = 30
    export_pdf: bool = True
    export_excel: bool = True
    export_csv: bool = False
    include_summary: bool = True
    include_category_breakdown: bool = True
    include_budget_comparison: bool = True
    include_expense_list: bool = False
    output_path: str = "exports/"
    filename_pattern: str = "expense_report_{year}_{month}"
    last_export: Optional[datetime] = None
    next_export: Optional[datetime] = None
```

### Task 11.6.2: Create AutoExporter class
- [ ] Add AutoExporter class:
```python
class AutoExporter:
    """Handles scheduled automatic report exports."""

    def __init__(self, config: AutoExportConfig, pdf_exporter, excel_exporter):
        """Initialize with config and exporters."""
        self.config = config
        self.pdf_exporter = pdf_exporter
        self.excel_exporter = excel_exporter

    def is_export_due(self) -> bool:
        """Check if export is due."""
        if not self.config.enabled:
            return False

        if not self.config.next_export:
            return True

        return datetime.now() >= self.config.next_export

    def calculate_next_export(self) -> datetime:
        """Calculate next export date based on schedule."""
        now = datetime.now()

        if self.config.schedule == ExportSchedule.DAILY:
            return now.replace(hour=0, minute=0, second=0) + timedelta(days=1)
        elif self.config.schedule == ExportSchedule.WEEKLY:
            days_until_monday = (7 - now.weekday()) % 7 or 7
            return now.replace(hour=0, minute=0, second=0) + timedelta(days=days_until_monday)
        elif self.config.schedule == ExportSchedule.MONTHLY:
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=self.config.day_of_month)
            else:
                next_month = now.replace(month=now.month + 1, day=self.config.day_of_month)
            return next_month.replace(hour=0, minute=0, second=0)
        else:  # Custom
            return now + timedelta(days=self.config.custom_days)

    def run_export(self, report_generator, expenses_df) -> List[str]:
        """Execute the automatic export."""
        exported_files = []
        now = datetime.now()

        # Generate filename
        filename_base = self.config.filename_pattern.format(
            year=now.year,
            month=str(now.month).zfill(2)
        )

        output_dir = self.config.output_path

        # Export PDF
        if self.config.export_pdf:
            pdf_path = f"{output_dir}/{filename_base}.pdf"
            self.pdf_exporter.export_report(pdf_path, self._get_pdf_config(), expenses_df)
            exported_files.append(pdf_path)

        # Export Excel
        if self.config.export_excel:
            excel_path = f"{output_dir}/{filename_base}.xlsx"
            self.excel_exporter.export(excel_path, self._get_excel_config(), expenses_df)
            exported_files.append(excel_path)

        # Update last/next export
        self.config.last_export = now
        self.config.next_export = self.calculate_next_export()

        return exported_files

    def _get_pdf_config(self):
        """Get PDF export config based on auto-export settings."""
        from exports.pdf_exporter import PDFReportConfig
        return PDFReportConfig(
            include_summary=self.config.include_summary,
            include_category_breakdown=self.config.include_category_breakdown
        )

    def _get_excel_config(self):
        """Get Excel export config based on auto-export settings."""
        from exports.excel_exporter import ExcelExportConfig
        return ExcelExportConfig(
            include_summary=self.config.include_summary,
            include_category_breakdown=self.config.include_category_breakdown,
            include_expenses=self.config.include_expense_list
        )
```

### Task 11.6.3: Create auto-export settings dialog
- [ ] Create `ui/dialogs/auto_export_dialog.py`:
  - Enable checkbox
  - Schedule options
  - Format checkboxes
  - Content options
  - Output path picker
  - Filename pattern
  - Run Now button

### Task 11.6.4: Integrate with startup
- [ ] Check for due exports on startup
- [ ] Run export in background
- [ ] Notify user when complete

---

## Completion Checklist

### Story 11.1: Undo/Redo
- [ ] UndoManager class created
- [ ] Action recording working
- [ ] Undo working
- [ ] Redo working
- [ ] Menu integration working
- [ ] Tests passing

### Story 11.2: Keyboard Navigation
- [ ] Shortcuts dialog created
- [ ] List navigation working
- [ ] Form navigation working

### Story 11.3: Enhanced Validation
- [ ] Enhanced summary dialog created
- [ ] User preferences working

### Story 11.4: Template Manager
- [ ] Enhanced dialog created
- [ ] Search and sort working
- [ ] Quick add buttons working

### Story 11.5: Print Support
- [ ] Print preview created
- [ ] Page setup working
- [ ] Print action working

### Story 11.6: Auto-Export
- [ ] AutoExporter class created
- [ ] Settings dialog created
- [ ] Startup integration working
- [ ] Background export working

---

## Implementation Notes

These stories are optional and can be implemented based on user feedback and priorities. They enhance the user experience but are not required for core functionality.

### Recommended Implementation Order

1. **Story 11.2: Keyboard Navigation** - Improves usability immediately
2. **Story 11.1: Undo/Redo** - Important safety feature
3. **Story 11.4: Template Manager** - Enhances productivity
4. **Story 11.3: Enhanced Validation** - Better error handling
5. **Story 11.5: Print Support** - Business need
6. **Story 11.6: Auto-Export** - Automation convenience

### Technical Considerations

- Undo/Redo requires careful integration with existing managers
- Print support may require platform-specific code
- Auto-export should run in background thread to not block UI
