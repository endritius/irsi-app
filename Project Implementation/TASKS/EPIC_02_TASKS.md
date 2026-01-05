# Epic 2: Expense Management (CRUD Operations) - Implementation Tasks

**Phase:** 4 (Core Features)
**Priority:** High
**Dependencies:** Epic 1, Epic 9, Epic 7
**Estimated Tasks:** 45+

---

## Story 2.1: ExpenseManager Class

**Prerequisites:** Epic 1 (models), Epic 7 (DataManager), Epic 9 (validators)

### Task 2.1.1: Create managers package
- [ ] Create `managers/__init__.py`:
```python
"""
Business logic managers for Beauty Salon Expense Manager.
"""

from .expense_manager import ExpenseManager
from .budget_manager import BudgetManager
from .filter_manager import FilterManager
from .template_manager import TemplateManager
from .recurring_handler import RecurringHandler

__all__ = [
    'ExpenseManager',
    'BudgetManager',
    'FilterManager',
    'TemplateManager',
    'RecurringHandler'
]
```

### Task 2.1.2: Create ExpenseManager class
- [ ] Create `managers/expense_manager.py`:
```python
"""
ExpenseManager - Manages all expense CRUD operations.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

import pandas as pd

from models.expense import Expense
from persistence.data_manager import DataManager
from utils.validators import validate_expense
from utils.exceptions import ValidationError, MultipleValidationError
from utils.error_handler import get_error_handler


class ExpenseManager:
    """
    Manages all expense CRUD operations.

    Maintains an in-memory cache of expenses for fast access
    and auto-saves after each modification.
    """

    def __init__(self, data_manager: DataManager):
        """
        Initialize with DataManager.

        Args:
            data_manager: DataManager instance for file operations
        """
        self.data_manager = data_manager
        self.error_handler = get_error_handler()

        # In-memory cache
        self._expenses: Dict[str, Expense] = {}
        self._vendors_cache: List[str] = []
        self._tags_cache: Set[str] = set()

        # Load expenses on init
        self.load_expenses()
```

### Task 2.1.3: Implement load/save methods
- [ ] Add load and save functionality:
```python
    def load_expenses(self) -> None:
        """Load expenses from CSV into memory cache."""
        df = self.data_manager.load_expenses()
        self._expenses = {}

        for _, row in df.iterrows():
            try:
                expense = Expense.from_dict(row.to_dict())
                self._expenses[expense.expense_id] = expense
            except Exception as e:
                self.error_handler.log_warning(
                    f"Failed to load expense: {row.get('expense_id')}: {e}"
                )

        self._update_caches()
        self.error_handler.log_info(f"Loaded {len(self._expenses)} expenses")

    def save_expenses(self) -> None:
        """Save all expenses to CSV."""
        data = [exp.to_dict() for exp in self._expenses.values()]
        df = pd.DataFrame(data)
        self.data_manager.save_expenses(df)

    def _update_caches(self) -> None:
        """Update vendor and tag caches."""
        active = self.get_all_expenses(include_deleted=False)

        # Update vendors cache (sorted by recency)
        vendors = {}
        for exp in active:
            if exp.vendor not in vendors or exp.date > vendors[exp.vendor]:
                vendors[exp.vendor] = exp.date
        self._vendors_cache = sorted(vendors.keys(), key=lambda v: vendors[v], reverse=True)

        # Update tags cache
        self._tags_cache = set()
        for exp in active:
            self._tags_cache.update(exp.tags)
```

### Task 2.1.4: Implement CRUD operations
- [ ] Add create, read, update, delete methods:
```python
    def add_expense(self, expense: Expense) -> str:
        """
        Add new expense.

        Args:
            expense: Expense object to add

        Returns:
            expense_id of the added expense

        Raises:
            MultipleValidationError: If validation fails
        """
        # Validate
        errors = validate_expense(expense)
        if errors:
            error = MultipleValidationError()
            for field, msg in errors:
                error.add_error(field, msg)
            raise error

        # Generate ID if needed
        if not expense.expense_id:
            expense.expense_id = str(uuid.uuid4())

        # Set timestamps
        now = datetime.now()
        expense.created_at = now
        expense.updated_at = now

        # Add to cache
        self._expenses[expense.expense_id] = expense
        self._update_caches()

        # Auto-save
        self.save_expenses()

        self.error_handler.log_info(f"Added expense: {expense.expense_id}")
        return expense.expense_id

    def get_expense(self, expense_id: str) -> Optional[Expense]:
        """Get single expense by ID."""
        return self._expenses.get(expense_id)

    def update_expense(self, expense_id: str, updates: Dict) -> bool:
        """
        Update expense fields.

        Args:
            expense_id: ID of expense to update
            updates: Dictionary of field updates

        Returns:
            True on success
        """
        expense = self._expenses.get(expense_id)
        if not expense:
            return False

        # Apply updates
        for field, value in updates.items():
            if hasattr(expense, field):
                setattr(expense, field, value)

        expense.updated_at = datetime.now()

        # Validate
        errors = validate_expense(expense)
        if errors:
            error = MultipleValidationError()
            for field, msg in errors:
                error.add_error(field, msg)
            raise error

        # Update cache and save
        self._expenses[expense_id] = expense
        self._update_caches()
        self.save_expenses()

        self.error_handler.log_info(f"Updated expense: {expense_id}")
        return True

    def delete_expense(self, expense_id: str, permanent: bool = False) -> bool:
        """
        Delete expense (soft or permanent).

        Args:
            expense_id: ID of expense to delete
            permanent: If True, permanently delete

        Returns:
            True on success
        """
        expense = self._expenses.get(expense_id)
        if not expense:
            return False

        if permanent:
            del self._expenses[expense_id]
            self.error_handler.log_info(f"Permanently deleted expense: {expense_id}")
        else:
            expense.is_deleted = True
            expense.deleted_at = datetime.now()
            expense.updated_at = datetime.now()
            self.error_handler.log_info(f"Soft deleted expense: {expense_id}")

        self._update_caches()
        self.save_expenses()
        return True

    def restore_expense(self, expense_id: str) -> bool:
        """Restore a soft-deleted expense."""
        expense = self._expenses.get(expense_id)
        if not expense or not expense.is_deleted:
            return False

        expense.is_deleted = False
        expense.deleted_at = None
        expense.updated_at = datetime.now()

        self._update_caches()
        self.save_expenses()

        self.error_handler.log_info(f"Restored expense: {expense_id}")
        return True

    def bulk_delete(self, expense_ids: List[str], permanent: bool = False) -> int:
        """Delete multiple expenses. Returns count deleted."""
        deleted = 0
        for expense_id in expense_ids:
            if self.delete_expense(expense_id, permanent):
                deleted += 1
        return deleted
```

### Task 2.1.5: Implement query methods
- [ ] Add query and utility methods:
```python
    def get_all_expenses(self, include_deleted: bool = False) -> List[Expense]:
        """Get all expenses (optionally including deleted)."""
        if include_deleted:
            return list(self._expenses.values())
        return [e for e in self._expenses.values() if not e.is_deleted]

    def get_deleted_expenses(self) -> List[Expense]:
        """Get only soft-deleted expenses."""
        return [e for e in self._expenses.values() if e.is_deleted]

    def get_expenses_dataframe(self, include_deleted: bool = False) -> pd.DataFrame:
        """Get expenses as DataFrame for analysis."""
        expenses = self.get_all_expenses(include_deleted)
        if not expenses:
            return pd.DataFrame()
        return pd.DataFrame([e.to_dict() for e in expenses])

    def get_unique_vendors(self) -> List[str]:
        """Get sorted list of unique vendors (most recent first)."""
        return self._vendors_cache.copy()

    def get_unique_tags(self) -> Set[str]:
        """Get set of all used tags."""
        return self._tags_cache.copy()

    def find_duplicates(self, expense: Expense, days_threshold: int = 3) -> List[Expense]:
        """Find potential duplicate expenses."""
        duplicates = []
        threshold_start = expense.date - timedelta(days=days_threshold)
        threshold_end = expense.date + timedelta(days=days_threshold)

        for exp in self.get_all_expenses():
            if exp.expense_id == expense.expense_id:
                continue
            if (exp.vendor == expense.vendor and
                exp.amount == expense.amount and
                threshold_start <= exp.date <= threshold_end):
                duplicates.append(exp)

        return duplicates

    def get_recurring_expenses(self) -> List[Expense]:
        """Get all recurring expense definitions."""
        return [e for e in self.get_all_expenses() if e.is_recurring]

    def get_due_recurring_expenses(self) -> List[Expense]:
        """Get recurring expenses due for generation/reminder."""
        today = datetime.now().date()
        due = []
        for exp in self.get_recurring_expenses():
            if exp.next_due_date and exp.next_due_date.date() <= today:
                due.append(exp)
        return due
```

### Task 2.1.6: Create ExpenseManager tests
- [ ] Create `tests/test_managers/__init__.py`
- [ ] Create `tests/test_managers/test_expense_manager.py`

---

## Story 2.2: Add Expense GUI Form

**Prerequisites:** Story 2.1, Epic 1

### Task 2.2.1: Create UI package structure
- [ ] Create `ui/__init__.py`
- [ ] Create `ui/forms/__init__.py`

### Task 2.2.2: Create ExpenseForm class
- [ ] Create `ui/forms/expense_form.py` with form fields:
  - Amount entry with validation
  - Date picker (tkcalendar.DateEntry)
  - Category/Subcategory dropdowns
  - Vendor entry with autocomplete
  - Payment method dropdown
  - Description text area
  - Tags entry
  - Recurring options (collapsible)
  - Save/Clear/Cancel buttons

### Task 2.2.3: Implement form validation UI
- [ ] Red border on invalid fields
- [ ] Error message display
- [ ] Disable Save until valid

### Task 2.2.4: Implement vendor autocomplete
- [ ] Show dropdown with matching vendors (min 2 chars)
- [ ] "Recent:" section with 5 most recent vendors
- [ ] Source from ExpenseManager.get_unique_vendors()

### Task 2.2.5: Implement save flow
- [ ] Validate all fields
- [ ] Check for duplicates
- [ ] Save expense
- [ ] Show success toast
- [ ] Option to add another or close

---

## Story 2.3: View Expenses List

**Prerequisites:** Story 2.1

### Task 2.3.1: Create expense list view
- [ ] Create `ui/views/__init__.py`
- [ ] Create `ui/views/expense_list.py`:
  - Summary bar (Total, Count, Average)
  - Search box with real-time filtering
  - Treeview table with columns
  - Pagination controls

### Task 2.3.2: Implement table features
- [ ] Alternating row colors
- [ ] Multi-select (Ctrl+Click, Shift+Click)
- [ ] Recurring expense indicator
- [ ] Right-click context menu

### Task 2.3.3: Implement pagination
- [ ] 50 items per page
- [ ] First/Prev/Next/Last navigation
- [ ] Page number display

---

## Story 2.4: Edit Expense

**Prerequisites:** Story 2.2

### Task 2.4.1: Implement edit mode for expense form
- [ ] Pre-populate fields with existing values
- [ ] Show read-only metadata (ID, Created, Updated)
- [ ] Visual "Edit Mode" indication
- [ ] Track and highlight modified fields

### Task 2.4.2: Implement change warnings
- [ ] Warn if amount changes by >50%
- [ ] Confirmation dialog for significant changes

---

## Story 2.5: Delete Expense

**Prerequisites:** Story 2.1

### Task 2.5.1: Implement soft delete
- [ ] Confirmation dialog
- [ ] Mark is_deleted = True
- [ ] Remove from main list

### Task 2.5.2: Implement permanent delete
- [ ] Additional confirmation
- [ ] Remove from database completely

### Task 2.5.3: Implement bulk delete
- [ ] Multi-select support
- [ ] Count and total in confirmation
- [ ] Progress for large batches

### Task 2.5.4: Implement keyboard support
- [ ] Delete key: soft delete
- [ ] Shift+Delete: permanent delete (with confirmation)

---

## Story 2.6: Expense Details Dialog

**Prerequisites:** Story 2.1

### Task 2.6.1: Create expense details dialog
- [ ] Create `ui/dialogs/__init__.py`
- [ ] Create `ui/dialogs/expense_details.py`:
  - Header with vendor and amount
  - Details grid
  - Tags as chips
  - Recurring info (if applicable)
  - Metadata section
  - Action buttons (Edit, Delete, Copy, Close)

---

## Story 2.7: Deleted Items View

**Prerequisites:** Story 2.5

### Task 2.7.1: Create deleted items view
- [ ] Create `ui/views/deleted_items.py`:
  - List of soft-deleted expenses
  - Deleted On column
  - Restore/Permanent Delete buttons
  - Bulk actions

### Task 2.7.2: Implement auto-cleanup option
- [ ] Setting for auto-delete after X days
- [ ] Cleanup on startup

---

## Story 2.8: Empty State Handling

**Prerequisites:** Story 2.3

### Task 2.8.1: Create empty state components
- [ ] Create `ui/components/__init__.py`
- [ ] Create `ui/components/empty_state.py`:
  - No expenses state
  - No search results state
  - No filtered results state

---

## Story 2.9: Duplicate Expense Detection

**Prerequisites:** Story 2.1, Story 2.2

### Task 2.9.1: Implement duplicate detection
- [ ] Check on save for similar expenses
- [ ] Show warning dialog with comparison
- [ ] Options: View Existing, Save Anyway, Cancel

### Task 2.9.2: Add duplicate settings
- [ ] Enable/disable in settings
- [ ] Configurable days threshold

---

## Story 2.10: Quick Add Templates

**Prerequisites:** Story 2.2, Epic 7

### Task 2.10.1: Create ExpenseTemplate model
- [ ] Create `models/template.py` with ExpenseTemplate dataclass:
```python
@dataclass
class ExpenseTemplate:
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = ""
    subcategory: str = ""
    vendor: str = ""
    typical_amount: float = 0.0
    payment_method: str = "Cash"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    use_count: int = 0
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, data: dict) -> 'ExpenseTemplate'
    def to_expense(self, date: datetime, amount: float = None) -> 'Expense'
    def increment_usage(self) -> None
```

### Task 2.10.2: Create TemplateManager
- [ ] Create `managers/template_manager.py`:
```python
"""
TemplateManager - Manages expense templates for quick entry.
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid

from models.template import ExpenseTemplate
from persistence.data_manager import DataManager
from utils.error_handler import get_error_handler


class TemplateManager:
    """Manages expense templates for quick entry."""

    def __init__(self, data_manager: DataManager):
        """Initialize with DataManager."""
        self.data_manager = data_manager
        self.error_handler = get_error_handler()
        self._templates: Dict[str, ExpenseTemplate] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """Load templates from storage."""
        df = self.data_manager.load_templates()
        for _, row in df.iterrows():
            try:
                template = ExpenseTemplate.from_dict(row.to_dict())
                self._templates[template.template_id] = template
            except Exception as e:
                self.error_handler.log_warning(f"Failed to load template: {e}")

    def save_templates(self) -> None:
        """Save all templates to storage."""
        import pandas as pd
        data = [t.to_dict() for t in self._templates.values()]
        df = pd.DataFrame(data)
        self.data_manager.save_templates(df)

    def get_all_templates(self) -> List[ExpenseTemplate]:
        """Get all templates."""
        return list(self._templates.values())

    def get_template(self, template_id: str) -> Optional[ExpenseTemplate]:
        """Get template by ID."""
        return self._templates.get(template_id)

    def get_top_templates(self, limit: int = 5) -> List[ExpenseTemplate]:
        """Get most-used templates."""
        templates = sorted(
            self._templates.values(),
            key=lambda t: t.use_count,
            reverse=True
        )
        return templates[:limit]

    def add_template(self, template: ExpenseTemplate) -> str:
        """Add new template."""
        if not template.template_id:
            template.template_id = str(uuid.uuid4())
        self._templates[template.template_id] = template
        self.save_templates()
        return template.template_id

    def update_template(self, template_id: str, updates: Dict) -> bool:
        """Update existing template."""
        template = self._templates.get(template_id)
        if not template:
            return False
        for key, value in updates.items():
            if hasattr(template, key):
                setattr(template, key, value)
        self.save_templates()
        return True

    def delete_template(self, template_id: str) -> bool:
        """Delete template."""
        if template_id in self._templates:
            del self._templates[template_id]
            self.save_templates()
            return True
        return False

    def create_from_expense(self, expense, name: str) -> ExpenseTemplate:
        """Create template from an expense."""
        template = ExpenseTemplate(
            template_id=str(uuid.uuid4()),
            name=name,
            category=expense.category,
            subcategory=expense.subcategory,
            vendor=expense.vendor,
            payment_method=expense.payment_method,
            description=expense.description,
            typical_amount=expense.amount,
            tags=expense.tags.copy() if expense.tags else []
        )
        self.add_template(template)
        return template

    def search_templates(self, query: str) -> List[ExpenseTemplate]:
        """Search templates by name, vendor, or category."""
        query = query.lower()
        return [
            t for t in self._templates.values()
            if query in t.name.lower() or
               query in t.vendor.lower() or
               query in t.category.lower()
        ]
```

### Task 2.10.3: Create template UI
- [ ] Quick add button/menu
- [ ] Template selection dialog
- [ ] Template manager dialog

---

## Completion Checklist

### Story 2.1: ExpenseManager
- [ ] Class created with all methods
- [ ] In-memory cache working
- [ ] CRUD operations working
- [ ] Auto-save working
- [ ] Vendor/tag caches working
- [ ] Duplicate detection working
- [ ] Tests passing

### Story 2.2-2.9: UI Components
- [ ] Expense form created
- [ ] Expense list view working
- [ ] Edit mode working
- [ ] Delete (soft/permanent) working
- [ ] Details dialog working
- [ ] Deleted items view working
- [ ] Empty states implemented
- [ ] Duplicate warnings working

### Story 2.10: Templates
- [ ] ExpenseTemplate model created
- [ ] TemplateManager created
- [ ] Template UI components created
- [ ] Create from expense working
- [ ] Tests passing

---

## Next Steps

After completing Epic 2, proceed to:
- **Epic 3: Filtering & Sorting** - Uses ExpenseManager
